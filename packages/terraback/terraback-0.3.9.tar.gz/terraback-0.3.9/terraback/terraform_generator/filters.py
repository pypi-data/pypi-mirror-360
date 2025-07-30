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

def to_terraform_resource_name(value: str) -> str:
    """Return a string safe to use as a Terraform resource name."""
    if not value:
        return "unnamed_resource"

    name = str(value)

    # If an ARN or path-like string is provided, grab the last segment
    if name.startswith("arn:"):
        name = name.split(":")[-1]
    if "/" in name:
        name = name.split("/")[-1]

    # Replace invalid characters with underscores
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    
    name = name.replace("-", "_")
    
    name = re.sub(r"_{2,}", "_", name)
    name = name.strip("_-")

    if name and name[0].isdigit():
        name = f"resource_{name}"

    if not name:
        name = "unnamed_resource"

    return name.lower()

# Enhanced conditional filters that prevent empty assignments
def has_value(value):
    """Check if a value exists and is not empty/None/whitespace."""
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    # Handle boolean False as having value (important for Terraform)
    if isinstance(value, bool):
        return True
    return True

def is_defined(value):
    """Check if value is defined (not None)"""
    return value is not None

def is_not_none(value):
    """Check if value is not None"""
    return value is not None

def safe_get(obj, key, default=None):
    """Safely get a value from a dict, handling None objects"""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default

def default_if_empty(value, default=""):
    """Return default if value is None or empty"""
    if not has_value(value):
        return default
    return value

def safe_int(value, default=0):
    """Safely convert to int with default and better error handling."""
    if value is None:
        return default
    try:
        if isinstance(value, str) and value.strip() == "":
            return default
        # Handle string floats like "3.0"
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_bool(value, default=False):
    """Safely convert to boolean string for Terraform with proper lowercase output."""
    if value is None:
        return str(default).lower()
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        return "true" if value.lower() in ['true', 'yes', '1', 'on', 'enabled'] else "false"
    return str(bool(value)).lower()

def terraform_bool(value):
    """Convert Python boolean to Terraform boolean string - enhanced version."""
    if value is None:
        return "false"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        # Handle various string representations
        if value.lower() in ['true', 'yes', '1', 'on', 'enabled']:
            return "true"
        elif value.lower() in ['false', 'no', '0', 'off', 'disabled']:
            return "false"
        else:
            # Try to parse as boolean
            try:
                return str(bool(value)).lower()
            except:
                return "false"
    return str(bool(value)).lower()

# JSON handling with better None/empty support
def tojson(value):
    """Formats a Python value as JSON for use in Terraform templates."""
    if value is None:
        return "null"
    
    if isinstance(value, bool):
        return str(value).lower()  # Ensure terraform-style booleans
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return json.dumps(value)
    elif isinstance(value, (list, dict)):
        return json.dumps(value, indent=2, default=str)
    else:
        return json.dumps(str(value))

# AWS ID prefix removal with better handling
AWS_ID_PREFIXES = [
    "vpc-", "subnet-", "sg-", "i-", "ami-", "vol-", "lt-", "lc-", 
    "eni-", "rtb-", "acl-", "igw-", "snap-", "eipalloc-", "eipassoc-", 
    "pcx-", "lb-", "tg-", "natgw-", "vpce-", "rtbassoc-"
]

def strip_id_prefix(id_str: str) -> str:
    """Remove common AWS ID prefixes and ARN prefixes from a string."""
    if not isinstance(id_str, str):
        return str(id_str) if id_str is not None else "unknown"

    val = str(id_str)

    if val.startswith("arn:"):
        val = val.split(":")[-1]
        val = val.split("/")[-1]

    for prefix in AWS_ID_PREFIXES:
        if val.startswith(prefix):
            val = val[len(prefix):]
            break

    # Remove common IAM path prefixes
    for p in ("role/", "policy/", "user/"):
        if val.startswith(p):
            val = val[len(p):]
            break

    # Ensure we return something valid
    if not val:
        val = "unknown"

    return val

# Enhanced Terraform type converters that never generate empty assignments
def to_terraform_string(value):
    """Formats a Python string into a Terraform-safe string."""
    if value is None:
        return None  # Return None so template can skip the assignment
    return json.dumps(str(value))

def to_terraform_list(value):
    """Formats a Python list into a Terraform list."""
    if value is None or (isinstance(value, list) and len(value) == 0):
        return None  # Return None so template can skip the assignment
    if not isinstance(value, list):
        value = [value]
    return json.dumps(value)

def to_terraform_map(value):
    """Formats a Python dictionary into a Terraform map."""
    if value is None or (isinstance(value, dict) and len(value) == 0):
        return None  # Return None so template can skip the assignment
    if not isinstance(value, dict):
        return None
    return json.dumps(value)

def to_terraform_bool(value):
    """Formats a Python boolean into a Terraform boolean."""
    if value is None:
        return None  # Return None so template can skip the assignment
    return terraform_bool(value)

def to_terraform_int(value):
    """Formats a Python integer into a Terraform number."""
    if value is None:
        return None  # Return None so template can skip the assignment
    try:
        return str(int(value))
    except (ValueError, TypeError):
        return None

def to_terraform_float(value):
    """Formats a Python float into a Terraform number."""
    if value is None:
        return None  # Return None so template can skip the assignment
    try:
        return str(float(value))
    except (ValueError, TypeError):
        return None

# Resource name generator with guaranteed valid output
def generate_resource_name(resource_data, fallback_prefix="resource"):
    """Generate a valid Terraform resource name from resource data"""
    
    # Try various fields that might contain a name
    name_candidates = []
    
    if isinstance(resource_data, dict):
        # Common name fields
        for field in ['Name', 'name', 'ResourceName', 'FunctionName', 'AlarmName', 
                     'PolicyName', 'RoleName', 'LoadBalancerName', 'TargetGroupName',
                     'ClusterName', 'TableName', 'BucketName']:
            if field in resource_data and resource_data[field]:
                name_candidates.append(str(resource_data[field]))
        
        # Try ID fields as fallback
        for field in ['Id', 'id', 'ResourceId', 'InstanceId', 'VolumeId']:
            if field in resource_data and resource_data[field]:
                name_candidates.append(str(resource_data[field]))
    
    # Use the first valid candidate
    for candidate in name_candidates:
        sanitized = to_terraform_resource_name(candidate)
        if sanitized != "unnamed_resource":
            return sanitized
    
    # Ultimate fallback
    return f"{fallback_prefix}_resource"

# String manipulation filters with enhanced null safety
def escape_quotes(value):
    """Escape quotes in strings for Terraform with better null handling."""
    if value is None:
        return ""
    return str(value).replace('"', '\\"').replace("'", "\\'")

def strip_whitespace(value):
    """Strip whitespace from strings"""
    if value is None:
        return ""
    return str(value).strip()

def terraform_name(value):
    """Comprehensive name sanitization for Terraform identifiers - enhanced version."""
    if not value:
        return "unnamed_resource"
    
    # Convert to string and handle various input types
    name = str(value)
    
    # Extract meaningful part from ARNs, paths, etc.
    if ":" in name:
        name = name.split(":")[-1]
    if "/" in name:
        name = name.split("/")[-1]
    
    # Remove or replace invalid characters
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    name = re.sub(r'_+', '_', name)  # Replace multiple underscores
    name = name.strip('_-')
    
    # Ensure it starts with letter or underscore
    if name and name[0].isdigit():
        name = f"res_{name}"
    
    # Ensure minimum length and validity
    if not name or len(name) < 1:
        name = "unnamed_resource"
    
    return name.lower()

def terraform_sanitize_name(value):
    """Alias for terraform_name for backward compatibility."""
    return terraform_name(value)

# Template-specific helpers with enhanced functionality
def format_tags(tags_dict):
    """Format tags dictionary for Terraform with proper escaping"""
    if not tags_dict or not isinstance(tags_dict, dict):
        return None
    
    formatted = {}
    for key, value in tags_dict.items():
        if key and value is not None:
            # Handle various value types
            if isinstance(value, bool):
                formatted[str(key)] = str(value).lower()
            else:
                formatted[str(key)] = str(value)
    
    return formatted if formatted else None

def format_cidr_blocks(cidr_list):
    """Format CIDR blocks list for Terraform"""
    if not cidr_list:
        return None
    
    if isinstance(cidr_list, str):
        return [cidr_list]
    
    if isinstance(cidr_list, list):
        return [str(cidr) for cidr in cidr_list if cidr]
    
    return None

def format_security_groups(sg_list):
    """Format security groups list for Terraform"""
    if not sg_list:
        return None
    
    if isinstance(sg_list, str):
        return [sg_list]
    
    if isinstance(sg_list, list):
        formatted = []
        for sg in sg_list:
            if isinstance(sg, dict) and 'GroupId' in sg:
                formatted.append(sg['GroupId'])
            elif isinstance(sg, str):
                formatted.append(sg)
        return formatted if formatted else None
    
    return None

def format_resource_reference(resource_type, resource_name):
    """Format a Terraform resource reference properly."""
    safe_type = terraform_name(resource_type)
    safe_name = terraform_name(resource_name)
    return f"{safe_type}.{safe_name}"

def conditional_block(condition, content):
    """Only render content block if condition is true and content exists."""
    if not condition or not content:
        return ""
    return content

def strip_empty_lines(text):
    """Remove excessive empty lines from generated content."""
    if not text:
        return ""
    # Replace multiple consecutive newlines with double newline
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    return cleaned.strip()

def join_with_commas(items, quote=True):
    """Join items with commas, optionally quoting strings."""
    if not items:
        return ""
    
    if quote:
        quoted_items = [f'"{item}"' for item in items]
        return ", ".join(quoted_items)
    else:
        return ", ".join(str(item) for item in items)

def indent_text(text, spaces=2):
    """Indent text by specified number of spaces."""
    if not text:
        return ""
    
    indent = " " * spaces
    lines = text.split('\n')
    return '\n'.join(indent + line if line.strip() else line for line in lines)

# Enhanced validation filters
def validate_port(port, default=80):
    """Validate and return a valid port number."""
    try:
        port_num = int(port)
        if 1 <= port_num <= 65535:
            return port_num
        return default
    except (ValueError, TypeError):
        return default

def validate_cidr(cidr, default="0.0.0.0/0"):
    """Basic CIDR validation."""
    if not cidr or not isinstance(cidr, str):
        return default
    
    # Basic regex for CIDR format
    cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    if re.match(cidr_pattern, cidr.strip()):
        return cidr.strip()
    return default

def validate_arn(arn):
    """Basic ARN validation."""
    if not arn or not isinstance(arn, str):
        return False
    return arn.startswith('arn:aws:')

# Standard string filters with null safety - enhanced versions
def safe_lower(value):
    """Safely convert to lowercase."""
    return str(value).lower() if value is not None else ''

def safe_upper(value):
    """Safely convert to uppercase.""" 
    return str(value).upper() if value is not None else ''

def safe_replace(value, old, new):
    """Safely replace substrings."""
    return str(value).replace(old, new) if value is not None else ''

def safe_default(value, default=''):
    """Safely provide default value."""
    return value if value is not None else default

def safe_split(value, delimiter=','):
    """Safely split string into list."""
    if not value:
        return []
    return str(value).split(delimiter)

def safe_join(value, delimiter=', '):
    """Safely join list into string."""
    if not value or not isinstance(value, (list, tuple)):
        return ""
    return delimiter.join(str(item) for item in value)

# Special AWS filters
def extract_region_from_arn(arn):
    """Extract AWS region from ARN."""
    if not arn or not isinstance(arn, str):
        return ""
    
    parts = arn.split(':')
    if len(parts) >= 4:
        return parts[3]  # Region is the 4th component
    return ""

def extract_account_from_arn(arn):
    """Extract AWS account ID from ARN."""
    if not arn or not isinstance(arn, str):
        return ""
    
    parts = arn.split(':')
    if len(parts) >= 5:
        return parts[4]  # Account is the 5th component
    return ""

def extract_resource_from_arn(arn):
    """Extract resource name from ARN."""
    if not arn or not isinstance(arn, str):
        return ""
    
    parts = arn.split(':')
    if len(parts) >= 6:
        resource_part = parts[5]
        # Handle resource-type/resource-name format
        if '/' in resource_part:
            return resource_part.split('/')[-1]
        return resource_part
    return ""

# Collection manipulation filters
def group_by_key(items, key):
    """Group list of dicts by a specific key."""
    if not items or not isinstance(items, list):
        return {}
    
    grouped = {}
    for item in items:
        if isinstance(item, dict) and key in item:
            group_key = item[key]
            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(item)
    
    return grouped

def unique_values(items):
    """Get unique values from a list while preserving order."""
    if not items:
        return []
    
    seen = set()
    unique = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    
    return unique

def filter_by_key(items, key, value):
    """Filter list of dicts by key-value pair."""
    if not items or not isinstance(items, list):
        return []
    
    return [item for item in items 
            if isinstance(item, dict) and item.get(key) == value]

def sort_by_key(items, key, reverse=False):
    """Sort list of dicts by a specific key."""
    if not items or not isinstance(items, list):
        return items
    
    return sorted(items, 
                 key=lambda x: x.get(key, '') if isinstance(x, dict) else str(x),
                 reverse=reverse)

# Export all filters for easy registration
ALL_FILTERS = {
    # Basic sanitization
    'sanitize': sanitize_for_terraform,
    'tf_resource_name': to_terraform_resource_name,
    'terraform_name': terraform_name,
    'terraform_sanitize_name': terraform_sanitize_name,
    
    # Type conversion
    'tf_string': to_terraform_string,
    'tf_list': to_terraform_list,
    'tf_map': to_terraform_map,
    'tf_bool': to_terraform_bool,
    'tf_int': to_terraform_int,
    'tf_float': to_terraform_float,
    'tojson': tojson,
    
    # Safe conversion
    'safe_int': safe_int,
    'safe_bool': safe_bool,
    'terraform_bool': terraform_bool,
    'safe_lower': safe_lower,
    'safe_upper': safe_upper,
    'safe_replace': safe_replace,
    'safe_default': safe_default,
    'safe_split': safe_split,
    'safe_join': safe_join,
    
    # ID and name handling
    'strip_id_prefix': strip_id_prefix,
    'generate_name': generate_resource_name,
    
    # Conditional checks
    'has_value': has_value,
    'is_defined': is_defined,
    'is_not_none': is_not_none,
    'safe_get': safe_get,
    'default_if_empty': default_if_empty,
    
    # String manipulation
    'escape_quotes': escape_quotes,
    'strip_whitespace': strip_whitespace,
    'strip_empty_lines': strip_empty_lines,
    'indent_text': indent_text,
    'join_with_commas': join_with_commas,
    
    # Formatting helpers
    'format_tags': format_tags,
    'format_cidrs': format_cidr_blocks,
    'format_sgs': format_security_groups,
    'format_resource_reference': format_resource_reference,
    'conditional_block': conditional_block,
    
    # Validation
    'validate_port': validate_port,
    'validate_cidr': validate_cidr,
    'validate_arn': validate_arn,
    
    # AWS specific
    'extract_region_from_arn': extract_region_from_arn,
    'extract_account_from_arn': extract_account_from_arn,
    'extract_resource_from_arn': extract_resource_from_arn,
    
    # Collection manipulation
    'group_by_key': group_by_key,
    'unique_values': unique_values,
    'filter_by_key': filter_by_key,
    'sort_by_key': sort_by_key,
    
    # Legacy compatibility
    'lower': safe_lower,
    'upper': safe_upper,
    'replace': safe_replace,
    'default': safe_default,
    'safe': lambda x: x,  # For marking strings as safe
}
