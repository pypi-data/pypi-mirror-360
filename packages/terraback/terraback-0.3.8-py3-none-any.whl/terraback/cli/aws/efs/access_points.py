from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_access_points(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for EFS access points and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    efs_client = boto_session.client("efs")
    
    print(f"Scanning for EFS access points in region {region}...")
    
    # Get all access points
    access_points = []
    paginator = efs_client.get_paginator('describe_access_points')
    
    for page in paginator.paginate():
        for ap in page['AccessPoints']:
            # Add sanitized name for resource naming
            ap_id = ap['AccessPointId']
            ap['name_sanitized'] = ap_id.replace('-', '_')
            
            # Add file system ID sanitized for cross-referencing
            fs_id = ap['FileSystemId']
            ap['file_system_id_sanitized'] = fs_id.replace('-', '_')
            
            # Format POSIX user for easier template usage
            if ap.get('PosixUser'):
                posix_user = ap['PosixUser']
                ap['posix_user_formatted'] = {
                    'uid': posix_user.get('Uid'),
                    'gid': posix_user.get('Gid'),
                    'secondary_gids': posix_user.get('SecondaryGids', [])
                }
            else:
                ap['posix_user_formatted'] = None
            
            # Format root directory for easier template usage
            if ap.get('RootDirectory'):
                root_dir = ap['RootDirectory']
                ap['root_directory_formatted'] = {
                    'path': root_dir.get('Path', '/'),
                    'creation_info': None
                }
                
                if root_dir.get('CreationInfo'):
                    creation_info = root_dir['CreationInfo']
                    ap['root_directory_formatted']['creation_info'] = {
                        'owner_uid': creation_info.get('OwnerUid'),
                        'owner_gid': creation_info.get('OwnerGid'),
                        'permissions': creation_info.get('Permissions')
                    }
            else:
                ap['root_directory_formatted'] = {
                    'path': '/',
                    'creation_info': None
                }
            
            # Get tags
            try:
                tags_response = efs_client.describe_tags(FileSystemId=fs_id)
                ap['tags_formatted'] = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
            except Exception as e:
                print(f"  - Warning: Could not retrieve tags for access point {ap_id}: {e}")
                ap['tags_formatted'] = {}
            
            access_points.append(ap)
    
    output_file = output_dir / "efs_access_point.tf"
    generate_tf(access_points, "efs_access_point", output_file)
    print(f"Generated Terraform for {len(access_points)} EFS access points -> {output_file}")
    generate_imports_file(
        "efs_access_point", 
        access_points, 
        remote_resource_id_key="AccessPointId", 
        output_dir=output_dir
    )

def list_access_points(output_dir: Path):
    """Lists all EFS access point resources previously generated."""
    ImportManager(output_dir, "efs_access_point").list_all()

def import_access_point(access_point_id: str, output_dir: Path):
    """Runs terraform import for a specific EFS access point by its ID."""
    ImportManager(output_dir, "efs_access_point").find_and_import(access_point_id)