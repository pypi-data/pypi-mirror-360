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
    name = re.sub(r"_{2,}", "_", name)
    name = name.strip("_-")

    if name and name[0].isdigit():
        name = f"resource_{name}"

    if not name:
        name = "unnamed_resource"

    return name.lower()

# Enhanced conditional filters that prevent empty assignments
def has_value(value):
    """Check if a value exists and is not empty/None"""
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
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
    """Safely convert to int with default"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_bool(value, default=False):
    """Safely convert to boolean with default"""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ['true', 'yes', '1', 'on', 'enabled']
    return bool(value)

# JSON handling with better None/empty support
def tojson(value):
    """Formats a Python value as JSON for use in Terraform templates."""
    if value is None:
        return "null"
    
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return json.dumps(value)
    elif isinstance(value, (list, dict)):
        return json.dumps(value, indent=2)
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
    if isinstance(value, str):
        return "true" if value.lower() in ['true', 'yes', '1', 'on', 'enabled'] else "false"
    return "true" if value else "false"

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

# String manipulation filters
def escape_quotes(value):
    """Escape quotes in strings for Terraform"""
    if value is None:
        return ""
    return str(value).replace('"', '\\"')

def strip_whitespace(value):
    """Strip whitespace from strings"""
    if value is None:
        return ""
    return str(value).strip()

def terraform_sanitize_name(value):
    """Comprehensive name sanitization for Terraform identifiers"""
    if not value:
        return "default_resource"
    
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
        name = "default_resource"
    
    return name.lower()

# Template-specific helpers
def format_tags(tags_dict):
    """Format tags dictionary for Terraform with proper escaping"""
    if not tags_dict or not isinstance(tags_dict, dict):
        return None
    
    formatted = {}
    for key, value in tags_dict.items():
        if key and value is not None:
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