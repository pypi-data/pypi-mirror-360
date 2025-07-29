from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_log_groups(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for CloudWatch Log Groups and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    logs_client = boto_session.client("logs")
    
    print(f"Scanning for CloudWatch Log Groups in region {region}...")
    
    # Get all log groups using pagination
    paginator = logs_client.get_paginator('describe_log_groups')
    log_groups = []
    
    for page in paginator.paginate():
        for log_group in page['logGroups']:
            # Get tags for each log group
            try:
                tags_response = logs_client.list_tags_log_group(
                    logGroupName=log_group['logGroupName']
                )
                log_group['tags'] = tags_response.get('tags', {})
            except Exception as e:
                print(f"  - Warning: Could not retrieve tags for log group {log_group['logGroupName']}: {e}")
                log_group['tags'] = {}
            
            # Add some computed fields for easier template usage
            log_group['name_sanitized'] = log_group['logGroupName'].replace('/', '_').replace('-', '_').lstrip('_')
            log_groups.append(log_group)

    output_file = output_dir / "cloudwatch_log_group.tf"
    generate_tf(log_groups, "cloudwatch_log_group", output_file)
    print(f"Generated Terraform for {len(log_groups)} CloudWatch Log Groups -> {output_file}")
    generate_imports_file(
        "cloudwatch_log_group", 
        log_groups, 
        remote_resource_id_key="logGroupName", 
        output_dir=output_dir
    )

def list_log_groups(output_dir: Path):
    """Lists all CloudWatch Log Group resources previously generated."""
    ImportManager(output_dir, "cloudwatch_log_group").list_all()

def import_log_group(log_group_name: str, output_dir: Path):
    """Runs terraform import for a specific CloudWatch Log Group by its name."""
    ImportManager(output_dir, "cloudwatch_log_group").find_and_import(log_group_name)