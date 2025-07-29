from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_eips(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    
    addresses = ec2_client.describe_addresses()["Addresses"]
    
    output_file = output_dir / "eips.tf"
    generate_tf(addresses, "eips", output_file)
    print(f"Generated Terraform for {len(addresses)} EIPs -> {output_file}")
    generate_imports_file("eips", addresses, remote_resource_id_key="AllocationId", output_dir=output_dir)

def list_eips(output_dir: Path):
    ImportManager(output_dir, "eips").list_all()

def import_eip(allocation_id: str, output_dir: Path):
    ImportManager(output_dir, "eips").find_and_import(allocation_id)