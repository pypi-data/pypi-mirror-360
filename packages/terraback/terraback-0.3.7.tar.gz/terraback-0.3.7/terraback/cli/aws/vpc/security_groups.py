from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_security_groups(output_dir: Path, profile: str = None, region: str = "us-east-1", include_all: bool = False):
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    
    all_groups = ec2_client.describe_security_groups()["SecurityGroups"]
    
    security_groups = [sg for sg in all_groups if include_all or sg['GroupName'] != 'default']

    output_file = output_dir / "security_groups.tf"
    generate_tf(security_groups, "security_groups", output_file)
    print(f"Generated Terraform for {len(security_groups)} Security Groups -> {output_file}")
    generate_imports_file("security_groups", security_groups, remote_resource_id_key="GroupId", output_dir=output_dir)

def list_security_groups(output_dir: Path):
    ImportManager(output_dir, "security_groups").list_all()

def import_security_groups(group_id: str, output_dir: Path):
    ImportManager(output_dir, "security_groups").find_and_import(group_id)