from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_replication_groups(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for ElastiCache Redis replication groups and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    elasticache_client = boto_session.client("elasticache")
    
    print(f"Scanning for ElastiCache Redis replication groups in region {region}...")
    
    # Get all replication groups
    replication_groups = []
    paginator = elasticache_client.get_paginator('describe_replication_groups')
    
    for page in paginator.paginate():
        for rg in page['ReplicationGroups']:
            # Add sanitized name for resource naming
            rg_id = rg['ReplicationGroupId']
            rg['name_sanitized'] = rg_id.replace('-', '_').replace('.', '_').lower()
            
            # Format node groups for easier template usage
            if rg.get('NodeGroups'):
                rg['node_groups_formatted'] = []
                for ng in rg['NodeGroups']:
                    formatted_ng = {
                        'node_group_id': ng.get('NodeGroupId'),
                        'slots': ng.get('Slots'),
                        'primary_endpoint': ng.get('PrimaryEndpoint'),
                        'reader_endpoint': ng.get('ReaderEndpoint'),
                        'node_group_members': []
                    }
                    
                    if ng.get('NodeGroupMembers'):
                        for member in ng['NodeGroupMembers']:
                            formatted_member = {
                                'cache_cluster_id': member.get('CacheClusterId'),
                                'cache_node_id': member.get('CacheNodeId'),
                                'current_role': member.get('CurrentRole'),
                                'preferred_availability_zone': member.get('PreferredAvailabilityZone'),
                                'preferred_outpost_arn': member.get('PreferredOutpostArn'),
                                'read_endpoint': member.get('ReadEndpoint')
                            }
                            formatted_ng['node_group_members'].append(formatted_member)
                    
                    rg['node_groups_formatted'].append(formatted_ng)
            else:
                rg['node_groups_formatted'] = []
            
            # Format log delivery configurations
            if rg.get('LogDeliveryConfigurations'):
                rg['log_delivery_configurations_formatted'] = []
                for log_config in rg['LogDeliveryConfigurations']:
                    formatted_log_config = {
                        'destination_type': log_config.get('DestinationType'),
                        'destination_details': log_config.get('DestinationDetails', {}),
                        'log_format': log_config.get('LogFormat'),
                        'log_type': log_config.get('LogType'),
                        'status': log_config.get('Status')
                    }
                    rg['log_delivery_configurations_formatted'].append(formatted_log_config)
            else:
                rg['log_delivery_configurations_formatted'] = []
            
            # Format member clusters for easier template usage
            if rg.get('MemberClusters'):
                rg['member_clusters_formatted'] = rg['MemberClusters']
            else:
                rg['member_clusters_formatted'] = []
            
            # Extract network configuration
            if rg.get('CacheSubnetGroupName'):
                rg['cache_subnet_group_name'] = rg['CacheSubnetGroupName']
            else:
                rg['cache_subnet_group_name'] = None
            
            # Format security group IDs
            if rg.get('SecurityGroups'):
                rg['security_group_ids'] = [sg['SecurityGroupId'] for sg in rg['SecurityGroups']]
            else:
                rg['security_group_ids'] = []
            
            # Determine cluster mode
            rg['cluster_mode_enabled'] = rg.get('ClusterEnabled', False)
            
            # Format user group IDs
            if rg.get('UserGroupIds'):
                rg['user_group_ids_formatted'] = rg['UserGroupIds']
            else:
                rg['user_group_ids_formatted'] = []
            
            # Format data tiering status
            rg['data_tiering_enabled'] = rg.get('DataTiering') == 'enabled'
            
            # Get tags
            try:
                tags_response = elasticache_client.list_tags_for_resource(
                    ResourceName=rg['ARN']
                )
                rg['tags_formatted'] = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
            except Exception as e:
                print(f"  - Warning: Could not retrieve tags for replication group {rg_id}: {e}")
                rg['tags_formatted'] = {}
            
            replication_groups.append(rg)
    
    output_file = output_dir / "elasticache_replication_group.tf"
    generate_tf(replication_groups, "elasticache_replication_group", output_file)
    print(f"Generated Terraform for {len(replication_groups)} ElastiCache replication groups -> {output_file}")
    generate_imports_file(
        "elasticache_replication_group", 
        replication_groups, 
        remote_resource_id_key="ReplicationGroupId", 
        output_dir=output_dir
    )

def list_replication_groups(output_dir: Path):
    """Lists all ElastiCache replication group resources previously generated."""
    ImportManager(output_dir, "elasticache_replication_group").list_all()

def import_replication_group(replication_group_id: str, output_dir: Path):
    """Runs terraform import for a specific ElastiCache replication group by its ID."""
    ImportManager(output_dir, "elasticache_replication_group").find_and_import(replication_group_id)