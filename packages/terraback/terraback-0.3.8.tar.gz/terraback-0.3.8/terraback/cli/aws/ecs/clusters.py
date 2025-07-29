from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_clusters(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for ECS Clusters and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ecs_client = boto_session.client("ecs")
    
    print(f"Scanning for ECS Clusters in region {region}...")
    
    # Get all cluster ARNs
    cluster_arns = []
    paginator = ecs_client.get_paginator('list_clusters')
    
    for page in paginator.paginate():
        cluster_arns.extend(page['clusterArns'])
    
    if not cluster_arns:
        print("No ECS clusters found")
        return
    
    # Get detailed cluster information
    clusters = []
    # Process clusters in batches of 100 (API limit)
    for i in range(0, len(cluster_arns), 100):
        batch_arns = cluster_arns[i:i+100]
        
        response = ecs_client.describe_clusters(
            clusters=batch_arns,
            include=['ATTACHMENTS', 'CONFIGURATIONS', 'STATISTICS', 'TAGS']
        )
        
        for cluster in response['clusters']:
            # Add sanitized name for resource naming
            cluster_name = cluster['clusterName']
            cluster['name_sanitized'] = cluster_name.replace('-', '_').replace(' ', '_').replace('.', '_').lower()
            
            # Format capacity providers for easier template usage
            if cluster.get('capacityProviders'):
                cluster['capacity_providers_formatted'] = cluster['capacityProviders']
            else:
                cluster['capacity_providers_formatted'] = []
            
            # Format default capacity provider strategy
            if cluster.get('defaultCapacityProviderStrategy'):
                cluster['default_capacity_strategy_formatted'] = []
                for strategy in cluster['defaultCapacityProviderStrategy']:
                    formatted_strategy = {
                        'capacityProvider': strategy['capacityProvider'],
                        'weight': strategy.get('weight', 0),
                        'base': strategy.get('base', 0)
                    }
                    cluster['default_capacity_strategy_formatted'].append(formatted_strategy)
            else:
                cluster['default_capacity_strategy_formatted'] = []
            
            # Format cluster settings
            if cluster.get('settings'):
                cluster['settings_formatted'] = {}
                for setting in cluster['settings']:
                    cluster['settings_formatted'][setting['name']] = setting['value']
            else:
                cluster['settings_formatted'] = {}
            
            # Format configuration (logging)
            if cluster.get('configuration'):
                cluster['configuration_formatted'] = cluster['configuration']
                if cluster['configuration'].get('executeCommandConfiguration'):
                    cluster['execute_command_enabled'] = True
                    cluster['execute_command_config'] = cluster['configuration']['executeCommandConfiguration']
                else:
                    cluster['execute_command_enabled'] = False
                    cluster['execute_command_config'] = {}
            else:
                cluster['configuration_formatted'] = {}
                cluster['execute_command_enabled'] = False
                cluster['execute_command_config'] = {}
            
            # Format service connect defaults
            if cluster.get('serviceConnectDefaults'):
                cluster['service_connect_defaults_formatted'] = cluster['serviceConnectDefaults']
            else:
                cluster['service_connect_defaults_formatted'] = {}
            
            # Process cluster insights (Container Insights)
            cluster['container_insights_enabled'] = cluster['settings_formatted'].get('containerInsights') == 'enabled'
            
            clusters.append(cluster)
    
    output_file = output_dir / "ecs_cluster.tf"
    generate_tf(clusters, "ecs_cluster", output_file)
    print(f"Generated Terraform for {len(clusters)} ECS Clusters -> {output_file}")
    generate_imports_file(
        "ecs_cluster", 
        clusters, 
        remote_resource_id_key="clusterName", 
        output_dir=output_dir
    )

def list_clusters(output_dir: Path):
    """Lists all ECS Cluster resources previously generated."""
    ImportManager(output_dir, "ecs_cluster").list_all()

def import_cluster(cluster_name: str, output_dir: Path):
    """Runs terraform import for a specific ECS Cluster by its name."""
    ImportManager(output_dir, "ecs_cluster").find_and_import(cluster_name)