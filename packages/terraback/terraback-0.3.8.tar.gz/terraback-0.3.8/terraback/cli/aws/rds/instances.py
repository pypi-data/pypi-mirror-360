from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_rds_instances(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for RDS DB instances and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    rds_client = boto_session.client("rds")
    
    print(f"Scanning for RDS DB Instances in region {region}...")
    db_instances = rds_client.describe_db_instances()["DBInstances"]
    
    # Boto3 doesn't return tags in the describe call, so we fetch them separately for each instance.
    for db in db_instances:
        tags = rds_client.list_tags_for_resource(ResourceName=db['DBInstanceArn'])
        db['TagList'] = tags['TagList']

    output_file = output_dir / "rds_instance.tf"
    generate_tf(db_instances, "rds_instance", output_file)
    print(f"Generated Terraform for {len(db_instances)} RDS DB Instances -> {output_file}")
    generate_imports_file("rds_instance", db_instances, remote_resource_id_key="DBInstanceIdentifier", output_dir=output_dir)

def list_rds_instances(output_dir: Path):
    """List all RDS DB Instance resources previously generated."""
    ImportManager(output_dir, "rds_instance").list_all()

def import_rds_instance(db_instance_id: str, output_dir: Path):
    """Run terraform import for a specific RDS DB Instance by its identifier."""
    ImportManager(output_dir, "rds_instance").find_and_import(db_instance_id)