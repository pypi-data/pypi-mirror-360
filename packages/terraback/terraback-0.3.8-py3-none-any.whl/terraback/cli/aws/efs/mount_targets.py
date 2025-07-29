from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_mount_targets(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for EFS mount targets and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    efs_client = boto_session.client("efs")
    
    print(f"Scanning for EFS mount targets in region {region}...")
    
    # First get all file systems to scan their mount targets
    file_systems = []
    paginator = efs_client.get_paginator('describe_file_systems')
    
    for page in paginator.paginate():
        file_systems.extend(page['FileSystems'])
    
    # Get mount targets for each file system
    mount_targets = []
    for fs in file_systems:
        fs_id = fs['FileSystemId']
        
        try:
            mt_response = efs_client.describe_mount_targets(FileSystemId=fs_id)
            
            for mt in mt_response['MountTargets']:
                # Add file system information
                mt['FileSystemId'] = fs_id
                mt['file_system_id_sanitized'] = fs_id.replace('-', '_')
                
                # Add sanitized name for resource naming
                mt_id = mt['MountTargetId']
                mt['name_sanitized'] = mt_id.replace('-', '_')
                
                # Add availability zone for easier identification
                mt['availability_zone'] = mt.get('AvailabilityZoneName', '')
                
                mount_targets.append(mt)
                
        except Exception as e:
            print(f"  - Warning: Could not retrieve mount targets for file system {fs_id}: {e}")
            continue
    
    output_file = output_dir / "efs_mount_target.tf"
    generate_tf(mount_targets, "efs_mount_target", output_file)
    print(f"Generated Terraform for {len(mount_targets)} EFS mount targets -> {output_file}")
    generate_imports_file(
        "efs_mount_target", 
        mount_targets, 
        remote_resource_id_key="MountTargetId", 
        output_dir=output_dir
    )

def list_mount_targets(output_dir: Path):
    """Lists all EFS mount target resources previously generated."""
    ImportManager(output_dir, "efs_mount_target").list_all()

def import_mount_target(mount_target_id: str, output_dir: Path):
    """Runs terraform import for a specific EFS mount target by its ID."""
    ImportManager(output_dir, "efs_mount_target").find_and_import(mount_target_id)