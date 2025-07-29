import json
from pathlib import Path
from typing import List, Dict, Any, Optional

def generate_imports_file(
    resource_type: str,
    resources: List[Dict[str, Any]],
    remote_resource_id_key: str,
    output_dir: Path,
    composite_keys: Optional[List[str]] = None
):
    """
    Generates a .json file containing the necessary data for terraform import commands.

    Args:
        resource_type: The Terraform resource type (e.g., "aws_instance").
        resources: The list of resource dictionaries from the AWS API.
        remote_resource_id_key: The key in the resource dict that holds the unique ID.
        output_dir: The directory to save the file in.
        composite_keys (optional): A list of keys to join with '/' to form a composite ID,
                                   required for some resources like API Gateway methods.
    """
    import_data = []
    for resource in resources:
        # Determine the remote ID for the 'terraform import' command.
        if composite_keys:
            # Build the ID from multiple keys, e.g., "api_id/resource_id/method".
            # This is necessary for many API Gateway resources.
            try:
                remote_id = "/".join([str(resource[key]) for key in composite_keys])
            except KeyError as e:
                print(f"Warning: Missing key {e} when building composite ID for a {resource_type}. Skipping.")
                continue
        else:
            remote_id = resource.get(remote_resource_id_key)

        if not remote_id:
            print(f"Warning: Could not determine remote ID for a {resource_type} using key '{remote_resource_id_key}'. Skipping.")
            continue

        # Create a sanitized, unique name for the resource in the Terraform state.
        # Replace ALL invalid characters including |, :, /, spaces, etc.
        import re
        sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', str(remote_id))
        # Ensure it doesn't start with a number
        if sanitized_name and sanitized_name[0].isdigit():
            sanitized_name = '_' + sanitized_name
        # Clean up multiple underscores
        sanitized_name = re.sub(r'_{2,}', '_', sanitized_name)
        sanitized_name = sanitized_name.lower()
        
        import_data.append({
            "resource_type": resource_type,
            "resource_name": f"{resource_type[len('aws_'):] if resource_type.startswith('aws_') else resource_type}_{sanitized_name}",
            "remote_id": remote_id
        })
    
    # Write the data to the corresponding _import.json file.
    import_file = output_dir / f"{resource_type}_import.json"
    try:
        with open(import_file, "w", encoding="utf-8") as f:
            json.dump(import_data, f, indent=2)
    except IOError as e:
        print(f"Error writing import file {import_file}: {e}")