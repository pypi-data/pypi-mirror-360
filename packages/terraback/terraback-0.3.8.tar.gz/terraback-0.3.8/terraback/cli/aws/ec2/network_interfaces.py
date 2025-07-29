from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_network_interfaces(
    output_dir: Path,
    profile: str = None,
    region: str = "us-east-1",
    interface_id: str = None,
    attached_only: bool = False
):
    boto_session = get_boto_session(profile, region)
    ec2_client = boto_session.client("ec2")

    filters = []
    if interface_id:
        filters.append({'Name': 'network-interface-id', 'Values': [interface_id]})
    if attached_only:
        filters.append({'Name': 'status', 'Values': ['in-use']})
        
    network_interfaces = ec2_client.describe_network_interfaces(Filters=filters)["NetworkInterfaces"]

    output_file = output_dir / "network_interfaces.tf"
    generate_tf(network_interfaces, "network_interfaces", output_file)
    print(f"Generated Terraform for {len(network_interfaces)} Network Interfaces -> {output_file}")
    generate_imports_file("network_interfaces", network_interfaces, remote_resource_id_key="NetworkInterfaceId", output_dir=output_dir)

def list_network_interfaces(output_dir: Path):
    ImportManager(output_dir, "network_interfaces").list_all()

def import_network_interfaces(interface_id: str, output_dir: Path):
    ImportManager(output_dir, "network_interfaces").find_and_import(interface_id)