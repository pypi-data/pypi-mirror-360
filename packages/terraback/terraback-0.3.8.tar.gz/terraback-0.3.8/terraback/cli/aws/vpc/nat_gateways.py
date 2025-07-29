from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_nat_gateways(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for NAT Gateways and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    
    print(f"Scanning for NAT Gateways in region {region}...")
    
    # Get all NAT Gateways using pagination
    paginator = ec2_client.get_paginator('describe_nat_gateways')
    nat_gateways = []
    
    for page in paginator.paginate():
        for natgw in page['NatGateways']:
            # Add sanitized name for resource naming
            natgw_id = natgw['NatGatewayId']
            natgw['name_sanitized'] = natgw_id.replace('-', '_')
            
            # Format NAT Gateway addresses for easier template usage
            if natgw.get('NatGatewayAddresses'):
                natgw['addresses_formatted'] = []
                for address in natgw['NatGatewayAddresses']:
                    formatted_address = {
                        'AllocationId': address.get('AllocationId'),
                        'NetworkInterfaceId': address.get('NetworkInterfaceId'),
                        'PrivateIp': address.get('PrivateIp'),
                        'PublicIp': address.get('PublicIp')
                    }
                    natgw['addresses_formatted'].append(formatted_address)
                
                # Extract primary allocation ID for template
                primary_address = natgw['addresses_formatted'][0] if natgw['addresses_formatted'] else {}
                natgw['primary_allocation_id'] = primary_address.get('AllocationId')
            else:
                natgw['addresses_formatted'] = []
                natgw['primary_allocation_id'] = None
            
            # Determine connectivity type
            natgw['connectivity_type'] = natgw.get('ConnectivityType', 'public')
            natgw['is_private'] = natgw['connectivity_type'] == 'private'
            
            nat_gateways.append(natgw)

    output_file = output_dir / "nat_gateway.tf"
    generate_tf(nat_gateways, "nat_gateway", output_file)
    print(f"Generated Terraform for {len(nat_gateways)} NAT Gateways -> {output_file}")
    generate_imports_file(
        "nat_gateway", 
        nat_gateways, 
        remote_resource_id_key="NatGatewayId", 
        output_dir=output_dir
    )

def list_nat_gateways(output_dir: Path):
    """Lists all NAT Gateway resources previously generated."""
    ImportManager(output_dir, "nat_gateway").list_all()

def import_nat_gateway(natgw_id: str, output_dir: Path):
    """Runs terraform import for a specific NAT Gateway by its ID."""
    ImportManager(output_dir, "nat_gateway").find_and_import(natgw_id)