from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_subnet_groups(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for ElastiCache subnet groups and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    elasticache_client = boto_session.client("elasticache")
    
    print(f"Scanning for ElastiCache subnet groups in region {region}...")
    
    # Get all cache subnet groups
    subnet_groups = []
    paginator = elasticache_client.get_paginator('describe_cache_subnet_groups')
    
    for page in paginator.paginate():
        for sg in page['CacheSubnetGroups']:
            # Add sanitized name for resource naming
            sg_name = sg['CacheSubnetGroupName']
            sg['name_sanitized'] = sg_name.replace('-', '_').replace('.', '_').lower()
            
            # Format subnets for easier template usage
            if sg.get('Subnets'):
                sg['subnets_formatted'] = []
                sg['subnet_ids'] = []
                
                for subnet in sg['Subnets']:
                    formatted_subnet = {
                        'subnet_id': subnet['SubnetIdentifier'],
                        'availability_zone': subnet.get('SubnetAvailabilityZone', {}).get('Name'),
                        'outpost_arn': subnet.get('SubnetOutpost', {}).get('SubnetOutpostArn')
                    }
                    sg['subnets_formatted'].append(formatted_subnet)
                    sg['subnet_ids'].append(subnet['SubnetIdentifier'])
            else:
                sg['subnets_formatted'] = []
                sg['subnet_ids'] = []
            
            # Extract VPC ID from the first subnet (all subnets in a group are in the same VPC)
            if sg['subnets_formatted']:
                # We'll need to get VPC ID from subnet info if available
                sg['vpc_id'] = sg.get('VpcId')
            else:
                sg['vpc_id'] = sg.get('VpcId')
            
            # Format supported network types
            if sg.get('SupportedNetworkTypes'):
                sg['supported_network_types'] = sg['SupportedNetworkTypes']
            else:
                sg['supported_network_types'] = ['ipv4']  # Default
            
            # Get tags
            try:
                tags_response = elasticache_client.list_tags_for_resource(
                    ResourceName=sg['ARN']
                )
                sg['tags_formatted'] = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
            except Exception as e:
                print(f"  - Warning: Could not retrieve tags for subnet group {sg_name}: {e}")
                sg['tags_formatted'] = {}
            
            subnet_groups.append(sg)
    
    output_file = output_dir / "elasticache_subnet_group.tf"
    generate_tf(subnet_groups, "elasticache_subnet_group", output_file)
    print(f"Generated Terraform for {len(subnet_groups)} ElastiCache subnet groups -> {output_file}")
    generate_imports_file(
        "elasticache_subnet_group", 
        subnet_groups, 
        remote_resource_id_key="CacheSubnetGroupName", 
        output_dir=output_dir
    )

def list_subnet_groups(output_dir: Path):
    """Lists all ElastiCache subnet group resources previously generated."""
    ImportManager(output_dir, "elasticache_subnet_group").list_all()

def import_subnet_group(subnet_group_name: str, output_dir: Path):
    """Runs terraform import for a specific ElastiCache subnet group by its name."""
    ImportManager(output_dir, "elasticache_subnet_group").find_and_import(subnet_group_name)