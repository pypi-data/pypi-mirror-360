import typer
from pathlib import Path

from .addresses import scan_eips, list_eips, import_eip
from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="eips",
    help="Manage Elastic IP (EIP) resources.",
    no_args_is_help=True
)

@app.command(name="scan", help="Scan EIPs and generate Terraform code.")
def scan_eips_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_eips(output_dir, profile, region)

@app.command(name="list", help="List all EIP resources previously generated.")
def list_eips_command(output_dir: Path = typer.Option("generated", help="Directory...")):
    list_eips(output_dir)

@app.command(name="import", help="Run terraform import for a specific EIP by Allocation ID.")
def import_eip_command(
    allocation_id: str,
    output_dir: Path = typer.Option("generated", help="Directory...")
):
    import_eip(allocation_id, output_dir)

def register():
    """Registers the scan functions for the EIPs module."""
    register_scan_function("eip", scan_eips)
    cross_scan_registry.register_dependency("ec2", "eip") # An EC2 instance can have an EIP