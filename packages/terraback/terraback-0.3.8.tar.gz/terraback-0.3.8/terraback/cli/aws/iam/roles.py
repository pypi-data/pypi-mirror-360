from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_roles(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    boto_session = get_boto_session(profile, region)
    iam_client = boto_session.client("iam")
    
    paginator = iam_client.get_paginator('list_roles')
    roles = []
    for page in paginator.paginate():
        roles.extend(page['Roles'])
        
    output_file = output_dir / "iam_roles.tf"
    generate_tf(roles, "iam_roles", output_file)
    print(f"Generated Terraform for {len(roles)} IAM Roles -> {output_file}")
    generate_imports_file("iam_roles", roles, remote_resource_id_key="RoleName", output_dir=output_dir)

def list_roles(output_dir: Path):
    ImportManager(output_dir, "iam_roles").list_all()

def import_role(role_name: str, output_dir: Path):
    ImportManager(output_dir, "iam_roles").find_and_import(role_name)