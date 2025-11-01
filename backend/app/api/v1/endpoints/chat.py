"""Chat API endpoints."""
import json
import logging
import asyncio
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from anthropic import Anthropic
from anthropic import APIError

from app.api.deps import get_db
from app.models.user import User
from app.models.brand import Brand
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.template import Template
from app.models.dom_selector import DOMSelector
from app.models.code_rule import CodeRule
from app.models.generated_code import GeneratedCode
from app.models.enums import TestType, PageType, SelectorStatus, ValidationStatus, ConversationStatus, BrandRole, NotificationType
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationPreview,
    ConversationHistoryResponse,
    MessageResponse
)
from app.schemas.generated_code import GeneratedCodeResponse
from app.core.auth import get_current_user_dependency
from app.core.prompts.chat_prompt import build_chat_prompt, build_conversation_messages
from app.services.code_generator import CodeGeneratorService
from app.services.notification_service import NotificationService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def parse_claude_response(response_text: str) -> dict:
    """Parse Claude API response JSON."""
    # Strip markdown code block markers if present
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response as JSON: {e}")
        logger.error(f"Response text: {text[:200]}")
        # Return fallback response
        return {
            "message": response_text[:500] if response_text else "I'm having trouble processing that. Could you rephrase?",
            "ready_to_generate": False
        }


@router.post("/message", response_model=ChatMessageResponse, status_code=status.HTTP_200_OK)
async def send_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Send a chat message and get assistant response."""
    try:
        # Get or create conversation
        if request.conversation_id:
            # Get existing conversation
            conv_result = await db.execute(
                select(Conversation).where(Conversation.id == request.conversation_id)
            )
            conversation = conv_result.scalar_one_or_none()
            
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            
            # Verify user owns conversation
            if conversation.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this conversation"
                )
        else:
            # Create new conversation
            if not current_user.brand_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must have a brand_id to create conversations"
                )
            
            conversation = Conversation(
                user_id=current_user.id,
                brand_id=current_user.brand_id,
                status=ConversationStatus.ACTIVE
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        await db.commit()
        
        # Get user's brand
        if not conversation.brand_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation must have a brand_id"
            )
        
        brand_result = await db.execute(
            select(Brand).where(Brand.id == conversation.brand_id)
        )
        brand = brand_result.scalar_one_or_none()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found"
            )
        
        # Get conversation history
        messages_result = await db.execute(
            select(Message).where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        )
        messages = messages_result.scalars().all()
        
        # Build conversation history (exclude current user message for prompt)
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages[:-1]  # Exclude the message we just added
        ]
        
        # Get available test types and page types
        test_types = [t.value for t in TestType]
        page_types = [p.value for p in PageType]
        
        # Build chat prompt
        system_prompt = build_chat_prompt(
            conversation_history=conversation_history,
            brand_name=brand.name,
            brand_domain=brand.domain,
            test_types=test_types,
            page_types=page_types
        )
        
        # Build messages for Claude
        claude_messages = build_conversation_messages(
            conversation_history=conversation_history,
            user_message=request.message
        )
        
        # Call Claude API
        try:
            anthropic_client = Anthropic(api_key=str(settings.ANTHROPIC_API_KEY).strip())
            
            response = await asyncio.to_thread(
                anthropic_client.messages.create,
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system_prompt,
                messages=claude_messages
            )
            
            # Extract text from response
            content = response.content
            if isinstance(content, list):
                text = ""
                for block in content:
                    if hasattr(block, 'text'):
                        text += block.text
                    elif isinstance(block, str):
                        text += block
            elif hasattr(content, 'text'):
                text = content.text
            elif isinstance(content, str):
                text = content
            else:
                text = str(content)
            
            # Parse Claude response
            claude_data = parse_claude_response(text)
            
            assistant_message_text = claude_data.get("message", "I'm sorry, I didn't understand that.")
            ready_to_generate = claude_data.get("ready_to_generate", False)
            extracted_params = claude_data.get("extracted_params", {})
            
        except APIError as e:
            logger.error(f"Claude API error: {str(e)}")
            assistant_message_text = "I'm having trouble connecting right now. Please try again."
            ready_to_generate = False
            extracted_params = {}
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            assistant_message_text = "I'm having trouble processing that. Could you try again?"
            ready_to_generate = False
            extracted_params = {}
        
        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_message_text
        )
        db.add(assistant_message)
        
        generated_code_response = None
        confidence_score = None
        response_status = "gathering_info"
        
        # If ready to generate, generate code
        if ready_to_generate and extracted_params:
            try:
                test_type_str = extracted_params.get("test_type", "").lower()
                page_type_str = extracted_params.get("page_type", "").lower()
                
                # Validate test_type
                try:
                    test_type_enum = TestType(test_type_str)
                except ValueError:
                    logger.warning(f"Invalid test_type: {test_type_str}, skipping code generation")
                    test_type_enum = None
                
                if test_type_enum:
                    # Query templates
                    templates_result = await db.execute(
                        select(Template).where(
                            Template.brand_id == brand.id,
                            Template.test_type == test_type_enum,
                            Template.is_active == True
                        )
                    )
                    templates = templates_result.scalars().all()
                    
                    # Query selectors
                    try:
                        page_type_enum = PageType(page_type_str)
                    except ValueError:
                        page_type_enum = None
                    
                    selectors = []
                    if page_type_enum:
                        selectors_result = await db.execute(
                            select(DOMSelector).where(
                                DOMSelector.brand_id == brand.id,
                                DOMSelector.page_type == page_type_enum,
                                DOMSelector.status == SelectorStatus.ACTIVE
                            )
                        )
                        selectors = selectors_result.scalars().all()
                    
                    # Query rules
                    rules_result = await db.execute(
                        select(CodeRule).where(CodeRule.brand_id == brand.id)
                    )
                    rules = rules_result.scalars().all()
                    
                    # Prepare data for code generator
                    brand_context = {
                        "name": brand.name,
                        "domain": brand.domain,
                        "id": brand.id,
                        "config": brand.config or {}
                    }
                    
                    templates_data = [
                        {
                            "test_type": t.test_type.value,
                            "template_code": t.template_code,
                            "description": t.description
                        }
                        for t in templates
                    ]
                    
                    selectors_data = [
                        {
                            "selector": s.selector,
                            "description": s.description
                        }
                        for s in selectors
                    ]
                    
                    rules_data = [
                        {
                            "rule_type": r.rule_type.value,
                            "rule_content": r.rule_content,
                            "priority": r.priority
                        }
                        for r in rules
                    ]
                    
                    # Build test description from conversation
                    test_description = " ".join([
                        msg.content for msg in messages
                        if msg.role == "user"
                    ])
                    
                    # Generate code
                    code_generator = CodeGeneratorService()
                    result = await code_generator.generate_code(
                        brand_context=brand_context,
                        templates=templates_data,
                        selectors=selectors_data,
                        rules=rules_data,
                        test_description=test_description
                    )
                    
                    # Defensive check: if result is a string (shouldn't happen, but handle it)
                    if isinstance(result, str):
                        logger.warning("CodeGeneratorService returned string instead of dict, attempting to parse")
                        try:
                            result = json.loads(result)
                        except json.JSONDecodeError:
                            logger.error("Failed to parse result as JSON, using as code string")
                            result = {"generated_code": result, "confidence_score": 0.5}
                    
                    # Ensure result is a dict
                    if not isinstance(result, dict):
                        logger.error(f"CodeGeneratorService returned unexpected type: {type(result)}")
                        result = {"generated_code": str(result), "confidence_score": 0.5}
                    
                    # Extract the generated code
                    # CodeGeneratorService now returns raw JavaScript (preferred) or handles JSON parsing internally
                    code_string = result.get("generated_code", "")
                    
                    # Log the raw result for debugging
                    logger.debug(f"Code generator result type: {type(code_string)}, length: {len(str(code_string)) if code_string else 0}")
                    
                    # Ensure code_string is a string and not None
                    if not code_string:
                        logger.error("Generated code is empty after processing!")
                        code_string = ""
                    else:
                        code_string = str(code_string).strip()
                        logger.debug(f"Final code_string length: {len(code_string)}, first 100 chars: {code_string[:100]}")
                    
                    # Extract usage data and calculate cost
                    prompt_tokens = result.get("prompt_tokens", 0)
                    completion_tokens = result.get("completion_tokens", 0)
                    total_tokens = result.get("total_tokens", 0)
                    
                    # Calculate LLM cost
                    from app.core.constants import calculate_llm_cost
                    llm_cost_usd = calculate_llm_cost(prompt_tokens, completion_tokens) if prompt_tokens > 0 or completion_tokens > 0 else None
                    
                    # Save generated code
                    generated_code_record = GeneratedCode(
                        brand_id=brand.id,
                        conversation_id=conversation.id,
                        user_id=current_user.id,
                        request_data={
                            "extracted_params": extracted_params,
                            "conversation_id": str(conversation.id),
                            "implementation_notes": result.get("implementation_notes"),
                            "testing_checklist": result.get("testing_checklist")
                        },
                        generated_code=code_string,
                        confidence_score=result.get("confidence_score"),
                        validation_status=ValidationStatus.PENDING,
                        prompt_tokens=prompt_tokens if prompt_tokens > 0 else None,
                        completion_tokens=completion_tokens if completion_tokens > 0 else None,
                        total_tokens=total_tokens if total_tokens > 0 else None,
                        llm_cost_usd=llm_cost_usd
                    )
                    
                    db.add(generated_code_record)
                    await db.commit()
                    await db.refresh(generated_code_record)
                    
                    # Notify brand admins about new code that needs review
                    # Get brand admins for this brand
                    admin_query = select(User).where(
                        User.brand_id == generated_code_record.brand_id,
                        User.brand_role == BrandRole.BRAND_ADMIN.value
                    )
                    result = await db.execute(admin_query)
                    brand_admins = result.scalars().all()
                    
                    # Create notification for each brand admin
                    for admin in brand_admins:
                        # Extract change description from request data
                        change_description = generated_code_record.request_data.get('extracted_params', {}).get('change_description', 'Code generation request')
                        user_display_name = current_user.name or current_user.email
                        
                        await NotificationService.create_notification(
                            db=db,
                            user_id=admin.id,
                            generated_code_id=generated_code_record.id,
                            notification_type=NotificationType.CODE_NEEDS_REVIEW.value,
                            title="New Code Needs Review",
                            message=f"New code request from {user_display_name}: {change_description}"
                        )
                    
                    # Link message to generated code
                    assistant_message.generated_code_id = generated_code_record.id
                    
                    # Update conversation status
                    conversation.status = ConversationStatus.COMPLETED
                    
                    # Create response
                    generated_code_response = GeneratedCodeResponse(
                        id=generated_code_record.id,
                        brand_id=generated_code_record.brand_id,
                        generated_code=generated_code_record.generated_code,
                        confidence_score=generated_code_record.confidence_score,
                        validation_status=generated_code_record.validation_status,
                        deployment_status=generated_code_record.deployment_status,
                        created_at=generated_code_record.created_at,
                        request_data=generated_code_record.request_data,
                        user_feedback=generated_code_record.user_feedback,
                        error_logs=generated_code_record.error_logs
                    )
                    confidence_score = result["confidence_score"]
                    response_status = "code_generated"
                    
            except Exception as e:
                logger.error(f"Error generating code: {str(e)}", exc_info=True)
                # Continue with assistant message but don't generate code
        
        await db.commit()
        await db.refresh(conversation)
        
        return ChatMessageResponse(
            conversation_id=conversation.id,
            message=assistant_message_text,
            generated_code=generated_code_response,
            confidence_score=confidence_score,
            status=response_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your message"
        )


@router.get("/conversations", response_model=List[ConversationPreview], status_code=status.HTTP_200_OK)
async def list_conversations(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """List all conversations for the current user."""
    # Get conversations for current user
    conversations_result = await db.execute(
        select(Conversation).where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = conversations_result.scalars().all()
    
    # Build response with preview and last message
    result = []
    for conv in conversations:
        # Get first user message for preview
        first_user_msg_result = await db.execute(
            select(Message).where(
                Message.conversation_id == conv.id,
                Message.role == "user"
            ).order_by(Message.created_at).limit(1)
        )
        first_user_msg = first_user_msg_result.scalar_one_or_none()
        preview = first_user_msg.content[:100] if first_user_msg else "New conversation"
        
        # Get last message
        last_msg_result = await db.execute(
            select(Message).where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc()).limit(1)
        )
        last_msg = last_msg_result.scalar_one_or_none()
        last_message = last_msg.content[:100] if last_msg else None
        
        result.append(ConversationPreview(
            id=conv.id,
            preview=preview,
            last_message=last_message,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            status=ConversationStatus(conv.status)
        ))
    
    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse, status_code=status.HTTP_200_OK)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get full conversation history."""
    # Get conversation
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Verify user owns conversation
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this conversation"
        )
    
    # Get all messages
    messages_result = await db.execute(
        select(Message).where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()
    
    # Get generated code if any message has it
    generated_code_record = None
    for msg in messages:
        if msg.generated_code_id:
            code_result = await db.execute(
                select(GeneratedCode).where(GeneratedCode.id == msg.generated_code_id)
            )
            generated_code_record = code_result.scalar_one_or_none()
            break
    
    # Build response
    message_responses = [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at,
            generated_code_id=msg.generated_code_id
        )
        for msg in messages
    ]
    
    generated_code_response = None
    if generated_code_record:
        generated_code_response = GeneratedCodeResponse(
            id=generated_code_record.id,
            brand_id=generated_code_record.brand_id,
            generated_code=generated_code_record.generated_code,
            confidence_score=generated_code_record.confidence_score,
            validation_status=generated_code_record.validation_status,
            deployment_status=generated_code_record.deployment_status,
            created_at=generated_code_record.created_at,
            request_data=generated_code_record.request_data,
            user_feedback=generated_code_record.user_feedback,
            error_logs=generated_code_record.error_logs
        )
    
    return ConversationHistoryResponse(
        conversation_id=conversation.id,
        messages=message_responses,
        generated_code=generated_code_response,
        status=ConversationStatus(conversation.status),
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )

