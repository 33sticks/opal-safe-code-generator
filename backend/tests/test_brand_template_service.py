"""Tests for Brand Template Service."""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from app.services.brand_template_service import BrandTemplateService


class TestBrandTemplateService:
    """Tests for BrandTemplateService."""
    
    def test_load_all_templates_successfully(self):
        """Test that all 4 templates load correctly."""
        service = BrandTemplateService()
        
        templates = service.get_available_templates()
        
        # Should have loaded all 4 templates
        assert len(templates) == 4
        
        # Verify all templates have required fields
        for template in templates:
            assert "name" in template
            assert "description" in template
            assert "platform" in template
            assert isinstance(template["name"], str)
            assert isinstance(template["description"], str)
            assert isinstance(template["platform"], str)
            assert len(template["name"]) > 0
            assert len(template["description"]) > 0
    
    def test_get_template_by_name_exists(self):
        """Test getting a specific template by name."""
        service = BrandTemplateService()
        
        # Get template names to use an actual template
        template_names = service.get_template_names()
        assert len(template_names) > 0
        
        # Try to get the first template
        template_name = template_names[0]
        template = service.get_template_by_name(template_name)
        
        # Verify it's the full template with all fields
        assert isinstance(template, dict)
        assert template["name"] == template_name
        assert "description" in template
        assert "platform" in template
        
        # Verify it's case-insensitive
        template_lower = service.get_template_by_name(template_name.lower())
        assert template_lower["name"] == template["name"]
    
    def test_get_template_by_name_not_found(self):
        """Test that FileNotFoundError is raised for non-existent template."""
        service = BrandTemplateService()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            service.get_template_by_name("NonExistentTemplate")
        
        error_message = str(exc_info.value)
        assert "NonExistentTemplate" in error_message
        assert "not found" in error_message.lower()
        # Should mention available templates
        assert "Available templates" in error_message
    
    def test_get_available_templates_format(self):
        """Test that get_available_templates returns correct format."""
        service = BrandTemplateService()
        
        templates = service.get_available_templates()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
        
        # Verify format matches expected structure
        for template in templates:
            assert isinstance(template, dict)
            assert set(template.keys()) == {"name", "description", "platform"}
            assert isinstance(template["name"], str)
            assert isinstance(template["description"], str)
            assert isinstance(template["platform"], str)
    
    def test_get_template_names(self):
        """Test that get_template_names returns simple list of names."""
        service = BrandTemplateService()
        
        names = service.get_template_names()
        
        assert isinstance(names, list)
        assert len(names) == 4  # Should match number of templates
        
        # Verify all are strings
        for name in names:
            assert isinstance(name, str)
            assert len(name) > 0
    
    def test_validate_template_valid(self):
        """Test validation with a valid template structure."""
        service = BrandTemplateService()
        
        valid_template = {
            "name": "Test Template",
            "description": "A test template",
            "platform": "test_platform",
            "code_structure": {
                "use_strict": True,
                "sections": ["CONFIG", "EXECUTION"]
            },
            "logging": {
                "enabled": True,
                "levels": ["INFO", "ERROR"]
            }
        }
        
        is_valid, errors = service.validate_template(valid_template)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_template_missing_required_fields(self):
        """Test validation catches missing required fields."""
        service = BrandTemplateService()
        
        # Missing all required fields
        invalid_template = {}
        is_valid, errors = service.validate_template(invalid_template)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("name" in error.lower() for error in errors)
        assert any("description" in error.lower() for error in errors)
        assert any("platform" in error.lower() for error in errors)
        
        # Missing one required field
        partial_template = {
            "name": "Test",
            "description": "Test desc"
            # Missing platform
        }
        is_valid, errors = service.validate_template(partial_template)
        
        assert is_valid is False
        assert any("platform" in error.lower() for error in errors)
    
    def test_validate_template_empty_required_fields(self):
        """Test validation catches empty required fields."""
        service = BrandTemplateService()
        
        invalid_template = {
            "name": "   ",  # Empty/whitespace only
            "description": "Valid description",
            "platform": "valid_platform"
        }
        
        is_valid, errors = service.validate_template(invalid_template)
        
        assert is_valid is False
        assert any("name" in error.lower() and "empty" in error.lower() for error in errors)
    
    def test_validate_template_invalid_structure(self):
        """Test validation catches malformed data types."""
        service = BrandTemplateService()
        
        # Wrong type for required field
        invalid_template = {
            "name": 123,  # Should be string
            "description": "Valid",
            "platform": "valid"
        }
        
        is_valid, errors = service.validate_template(invalid_template)
        
        assert is_valid is False
        assert any("name" in error.lower() and "string" in error.lower() for error in errors)
        
        # Wrong type for optional field
        invalid_template2 = {
            "name": "Valid",
            "description": "Valid",
            "platform": "valid",
            "code_structure": "not a dict"  # Should be dict
        }
        
        is_valid, errors = service.validate_template(invalid_template2)
        
        assert is_valid is False
        assert any("code_structure" in error.lower() and "dict" in error.lower() for error in errors)
        
        # Wrong type for nested field
        invalid_template3 = {
            "name": "Valid",
            "description": "Valid",
            "platform": "valid",
            "code_structure": {
                "sections": "not a list"  # Should be list
            }
        }
        
        is_valid, errors = service.validate_template(invalid_template3)
        
        assert is_valid is False
        assert any("sections" in error.lower() and "list" in error.lower() for error in errors)
    
    def test_validate_template_not_dict(self):
        """Test validation handles non-dict input."""
        service = BrandTemplateService()
        
        is_valid, errors = service.validate_template("not a dict")
        
        assert is_valid is False
        assert len(errors) > 0
        assert "dictionary" in errors[0].lower()
    
    def test_templates_cached(self):
        """Test that templates are cached and not reloaded from disk."""
        service = BrandTemplateService()
        
        # Get templates multiple times
        templates1 = service.get_available_templates()
        templates2 = service.get_available_templates()
        templates3 = service.get_template_by_name(service.get_template_names()[0])
        
        # Should return same data (cached)
        assert templates1 == templates2
        assert len(templates1) > 0
    
    def test_get_template_by_name_case_insensitive(self):
        """Test that template lookup is case-insensitive."""
        service = BrandTemplateService()
        
        template_names = service.get_template_names()
        if len(template_names) > 0:
            original_name = template_names[0]
            
            # Try different cases
            template_lower = service.get_template_by_name(original_name.lower())
            template_upper = service.get_template_by_name(original_name.upper())
            template_mixed = service.get_template_by_name(original_name.swapcase())
            
            # All should return the same template
            assert template_lower["name"] == original_name
            assert template_upper["name"] == original_name
            assert template_mixed["name"] == original_name
    
    def test_custom_templates_dir(self):
        """Test service with custom templates directory."""
        # Create a temporary directory with test templates
        with tempfile.TemporaryDirectory() as tmpdir:
            templates_dir = Path(tmpdir) / "brand_templates"
            templates_dir.mkdir()
            
            # Create a valid test template
            test_template = {
                "name": "Custom Test Template",
                "description": "A custom test template",
                "platform": "test"
            }
            
            template_file = templates_dir / "custom_test.json"
            with open(template_file, 'w') as f:
                json.dump(test_template, f)
            
            # Initialize service with custom directory
            service = BrandTemplateService(templates_dir=templates_dir)
            
            # Verify template loaded
            templates = service.get_available_templates()
            assert len(templates) == 1
            assert templates[0]["name"] == "Custom Test Template"
            
            # Verify can get by name
            template = service.get_template_by_name("Custom Test Template")
            assert template["name"] == "Custom Test Template"
    
    def test_invalid_templates_directory(self):
        """Test error handling for invalid templates directory."""
        with pytest.raises(ValueError) as exc_info:
            BrandTemplateService(templates_dir=Path("/nonexistent/path"))
        
        assert "not found" in str(exc_info.value).lower() or "doesn't exist" in str(exc_info.value).lower()
    
    def test_reload_templates(self):
        """Test reloading templates from disk."""
        service = BrandTemplateService()
        
        initial_count = len(service.get_available_templates())
        
        # Reload should maintain same count (using actual files)
        service.reload_templates()
        
        after_reload_count = len(service.get_available_templates())
        
        assert after_reload_count == initial_count
        assert after_reload_count > 0

