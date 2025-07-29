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
    tojson
)

class AutoDiscoveryTemplateLoader:
    """
    Automatically discovers and loads Jinja2 templates from the package's
    'templates' directory. This class is a singleton to ensure the template
    environment is initialized only once.
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
        )
        self.register_custom_filters()
        self.initialized = True

    def _find_main_templates_dir(self) -> Path:
        """
        Reliably find the 'templates' directory within the installed terraback package.
        """
        try:
            return Path(str(importlib.resources.files('terraback').joinpath('templates')))
        except (ModuleNotFoundError, AttributeError):
            return Path(__file__).resolve().parent.parent / "templates"

    def register_custom_filters(self):
        """Register all custom Jinja2 filters."""
        self.env.filters['sanitize'] = sanitize_for_terraform
        self.env.filters['tf_string'] = to_terraform_string
        self.env.filters['tf_list'] = to_terraform_list
        self.env.filters['tf_map'] = to_terraform_map
        self.env.filters['tf_bool'] = to_terraform_bool
        self.env.filters['tf_int'] = to_terraform_int
        self.env.filters['tf_float'] = to_terraform_float
        self.env.filters['tf_resource_name'] = to_terraform_resource_name
        self.env.filters['tojson'] = tojson
        self.env.filters['lower'] = lambda x: str(x).lower() if x is not None else ''
        self.env.filters['upper'] = lambda x: str(x).upper() if x is not None else ''
        self.env.filters['replace'] = lambda x, old, new: str(x).replace(old, new) if x is not None else ''
        self.env.filters['default'] = lambda x, default='': x if x is not None else default
        self.env.filters['safe'] = lambda x: x  # For marking strings as safe

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

    def render_template(self, resource_type: str, resources: list, provider: str = 'aws'):
        """Render template with resources."""
        template_path = self.get_template_path(resource_type, provider)
        template = self.env.get_template(template_path)
        return template.render(resources=resources)

# Global Functions

_loader = None

def get_template_loader():
    """Get the global template loader instance."""
    global _loader
    if _loader is None:
        _loader = AutoDiscoveryTemplateLoader()
    return _loader

def generate_tf(resources: List, resource_type: str, output_path: Path, provider: str = 'aws'):
    """Generate Terraform file using the auto-discovering template loader."""
    if not resources:
        return
        
    loader = get_template_loader()
    tf_output = loader.render_template(resource_type, resources, provider)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tf_output)