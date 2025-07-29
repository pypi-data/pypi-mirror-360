from pathlib import Path
import json
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_task_definitions(output_dir: Path, profile: str = None, region: str = "us-east-1", family_prefix: str = None, include_inactive: bool = False):
    """
    Scans for ECS Task Definitions and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ecs_client = boto_session.client("ecs")
    
    print(f"Scanning for ECS Task Definitions in region {region}...")
    
    # Get task definition families first
    families = []
    paginator = ecs_client.get_paginator('list_task_definition_families')
    
    list_params = {}
    if not include_inactive:
        list_params['status'] = 'ACTIVE'
    if family_prefix:
        list_params['familyPrefix'] = family_prefix
    
    for page in paginator.paginate(**list_params):
        families.extend(page['families'])
    
    if not families:
        print("No task definition families found")
        return
    
    # For each family, get the latest task definition
    task_definitions = []
    for family in families:
        try:
            # Get the latest task definition for this family
            response = ecs_client.describe_task_definition(
                taskDefinition=family,
                include=['TAGS']
            )
            
            task_def = response['taskDefinition']
            
            # Add sanitized name for resource naming
            family_name = task_def['family']
            task_def['family_sanitized'] = family_name.replace('-', '_').replace(' ', '_').replace('.', '_').lower()
            
            # Format container definitions for easier template usage
            if task_def.get('containerDefinitions'):
                task_def['containers_formatted'] = []
                for container in task_def['containerDefinitions']:
                    formatted_container = {
                        'name': container['name'],
                        'image': container['image'],
                        'memory': container.get('memory'),
                        'memory_reservation': container.get('memoryReservation'),
                        'cpu': container.get('cpu', 0),
                        'essential': container.get('essential', True),
                        'entry_point': container.get('entryPoint', []),
                        'command': container.get('command', []),
                        'working_directory': container.get('workingDirectory'),
                        'environment': container.get('environment', []),
                        'secrets': container.get('secrets', []),
                        'mount_points': container.get('mountPoints', []),
                        'volumes_from': container.get('volumesFrom', []),
                        'port_mappings': container.get('portMappings', []),
                        'depends_on': container.get('dependsOn', []),
                        'links': container.get('links', []),
                        'hostname': container.get('hostname'),
                        'user': container.get('user'),
                        'disable_networking': container.get('disableNetworking', False),
                        'privileged': container.get('privileged', False),
                        'readonly_root_filesystem': container.get('readonlyRootFilesystem', False),
                        'dns_servers': container.get('dnsServers', []),
                        'dns_search_domains': container.get('dnsSearchDomains', []),
                        'extra_hosts': container.get('extraHosts', []),
                        'docker_security_options': container.get('dockerSecurityOptions', []),
                        'interactive': container.get('interactive', False),
                        'pseudo_terminal': container.get('pseudoTerminal', False),
                        'docker_labels': container.get('dockerLabels', {}),
                        'ulimits': container.get('ulimits', []),
                        'start_timeout': container.get('startTimeout'),
                        'stop_timeout': container.get('stopTimeout'),
                        'system_controls': container.get('systemControls', [])
                    }
                    
                    # Format log configuration
                    if container.get('logConfiguration'):
                        log_config = container['logConfiguration']
                        formatted_container['log_configuration'] = {
                            'log_driver': log_config.get('logDriver'),
                            'options': log_config.get('options', {}),
                            'secret_options': log_config.get('secretOptions', [])
                        }
                    else:
                        formatted_container['log_configuration'] = None
                    
                    # Format health check
                    if container.get('healthCheck'):
                        health_check = container['healthCheck']
                        formatted_container['health_check'] = {
                            'command': health_check.get('command', []),
                            'interval': health_check.get('interval'),
                            'timeout': health_check.get('timeout'),
                            'retries': health_check.get('retries'),
                            'start_period': health_check.get('startPeriod')
                        }
                    else:
                        formatted_container['health_check'] = None
                    
                    # Format repository credentials
                    if container.get('repositoryCredentials'):
                        formatted_container['repository_credentials'] = container['repositoryCredentials']
                    else:
                        formatted_container['repository_credentials'] = None
                    
                    # Format Linux parameters
                    if container.get('linuxParameters'):
                        linux_params = container['linuxParameters']
                        formatted_container['linux_parameters'] = {
                            'capabilities': linux_params.get('capabilities', {}),
                            'devices': linux_params.get('devices', []),
                            'init_process_enabled': linux_params.get('initProcessEnabled', False),
                            'shared_memory_size': linux_params.get('sharedMemorySize'),
                            'tmpfs': linux_params.get('tmpfs', []),
                            'max_swap': linux_params.get('maxSwap'),
                            'swappiness': linux_params.get('swappiness')
                        }
                    else:
                        formatted_container['linux_parameters'] = None
                    
                    # Format firelens configuration
                    if container.get('firelensConfiguration'):
                        formatted_container['firelens_configuration'] = container['firelensConfiguration']
                    else:
                        formatted_container['firelens_configuration'] = None
                    
                    task_def['containers_formatted'].append(formatted_container)
            else:
                task_def['containers_formatted'] = []
            
            # Format volumes
            if task_def.get('volumes'):
                task_def['volumes_formatted'] = []
                for volume in task_def['volumes']:
                    formatted_volume = {
                        'name': volume['name'],
                        'host': volume.get('host'),
                        'docker_volume_configuration': volume.get('dockerVolumeConfiguration'),
                        'efs_volume_configuration': volume.get('efsVolumeConfiguration'),
                        'fsx_windows_file_server_volume_configuration': volume.get('fsxWindowsFileServerVolumeConfiguration')
                    }
                    task_def['volumes_formatted'].append(formatted_volume)
            else:
                task_def['volumes_formatted'] = []
            
            # Format placement constraints
            if task_def.get('placementConstraints'):
                task_def['placement_constraints_formatted'] = []
                for constraint in task_def['placementConstraints']:
                    formatted_constraint = {
                        'type': constraint.get('type'),
                        'expression': constraint.get('expression')
                    }
                    task_def['placement_constraints_formatted'].append(formatted_constraint)
            else:
                task_def['placement_constraints_formatted'] = []
            
            # Format proxy configuration
            if task_def.get('proxyConfiguration'):
                proxy_config = task_def['proxyConfiguration']
                task_def['proxy_configuration_formatted'] = {
                    'type': proxy_config.get('type'),
                    'container_name': proxy_config.get('containerName'),
                    'properties': proxy_config.get('properties', [])
                }
            else:
                task_def['proxy_configuration_formatted'] = None
            
            # Format inference accelerators
            if task_def.get('inferenceAccelerators'):
                task_def['inference_accelerators_formatted'] = []
                for accelerator in task_def['inferenceAccelerators']:
                    formatted_accelerator = {
                        'device_name': accelerator.get('deviceName'),
                        'device_type': accelerator.get('deviceType')
                    }
                    task_def['inference_accelerators_formatted'].append(formatted_accelerator)
            else:
                task_def['inference_accelerators_formatted'] = []
            
            # Format ephemeral storage
            if task_def.get('ephemeralStorage'):
                task_def['ephemeral_storage_formatted'] = {
                    'size_in_gib': task_def['ephemeralStorage']['sizeInGiB']
                }
            else:
                task_def['ephemeral_storage_formatted'] = None
            
            # Format runtime platform
            if task_def.get('runtimePlatform'):
                runtime_platform = task_def['runtimePlatform']
                task_def['runtime_platform_formatted'] = {
                    'cpu_architecture': runtime_platform.get('cpuArchitecture'),
                    'operating_system_family': runtime_platform.get('operatingSystemFamily')
                }
            else:
                task_def['runtime_platform_formatted'] = None
            
            # Determine if it's Fargate compatible
            task_def['is_fargate_compatible'] = task_def.get('requiresCompatibilities') and 'FARGATE' in task_def['requiresCompatibilities']
            task_def['is_ec2_compatible'] = task_def.get('requiresCompatibilities') and 'EC2' in task_def['requiresCompatibilities']
            
            # Get tags if available
            if 'tags' in response:
                task_def['tags_formatted'] = {tag['key']: tag['value'] for tag in response['tags']}
            else:
                task_def['tags_formatted'] = {}
            
            task_definitions.append(task_def)
            
        except Exception as e:
            print(f"  - Warning: Could not retrieve task definition for family {family}: {e}")
            continue
    
    output_file = output_dir / "ecs_task_definition.tf"
    generate_tf(task_definitions, "ecs_task_definition", output_file)
    print(f"Generated Terraform for {len(task_definitions)} ECS Task Definitions -> {output_file}")
    generate_imports_file(
        "ecs_task_definition", 
        task_definitions, 
        remote_resource_id_key="taskDefinitionArn", 
        output_dir=output_dir
    )

def list_task_definitions(output_dir: Path):
    """Lists all ECS Task Definition resources previously generated."""
    ImportManager(output_dir, "ecs_task_definition").list_all()

def import_task_definition(task_definition_arn: str, output_dir: Path):
    """Runs terraform import for a specific ECS Task Definition by its ARN."""
    ImportManager(output_dir, "ecs_task_definition").find_and_import(task_definition_arn)