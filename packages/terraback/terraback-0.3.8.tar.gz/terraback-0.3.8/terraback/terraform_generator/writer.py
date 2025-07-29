# terraback/terraform_generator/writer.py

import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
import importlib.resources
from typing import Optional, List

from .filters import (
    sanitize_for_terraform,
    to_terraform_string,
    to_terraform_list,
    to_terraform_map,
    to_terraform_bool,
    to_terraform_int,
    to_terraform_float,
    to_terraform_resource_name,
    strip_id_prefix,
    tojson,
    has_value,
    is_defined,
    is_not_none,
    safe_get,
    default_if_empty,
    safe_int,
    safe_bool,
    generate_resource_name,
    escape_quotes,
    strip_whitespace,
    terraform_sanitize_name,
    format_tags,
    format_cidr_blocks,
    format_security_groups
)

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
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,  # Ensure proper file endings
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
        """Register all custom Jinja2 filters."""
        # Basic Terraform type filters
        self.env.filters['sanitize'] = sanitize_for_terraform
        self.env.filters['tf_string'] = to_terraform_string
        self.env.filters['tf_list'] = to_terraform_list
        self.env.filters['tf_map'] = to_terraform_map
        self.env.filters['tf_bool'] = to_terraform_bool
        self.env.filters['tf_int'] = to_terraform_int
        self.env.filters['tf_float'] = to_terraform_float
        self.env.filters['tf_resource_name'] = to_terraform_resource_name
        self.env.filters['strip_id_prefix'] = strip_id_prefix
        self.env.filters['tojson'] = tojson
        
        # Enhanced conditional filters
        self.env.filters['has_value'] = has_value
        self.env.filters['is_defined'] = is_defined
        self.env.filters['is_not_none'] = is_not_none
        self.env.filters['safe_get'] = safe_get
        self.env.filters['default_if_empty'] = default_if_empty
        self.env.filters['safe_int'] = safe_int
        self.env.filters['safe_bool'] = safe_bool
        
        # Name generation and sanitization
        self.env.filters['generate_name'] = generate_resource_name
        self.env.filters['escape_quotes'] = escape_quotes
        self.env.filters['strip_whitespace'] = strip_whitespace
        self.env.filters['terraform_name'] = terraform_sanitize_name
        
        # AWS/Cloud specific formatters
        self.env.filters['format_tags'] = format_tags
        self.env.filters['format_cidrs'] = format_cidr_blocks
        self.env.filters['format_sgs'] = format_security_groups
        
        # Standard string filters with null safety
        self.env.filters['lower'] = lambda x: str(x).lower() if x is not None else ''
        self.env.filters['upper'] = lambda x: str(x).upper() if x is not None else ''
        self.env.filters['replace'] = lambda x, old, new: str(x).replace(old, new) if x is not None else ''
        self.env.filters['default'] = lambda x, default='': x if x is not None else default
        self.env.filters['safe'] = lambda x: x  # For marking strings as safe

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
            if (stripped.endswith('=') or 
                re.match(r'^\s*\w+\s*=\s*$', stripped)):
                continue  # Skip empty assignments
            
            # Fix resource names that are empty
            if re.match(r'resource\s+"[^"]+"\s+""', stripped):
                line = re.sub(
                    r'(resource\s+"[^"]+"\s+)""',
                    rf'\1"default_{resource_type}"',
                    line
                )
            
            cleaned_lines.append(line)
        
        # Ensure proper spacing between resources
        output = '\n'.join(cleaned_lines)
        output = re.sub(r'\n\s*\n\s*\n', '\n\n', output)  # Remove excessive empty lines
        
        return output

    def render_template(self, resource_type: str, resources: list, provider: str = 'aws'):
        """Render template with resources and validate output."""
        if not resources:
            return ""
        
        template_path = self.get_template_path(resource_type, provider)
        template = self.env.get_template(template_path)
        
        # Pre-process resources to ensure they have valid names
        processed_resources = []
        for i, resource in enumerate(resources):
            if isinstance(resource, dict):
                # Ensure each resource has a sanitized name for Terraform
                if 'name_sanitized' not in resource:
                    resource['name_sanitized'] = generate_resource_name(resource, resource_type)
                
                # Ensure name_sanitized is never empty
                if not resource['name_sanitized'] or resource['name_sanitized'] == 'unnamed_resource':
                    resource['name_sanitized'] = f"{resource_type}_{i}"
            
            processed_resources.append(resource)
        
        # Render the template
        output = template.render(resources=processed_resources)
        
        # Validate and clean the output
        output = self.validate_template_output(output, resource_type)
        
        return output


# Global Functions

_loader = None

def get_template_loader():
    """Get the global template loader instance."""
    global _loader
    if _loader is None:
        _loader = AutoDiscoveryTemplateLoader()
    return _loader

def generate_tf(resources: List, resource_type: str, output_path: Path, provider: str = 'aws'):
    """Generate Terraform file using the enhanced template loader."""
    if not resources:
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
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for common syntax errors
            if stripped.endswith('=') or re.match(r'^\s*\w+\s*=\s*$', stripped):
                errors.append(f"Line {i}: Empty assignment - {stripped}")
            
            if re.match(r'resource\s+"[^"]+"\s+""', stripped):
                errors.append(f"Line {i}: Empty resource name")
            
            # Check for missing closing braces
            open_braces = stripped.count('{')
            close_braces = stripped.count('}')
            if open_braces > close_braces + 1:  # Allow one unclosed brace per line
                errors.append(f"Line {i}: Possible missing closing brace")
    
    except Exception as e:
        errors.append(f"Failed to validate file: {e}")
    
    return errors

# Export commonly used functions
__all__ = [
    'get_template_loader',
    'generate_tf',
    'validate_terraform_syntax',
    'AutoDiscoveryTemplateLoader'
]