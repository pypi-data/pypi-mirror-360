from pathlib import Path
from typing import Optional
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_vpcs(output_dir: Path, profile: Optional[str] = None, region: str = "us-east-1"):
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    vpcs = ec2_client.describe_vpcs()["Vpcs"]
    
    output_file = output_dir / "vpc.tf"
    generate_tf(vpcs, "vpc", output_file)
    print(f"Generated Terraform for {len(vpcs)} VPCs -> {output_file}")
    generate_imports_file("vpc", vpcs, remote_resource_id_key="VpcId", output_dir=output_dir)

def list_vpcs(output_dir: Path):
    ImportManager(output_dir, "vpc").list_all()

def import_vpc(vpc_id: str, output_dir: Path):
    ImportManager(output_dir, "vpc").find_and_import(vpc_id)
