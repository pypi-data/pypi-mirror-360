from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_route_tables(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for Route Tables and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    
    print(f"Scanning for Route Tables in region {region}...")
    
    # Get all Route Tables using pagination
    paginator = ec2_client.get_paginator('describe_route_tables')
    route_tables = []
    
    for page in paginator.paginate():
        for rt in page['RouteTables']:
            # Add sanitized name for resource naming
            rt_id = rt['RouteTableId']
            rt['name_sanitized'] = rt_id.replace('-', '_')
            
            # Format routes for easier template usage
            if rt.get('Routes'):
                rt['routes_formatted'] = []
                for route in rt['Routes']:
                    # Skip local routes as they are automatically managed
                    if route.get('GatewayId') == 'local':
                        continue
                    
                    formatted_route = {
                        'DestinationCidrBlock': route.get('DestinationCidrBlock'),
                        'DestinationIpv6CidrBlock': route.get('DestinationIpv6CidrBlock'),
                        'DestinationPrefixListId': route.get('DestinationPrefixListId'),
                        'GatewayId': route.get('GatewayId'),
                        'InstanceId': route.get('InstanceId'),
                        'NatGatewayId': route.get('NatGatewayId'),
                        'NetworkInterfaceId': route.get('NetworkInterfaceId'),
                        'TransitGatewayId': route.get('TransitGatewayId'),
                        'VpcPeeringConnectionId': route.get('VpcPeeringConnectionId'),
                        'CarrierGatewayId': route.get('CarrierGatewayId'),
                        'CoreNetworkArn': route.get('CoreNetworkArn'),
                        'EgressOnlyInternetGatewayId': route.get('EgressOnlyInternetGatewayId'),
                        'LocalGatewayId': route.get('LocalGatewayId'),
                        'State': route.get('State'),
                        'Origin': route.get('Origin')
                    }
                    rt['routes_formatted'].append(formatted_route)
            else:
                rt['routes_formatted'] = []
            
            # Format associations for easier template usage
            if rt.get('Associations'):
                rt['associations_formatted'] = []
                for assoc in rt['Associations']:
                    formatted_assoc = {
                        'RouteTableAssociationId': assoc.get('RouteTableAssociationId'),
                        'SubnetId': assoc.get('SubnetId'),
                        'GatewayId': assoc.get('GatewayId'),
                        'Main': assoc.get('Main', False),
                        'AssociationState': assoc.get('AssociationState', {}).get('State')
                    }
                    rt['associations_formatted'].append(formatted_assoc)
                
                # Identify main route table
                rt['is_main'] = any(assoc.get('Main', False) for assoc in rt['Associations'])
            else:
                rt['associations_formatted'] = []
                rt['is_main'] = False
            
            # Format propagating VGWs
            if rt.get('PropagatingVgws'):
                rt['propagating_vgws_formatted'] = [vgw['GatewayId'] for vgw in rt['PropagatingVgws']]
            else:
                rt['propagating_vgws_formatted'] = []
            
            route_tables.append(rt)

    output_file = output_dir / "route_table.tf"
    generate_tf(route_tables, "route_table", output_file)
    print(f"Generated Terraform for {len(route_tables)} Route Tables -> {output_file}")
    generate_imports_file(
        "route_table", 
        route_tables, 
        remote_resource_id_key="RouteTableId", 
        output_dir=output_dir
    )

def list_route_tables(output_dir: Path):
    """Lists all Route Table resources previously generated."""
    ImportManager(output_dir, "route_table").list_all()

def import_route_table(rt_id: str, output_dir: Path):
    """Runs terraform import for a specific Route Table by its ID."""
    ImportManager(output_dir, "route_table").find_and_import(rt_id)