from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_amis(
    output_dir: Path,
    profile: str = None,
    region: str = "us-east-1",
    amis_id: str = None,
    owned_by_me: bool = True,
    include_public: bool = False
):
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")
    
    filters = []
    owners = []
    if amis_id:
        filters.append({'Name': 'image-id', 'Values': [amis_id]})
    if owned_by_me:
        owners.append('self')
    if include_public:
        owners.append('amazon')

    if not owners and not amis_id:
        print("Warning: No owners specified for amis scan. Defaulting to 'self'.")
        owners.append('self')
        
    amis = ec2_client.describe_images(Owners=owners, Filters=filters)["Images"]

    output_file = output_dir / "amis.tf"
    generate_tf(amis, "amis", output_file)
    print(f"Generated Terraform for {len(amis)} amis -> {output_file}")
    generate_imports_file("amis", amis, remote_resource_id_key="ImageId", output_dir=output_dir)

def list_amis(output_dir: Path):
    ImportManager(output_dir, "amis").list_all()

def import_amis(amis_id: str, output_dir: Path):
    ImportManager(output_dir, "amis").find_and_import(amis_id)