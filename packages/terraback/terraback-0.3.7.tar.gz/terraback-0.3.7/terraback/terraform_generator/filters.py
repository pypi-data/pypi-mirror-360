# terraback/terraform_generator/filters.py

import json
import re

def sanitize_for_terraform(value):
    """
    A general-purpose sanitizer for Terraform resource names.
    
    Terraform resource names must:
    - Contain only letters, numbers, underscores, and hyphens
    - Start with a letter or underscore
    - Be unique within their resource type
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Replace dots and other special characters with underscores
    # This handles: . / - : | @ # $ % ^ & * ( ) + = { } [ ] ; ' " , < > ? space
    value = re.sub(r'[^a-zA-Z0-9_-]', '_', value)
    
    # Replace multiple consecutive underscores with a single underscore
    value = re.sub(r'_{2,}', '_', value)
    
    # Remove leading/trailing underscores or hyphens
    value = value.strip('_-')
    
    # Ensure it starts with a letter or underscore (not a number)
    if value and value[0].isdigit():
        value = 'resource_' + value
    
    # Ensure we have a valid name
    if not value:
        value = "unnamed_resource"
    
    return value
def to_terraform_string(value):
    """Formats a Python string into a Terraform-safe string."""
    if value is None:
        return "null"
    # json.dumps properly escapes strings and uses double quotes
    return json.dumps(value)

def to_terraform_list(value):
    """Formats a Python list into a Terraform list."""
    if value is None:
        return "[]"
    if not isinstance(value, list):
        value = [value]
    return json.dumps(value)

def to_terraform_map(value):
    """Formats a Python dictionary into a Terraform map."""
    if value is None:
        return "{}"
    if not isinstance(value, dict):
        return "{}"
    return json.dumps(value)

def to_terraform_bool(value):
    """Formats a Python boolean into a Terraform boolean."""
    if value is None:
        return "null"
    # Handle various truthy/falsy values
    if isinstance(value, str):
        return "true" if value.lower() in ['true', 'yes', '1', 'on'] else "false"
    return "true" if value else "false"

def to_terraform_int(value):
    """Formats a Python integer into a Terraform number."""
    if value is None:
        return "null"
    try:
        return str(int(value))
    except (ValueError, TypeError):
        return "0"

def to_terraform_float(value):
    """Formats a Python float into a Terraform number."""
    if value is None:
        return "null"
    try:
        return str(float(value))
    except (ValueError, TypeError):
        return "0.0"

def to_terraform_resource_name(value):
    """
    Creates a valid Terraform resource name from a string.
    This is more aggressive than sanitize_for_terraform and ensures
    consistency by converting to lowercase.
    """
    if not value:
        return "unnamed_resource"
    
    # Convert to string if needed
    name = str(value)
    
    # Replace common separators and invalid characters with underscores
    # This handles: . / - : | @ # $ % ^ & * ( ) + = { } [ ] ; ' " , < > ? space
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Replace multiple consecutive underscores with a single underscore
    name = re.sub(r'_{2,}', '_', name)
    
    # Remove leading/trailing underscores
    name = name.strip('_')
    
    # Ensure it starts with a letter or underscore
    if name and name[0].isdigit():
        name = '_' + name
    
    # Ensure we have a valid name
    if not name:
        name = "unnamed_resource"
    
    # Convert to lowercase for consistency
    return name.lower()

def to_terraform_heredoc(value, indent=0):
    """
    Formats a multi-line string as a Terraform heredoc.
    Useful for policies, scripts, and other multi-line content.
    """
    if value is None:
        return '""'
    
    # Ensure it's a string
    value = str(value)
    
    # If it's a single line without special characters, use regular string
    if '\n' not in value and '"' not in value and '${' not in value:
        return to_terraform_string(value)
    
    # Use heredoc for multi-line or complex strings
    indent_str = ' ' * indent
    return f'<<-EOT\n{value}\n{indent_str}EOT'

def to_terraform_jsonencode(value):
    """
    Formats a Python dict/list for Terraform's jsonencode() function.
    This ensures proper formatting for IAM policies and similar JSON structures.
    """
    if value is None:
        return "null"
    
    # If it's already a string (pre-encoded JSON), decode it first
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            # If it's not valid JSON, return it as a string
            return to_terraform_string(value)
    
    # Format with proper indentation for readability
    json_str = json.dumps(value, indent=2)
    return f"jsonencode({json_str})"

# Additional utility functions that might be useful

def escape_terraform_interpolation(value):
    """
    Escapes Terraform interpolation syntax in strings.
    Converts ${var} to $${var} to prevent Terraform from interpreting it.
    """
    if not isinstance(value, str):
        return value
    return value.replace('${', '$${')

def to_terraform_tags(tags_dict):
    """
    Formats a dictionary of tags for Terraform.
    Ensures all tag values are strings and properly formatted.
    """
    if not tags_dict:
        return "{}"
    
    formatted_tags = {}
    for key, value in tags_dict.items():
        # Ensure both key and value are strings
        formatted_tags[str(key)] = str(value) if value is not None else ""
    
    return json.dumps(formatted_tags, indent=2)

def tojson(value):
    """
    Formats a Python value as JSON for use in Terraform templates.
    This is the missing function that's imported in writer.py.
    """
    if value is None:
        return "null"
    
    # Handle different types appropriately
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return json.dumps(value)
    elif isinstance(value, (list, dict)):
        return json.dumps(value, indent=2)
    else:
        # Convert to string and then to JSON
        return json.dumps(str(value))