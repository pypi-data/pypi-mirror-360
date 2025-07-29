from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_subnets(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    subnets = ec2_client.describe_subnets()["Subnets"]
    
    output_file = output_dir / "subnets.tf"
    generate_tf(subnets, "subnets", output_file)
    print(f"Generated Terraform for {len(subnets)} subnets -> {output_file}")
    generate_imports_file("subnets", subnets, remote_resource_id_key="SubnetId", output_dir=output_dir)

def list_subnets(output_dir: Path):
    ImportManager(output_dir, "subnets").list_all()

def import_subnets(subnets_id: str, output_dir: Path):
    ImportManager(output_dir, "subnets").find_and_import(subnets_id)