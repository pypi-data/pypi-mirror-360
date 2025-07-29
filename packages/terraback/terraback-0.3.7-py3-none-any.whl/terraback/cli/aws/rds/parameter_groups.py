from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_db_parameter_groups(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for RDS DB Parameter Groups and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    rds_client = boto_session.client("rds")
    
    print(f"Scanning for RDS DB Parameter Groups in region {region}...")
    db_parameter_groups = rds_client.describe_db_parameter_groups()["DBParameterGroups"]
    
    for group in db_parameter_groups:
        # We only want to export non-default parameters
        params_paginator = rds_client.get_paginator('describe_db_parameters')
        custom_parameters = []
        for page in params_paginator.paginate(DBParameterGroupName=group['DBParameterGroupName']):
            for param in page['Parameters']:
                # 'user' source means it was modified from the default
                if param.get('Source') == 'user':
                    custom_parameters.append(param)
        group['Parameters'] = custom_parameters

        # Fetch tags separately
        tags = rds_client.list_tags_for_resource(ResourceName=group['DBParameterGroupArn'])
        group['Tags'] = tags['TagList']

    output_file = output_dir / "rds_parameter_group.tf"
    generate_tf(db_parameter_groups, "rds_parameter_group", output_file)
    print(f"Generated Terraform for {len(db_parameter_groups)} RDS DB Parameter Groups -> {output_file}")
    generate_imports_file("rds_parameter_group", db_parameter_groups, remote_resource_id_key="DBParameterGroupName", output_dir=output_dir)

def list_db_parameter_groups(output_dir: Path):
    """Lists all RDS DB Parameter Group resources previously generated."""
    ImportManager(output_dir, "rds_parameter_group").list_all()

def import_db_parameter_group(parameter_group_name: str, output_dir: Path):
    """Runs terraform import for a specific RDS DB Parameter Group by its name."""
    ImportManager(output_dir, "rds_parameter_group").find_and_import(parameter_group_name)