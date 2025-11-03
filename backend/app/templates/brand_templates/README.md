# Brand Template JSON Definitions

This directory contains starter brand code template JSON files that define how generated code should be structured, styled, and formatted for different platforms and use cases.

## Purpose

These templates are metadata files (not actual code) that guide the code generation process. They define:
- Code structure and sections
- Header format and content
- Variable naming conventions and styles
- Logging configuration
- Platform-specific utilities
- Error handling patterns
- Special features (page detection, SPA navigation, etc.)

## Available Templates

### 1. Optimizely Standard (`optimizely_standard.json`)

**Best for:** Modern Optimizely implementations requiring robust features and utils integration.

**Characteristics:**
- ES6+ syntax (const, let, arrow functions)
- Detailed block comment header with test info
- Configuration section with constants
- Logging with levels (DEBUG, INFO, WARN, ERROR)
- Optimizely utils for element waiting
- Promise-based patterns
- Professional tone, no emojis

**When to use:**
- Optimizely platform deployments
- Tests requiring element waiting/utilities
- Modern JavaScript environment
- Production-grade code needs

### 2. Adobe Target Standard (`adobe_target_standard.json`)

**Best for:** Enterprise Adobe Target implementations requiring conservative, compatible code.

**Characteristics:**
- IIFE wrapper for scope isolation
- ES5 syntax (var, function expressions)
- Detailed block comment header
- Configuration variables section
- Toggleable logging function
- Page detection before execution
- Monitoring intervals with timeouts
- SPA navigation handling

**When to use:**
- Adobe Target platform deployments
- Enterprise environments requiring browser compatibility
- Single Page Applications (SPAs)
- Tests requiring page detection and monitoring

### 3. Minimal (`minimal.json`)

**Best for:** Simple tests that need lean, essential-only code.

**Characteristics:**
- No wrapper
- Minimal sections (CONFIG, EXECUTION)
- Basic logging
- No external dependencies
- Short and simple structure
- Single-line comment header

**When to use:**
- Simple, straightforward tests
- Quick prototypes
- When code size is a priority
- Basic DOM manipulation without complex logic

### 4. Debug-Focused (`debug_focused.json`)

**Best for:** Troubleshooting and development scenarios requiring maximum visibility.

**Characteristics:**
- Verbose logging (default DEBUG level)
- Performance tracking
- State snapshots
- Detailed error information
- Timestamps in log messages
- Performance timing utilities

**When to use:**
- Development and debugging
- Troubleshooting production issues
- Performance analysis
- Code review and validation

## Template Loading and Application

These template JSON files are intended to be:
1. Loaded by admin users when configuring brands
2. Applied to brand `code_template` fields in the database
3. Used by the code generator service to structure generated code
4. Referenced during code generation to ensure consistent formatting

### Usage Flow

1. Admin selects a template JSON file
2. Template is loaded and parsed
3. Template configuration is stored in brand's `code_template` field
4. Code generator reads template during generation
5. Generated code follows template structure and formatting rules

## JSON Structure Explanation

Each template JSON file contains the following top-level sections:

### `name` (string)
Human-readable name of the template.

### `description` (string)
Brief description of when and why to use this template.

### `platform` (string)
Target platform: `"optimizely"`, `"adobe_target"`, or `"agnostic"`.

### `code_structure` (object)
Defines how code should be organized:
- `use_strict` (boolean): Whether to include 'use strict' directive
- `wrapper` (string, optional): Code wrapper type (e.g., "iife")
- `sections` (array): Ordered list of code section names
- `section_separator` (string): Separator line between sections
- `minimal` (boolean, optional): Flag indicating minimal structure

### `header_format` (object)
Defines test header comment format:
- `style` (string): "block_comment" or "single_line_comment"
- `includes` (array): List of fields to include in header

### `variables` (object)
Variable declaration style:
- `style` (string): "const", "let", or "var"
- `naming_convention` (string): "UPPER_SNAKE_CASE" or other convention
- `config_object_name` (string, optional): Name for config object
- `version_constant` (string, optional): Name for version constant
- `test_id_constant` (string, optional): Name for test ID constant
- `minimal` (boolean, optional): Flag for minimal variable setup

### `logging` (object)
Logging configuration:
- `enabled` (boolean): Whether logging is enabled
- `toggleable` (boolean, optional): Whether logging can be toggled
- `function_name` (string): Name of logging function
- `prefix_format` (string): Format string for log prefixes
- `levels` (array): Available log levels
- `default_level` (string): Default log level
- `config_var` (string, optional): Variable name for logging toggle
- `use_emojis` (boolean): Whether to use emojis in logs
- `timestamps` (boolean, optional): Whether to include timestamps
- `verbose` (boolean, optional): Whether to use verbose logging
- `minimal` (boolean, optional): Flag for minimal logging setup

### `utilities` (object)
Platform-specific utilities:
- `platform` (string): Platform name
- `use_utils` (boolean): Whether to use platform utils
- `utils_variable` (string, optional): How to access utils
- `wait_method` (string, optional): Element waiting method name
- `monitoring` (object, optional): Monitoring configuration
  - `use_intervals` (boolean): Whether to use monitoring intervals
  - `duration_var` (string): Variable name for duration
  - `interval_var` (string): Variable name for interval

### `error_handling` (object, optional)
Error handling configuration:
- `use_try_catch` (boolean): Whether to use try/catch blocks
- `log_errors` (boolean): Whether to log errors

### `features` (object, optional)
Special features:
- `page_detection` (string): Page detection requirement ("required", "optional")
- `spa_navigation` (string): SPA navigation handling style
- `processed_attribute` (boolean): Whether to track processed elements
- `performance_timing` (boolean): Whether to include performance tracking
- `state_tracking` (boolean): Whether to track state changes

## Example: Using a Template

```python
# Load template JSON
with open('optimizely_standard.json') as f:
    template = json.load(f)

# Apply to brand
brand.code_template = template

# Code generator will use template structure when generating code
```

## Notes

- Templates are JSON files and must be valid JSON
- Template structure is flexible and can be extended with additional fields
- Templates are platform-agnostic in their file format, but contain platform-specific configuration
- Multiple templates can be mixed/modified to create custom templates
- Template selection should match the target platform and use case requirements