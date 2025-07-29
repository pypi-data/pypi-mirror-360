from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_secret_versions(output_dir: Path, profile: str = None, region: str = "us-east-1", secret_arn: str = None):
    """
    Scans for secret versions and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    secrets_client = boto_session.client("secretsmanager")
    
    print(f"Scanning for secret versions in region {region}...")
    
    # Get secrets to scan versions for
    if secret_arn:
        secret_arns = [secret_arn]
    else:
        # Get all secrets first
        secret_arns = []
        paginator = secrets_client.get_paginator('list_secrets')
        for page in paginator.paginate():
            for secret in page.get('SecretList', []):
                secret_arns.append(secret['ARN'])
    
    secret_versions = []
    
    for secret_arn in secret_arns:
        try:
            # Get secret name for easier identification
            secret_name = secret_arn.split(':')[-1]
            
            # List versions for this secret
            versions_response = secrets_client.list_secret_version_ids(SecretId=secret_arn)
            
            for version in versions_response.get('Versions', []):
                version_id = version['VersionId']
                version_stages = version.get('VersionStages', [])
                
                # Create version object
                secret_version = {
                    'SecretArn': secret_arn,
                    'SecretName': secret_name,
                    'VersionId': version_id,
                    'VersionStages': version_stages,
                    'CreatedDate': version.get('CreatedDate'),
                    'LastAccessedDate': version.get('LastAccessedDate')
                }
                
                # Add sanitized names for resource naming
                secret_version['secret_name_sanitized'] = secret_name.replace('/', '_').replace('-', '_').replace(' ', '_').replace('.', '_').lower()
                secret_version['version_id_sanitized'] = version_id.replace('-', '_').lower()
                
                # Determine version type based on stages
                if 'AWSCURRENT' in version_stages:
                    secret_version['is_current'] = True
                    secret_version['is_pending'] = False
                    secret_version['is_previous'] = False
                elif 'AWSPENDING' in version_stages:
                    secret_version['is_current'] = False
                    secret_version['is_pending'] = True
                    secret_version['is_previous'] = False
                elif 'AWSPREVIOUS' in version_stages:
                    secret_version['is_current'] = False
                    secret_version['is_pending'] = False
                    secret_version['is_previous'] = True
                else:
                    secret_version['is_current'] = False
                    secret_version['is_pending'] = False
                    secret_version['is_previous'] = False
                
                # Create composite ID for import (secret_arn|version_id)
                secret_version['composite_id'] = f"{secret_arn}|{version_id}"
                
                # Format version stages for template usage
                secret_version['version_stages_formatted'] = version_stages
                
                secret_versions.append(secret_version)
                
        except Exception as e:
            print(f"  - Warning: Could not retrieve versions for secret {secret_arn}: {e}")
            continue
    
    # Generate secret versions
    if secret_versions:
        output_file = output_dir / "secretsmanager_secret_version.tf"
        generate_tf(secret_versions, "secretsmanager_secret_version", output_file)
        print(f"Generated Terraform for {len(secret_versions)} secret versions -> {output_file}")
        generate_imports_file(
            "secretsmanager_secret_version", 
            secret_versions, 
            remote_resource_id_key="composite_id", 
            output_dir=output_dir
        )

def list_secret_versions(output_dir: Path):
    """Lists all secret version resources previously generated."""
    ImportManager(output_dir, "secretsmanager_secret_version").list_all()

def import_secret_version(composite_id: str, output_dir: Path):
    """Runs terraform import for a specific secret version by its composite ID."""
    ImportManager(output_dir, "secretsmanager_secret_version").find_and_import(composite_id)