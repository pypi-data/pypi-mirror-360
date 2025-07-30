from pathlib import Path
import json
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_secrets(output_dir: Path, profile: str = None, region: str = "us-east-1", 
                include_versions: bool = False, include_deleted: bool = False):
    """
    Scans for AWS Secrets Manager secrets and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    secrets_client = boto_session.client("secretsmanager")
    
    print(f"Scanning for Secrets Manager secrets in region {region}...")
    
    # Get all secrets
    secrets = []
    paginator = secrets_client.get_paginator('list_secrets')
    
    # Build pagination parameters
    list_params = {}
    if include_deleted:
        list_params['IncludePlannedDeletion'] = True
    
    for page in paginator.paginate(**list_params):
        for secret_summary in page.get('SecretList', []):
            secret_arn = secret_summary['ARN']
            secret_name = secret_summary['Name']
            
            try:
                # Get detailed secret information
                secret_detail = secrets_client.describe_secret(SecretId=secret_arn)
                
                # Create secret object
                secret = {
                    'ARN': secret_arn,
                    'Name': secret_name,
                    'Description': secret_detail.get('Description', ''),
                    'CreatedDate': secret_detail.get('CreatedDate'),
                    'LastChangedDate': secret_detail.get('LastChangedDate'),
                    'LastAccessedDate': secret_detail.get('LastAccessedDate'),
                    'VersionIdsToStages': secret_detail.get('VersionIdsToStages', {}),
                    'OwningService': secret_detail.get('OwningService'),
                    'PrimaryRegion': secret_detail.get('PrimaryRegion'),
                    'ReplicationStatus': secret_detail.get('ReplicationStatus', [])
                }
                
                # Add sanitized name for resource naming
                secret['name_sanitized'] = secret_name.replace('/', '_').replace('-', '_').replace(' ', '_').replace('.', '_').lower()
                
                # Handle KMS encryption
                kms_key_id = secret_detail.get('KmsKeyId')
                if kms_key_id:
                    secret['kms_encrypted'] = True
                    secret['kms_key_id'] = kms_key_id
                else:
                    secret['kms_encrypted'] = False
                    secret['kms_key_id'] = None
                
                # Handle automatic rotation
                rotation_enabled = secret_detail.get('RotationEnabled', False)
                secret['rotation_enabled'] = rotation_enabled
                
                if rotation_enabled:
                    secret['rotation_lambda_arn'] = secret_detail.get('RotationLambdaARN')
                    secret['rotation_rules'] = secret_detail.get('RotationRules', {})
                    secret['next_rotation_date'] = secret_detail.get('NextRotationDate')
                    
                    # Format rotation rules for easier template usage
                    rotation_rules = secret_detail.get('RotationRules', {})
                    if rotation_rules:
                        secret['rotation_rules_formatted'] = {
                            'automatically_after_days': rotation_rules.get('AutomaticallyAfterDays')
                        }
                    else:
                        secret['rotation_rules_formatted'] = None
                else:
                    secret['rotation_lambda_arn'] = None
                    secret['rotation_rules'] = None
                    secret['rotation_rules_formatted'] = None
                    secret['next_rotation_date'] = None
                
                # Handle deletion protection
                secret['deletion_date'] = secret_detail.get('DeletedDate')
                secret['is_deleted'] = secret['deletion_date'] is not None
                
                # Handle replica configuration
                replica_regions = secret_detail.get('ReplicationStatus', [])
                if replica_regions:
                    secret['replica_regions_formatted'] = []
                    for replica in replica_regions:
                        formatted_replica = {
                            'region': replica.get('Region'),
                            'kms_key_id': replica.get('KmsKeyId'),
                            'status': replica.get('Status'),
                            'status_message': replica.get('StatusMessage'),
                            'last_accessed_date': replica.get('LastAccessedDate')
                        }
                        secret['replica_regions_formatted'].append(formatted_replica)
                else:
                    secret['replica_regions_formatted'] = []
                
                # Get resource policy
                try:
                    policy_response = secrets_client.get_resource_policy(SecretId=secret_arn)
                    policy_text = policy_response.get('ResourcePolicy')
                    if policy_text:
                        secret['resource_policy'] = json.loads(policy_text)
                    else:
                        secret['resource_policy'] = None
                except secrets_client.exceptions.ResourceNotFoundException:
                    secret['resource_policy'] = None
                except Exception as e:
                    print(f"  - Warning: Could not retrieve resource policy for secret {secret_name}: {e}")
                    secret['resource_policy'] = None
                
                # Get tags
                tags = secret_detail.get('Tags', [])
                secret['tags_formatted'] = {tag['Key']: tag['Value'] for tag in tags}
                
                # Determine secret type (based on naming convention and description)
                if secret_name.startswith('rds-db-credentials/'):
                    secret['secret_type'] = 'rds'
                elif secret_name.startswith('elasticache-user/'):
                    secret['secret_type'] = 'elasticache'
                elif secret_name.startswith('documentdb/'):
                    secret['secret_type'] = 'documentdb'
                elif secret_name.startswith('redshift/'):
                    secret['secret_type'] = 'redshift'
                elif 'api' in secret_name.lower() or 'key' in secret_name.lower():
                    secret['secret_type'] = 'api_key'
                elif 'password' in secret_name.lower() or 'pwd' in secret_name.lower():
                    secret['secret_type'] = 'password'
                else:
                    secret['secret_type'] = 'generic'
                
                # Check if managed by AWS service
                secret['is_aws_managed'] = secret.get('OwningService') is not None
                
                # Get current version info
                version_stages = secret.get('VersionIdsToStages', {})
                current_version_id = None
                pending_version_id = None
                
                for version_id, stages in version_stages.items():
                    if 'AWSCURRENT' in stages:
                        current_version_id = version_id
                    if 'AWSPENDING' in stages:
                        pending_version_id = version_id
                
                secret['current_version_id'] = current_version_id
                secret['pending_version_id'] = pending_version_id
                secret['has_pending_rotation'] = pending_version_id is not None
                
                secrets.append(secret)
                
            except Exception as e:
                print(f"  - Warning: Could not retrieve details for secret {secret_name}: {e}")
                continue
    
    # Generate secrets
    if secrets:
        output_file = output_dir / "secretsmanager_secret.tf"
        generate_tf(secrets, "secretsmanager_secret", output_file)
        print(f"Generated Terraform for {len(secrets)} Secrets Manager secrets -> {output_file}")
        generate_imports_file(
            "secretsmanager_secret", 
            secrets, 
            remote_resource_id_key="ARN", 
            output_dir=output_dir
        )
    
    # Scan secret versions if requested
    if include_versions:
        from .secret_versions import scan_secret_versions
        scan_secret_versions(output_dir, profile, region)

def list_secrets(output_dir: Path):
    """Lists all Secrets Manager secret resources previously generated."""
    ImportManager(output_dir, "secretsmanager_secret").list_all()

def import_secret(secret_arn: str, output_dir: Path):
    """Runs terraform import for a specific Secrets Manager secret by its ARN."""
    ImportManager(output_dir, "secretsmanager_secret").find_and_import(secret_arn)
