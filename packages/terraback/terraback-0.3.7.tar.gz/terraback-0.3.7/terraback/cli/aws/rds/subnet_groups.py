from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_db_subnet_groups(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for RDS DB Subnet Groups and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    rds_client = boto_session.client("rds")
    
    print(f"Scanning for RDS DB Subnet Groups in region {region}...")
    db_subnet_groups = rds_client.describe_db_subnet_groups()["DBSubnetGroups"]
    
    # Boto3 doesn't return tags in the describe call, so we fetch them separately.
    for group in db_subnet_groups:
        tags = rds_client.list_tags_for_resource(ResourceName=group['DBSubnetGroupArn'])
        group['Tags'] = tags['TagList']

    output_file = output_dir / "rds_subnet_group.tf"
    generate_tf(db_subnet_groups, "rds_subnet_group", output_file)
    print(f"Generated Terraform for {len(db_subnet_groups)} RDS DB Subnet Groups -> {output_file}")
    generate_imports_file("rds_subnet_group", db_subnet_groups, remote_resource_id_key="DBSubnetGroupName", output_dir=output_dir)

def list_db_subnet_groups(output_dir: Path):
    """Lists all RDS DB Subnet Group resources previously generated."""
    ImportManager(output_dir, "rds_subnet_group").list_all()

def import_db_subnet_group(subnet_group_name: str, output_dir: Path):
    """Runs terraform import for a specific RDS DB Subnet Group by its name."""
    ImportManager(output_dir, "rds_subnet_group").find_and_import(subnet_group_name)