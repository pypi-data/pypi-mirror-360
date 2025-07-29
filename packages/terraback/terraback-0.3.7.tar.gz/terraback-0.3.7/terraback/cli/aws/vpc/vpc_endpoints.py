from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_vpc_endpoints(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for VPC Endpoints and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    
    print(f"Scanning for VPC Endpoints in region {region}...")
    
    # Get all VPC Endpoints using pagination
    paginator = ec2_client.get_paginator('describe_vpc_endpoints')
    vpc_endpoints = []
    
    for page in paginator.paginate():
        for endpoint in page['VpcEndpoints']:
            # Add sanitized name for resource naming
            endpoint_id = endpoint['VpcEndpointId']
            endpoint['name_sanitized'] = endpoint_id.replace('-', '_')
            
            # Extract service name for easier identification
            service_name = endpoint.get('ServiceName', '')
            if service_name:
                # Extract just the service part (e.g., 's3' from 'com.amazonaws.us-east-1.s3')
                service_parts = service_name.split('.')
                if len(service_parts) >= 3:
                    endpoint['service_short_name'] = service_parts[-1]
                else:
                    endpoint['service_short_name'] = service_name
            else:
                endpoint['service_short_name'] = 'unknown'
            
            # Format DNS entries for easier template usage
            if endpoint.get('DnsEntries'):
                endpoint['dns_entries_formatted'] = []
                for dns_entry in endpoint['DnsEntries']:
                    formatted_entry = {
                        'DnsName': dns_entry.get('DnsName'),
                        'HostedZoneId': dns_entry.get('HostedZoneId')
                    }
                    endpoint['dns_entries_formatted'].append(formatted_entry)
            else:
                endpoint['dns_entries_formatted'] = []
            
            # Format policy document if present
            if endpoint.get('PolicyDocument'):
                endpoint['policy_document'] = endpoint['PolicyDocument']
            else:
                endpoint['policy_document'] = None
            
            # Format route table IDs
            if endpoint.get('RouteTableIds'):
                endpoint['route_table_ids_formatted'] = endpoint['RouteTableIds']
            else:
                endpoint['route_table_ids_formatted'] = []
            
            # Format subnet IDs
            if endpoint.get('SubnetIds'):
                endpoint['subnet_ids_formatted'] = endpoint['SubnetIds']
            else:
                endpoint['subnet_ids_formatted'] = []
            
            # Format security group IDs
            if endpoint.get('Groups'):
                endpoint['security_group_ids_formatted'] = [group['GroupId'] for group in endpoint['Groups']]
            else:
                endpoint['security_group_ids_formatted'] = []
            
            # Determine endpoint type characteristics
            endpoint['is_gateway'] = endpoint.get('VpcEndpointType') == 'Gateway'
            endpoint['is_interface'] = endpoint.get('VpcEndpointType') == 'Interface'
            endpoint['is_gateway_load_balancer'] = endpoint.get('VpcEndpointType') == 'GatewayLoadBalancer'
            
            # Format tags
            if endpoint.get('Tags'):
                endpoint['tags_formatted'] = {tag['Key']: tag['Value'] for tag in endpoint['Tags']}
            else:
                endpoint['tags_formatted'] = {}
            
            vpc_endpoints.append(endpoint)

    output_file = output_dir / "vpc_endpoint.tf"
    generate_tf(vpc_endpoints, "vpc_endpoint", output_file)
    print(f"Generated Terraform for {len(vpc_endpoints)} VPC Endpoints -> {output_file}")
    generate_imports_file(
        "vpc_endpoint", 
        vpc_endpoints, 
        remote_resource_id_key="VpcEndpointId", 
        output_dir=output_dir
    )

def list_vpc_endpoints(output_dir: Path):
    """Lists all VPC Endpoint resources previously generated."""
    ImportManager(output_dir, "vpc_endpoint").list_all()

def import_vpc_endpoint(endpoint_id: str, output_dir: Path):
    """Runs terraform import for a specific VPC Endpoint by its ID."""
    ImportManager(output_dir, "vpc_endpoint").find_and_import(endpoint_id)