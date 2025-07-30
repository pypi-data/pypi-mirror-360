# terraback/terraform_generator/writer.py

import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import re
from jinja2.exceptions import TemplateNotFound
import importlib.resources
from typing import Optional, List

# Import all filters from the updated filters module
from .filters import (
    ALL_FILTERS,
    has_value,
    validate_arn,
    validate_cidr,
    terraform_bool,
    safe_int,
    terraform_name,
    generate_resource_name,
    escape_quotes,
    strip_empty_lines
)

# Precompiled regular expressions for faster validation
EMPTY_ASSIGNMENT_RE = re.compile(r"^\s*\w+\s*=\s*$")
EMPTY_RESOURCE_NAME_RE = re.compile(r"(resource\s+\"[^\"]+\"\s+)\"\"")
PYTHON_BOOL_RE = re.compile(r"\b(True|False)\b")
MISSING_QUOTES_RE = re.compile(r"=\s*([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)")
EXCESSIVE_EMPTY_LINES_RE = re.compile(r"\n\s*\n\s*\n+")

def _make_joiner(separator):
    """Create a joiner function for comma-separated lists in templates."""
    class Joiner:
        def __init__(self, sep):
            self.sep = sep
            self.first = True
        
        def __call__(self):
            if self.first:
                self.first = False
                return ""
            return self.sep
    
    return Joiner(separator)

class AutoDiscoveryTemplateLoader:
    """
    Automatically discovers and loads Jinja2 templates from the package's
    'templates' directory. Enhanced with better error handling and template validation.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AutoDiscoveryTemplateLoader, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, template_dir_override: Optional[Path] = None):
        if self.initialized:
            return
        
        self.template_dir = template_dir_override or self._find_main_templates_dir()

        if not self.template_dir or not self.template_dir.exists():
            raise FileNotFoundError(f"Could not find the 'templates' directory. Looked for: {self.template_dir}")

        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            trim_blocks=False,
            lstrip_blocks=False,
        )
        self.register_custom_filters()
        self.register_custom_tests()
        self.register_global_functions()
        self.initialized = True

    def _find_main_templates_dir(self) -> Path:
        """Reliably find the 'templates' directory within the installed terraback package."""
        try:
            return Path(str(importlib.resources.files('terraback').joinpath('templates')))
        except (ModuleNotFoundError, AttributeError):
            return Path(__file__).resolve().parent.parent / "templates"

    def register_custom_filters(self):
        """Register all custom Jinja2 filters using the enhanced filter system."""
        # Register all filters from the centralized dictionary
        for filter_name, filter_func in ALL_FILTERS.items():
            self.env.filters[filter_name] = filter_func
        
        # Additional template-specific filters
        self.env.filters['joiner'] = lambda sep=',': _make_joiner(sep)
        
        # Ensure backward compatibility with any existing filter names
        self.env.filters['tf_resource_name'] = ALL_FILTERS['tf_resource_name']
        self.env.filters['strip_id_prefix'] = ALL_FILTERS['strip_id_prefix']
        self.env.filters['terraform_sanitize_name'] = ALL_FILTERS['terraform_sanitize_name']

    def register_custom_tests(self):
        """Register custom Jinja2 tests for better template logic."""
        self.env.tests['defined'] = lambda x: x is not None
        self.env.tests['none'] = lambda x: x is None
        self.env.tests['empty'] = lambda x: not has_value(x)
        self.env.tests['has_value'] = has_value
        self.env.tests['string'] = lambda x: isinstance(x, str)
        self.env.tests['list'] = lambda x: isinstance(x, list)
        self.env.tests['dict'] = lambda x: isinstance(x, dict)
        self.env.tests['boolean'] = lambda x: isinstance(x, bool)
        self.env.tests['number'] = lambda x: isinstance(x, (int, float))
        self.env.tests['valid_arn'] = validate_arn
        self.env.tests['valid_cidr'] = lambda x: validate_cidr(x) != "0.0.0.0/0"
        
        # Additional useful tests
        self.env.tests['aws_resource_id'] = lambda x: isinstance(x, str) and any(x.startswith(p) for p in ['i-', 'vol-', 'sg-', 'vpc-', 'subnet-'])
        self.env.tests['positive'] = lambda x: isinstance(x, (int, float)) and x > 0
        self.env.tests['valid_port'] = lambda x: isinstance(x, int) and 1 <= x <= 65535

    def register_global_functions(self):
        """Register global functions available in all templates."""
        self.env.globals['range'] = range
        self.env.globals['len'] = len
        self.env.globals['min'] = min
        self.env.globals['max'] = max
        self.env.globals['sum'] = sum
        self.env.globals['sorted'] = sorted
        self.env.globals['enumerate'] = enumerate
        self.env.globals['zip'] = zip
        
        # Custom global functions
        self.env.globals['joiner'] = lambda sep=',': _make_joiner(sep)
        
        # Template helper functions
        self.env.globals['debug_value'] = lambda x: f"DEBUG: {type(x).__name__} = {repr(x)}"
        self.env.globals['format_multiline'] = lambda text, indent=2: '\n'.join(' ' * indent + line for line in str(text).split('\n'))

    def get_template_path(self, resource_type: str, provider: str) -> str:
        """
        Recursively search the provider's template directory to find the
        correct template file, regardless of the subdirectory structure.
        """
        provider_dir = self.template_dir / provider
        if not provider_dir.is_dir():
            raise FileNotFoundError(f"Provider directory not found: {provider_dir}")

        template_name = f"{resource_type}.tf.j2"
        found_templates = list(provider_dir.rglob(template_name))

        if not found_templates:
            raise FileNotFoundError(f"Template '{template_name}' not found anywhere inside '{provider_dir}'")
        
        relative_path = found_templates[0].relative_to(self.template_dir)
        return str(relative_path).replace('\\', '/')

    def validate_template_output(self, output: str, resource_type: str) -> str:
        """Validate and clean template output to prevent syntax errors."""
        if not output.strip():
            return ""
        
        lines = output.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()

            # Skip lines that would cause syntax errors
            if stripped.endswith('=') or EMPTY_ASSIGNMENT_RE.match(stripped):
                continue  # Skip empty assignments

            # Fix resource names that are empty
            if EMPTY_RESOURCE_NAME_RE.match(stripped):
                line = EMPTY_RESOURCE_NAME_RE.sub(
                    rf'\1"default_{resource_type}"',
                    line,
                )

            # Fix Python-style booleans that might have slipped through
            line = PYTHON_BOOL_RE.sub(lambda m: m.group().lower(), line)

            # Fix missing quotes around resource references
            line = MISSING_QUOTES_RE.sub(r'= \1', line)
            
            cleaned_lines.append(line)
        
        # Ensure proper spacing between resources
        output = '\n'.join(cleaned_lines)
        output = EXCESSIVE_EMPTY_LINES_RE.sub('\n\n', output)  # Remove excessive empty lines
        
        # Apply final cleanup
        output = strip_empty_lines(output)
        
        return output

    def preprocess_resources(self, resources: list, resource_type: str) -> list:
        """Preprocess resources to ensure they have all required fields for templates."""
        processed_resources = []
        
        for i, resource in enumerate(resources):
            if isinstance(resource, dict):
                # Create a copy to avoid modifying original data
                processed_resource = dict(resource)
                
                # Ensure each resource has a sanitized name for Terraform
                if 'name_sanitized' not in processed_resource:
                    processed_resource['name_sanitized'] = generate_resource_name(processed_resource, resource_type)
                
                # Ensure name_sanitized is never empty
                if not processed_resource['name_sanitized'] or processed_resource['name_sanitized'] == 'unnamed_resource':
                    processed_resource['name_sanitized'] = f"{resource_type}_{i}"
                
                # Ensure name_sanitized is terraform-safe
                processed_resource['name_sanitized'] = terraform_name(processed_resource['name_sanitized'])
                
                # Add helper fields for common template patterns
                self._add_helper_fields(processed_resource, resource_type)
                
                processed_resources.append(processed_resource)
            else:
                processed_resources.append(resource)
        
        return processed_resources

    def _add_helper_fields(self, resource: dict, resource_type: str):
        """Add helper fields that templates commonly need."""
        # Add boolean helper for common AWS resource states
        if 'State' in resource:
            resource['is_active'] = resource['State'] in ['running', 'available', 'active', 'enabled']
        
        # Add formatted tags if tags exist
        if resource.get('Tags') and isinstance(resource['Tags'], list):
            resource['tags_formatted'] = {tag['Key']: tag['Value'] for tag in resource['Tags']}
        elif resource.get('tags') and isinstance(resource['tags'], dict):
            resource['tags_formatted'] = resource['tags']
        
        # Add region extraction from ARNs
        for field_name, field_value in list(resource.items()):
            if isinstance(field_value, str) and field_value.startswith('arn:aws:'):
                arn_parts = field_value.split(':')
                if len(arn_parts) >= 4:
                    resource[f'{field_name}_region'] = arn_parts[3]
                    resource[f'{field_name}_account'] = arn_parts[4] if len(arn_parts) >= 5 else ''

        # Add shorthand for common ID extractions
        for field_name, field_value in list(resource.items()):
            if isinstance(field_value, str) and any(field_value.startswith(prefix) for prefix in ['i-', 'vol-', 'sg-', 'vpc-', 'subnet-']):
                resource[f'{field_name}_short'] = terraform_name(field_value)

    def render_template(self, resource_type: str, resources: list, provider: str = 'aws'):
        """Render template with resources and validate output."""
        if not resources:
            return ""
        
        try:
            template_path = self.get_template_path(resource_type, provider)
            template = self.env.get_template(template_path)
            
            # Preprocess resources to ensure they have valid names and helper fields
            processed_resources = self.preprocess_resources(resources, resource_type)
            
            # Render the template with enhanced context
            template_context = {
                'resources': processed_resources,
                'resource_type': resource_type,
                'provider': provider,
                'resource_count': len(processed_resources)
            }
            
            output = template.render(**template_context)
            
            # Validate and clean the output
            output = self.validate_template_output(output, resource_type)
            
            return output
            
        except Exception as e:
            print(f"Error rendering template for {resource_type}: {e}")
            raise

    def get_available_templates(self, provider: str = 'aws') -> List[str]:
        """Get list of available templates for a provider."""
        provider_dir = self.template_dir / provider
        if not provider_dir.exists():
            return []
        
        templates = []
        for template_file in provider_dir.rglob("*.tf.j2"):
            # Extract resource type from filename
            resource_type = template_file.stem  # Remove .tf.j2 extension
            templates.append(resource_type)
        
        return sorted(templates)

    def validate_template_syntax(self, resource_type: str, provider: str = 'aws') -> List[str]:
        """Validate template syntax without rendering."""
        errors = []
        try:
            template_path = self.get_template_path(resource_type, provider)
            # Load the template source directly from the loader
            try:
                source, _, _ = self.env.loader.get_source(self.env, template_path)
            except Exception as e:
                errors.append(f"Failed to load template {template_path}: {e}")
                return errors

            # Try to parse the template source
            self.env.parse(source)
            
        except Exception as e:
            errors.append(f"Template syntax error in {resource_type}: {e}")
        
        return errors


# Global Functions

_loader = None

def get_template_loader():
    """Get the global template loader instance."""
    global _loader
    if _loader is None:
        _loader = AutoDiscoveryTemplateLoader()
    return _loader

def reset_template_loader():
    """Reset the global template loader instance (useful for testing)."""
    global _loader
    _loader = None

def generate_tf(resources: List, resource_type: str, output_path: Path, provider: str = 'aws'):
    """Generate Terraform file using the enhanced template loader."""
    if not resources:
        print(f"No resources provided for {resource_type}")
        return
    
    try:
        loader = get_template_loader()
        tf_output = loader.render_template(resource_type, resources, provider)
        
        if not tf_output.strip():
            print(f"Warning: No output generated for {resource_type}")
            return
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(tf_output)
            
        print(f"Generated: {output_path}")
        
        # Validate the generated file
        validation_errors = validate_terraform_syntax(output_path)
        if validation_errors:
            print(f"Warning: Validation issues in {output_path}:")
            for error in validation_errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
        
    except Exception as e:
        print(f"Error generating {resource_type}: {e}")
        raise

def validate_terraform_syntax(file_path: Path) -> List[str]:
    """Basic validation of generated Terraform files."""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
            
            # Check for common syntax errors
            if stripped.endswith('=') or re.match(r'^\s*\w+\s*=\s*$', stripped):
                errors.append(f"Line {i}: Empty assignment - {stripped}")
            
            if re.match(r'resource\s+"[^"]+"\s+""', stripped):
                errors.append(f"Line {i}: Empty resource name")
            
            # Check for Python-style booleans
            if re.search(r'\b(True|False)\b', stripped):
                errors.append(f"Line {i}: Python-style boolean found (use lowercase)")
            
            # Track brace balance (simplified)
            for char in line:
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
        
        # Check overall brace balance
        if brace_count != 0:
            errors.append(f"Unbalanced braces: {brace_count} unclosed")
    
    except Exception as e:
        errors.append(f"Failed to validate file: {e}")
    
    return errors

def list_available_templates(provider: str = 'aws') -> List[str]:
    """List all available templates for a provider."""
    try:
        loader = get_template_loader()
        return loader.get_available_templates(provider)
    except Exception as e:
        print(f"Error listing templates: {e}")
        return []

def validate_all_templates(provider: str = 'aws') -> dict:
    """Validate syntax of all templates for a provider."""
    try:
        loader = get_template_loader()
        templates = loader.get_available_templates(provider)
        
        results = {}
        for template in templates:
            errors = loader.validate_template_syntax(template, provider)
            results[template] = errors
        
        return results
    except Exception as e:
        print(f"Error validating templates: {e}")
        return {}

# Template debugging utilities
def debug_template_render(resource_type: str, resources: List, provider: str = 'aws') -> str:
    """Render template with debug information."""
    try:
        loader = get_template_loader()
        
        # Add debug information to resources
        debug_resources = []
        for i, resource in enumerate(resources):
            if isinstance(resource, dict):
                debug_resource = dict(resource)
                debug_resource['_debug_index'] = i
                debug_resource['_debug_type'] = resource_type
                debug_resources.append(debug_resource)
            else:
                debug_resources.append(resource)
        
        output = loader.render_template(resource_type, debug_resources, provider)
        
        # Add debug header
        debug_header = f"""# DEBUG RENDER: {resource_type}
# Provider: {provider}
# Resources: {len(resources)}
# Generated: {Path.cwd()}

"""
        
        return debug_header + output
        
    except Exception as e:
        return f"# ERROR: Failed to render {resource_type}: {e}\n"

# Export commonly used functions
__all__ = [
    'get_template_loader',
    'reset_template_loader',
    'generate_tf',
    'validate_terraform_syntax',
    'list_available_templates',
    'validate_all_templates',
    'debug_template_render',
    'AutoDiscoveryTemplateLoader'
]
