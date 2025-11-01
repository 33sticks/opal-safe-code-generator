"""Analytics API endpoints."""
from typing import List, Optional
from datetime import date, datetime
import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_, or_, distinct, cast, Date
from sqlalchemy.orm import joinedload

from app.api.deps import get_db
from app.models.generated_code import GeneratedCode
from app.models.user import User
from app.models.brand import Brand
from app.models.enums import CodeStatus, BrandRole
from app.schemas.analytics import (
    AnalyticsOverview,
    UsageDataPoint,
    QualityMetrics,
    BrandPerformance,
    UserActivity,
    LLMCostMetrics,
    BrandLLMCost
)
from app.core.auth import get_current_user_dependency, require_admin, get_user_brand_access

router = APIRouter()
logger = logging.getLogger(__name__)


def _apply_date_filter(query, start_date: Optional[date], end_date: Optional[date]):
    """Apply date filtering to query."""
    if start_date:
        query = query.where(GeneratedCode.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.where(GeneratedCode.created_at <= datetime.combine(end_date, datetime.max.time()))
    return query


def _apply_brand_filter(query, brand_ids: List[int], brand_id: Optional[int]):
    """Apply brand filtering to query."""
    if brand_id:
        query = query.where(GeneratedCode.brand_id == brand_id)
    elif brand_ids:  # Brand admin with specific brands
        query = query.where(GeneratedCode.brand_id.in_(brand_ids))
    # Super admin: no filter (see all brands)
    return query


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(
    start_date: Optional[date] = Query(None, description="Start date for period"),
    end_date: Optional[date] = Query(None, description="End date for period"),
    brand_id: Optional[int] = Query(None, description="Filter by brand ID (super admin only)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get analytics overview metrics."""
    brand_ids = get_user_brand_access(current_user)  # Returns [] for super_admin, [brand_id] for brand_admin
    
    logger.info(f"Querying analytics overview with filters: start={start_date}, end={end_date}, brand={brand_id}, brand_ids={brand_ids}")
    
    # Total code generations - build query directly instead of using subquery
    total_query = select(func.count(GeneratedCode.id))
    total_query = _apply_date_filter(total_query, start_date, end_date)
    total_query = _apply_brand_filter(total_query, brand_ids, brand_id)
    
    total_result = await db.execute(total_query)
    total_code_generations = total_result.scalar() or 0
    
    logger.info(f"Total code generations found: {total_code_generations}")
    
    # Active users (distinct users who generated code)
    active_users_query = select(func.count(distinct(GeneratedCode.user_id)))
    active_users_query = _apply_date_filter(active_users_query, start_date, end_date)
    active_users_query = _apply_brand_filter(active_users_query, brand_ids, brand_id)
    active_users_query = active_users_query.where(GeneratedCode.user_id.isnot(None))
    active_users_result = await db.execute(active_users_query)
    active_users = active_users_result.scalar() or 0
    
    # Average confidence
    avg_conf_query = select(func.avg(GeneratedCode.confidence_score))
    avg_conf_query = _apply_date_filter(avg_conf_query, start_date, end_date)
    avg_conf_query = _apply_brand_filter(avg_conf_query, brand_ids, brand_id)
    avg_conf_query = avg_conf_query.where(GeneratedCode.confidence_score.isnot(None))
    avg_conf_result = await db.execute(avg_conf_query)
    average_confidence = float(avg_conf_result.scalar() or 0.0)
    
    # Approval rate
    approved_query = select(func.count(GeneratedCode.id))
    approved_query = _apply_date_filter(approved_query, start_date, end_date)
    approved_query = _apply_brand_filter(approved_query, brand_ids, brand_id)
    approved_query = approved_query.where(GeneratedCode.status == CodeStatus.APPROVED.value)
    approved_result = await db.execute(approved_query)
    approved_count = approved_result.scalar() or 0
    
    # Rejection rate
    rejected_query = select(func.count(GeneratedCode.id))
    rejected_query = _apply_date_filter(rejected_query, start_date, end_date)
    rejected_query = _apply_brand_filter(rejected_query, brand_ids, brand_id)
    rejected_query = rejected_query.where(GeneratedCode.status == CodeStatus.REJECTED.value)
    rejected_result = await db.execute(rejected_query)
    rejected_count = rejected_result.scalar() or 0
    
    # Calculate rates
    approval_rate = (approved_count / total_code_generations * 100) if total_code_generations > 0 else 0.0
    rejection_rate = (rejected_count / total_code_generations * 100) if total_code_generations > 0 else 0.0
    
    return AnalyticsOverview(
        total_code_generations=total_code_generations,
        active_users=active_users,
        average_confidence=average_confidence,
        approval_rate=round(approval_rate, 2),
        rejection_rate=round(rejection_rate, 2),
        period_start=start_date,
        period_end=end_date
    )


@router.get("/usage-over-time", response_model=List[UsageDataPoint])
async def get_usage_over_time(
    start_date: Optional[date] = Query(None, description="Start date for period"),
    end_date: Optional[date] = Query(None, description="End date for period"),
    brand_id: Optional[int] = Query(None, description="Filter by brand ID (super admin only)"),
    interval: str = Query("day", description="Grouping interval: day, week, or month"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get code generation counts over time."""
    brand_ids = get_user_brand_access(current_user)
    
    # Determine date truncation function based on interval
    if interval == "week":
        date_trunc = func.date_trunc('week', GeneratedCode.created_at)
    elif interval == "month":
        date_trunc = func.date_trunc('month', GeneratedCode.created_at)
    else:  # default to day
        date_trunc = cast(GeneratedCode.created_at, Date)
    
    # Build query
    query = select(
        date_trunc.label('date'),
        func.count(GeneratedCode.id).label('count')
    )
    
    query = _apply_date_filter(query, start_date, end_date)
    query = _apply_brand_filter(query, brand_ids, brand_id)
    
    # Group by date (using label reference)
    query = query.group_by(date_trunc.label('date')).order_by(date_trunc.label('date'))
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        UsageDataPoint(
            date=row.date.date() if hasattr(row.date, 'date') else row.date,
            count=row.count,
            brand_name=None
        )
        for row in rows
    ]


@router.get("/quality-metrics", response_model=QualityMetrics)
async def get_quality_metrics(
    start_date: Optional[date] = Query(None, description="Start date for period"),
    end_date: Optional[date] = Query(None, description="End date for period"),
    brand_id: Optional[int] = Query(None, description="Filter by brand ID (super admin only)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get quality metrics including confidence distribution and status breakdown."""
    brand_ids = get_user_brand_access(current_user)
    
    # Base query for filtering
    base_query = select(GeneratedCode)
    base_query = _apply_date_filter(base_query, start_date, end_date)
    base_query = _apply_brand_filter(base_query, brand_ids, brand_id)
    
    # Average confidence
    avg_conf_query = select(func.avg(GeneratedCode.confidence_score))
    avg_conf_query = _apply_date_filter(avg_conf_query, start_date, end_date)
    avg_conf_query = _apply_brand_filter(avg_conf_query, brand_ids, brand_id)
    avg_conf_query = avg_conf_query.where(GeneratedCode.confidence_score.isnot(None))
    avg_conf_result = await db.execute(avg_conf_query)
    average_confidence = float(avg_conf_result.scalar() or 0.0)
    
    # Confidence distribution (0-20%, 20-40%, 40-60%, 60-80%, 80-100%)
    conf_dist_query = select(
        case(
            (GeneratedCode.confidence_score < 0.2, '0-20%'),
            ((GeneratedCode.confidence_score >= 0.2) & (GeneratedCode.confidence_score < 0.4), '20-40%'),
            ((GeneratedCode.confidence_score >= 0.4) & (GeneratedCode.confidence_score < 0.6), '40-60%'),
            ((GeneratedCode.confidence_score >= 0.6) & (GeneratedCode.confidence_score < 0.8), '60-80%'),
            (GeneratedCode.confidence_score >= 0.8, '80-100%'),
            else_='unknown'
        ).label('range'),
        func.count(GeneratedCode.id).label('count')
    )
    conf_dist_query = _apply_date_filter(conf_dist_query, start_date, end_date)
    conf_dist_query = _apply_brand_filter(conf_dist_query, brand_ids, brand_id)
    conf_dist_query = conf_dist_query.where(GeneratedCode.confidence_score.isnot(None))
    conf_dist_query = conf_dist_query.group_by('range')
    
    conf_dist_result = await db.execute(conf_dist_query)
    conf_dist_rows = conf_dist_result.all()
    confidence_distribution = {row.range: row.count for row in conf_dist_rows}
    
    # Status breakdown
    status_query = select(
        GeneratedCode.status,
        func.count(GeneratedCode.id).label('count')
    )
    status_query = _apply_date_filter(status_query, start_date, end_date)
    status_query = _apply_brand_filter(status_query, brand_ids, brand_id)
    status_query = status_query.group_by(GeneratedCode.status)
    
    status_result = await db.execute(status_query)
    status_rows = status_result.all()
    status_breakdown = {row.status: row.count for row in status_rows}
    
    return QualityMetrics(
        confidence_distribution=confidence_distribution,
        status_breakdown=status_breakdown,
        average_confidence=average_confidence
    )


@router.get("/brand-performance", response_model=List[BrandPerformance])
async def get_brand_performance(
    start_date: Optional[date] = Query(None, description="Start date for period"),
    end_date: Optional[date] = Query(None, description="End date for period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get performance metrics by brand."""
    brand_ids = get_user_brand_access(current_user)
    
    # Build base query with brand join
    query = select(
        Brand.id.label('brand_id'),
        Brand.name.label('brand_name'),
        func.count(GeneratedCode.id).label('code_generations'),
        func.avg(GeneratedCode.confidence_score).label('avg_confidence')
    ).join(GeneratedCode, Brand.id == GeneratedCode.brand_id)
    
    query = _apply_date_filter(query, start_date, end_date)
    if brand_ids:
        query = query.where(GeneratedCode.brand_id.in_(brand_ids))
    
    query = query.group_by(Brand.id, Brand.name)
    
    result = await db.execute(query)
    rows = result.all()
    
    # For each brand, get approval rate and top users
    brand_performances = []
    for row in rows:
        # Approval rate for this brand
        approved_query = select(func.count(GeneratedCode.id))
        approved_query = approved_query.where(GeneratedCode.brand_id == row.brand_id)
        approved_query = approved_query.where(GeneratedCode.status == CodeStatus.APPROVED.value)
        approved_query = _apply_date_filter(approved_query, start_date, end_date)
        approved_result = await db.execute(approved_query)
        approved_count = approved_result.scalar() or 0
        
        approval_rate = (approved_count / row.code_generations * 100) if row.code_generations > 0 else 0.0
        
        # Top users for this brand
        top_users_query = select(
            User.email
        ).join(GeneratedCode, User.id == GeneratedCode.user_id).where(
            GeneratedCode.brand_id == row.brand_id
        )
        top_users_query = _apply_date_filter(top_users_query, start_date, end_date)
        top_users_query = top_users_query.group_by(User.email)
        top_users_query = top_users_query.order_by(func.count(GeneratedCode.id).desc())
        top_users_query = top_users_query.limit(5)
        
        top_users_result = await db.execute(top_users_query)
        top_users = [user.email for user in top_users_result.scalars().all()]
        
        brand_performances.append(BrandPerformance(
            brand_id=row.brand_id,
            brand_name=row.brand_name,
            code_generations=row.code_generations,
            average_confidence=float(row.avg_confidence or 0.0),
            approval_rate=round(approval_rate, 2),
            top_users=top_users
        ))
    
    return brand_performances


@router.get("/user-activity", response_model=List[UserActivity])
async def get_user_activity(
    start_date: Optional[date] = Query(None, description="Start date for period"),
    end_date: Optional[date] = Query(None, description="End date for period"),
    brand_id: Optional[int] = Query(None, description="Filter by brand ID (super admin only)"),
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get most active users."""
    brand_ids = get_user_brand_access(current_user)
    
    query = select(
        User.id.label('user_id'),
        User.email.label('user_email'),
        User.name.label('user_name'),
        func.count(GeneratedCode.id).label('code_generations'),
        func.avg(GeneratedCode.confidence_score).label('avg_confidence'),
        func.max(GeneratedCode.created_at).label('last_active')
    ).join(GeneratedCode, User.id == GeneratedCode.user_id)
    
    query = _apply_date_filter(query, start_date, end_date)
    query = _apply_brand_filter(query, brand_ids, brand_id)
    query = query.where(GeneratedCode.user_id.isnot(None))
    query = query.group_by(User.id, User.email, User.name)
    query = query.order_by(func.count(GeneratedCode.id).desc())
    query = query.limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        UserActivity(
            user_id=row.user_id,
            user_email=row.user_email,
            user_name=row.user_name,
            code_generations=row.code_generations,
            average_confidence=float(row.avg_confidence or 0.0),
            last_active=row.last_active
        )
        for row in rows
    ]


@router.get("/llm-costs", response_model=LLMCostMetrics)
async def get_llm_costs(
    start_date: Optional[date] = Query(None, description="Start date for period"),
    end_date: Optional[date] = Query(None, description="End date for period"),
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get LLM cost metrics (SUPER ADMIN ONLY)."""
    if current_user.brand_role != BrandRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can view cost data"
        )
    
    query = select(
        func.sum(GeneratedCode.llm_cost_usd).label('total_cost'),
        func.avg(GeneratedCode.llm_cost_usd).label('avg_cost'),
        func.sum(GeneratedCode.total_tokens).label('total_tokens'),
        func.count(GeneratedCode.id).label('total_generations')
    ).where(GeneratedCode.llm_cost_usd.isnot(None))
    
    query = _apply_date_filter(query, start_date, end_date)
    if brand_id:
        query = query.where(GeneratedCode.brand_id == brand_id)
    
    result = await db.execute(query)
    data = result.one()
    
    return LLMCostMetrics(
        total_cost_usd=float(data.total_cost or 0),
        average_cost_per_generation=float(data.avg_cost or 0),
        total_tokens=int(data.total_tokens or 0),
        total_generations=int(data.total_generations or 0),
        period_start=start_date,
        period_end=end_date
    )


@router.get("/llm-costs-by-brand", response_model=List[BrandLLMCost])
async def get_llm_costs_by_brand(
    start_date: Optional[date] = Query(None, description="Start date for period"),
    end_date: Optional[date] = Query(None, description="End date for period"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """Get LLM costs broken down by brand (SUPER ADMIN ONLY)."""
    if current_user.brand_role != BrandRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can view cost data"
        )
    
    query = (
        select(
            Brand.name.label('brand_name'),
            func.sum(GeneratedCode.llm_cost_usd).label('total_cost'),
            func.count(GeneratedCode.id).label('generations')
        )
        .join(Brand, GeneratedCode.brand_id == Brand.id)
        .where(GeneratedCode.llm_cost_usd.isnot(None))
        .group_by(Brand.name)
    )
    
    query = _apply_date_filter(query, start_date, end_date)
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        BrandLLMCost(
            brand_name=row.brand_name,
            total_cost_usd=float(row.total_cost),
            generations=int(row.generations),
            cost_per_generation=float(row.total_cost / row.generations) if row.generations > 0 else None
        )
        for row in rows
    ]


@router.get("/debug/count")
async def debug_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Debug endpoint to verify count matches database."""
    # Direct count from generated_code table
    result = await db.execute(select(func.count(GeneratedCode.id)))
    generated_code_count = result.scalar() or 0
    
    # Also get breakdown by brand
    brand_counts_query = select(
        Brand.name,
        func.count(GeneratedCode.id).label('count')
    ).join(GeneratedCode, Brand.id == GeneratedCode.brand_id).group_by(Brand.name)
    
    brand_counts_result = await db.execute(brand_counts_query)
    brand_counts = {row.name: row.count for row in brand_counts_result.all()}
    
    return {
        "generated_code_table_count": generated_code_count,
        "breakdown_by_brand": brand_counts,
        "message": "This should match Generated Code page"
    }
