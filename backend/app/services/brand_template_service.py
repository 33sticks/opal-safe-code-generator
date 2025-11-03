"""Brand template service for loading and managing brand templates."""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class BrandTemplateService:
    """Service for loading, validating, and serving brand template JSON files."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize the service and load all templates from disk.
        
        Args:
            templates_dir: Optional path to templates directory.
                          If None, uses default location relative to this file.
        
        Raises:
            ValueError: If templates directory doesn't exist or templates fail to load.
        """
        if templates_dir is None:
            # Resolve path relative to this file
            # backend/app/services/brand_template_service.py -> backend/app/templates/brand_templates/
            templates_dir = Path(__file__).parent.parent / "templates" / "brand_templates"
        
        self.templates_dir = Path(templates_dir)
        
        if not self.templates_dir.exists():
            raise ValueError(f"Templates directory not found: {self.templates_dir}")
        
        if not self.templates_dir.is_dir():
            raise ValueError(f"Templates path is not a directory: {self.templates_dir}")
        
        # Cache for loaded templates (keyed by normalized name)
        self._templates: Dict[str, Dict[str, Any]] = {}
        
        # Cache for template metadata (for quick listing)
        self._template_metadata: List[Dict[str, Any]] = []
        
        # Load all templates
        self._load_all_templates()
    
    def _load_all_templates(self) -> None:
        """Load all JSON template files from the templates directory."""
        json_files = list(self.templates_dir.glob("*.json"))
        
        if not json_files:
            logger.warning(f"No JSON template files found in {self.templates_dir}")
            return
        
        for json_file in json_files:
            try:
                template_data = self._load_template_file(json_file)
                
                # Validate the loaded template
                is_valid, errors = self.validate_template(template_data)
                if not is_valid:
                    logger.error(
                        f"Invalid template {json_file.name}: {', '.join(errors)}. "
                        f"Skipping this template."
                    )
                    continue
                
                # Get template name (normalize for lookup)
                template_name = template_data.get("name", "")
                if not template_name:
                    logger.error(f"Template {json_file.name} missing 'name' field. Skipping.")
                    continue
                
                # Normalize name for internal lookup (lowercase, but preserve original in data)
                normalized_name = template_name.lower().strip()
                
                # Check for duplicates
                if normalized_name in self._templates:
                    logger.warning(
                        f"Duplicate template name '{template_name}' found. "
                        f"Overwriting previous template."
                    )
                
                # Store template
                self._templates[normalized_name] = template_data
                
                logger.info(f"Loaded template: {template_name} from {json_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to load template {json_file.name}: {str(e)}")
                continue
        
        # Build metadata list
        self._template_metadata = self._build_template_metadata()
        
        logger.info(f"Loaded {len(self._templates)} template(s) successfully")
    
    def _load_template_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and parse a single template JSON file.
        
        Args:
            file_path: Path to the JSON template file.
        
        Returns:
            Parsed template data as dictionary.
        
        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If JSON is invalid.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise ValueError(f"Template file must contain a JSON object, got {type(data)}")
            
            return data
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in template file {file_path.name}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error reading template file {file_path.name}: {str(e)}")
    
    def _build_template_metadata(self) -> List[Dict[str, Any]]:
        """Build metadata list for all loaded templates."""
        metadata = []
        for template_data in self._templates.values():
            metadata.append({
                "name": template_data.get("name", ""),
                "description": template_data.get("description", ""),
                "platform": template_data.get("platform", "agnostic")
            })
        return metadata
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """
        Get list of all available templates with metadata.
        
        Returns:
            List of dictionaries with 'name', 'description', and 'platform' fields.
        """
        return self._template_metadata.copy()
    
    def get_template_by_name(self, name: str) -> Dict[str, Any]:
        """
        Get full template JSON by name.
        
        Args:
            name: Template name (case-insensitive).
        
        Returns:
            Full template dictionary.
        
        Raises:
            FileNotFoundError: If template with given name doesn't exist.
        """
        normalized_name = name.lower().strip()
        
        if normalized_name not in self._templates:
            raise FileNotFoundError(
                f"Template '{name}' not found. "
                f"Available templates: {', '.join(self.get_template_names())}"
            )
        
        # Return a copy to prevent external modification
        return self._templates[normalized_name].copy()
    
    def get_template_names(self) -> List[str]:
        """
        Get simple list of template names.
        
        Returns:
            List of template names (preserving original case).
        """
        return [template_data.get("name", "") for template_data in self._templates.values()]
    
    def validate_template(self, template_data: dict) -> Tuple[bool, List[str]]:
        """
        Validate template structure.
        
        Args:
            template_data: Template dictionary to validate.
        
        Returns:
            Tuple of (is_valid, errors_list).
        """
        errors: List[str] = []
        
        if not isinstance(template_data, dict):
            return False, ["Template data must be a dictionary"]
        
        # Required fields
        required_fields = ["name", "description", "platform"]
        for field in required_fields:
            if field not in template_data:
                errors.append(f"Missing required field: '{field}'")
            elif not isinstance(template_data[field], str):
                errors.append(f"Field '{field}' must be a string")
            elif not template_data[field].strip():
                errors.append(f"Field '{field}' cannot be empty")
        
        # Optional fields validation (if present, validate structure)
        optional_fields = {
            "code_structure": dict,
            "header_format": dict,
            "variables": dict,
            "logging": dict,
            "utilities": dict,
            "error_handling": dict,
            "features": dict
        }
        
        for field, expected_type in optional_fields.items():
            if field in template_data:
                if not isinstance(template_data[field], expected_type):
                    errors.append(f"Field '{field}' must be a {expected_type.__name__}")
        
        # Validate nested structures if present
        if "code_structure" in template_data:
            code_struct = template_data["code_structure"]
            if isinstance(code_struct, dict):
                if "sections" in code_struct:
                    if not isinstance(code_struct["sections"], list):
                        errors.append("code_structure.sections must be a list")
        
        if "logging" in template_data:
            logging_config = template_data["logging"]
            if isinstance(logging_config, dict):
                if "levels" in logging_config:
                    if not isinstance(logging_config["levels"], list):
                        errors.append("logging.levels must be a list")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def reload_templates(self) -> None:
        """Reload all templates from disk (useful for development/testing)."""
        self._templates.clear()
        self._template_metadata.clear()
        self._load_all_templates()

