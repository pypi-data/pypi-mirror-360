from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_volumes(
    output_dir: Path,
    profile: str = None,
    region: str = "us-east-1",
    volume_id: str = None,
    include_attached_only: bool = False
):
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")

    filters = []
    if volume_id:
        filters.append({'Name': 'volume-id', 'Values': [volume_id]})
    if include_attached_only:
        filters.append({'Name': 'attachment.status', 'Values': ['attached']})
        
    volumes = ec2_client.describe_volumes(Filters=filters)["Volumes"]
    
    output_file = output_dir / "volumes.tf"
    generate_tf(volumes, "volumes", output_file)
    print(f"Generated Terraform for {len(volumes)} EBS Volumes -> {output_file}")
    generate_imports_file("volumes", volumes, remote_resource_id_key="VolumeId", output_dir=output_dir)

def list_volumes(output_dir: Path):
    ImportManager(output_dir, "volumes").list_all()

def import_volume(volume_id: str, output_dir: Path):
    ImportManager(output_dir, "volumes").find_and_import(volume_id)