from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_parameter_groups(output_dir: Path, profile: str = None, region: str = "us-east-1", family: str = None):
    """
    Scans for ElastiCache parameter groups and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    elasticache_client = boto_session.client("elasticache")
    
    print(f"Scanning for ElastiCache parameter groups in region {region}...")
    
    # Get all cache parameter groups
    parameter_groups = []
    paginator = elasticache_client.get_paginator('describe_cache_parameter_groups')
    
    # Build pagination parameters
    paginate_kwargs = {}
    if family:
        paginate_kwargs['CacheParameterGroupFamily'] = family
    
    for page in paginator.paginate(**paginate_kwargs):
        for pg in page['CacheParameterGroups']:
            # Skip default parameter groups unless specifically requested
            pg_name = pg['CacheParameterGroupName']
            if pg_name.startswith('default.'):
                continue
            
            # Add sanitized name for resource naming
            pg['name_sanitized'] = pg_name.replace('-', '_').replace('.', '_').lower()
            
            # Get parameters for this parameter group
            try:
                params_response = elasticache_client.describe_cache_parameters(
                    CacheParameterGroupName=pg_name
                )
                
                # Format parameters for easier template usage
                pg['parameters_formatted'] = []
                if params_response.get('Parameters'):
                    for param in params_response['Parameters']:
                        # Only include parameters that have been modified from defaults
                        if param.get('IsModifiable') and param.get('ParameterValue') != param.get('DefaultValue'):
                            formatted_param = {
                                'name': param['ParameterName'],
                                'value': param['ParameterValue'],
                                'description': param.get('Description', ''),
                                'data_type': param.get('DataType'),
                                'allowed_values': param.get('AllowedValues'),
                                'minimum_engine_version': param.get('MinimumEngineVersion'),
                                'change_type': param.get('ChangeType')
                            }
                            pg['parameters_formatted'].append(formatted_param)
                
            except Exception as e:
                print(f"  - Warning: Could not retrieve parameters for parameter group {pg_name}: {e}")
                pg['parameters_formatted'] = []
            
            # Determine engine type from family
            family_name = pg.get('CacheParameterGroupFamily', '')
            if family_name.startswith('redis'):
                pg['engine_type'] = 'redis'
            elif family_name.startswith('memcached'):
                pg['engine_type'] = 'memcached'
            else:
                pg['engine_type'] = 'unknown'
            
            # Get tags
            try:
                tags_response = elasticache_client.list_tags_for_resource(
                    ResourceName=pg['ARN']
                )
                pg['tags_formatted'] = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
            except Exception as e:
                print(f"  - Warning: Could not retrieve tags for parameter group {pg_name}: {e}")
                pg['tags_formatted'] = {}
            
            parameter_groups.append(pg)
    
    output_file = output_dir / "elasticache_parameter_group.tf"
    generate_tf(parameter_groups, "elasticache_parameter_group", output_file)
    print(f"Generated Terraform for {len(parameter_groups)} ElastiCache parameter groups -> {output_file}")
    generate_imports_file(
        "elasticache_parameter_group", 
        parameter_groups, 
        remote_resource_id_key="CacheParameterGroupName", 
        output_dir=output_dir
    )

def list_parameter_groups(output_dir: Path):
    """Lists all ElastiCache parameter group resources previously generated."""
    ImportManager(output_dir, "elasticache_parameter_group").list_all()

def import_parameter_group(parameter_group_name: str, output_dir: Path):
    """Runs terraform import for a specific ElastiCache parameter group by its name."""
    ImportManager(output_dir, "elasticache_parameter_group").find_and_import(parameter_group_name)