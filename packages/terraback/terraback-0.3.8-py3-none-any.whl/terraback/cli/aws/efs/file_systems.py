from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_file_systems(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for EFS file systems and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    efs_client = boto_session.client("efs")
    
    print(f"Scanning for EFS file systems in region {region}...")
    
    # Get all file systems
    file_systems = []
    paginator = efs_client.get_paginator('describe_file_systems')
    
    for page in paginator.paginate():
        for fs in page['FileSystems']:
            # Add sanitized name for resource naming
            fs_id = fs['FileSystemId']
            fs['name_sanitized'] = fs_id.replace('-', '_')
            
            # Get file system policy if it exists
            try:
                policy_response = efs_client.describe_file_system_policy(FileSystemId=fs_id)
                fs['file_system_policy'] = policy_response['Policy']
            except efs_client.exceptions.PolicyNotFound:
                fs['file_system_policy'] = None
            except Exception as e:
                print(f"  - Warning: Could not retrieve policy for file system {fs_id}: {e}")
                fs['file_system_policy'] = None
            
            # Get backup policy
            try:
                backup_response = efs_client.describe_backup_policy(FileSystemId=fs_id)
                fs['backup_policy'] = backup_response['BackupPolicy']['Status']
            except Exception as e:
                print(f"  - Warning: Could not retrieve backup policy for file system {fs_id}: {e}")
                fs['backup_policy'] = 'DISABLED'
            
            # Get tags
            try:
                tags_response = efs_client.describe_tags(FileSystemId=fs_id)
                fs['tags_formatted'] = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
            except Exception as e:
                print(f"  - Warning: Could not retrieve tags for file system {fs_id}: {e}")
                fs['tags_formatted'] = {}
            
            # Format creation token
            fs['creation_token_formatted'] = fs.get('CreationToken', fs_id)
            
            # Format performance mode
            fs['performance_mode_lowercase'] = fs.get('PerformanceMode', 'generalPurpose').lower()
            
            # Format throughput mode
            fs['throughput_mode_lowercase'] = fs.get('ThroughputMode', 'bursting').lower()
            
            # Format availability zone name for One Zone storage class
            if fs.get('AvailabilityZoneName'):
                fs['availability_zone_name'] = fs['AvailabilityZoneName']
                fs['is_one_zone'] = True
            else:
                fs['availability_zone_name'] = None
                fs['is_one_zone'] = False
            
            # Determine if encryption is enabled
            fs['is_encrypted'] = fs.get('Encrypted', False)
            
            file_systems.append(fs)
    
    output_file = output_dir / "efs_file_system.tf"
    generate_tf(file_systems, "efs_file_system", output_file)
    print(f"Generated Terraform for {len(file_systems)} EFS file systems -> {output_file}")
    generate_imports_file(
        "efs_file_system", 
        file_systems, 
        remote_resource_id_key="FileSystemId", 
        output_dir=output_dir
    )

def list_file_systems(output_dir: Path):
    """Lists all EFS file system resources previously generated."""
    ImportManager(output_dir, "efs_file_system").list_all()

def import_file_system(file_system_id: str, output_dir: Path):
    """Runs terraform import for a specific EFS file system by its ID."""
    ImportManager(output_dir, "efs_file_system").find_and_import(file_system_id)