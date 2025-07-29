from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_hosted_zones(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for Route 53 Hosted Zones and generates Terraform code.
    Note: Route 53 is a global service, so the 'region' parameter is not used.
    """
    # Route 53 is global, but boto3 still needs a session.
    boto_session = get_boto_session(profile, region)
    r53_client = boto_session.client("route53")
    
    print("Scanning for Route 53 Hosted Zones...")
    paginator = r53_client.get_paginator('list_hosted_zones')
    hosted_zones = []
    for page in paginator.paginate():
        # The 'Id' from the API is formatted as '/hostedzone/Z123ABC...', we need to strip the prefix.
        for zone in page['HostedZones']:
            zone['ZoneId'] = zone['Id'].replace('/hostedzone/', '')
            hosted_zones.append(zone)

    output_file = output_dir / "route53_zone.tf"
    generate_tf(hosted_zones, "route53_zone", output_file)
    print(f"Generated Terraform for {len(hosted_zones)} Hosted Zones -> {output_file}")
    generate_imports_file("route53_zone", hosted_zones, remote_resource_id_key="ZoneId", output_dir=output_dir)

def list_hosted_zones(output_dir: Path):
    ImportManager(output_dir, "route53_zone").list_all()

def import_hosted_zone(zone_id: str, output_dir: Path):
    ImportManager(output_dir, "route53_zone").find_and_import(zone_id)