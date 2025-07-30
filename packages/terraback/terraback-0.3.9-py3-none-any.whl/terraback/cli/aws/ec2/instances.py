from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

from typing import Optional

def scan_ec2(
    output_dir: Path,
    profile: Optional[str] = None,
    region: str = "us-east-1",
    include_all_states: bool = False
):
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    paginator = ec2_client.get_paginator("describe_instances")

    terraform_resources = []
    
    states_to_include = {
        'pending', 'running', 'shutting-down', 
        'terminated', 'stopping', 'stopped'
    } if include_all_states else {'running'}
    
    print(f"Scanning for EC2 instances in region {region}...")

    page_iterator = paginator.paginate()
    for page in page_iterator:
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                if instance['State']['Name'] in states_to_include:
                    terraform_resources.append(instance)
    
    output_file = output_dir / "ec2.tf"
    generate_tf(terraform_resources, "ec2", output_file)
    print(f"Generated Terraform for {len(terraform_resources)} EC2 instances -> {output_file}")
    generate_imports_file("ec2", terraform_resources, remote_resource_id_key="InstanceId", output_dir=output_dir)

def list_ec2(output_dir: Path):
    ImportManager(output_dir, "ec2").list_all()

def import_ec2(instance_id: str, output_dir: Path):
    ImportManager(output_dir, "ec2").find_and_import(instance_id)
