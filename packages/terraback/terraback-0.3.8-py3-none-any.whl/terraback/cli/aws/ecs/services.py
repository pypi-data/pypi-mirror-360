from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_services(output_dir: Path, profile: str = None, region: str = "us-east-1", cluster_name: str = None):
    """
    Scans for ECS Services and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ecs_client = boto_session.client("ecs")
    
    print(f"Scanning for ECS Services in region {region}...")
    
    # Get all clusters first
    cluster_arns = []
    if cluster_name:
        # If specific cluster specified, use it
        try:
            response = ecs_client.describe_clusters(clusters=[cluster_name])
            if response['clusters']:
                cluster_arns = [response['clusters'][0]['clusterArn']]
        except Exception as e:
            print(f"Error finding cluster {cluster_name}: {e}")
            return
    else:
        # Get all clusters
        paginator = ecs_client.get_paginator('list_clusters')
        for page in paginator.paginate():
            cluster_arns.extend(page['clusterArns'])
    
    if not cluster_arns:
        print("No ECS clusters found")
        return
    
    # Get services from all clusters
    services = []
    for cluster_arn in cluster_arns:
        cluster_name_from_arn = cluster_arn.split('/')[-1]
        print(f"  Scanning services in cluster: {cluster_name_from_arn}")
        
        # List services in this cluster
        service_arns = []
        paginator = ecs_client.get_paginator('list_services')
        
        for page in paginator.paginate(cluster=cluster_arn):
            service_arns.extend(page['serviceArns'])
        
        if not service_arns:
            continue
        
        # Get detailed service information (process in batches of 10)
        for i in range(0, len(service_arns), 10):
            batch_arns = service_arns[i:i+10]
            
            response = ecs_client.describe_services(
                cluster=cluster_arn,
                services=batch_arns,
                include=['TAGS']
            )
            
            for service in response['services']:
                # Add cluster information
                service['clusterName'] = cluster_name_from_arn
                service['cluster_name_sanitized'] = cluster_name_from_arn.replace('-', '_').replace(' ', '_').replace('.', '_').lower()
                
                # Add sanitized name for resource naming
                service_name = service['serviceName']
                service['name_sanitized'] = service_name.replace('-', '_').replace(' ', '_').replace('.', '_').lower()
                
                # Extract task definition family and revision
                if service.get('taskDefinition'):
                    td_arn = service['taskDefinition']
                    # Extract family:revision from ARN
                    td_parts = td_arn.split('/')[-1].split(':')
                    if len(td_parts) >= 2:
                        service['task_definition_family'] = td_parts[0]
                        service['task_definition_revision'] = td_parts[1]
                    else:
                        service['task_definition_family'] = td_parts[0]
                        service['task_definition_revision'] = None
                
                # Format network configuration for easier template usage
                if service.get('networkConfiguration'):
                    net_config = service['networkConfiguration']
                    if net_config.get('awsvpcConfiguration'):
                        vpc_config = net_config['awsvpcConfiguration']
                        service['network_config_formatted'] = {
                            'subnets': vpc_config.get('subnets', []),
                            'security_groups': vpc_config.get('securityGroups', []),
                            'assign_public_ip': vpc_config.get('assignPublicIp', 'DISABLED') == 'ENABLED'
                        }
                    else:
                        service['network_config_formatted'] = {}
                else:
                    service['network_config_formatted'] = {}
                
                # Format load balancers
                if service.get('loadBalancers'):
                    service['load_balancers_formatted'] = []
                    for lb in service['loadBalancers']:
                        formatted_lb = {
                            'target_group_arn': lb.get('targetGroupArn'),
                            'load_balancer_name': lb.get('loadBalancerName'),
                            'container_name': lb.get('containerName'),
                            'container_port': lb.get('containerPort')
                        }
                        service['load_balancers_formatted'].append(formatted_lb)
                else:
                    service['load_balancers_formatted'] = []
                
                # Format service registries (service discovery)
                if service.get('serviceRegistries'):
                    service['service_registries_formatted'] = []
                    for registry in service['serviceRegistries']:
                        formatted_registry = {
                            'registry_arn': registry.get('registryArn'),
                            'port': registry.get('port'),
                            'container_name': registry.get('containerName'),
                            'container_port': registry.get('containerPort')
                        }
                        service['service_registries_formatted'].append(formatted_registry)
                else:
                    service['service_registries_formatted'] = []
                
                # Format placement constraints
                if service.get('placementConstraints'):
                    service['placement_constraints_formatted'] = []
                    for constraint in service['placementConstraints']:
                        formatted_constraint = {
                            'type': constraint.get('type'),
                            'expression': constraint.get('expression')
                        }
                        service['placement_constraints_formatted'].append(formatted_constraint)
                else:
                    service['placement_constraints_formatted'] = []
                
                # Format placement strategy
                if service.get('placementStrategy'):
                    service['placement_strategy_formatted'] = []
                    for strategy in service['placementStrategy']:
                        formatted_strategy = {
                            'type': strategy.get('type'),
                            'field': strategy.get('field')
                        }
                        service['placement_strategy_formatted'].append(formatted_strategy)
                else:
                    service['placement_strategy_formatted'] = []
                
                # Format capacity provider strategy
                if service.get('capacityProviderStrategy'):
                    service['capacity_provider_strategy_formatted'] = []
                    for strategy in service['capacityProviderStrategy']:
                        formatted_strategy = {
                            'capacity_provider': strategy.get('capacityProvider'),
                            'weight': strategy.get('weight', 0),
                            'base': strategy.get('base', 0)
                        }
                        service['capacity_provider_strategy_formatted'].append(formatted_strategy)
                else:
                    service['capacity_provider_strategy_formatted'] = []
                
                # Determine launch type
                service['is_fargate'] = service.get('launchType') == 'FARGATE'
                service['is_ec2'] = service.get('launchType') == 'EC2'
                
                services.append(service)
    
    output_file = output_dir / "ecs_service.tf"
    generate_tf(services, "ecs_service", output_file)
    print(f"Generated Terraform for {len(services)} ECS Services -> {output_file}")
    generate_imports_file(
        "ecs_service", 
        services, 
        remote_resource_id_key="serviceArn", 
        output_dir=output_dir
    )

def list_services(output_dir: Path):
    """Lists all ECS Service resources previously generated."""
    ImportManager(output_dir, "ecs_service").list_all()

def import_service(service_arn: str, output_dir: Path):
    """Runs terraform import for a specific ECS Service by its ARN."""
    ImportManager(output_dir, "ecs_service").find_and_import(service_arn)