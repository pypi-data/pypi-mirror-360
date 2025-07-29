from pathlib import Path
from typing import List, Optional
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_parameters(output_dir: Path, profile: str = None, region: str = "us-east-1", 
                   parameter_filters: Optional[List[str]] = None, include_secure: bool = True,
                   max_results: int = 50):
    """
    Scans for Systems Manager parameters and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ssm_client = boto_session.client("ssm")
    
    print(f"Scanning for Systems Manager parameters in region {region}...")
    
    # Build parameter filters
    filters = []
    if parameter_filters:
        for filter_pattern in parameter_filters:
            filters.append({
                'Key': 'Name',
                'Option': 'BeginsWith',
                'Values': [filter_pattern.strip()]
            })
    
    # If no filters provided, add common filters to avoid AWS managed parameters
    if not filters:
        filters = [
            {
                'Key': 'Name',
                'Option': 'BeginsWith',
                'Values': ['/aws/', '/ssm/']
            }
        ]
    
    parameters = []
    
    try:
        # Get parameters using pagination
        paginator = ssm_client.get_paginator('describe_parameters')
        
        pagination_config = {
            'MaxItems': max_results,
            'PageSize': min(50, max_results)  # API limit is 50 per page
        }
        
        # Use filters if provided
        paginate_kwargs = {'PaginationConfig': pagination_config}
        if filters and not any(f['Values'] == ['/aws/', '/ssm/'] for f in filters):
            paginate_kwargs['ParameterFilters'] = filters
        
        for page in paginator.paginate(**paginate_kwargs):
            for param_metadata in page.get('Parameters', []):
                parameter_name = param_metadata['Name']
                parameter_type = param_metadata['Type']
                
                # Skip SecureString parameters if not requested
                if parameter_type == 'SecureString' and not include_secure:
                    continue
                
                # Skip AWS managed parameters unless specifically filtered
                if parameter_name.startswith('/aws/') and not any(
                    any(pattern in parameter_name for pattern in f.get('Values', []))
                    for f in (parameter_filters or [])
                ):
                    continue
                
                try:
                    # Get parameter details (but not the value for security)
                    parameter_detail = ssm_client.get_parameter(
                        Name=parameter_name,
                        WithDecryption=False  # Don't decrypt for security
                    )
                    
                    # Create parameter object
                    parameter = {
                        'Name': parameter_name,
                        'Type': parameter_type,
                        'Value': parameter_detail['Parameter']['Value'] if parameter_type != 'SecureString' else None,
                        'Version': parameter_detail['Parameter']['Version'],
                        'LastModifiedDate': parameter_detail['Parameter']['LastModifiedDate'],
                        'ARN': parameter_detail['Parameter']['ARN']
                    }
                    
                    # Add metadata from describe_parameters
                    parameter.update({
                        'Description': param_metadata.get('Description', ''),
                        'KeyId': param_metadata.get('KeyId'),  # KMS key for SecureString
                        'Tier': param_metadata.get('Tier', 'Standard'),
                        'Policies': param_metadata.get('Policies', []),
                        'DataType': param_metadata.get('DataType', 'text'),
                        'AllowedPattern': param_metadata.get('AllowedPattern')
                    })
                    
                    # Add sanitized name for resource naming
                    parameter['name_sanitized'] = parameter_name.replace('/', '_').replace('-', '_').replace(' ', '_').replace('.', '_').lower().lstrip('_')
                    
                    # Determine parameter category
                    if parameter_name.startswith('/aws/'):
                        parameter['category'] = 'aws_managed'
                    elif parameter_name.startswith('/ssm/'):
                        parameter['category'] = 'ssm_managed'
                    elif 'database' in parameter_name.lower() or 'db' in parameter_name.lower():
                        parameter['category'] = 'database'
                    elif 'api' in parameter_name.lower() or 'key' in parameter_name.lower():
                        parameter['category'] = 'api_key'
                    elif 'config' in parameter_name.lower() or 'setting' in parameter_name.lower():
                        parameter['category'] = 'configuration'
                    else:
                        parameter['category'] = 'custom'
                    
                    # Format for template usage
                    parameter['is_secure'] = parameter_type == 'SecureString'
                    parameter['is_string_list'] = parameter_type == 'StringList'
                    parameter['is_standard_tier'] = parameter['Tier'] == 'Standard'
                    parameter['is_advanced_tier'] = parameter['Tier'] == 'Advanced'
                    parameter['is_intelligent_tier'] = parameter['Tier'] == 'Intelligent-Tiering'
                    
                    # Handle KMS encryption
                    if parameter['is_secure'] and parameter.get('KeyId'):
                        parameter['kms_key_id'] = parameter['KeyId']
                    else:
                        parameter['kms_key_id'] = None
                    
                    # Format policies
                    parameter['policies_formatted'] = []
                    for policy in parameter.get('Policies', []):
                        formatted_policy = {
                            'PolicyType': policy.get('PolicyType'),
                            'PolicyStatus': policy.get('PolicyStatus'),
                            'PolicyText': policy.get('PolicyText')
                        }
                        parameter['policies_formatted'].append(formatted_policy)
                    
                    # Get tags
                    try:
                        tags_response = ssm_client.list_tags_for_resource(
                            ResourceType='Parameter',
                            ResourceId=parameter_name
                        )
                        parameter['tags_formatted'] = {
                            tag['Key']: tag['Value'] 
                            for tag in tags_response.get('TagList', [])
                        }
                    except Exception as e:
                        print(f"  - Warning: Could not retrieve tags for parameter {parameter_name}: {e}")
                        parameter['tags_formatted'] = {}
                    
                    parameters.append(parameter)
                    
                except Exception as e:
                    print(f"  - Warning: Could not retrieve details for parameter {parameter_name}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error scanning parameters: {e}")
        return
    
    # Generate parameters
    if parameters:
        output_file = output_dir / "ssm_parameter.tf"
        generate_tf(parameters, "ssm_parameter", output_file)
        print(f"Generated Terraform for {len(parameters)} Systems Manager parameters -> {output_file}")
        generate_imports_file(
            "ssm_parameter", 
            parameters, 
            remote_resource_id_key="Name", 
            output_dir=output_dir
        )

def list_parameters(output_dir: Path):
    """Lists all Systems Manager parameter resources previously generated."""
    ImportManager(output_dir, "ssm_parameter").list_all()

def import_parameter(parameter_name: str, output_dir: Path):
    """Runs terraform import for a specific Systems Manager parameter by its name."""
    ImportManager(output_dir, "ssm_parameter").find_and_import(parameter_name)