from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

# --- Helper functions to handle pagination and denest the logic ---

def _get_all_hosted_zones(r53_client):
    """A generator function that yields each hosted zone, handling pagination."""
    zone_paginator = r53_client.get_paginator('list_hosted_zones')
    for page in zone_paginator.paginate():
        for zone in page['HostedZones']:
            yield zone

def _get_records_in_zone(r53_client, zone_id):
    """A generator function that yields each DNS record for a given zone."""
    record_paginator = r53_client.get_paginator('list_resource_record_sets')
    for page in record_paginator.paginate(HostedZoneId=zone_id):
        for record in page['ResourceRecordSets']:
            # Exclude default NS and SOA records managed by AWS
            if record['Type'] not in ['NS', 'SOA']:
                yield record

# --- Main scan function ---

def scan_records(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for all records in all Route 53 Hosted Zones and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    r53_client = boto_session.client("route53")
    
    print("Scanning for all Route 53 Records...")
    all_records = []

    # The main logic is now much flatter and easier to read
    for zone in _get_all_hosted_zones(r53_client):
        zone_id = zone['Id'].replace('/hostedzone/', '')
        print(f"  - Scanning records in zone: {zone['Name']} ({zone_id})")
        
        for record in _get_records_in_zone(r53_client, zone_id):
            record['ZoneId'] = zone_id  # Add ZoneId to each record for the template
            
            # Create the composite ID for import
            # Format: ZONEID_RECORDNAME_RECORDTYPE_SETIDENTIFIER
            record_id_parts = [
                zone_id,
                record['Name'],
                record['Type']
            ]
            if record.get('SetIdentifier'):
                record_id_parts.append(record['SetIdentifier'])
            
            record['ImportId'] = "_".join(record_id_parts)
            all_records.append(record)

    # --- File Generation ---
    output_file = output_dir / "route53_record.tf"
    generate_tf(all_records, "route53_record", output_file)
    print(f"\nGenerated Terraform for {len(all_records)} DNS Records -> {output_file}")
    generate_imports_file("route53_record", all_records, remote_resource_id_key="ImportId", output_dir=output_dir)


# --- CLI helper functions (unchanged) ---

def list_records(output_dir: Path):
    """Lists all DNS Record resources previously generated."""
    ImportManager(output_dir, "route53_record").list_all()

def import_record(record_id: str, output_dir: Path):
    """Runs terraform import for a specific DNS Record by its composite ID."""
    ImportManager(output_dir, "route53_record").find_and_import(record_id)