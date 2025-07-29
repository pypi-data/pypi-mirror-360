from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_snapshots(
    output_dir: Path,
    profile: str = None,
    region: str = "us-east-1"
):
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")

    paginator = ec2_client.get_paginator('describe_snapshots')
    snapshots = []
    
    print(f"Scanning for EBS Snapshots in region {region}...")
    for page in paginator.paginate(OwnerIds=['self']):
        snapshots.extend(page['Snapshots'])

    output_file = output_dir / "ebs_snapshot.tf"
    generate_tf(snapshots, "ebs_snapshot", output_file)
    print(f"Generated Terraform for {len(snapshots)} EBS Snapshots -> {output_file}")
    generate_imports_file("ebs_snapshot", snapshots, remote_resource_id_key="SnapshotId", output_dir=output_dir)

def list_snapshots(output_dir: Path):
    ImportManager(output_dir, "ebs_snapshot").list_all()

def import_snapshot(snapshot_id: str, output_dir: Path):
    ImportManager(output_dir, "ebs_snapshot").find_and_import(snapshot_id)