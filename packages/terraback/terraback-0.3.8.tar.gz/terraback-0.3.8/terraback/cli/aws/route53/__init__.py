from terraback.core.license import require_professional
import typer
from pathlib import Path

from .zones import scan_hosted_zones, list_hosted_zones, import_hosted_zone
from .records import scan_records, list_records, import_record

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="route53",
    help="Manage Route 53 resources like Hosted Zones and Records.",
    no_args_is_help=True
)

# --- Hosted Zone Commands ---
@app.command(name="scan-zones", help="Scan Route 53 Hosted Zones.")
@require_professional
def scan_zones_command(output_dir: Path = typer.Option("generated"), profile: str = typer.Option(None), region: str = typer.Option("us-east-1")):
    scan_hosted_zones(output_dir, profile, region)

@app.command(name="list-zones")
@require_professional
def list_zones_command(output_dir: Path = typer.Option("generated")):
    list_hosted_zones(output_dir)

@app.command(name="import-zone")
@require_professional
def import_zone_command(zone_id: str, output_dir: Path = typer.Option("generated")):
    import_hosted_zone(zone_id, output_dir)


# --- Record Set Commands ---
@app.command(name="scan-records", help="Scan all DNS records in all Hosted Zones.")
@require_professional
def scan_records_command(output_dir: Path = typer.Option("generated"), profile: str = typer.Option(None), region: str = typer.Option("us-east-1")):
    scan_records(output_dir, profile, region)

@app.command(name="list-records")
@require_professional
def list_records_command(output_dir: Path = typer.Option("generated")):
    list_records(output_dir)

@app.command(name="import-record")
@require_professional
def import_record_command(record_id: str, output_dir: Path = typer.Option("generated")):
    import_record(record_id, output_dir)


# --- Registration ---
def register():
    """Registers scan functions and dependencies for the Route 53 module."""
    register_scan_function("route53_zone", scan_hosted_zones)
    register_scan_function("route53_record", scan_records)

    # Define dependencies
    cross_scan_registry.register_dependency("route53_zone", "route53_record") # A zone contains records
    cross_scan_registry.register_dependency("route53_zone", "vpc") # A private zone is associated with a VPC