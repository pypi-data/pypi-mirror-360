from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_redis_clusters(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for ElastiCache Redis clusters (individual cache clusters) and generates Terraform code.
    Note: This scans individual cache clusters, not replication groups.
    """
    boto_session = get_boto_session(profile, region)
    elasticache_client = boto_session.client("elasticache")
    
    print(f"Scanning for ElastiCache Redis clusters in region {region}...")
    
    # Get all cache clusters
    redis_clusters = []
    paginator = elasticache_client.get_paginator('describe_cache_clusters')
    
    for page in paginator.paginate(ShowCacheNodeInfo=True):
        for cluster in page['CacheClusters']:
            # Only process Redis clusters (not Memcached)
            if cluster.get('Engine') != 'redis':
                continue
            
            # Skip clusters that are part of replication groups (handled separately)
            if cluster.get('ReplicationGroupId'):
                continue
            
            # Add sanitized name for resource naming
            cluster_id = cluster['CacheClusterId']
            cluster['name_sanitized'] = cluster_id.replace('-', '_').replace('.', '_').lower()
            
            # Format cache nodes for easier template usage
            if cluster.get('CacheNodes'):
                cluster['cache_nodes_formatted'] = []
                for node in cluster['CacheNodes']:
                    formatted_node = {
                        'cache_node_id': node.get('CacheNodeId'),
                        'cache_node_status': node.get('CacheNodeStatus'),
                        'cache_node_create_time': node.get('CacheNodeCreateTime'),
                        'endpoint': node.get('Endpoint'),
                        'parameter_group_status': node.get('ParameterGroupStatus'),
                        'source_cache_node_id': node.get('SourceCacheNodeId'),
                        'customer_availability_zone': node.get('CustomerAvailabilityZone'),
                        'customer_outpost_arn': node.get('CustomerOutpostArn')
                    }
                    cluster['cache_nodes_formatted'].append(formatted_node)
            else:
                cluster['cache_nodes_formatted'] = []
            
            # Format log delivery configurations
            if cluster.get('LogDeliveryConfigurations'):
                cluster['log_delivery_configurations_formatted'] = []
                for log_config in cluster['LogDeliveryConfigurations']:
                    formatted_log_config = {
                        'destination_type': log_config.get('DestinationType'),
                        'destination_details': log_config.get('DestinationDetails', {}),
                        'log_format': log_config.get('LogFormat'),
                        'log_type': log_config.get('LogType'),
                        'status': log_config.get('Status')
                    }
                    cluster['log_delivery_configurations_formatted'].append(formatted_log_config)
            else:
                cluster['log_delivery_configurations_formatted'] = []
            
            # Format security group IDs
            if cluster.get('SecurityGroups'):
                cluster['security_group_ids'] = [sg['SecurityGroupId'] for sg in cluster['SecurityGroups']]
            else:
                cluster['security_group_ids'] = []
            
            # Format cache parameter groups
            if cluster.get('CacheParameterGroup'):
                cluster['cache_parameter_group_name'] = cluster['CacheParameterGroup']['CacheParameterGroupName']
            else:
                cluster['cache_parameter_group_name'] = None
            
            # Format notification topic ARN
            cluster['notification_topic_arn'] = cluster.get('NotificationConfiguration', {}).get('TopicArn')
            
            # Extract network type
            cluster['network_type'] = cluster.get('NetworkType', 'ipv4')
            
            # Get tags
            try:
                tags_response = elasticache_client.list_tags_for_resource(
                    ResourceName=cluster['ARN']
                )
                cluster['tags_formatted'] = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
            except Exception as e:
                print(f"  - Warning: Could not retrieve tags for Redis cluster {cluster_id}: {e}")
                cluster['tags_formatted'] = {}
            
            redis_clusters.append(cluster)
    
    output_file = output_dir / "elasticache_redis_cluster.tf"
    generate_tf(redis_clusters, "elasticache_redis_cluster", output_file)
    print(f"Generated Terraform for {len(redis_clusters)} ElastiCache Redis clusters -> {output_file}")
    generate_imports_file(
        "elasticache_redis_cluster", 
        redis_clusters, 
        remote_resource_id_key="CacheClusterId", 
        output_dir=output_dir
    )

def list_redis_clusters(output_dir: Path):
    """Lists all ElastiCache Redis cluster resources previously generated."""
    ImportManager(output_dir, "elasticache_redis_cluster").list_all()

def import_redis_cluster(cluster_id: str, output_dir: Path):
    """Runs terraform import for a specific ElastiCache Redis cluster by its ID."""
    ImportManager(output_dir, "elasticache_redis_cluster").find_and_import(cluster_id)