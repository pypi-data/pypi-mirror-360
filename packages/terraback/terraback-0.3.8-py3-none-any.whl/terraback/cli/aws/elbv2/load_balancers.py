from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_load_balancers(output_dir: Path, profile: str = None, region: str = "us-east-1", lb_type: str = None):
    """
    Scans for all modern (v2) Load Balancers (Application, Network, Gateway) 
    and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    elbv2_client = boto_session.client("elbv2")
    
    print(f"Scanning for all v2 Load Balancers (ALB, NLB, GWLB) in region {region}...")
    paginator = elbv2_client.get_paginator('describe_load_balancers')
    load_balancers = []
    for page in paginator.paginate():
        for lb in page['LoadBalancers']:
            # Filter by type if specified
            if lb_type and lb['Type'] != lb_type:
                continue
                
            # Fetch tags for each load balancer
            tags_response = elbv2_client.describe_tags(ResourceArns=[lb['LoadBalancerArn']])
            if tags_response['TagDescriptions']:
                lb['Tags'] = tags_response['TagDescriptions'][0]['Tags']
            else:
                lb['Tags'] = []
            
            # Fetch load balancer attributes
            try:
                attrs_response = elbv2_client.describe_load_balancer_attributes(
                    LoadBalancerArn=lb['LoadBalancerArn']
                )
                lb['Attributes'] = {}
                for attr in attrs_response.get('Attributes', []):
                    lb['Attributes'][attr['Key']] = attr['Value']
            except Exception as e:
                print(f"  - Warning: Could not retrieve attributes for LB {lb['LoadBalancerName']}: {e}")
                lb['Attributes'] = {}
            
            # Add sanitized name for resource naming
            lb['name_sanitized'] = lb['LoadBalancerName'].replace('-', '_').replace('.', '_').lower()
            
            # Format subnet mappings if present
            if lb.get('AvailabilityZones'):
                lb['subnet_mappings'] = []
                for az in lb['AvailabilityZones']:
                    mapping = {
                        'subnet_id': az['SubnetId'],
                        'zone_name': az.get('ZoneName'),
                        'outpost_id': az.get('OutpostId')
                    }
                    # Check for static IPs (NLB)
                    if az.get('LoadBalancerAddresses'):
                        for addr in az['LoadBalancerAddresses']:
                            if addr.get('AllocationId'):
                                mapping['allocation_id'] = addr['AllocationId']
                            if addr.get('PrivateIPv4Address'):
                                mapping['private_ipv4_address'] = addr['PrivateIPv4Address']
                            if addr.get('IPv6Address'):
                                mapping['ipv6_address'] = addr['IPv6Address']
                    lb['subnet_mappings'].append(mapping)
            
            load_balancers.append(lb)

    output_file = output_dir / "elbv2_load_balancer.tf"
    generate_tf(load_balancers, "elbv2_load_balancer", output_file)
    print(f"Generated Terraform for {len(load_balancers)} v2 Load Balancers -> {output_file}")
    generate_imports_file("elbv2_load_balancer", load_balancers, remote_resource_id_key="LoadBalancerArn", output_dir=output_dir)

def list_load_balancers(output_dir: Path):
    ImportManager(output_dir, "elbv2_load_balancer").list_all()

def import_load_balancer(lb_arn: str, output_dir: Path):
    ImportManager(output_dir, "elbv2_load_balancer").find_and_import(lb_arn)