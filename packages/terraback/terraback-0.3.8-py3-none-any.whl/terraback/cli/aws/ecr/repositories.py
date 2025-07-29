from pathlib import Path
import json
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_repositories(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for ECR repositories and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ecr_client = boto_session.client("ecr")
    
    print(f"Scanning for ECR repositories in region {region}...")
    
    # Get all repositories
    repositories = []
    paginator = ecr_client.get_paginator('describe_repositories')
    
    for page in paginator.paginate():
        for repo in page['repositories']:
            # Add sanitized name for resource naming
            repo_name = repo['repositoryName']
            repo['name_sanitized'] = repo_name.replace('/', '_').replace('-', '_').replace('.', '_').lower()
            
            # Get repository policy if it exists
            try:
                policy_response = ecr_client.get_repository_policy(repositoryName=repo_name)
                repo['repository_policy'] = policy_response['policyText']
            except ecr_client.exceptions.RepositoryPolicyNotFoundException:
                repo['repository_policy'] = None
            except Exception as e:
                print(f"  - Warning: Could not retrieve policy for repository {repo_name}: {e}")
                repo['repository_policy'] = None
            
            # Get lifecycle policy if it exists
            try:
                lifecycle_response = ecr_client.get_lifecycle_policy(repositoryName=repo_name)
                repo['lifecycle_policy'] = lifecycle_response['lifecyclePolicyText']
            except ecr_client.exceptions.LifecyclePolicyNotFoundException:
                repo['lifecycle_policy'] = None
            except Exception as e:
                print(f"  - Warning: Could not retrieve lifecycle policy for repository {repo_name}: {e}")
                repo['lifecycle_policy'] = None
            
            # Get tags
            try:
                tags_response = ecr_client.list_tags_for_resource(resourceArn=repo['repositoryArn'])
                repo['tags_formatted'] = {tag['Key']: tag['Value'] for tag in tags_response.get('tags', [])}
            except Exception as e:
                print(f"  - Warning: Could not retrieve tags for repository {repo_name}: {e}")
                repo['tags_formatted'] = {}
            
            # Format image scanning configuration
            if repo.get('imageScanningConfiguration'):
                repo['image_scanning_enabled'] = repo['imageScanningConfiguration'].get('scanOnPush', False)
            else:
                repo['image_scanning_enabled'] = False
            
            # Format image tag mutability
            repo['image_tag_mutability_lowercase'] = repo.get('imageTagMutability', 'MUTABLE').lower()
            
            # Format encryption configuration
            if repo.get('encryptionConfiguration'):
                encryption_config = repo['encryptionConfiguration']
                repo['encryption_config_formatted'] = {
                    'encryption_type': encryption_config.get('encryptionType', 'AES256'),
                    'kms_key': encryption_config.get('kmsKey')
                }
            else:
                repo['encryption_config_formatted'] = {
                    'encryption_type': 'AES256',
                    'kms_key': None
                }
            
            repositories.append(repo)
    
    output_file = output_dir / "ecr_repository.tf"
    generate_tf(repositories, "ecr_repository", output_file)
    print(f"Generated Terraform for {len(repositories)} ECR repositories -> {output_file}")
    generate_imports_file(
        "ecr_repository", 
        repositories, 
        remote_resource_id_key="repositoryName", 
        output_dir=output_dir
    )

def list_repositories(output_dir: Path):
    """Lists all ECR repository resources previously generated."""
    ImportManager(output_dir, "ecr_repository").list_all()

def import_repository(repository_name: str, output_dir: Path):
    """Runs terraform import for a specific ECR repository by its name."""
    ImportManager(output_dir, "ecr_repository").find_and_import(repository_name)