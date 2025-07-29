from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_launch_templates(
    output_dir: Path,
    profile: str = None,
    region: str = "us-east-1",
    template_id: str = None,
    template_name: str = None
):
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    
    filters = []
    if template_id:
        filters.append({'Name': 'launch-template-id', 'Values': [template_id]})
    if template_name:
        filters.append({'Name': 'launch-template-name', 'Values': [template_name]})
        
    launch_templates = ec2_client.describe_launch_templates(Filters=filters)["LaunchTemplates"]

    output_file = output_dir / "launch_template.tf"
    generate_tf(launch_templates, "launch_template", output_file)
    print(f"Generated Terraform for {len(launch_templates)} Launch Templates -> {output_file}")
    generate_imports_file("launch_template", launch_templates, remote_resource_id_key="LaunchTemplateId", output_dir=output_dir)

def list_launch_templates(output_dir: Path):
    ImportManager(output_dir, "launch_template").list_all()

def import_launch_template(template_id: str, output_dir: Path):
    ImportManager(output_dir, "launch_template").find_and_import(template_id)