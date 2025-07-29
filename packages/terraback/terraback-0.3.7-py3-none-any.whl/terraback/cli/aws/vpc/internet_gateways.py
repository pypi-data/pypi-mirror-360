from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_internet_gateways(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for Internet Gateways and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    
    print(f"Scanning for Internet Gateways in region {region}...")
    
    # Get all Internet Gateways
    response = ec2_client.describe_internet_gateways()
    internet_gateways = []
    
    for igw in response['InternetGateways']:
        # Add sanitized name for resource naming
        igw_id = igw['InternetGatewayId']
        igw['name_sanitized'] = igw_id.replace('-', '_')
        
        # Format attachments for easier template usage
        if igw.get('Attachments'):
            igw['attachments_formatted'] = []
            for attachment in igw['Attachments']:
                formatted_attachment = {
                    'VpcId': attachment['VpcId'],
                    'State': attachment['State']
                }
                igw['attachments_formatted'].append(formatted_attachment)
        else:
            igw['attachments_formatted'] = []
        
        # Check if IGW is attached to any VPC
        igw['is_attached'] = len(igw['attachments_formatted']) > 0
        if igw['is_attached']:
            igw['attached_vpc_id'] = igw['attachments_formatted'][0]['VpcId']
        else:
            igw['attached_vpc_id'] = None
        
        internet_gateways.append(igw)

    output_file = output_dir / "internet_gateway.tf"
    generate_tf(internet_gateways, "internet_gateway", output_file)
    print(f"Generated Terraform for {len(internet_gateways)} Internet Gateways -> {output_file}")
    generate_imports_file(
        "internet_gateway", 
        internet_gateways, 
        remote_resource_id_key="InternetGatewayId", 
        output_dir=output_dir
    )

def list_internet_gateways(output_dir: Path):
    """Lists all Internet Gateway resources previously generated."""
    ImportManager(output_dir, "internet_gateway").list_all()

def import_internet_gateway(igw_id: str, output_dir: Path):
    """Runs terraform import for a specific Internet Gateway by its ID."""
    ImportManager(output_dir, "internet_gateway").find_and_import(igw_id)