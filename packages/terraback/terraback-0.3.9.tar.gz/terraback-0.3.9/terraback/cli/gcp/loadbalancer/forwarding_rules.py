# terraback/cli/gcp/loadbalancer/forwarding_rules.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any

from terraback.cli.gcp.session import get_default_project_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="forwarding-rule", help="Scan and import GCP forwarding rules.")

def get_forwarding_rule_data(project_id: str, region: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch forwarding rule data from GCP."""
    # TODO: Implement actual GCP API calls
    forwarding_rules = []
    typer.echo("[TODO] Forwarding rule scanning not yet implemented")
    return forwarding_rules

@app.command("scan")
def scan_forwarding_rules(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    with_deps: bool = typer.Option(False, "--with-deps")
):
    """Scans GCP forwarding rules and generates Terraform code."""
    typer.echo("GCP forwarding rule scanning not yet implemented.")

# Scan function for cross-scan registry
def scan_gcp_forwarding_rules(
    output_dir: Path, 
    project_id: Optional[str] = None, 
    region: Optional[str] = None,
    **kwargs
):
    """Scan function to be registered with cross-scan registry."""
    if not project_id:
        project_id = get_default_project_id()
    typer.echo(f"[Cross-scan] Forwarding rule scanning not yet implemented for project {project_id}")

@app.command("list")
def list_forwarding_rules(output_dir: Path = typer.Option("generated", "-o", "--output-dir")):
    """List all GCP forwarding rule resources previously generated."""
    ImportManager(output_dir, "gcp_global_forwarding_rule").list_all()

@app.command("import")
def import_forwarding_rule(
    rule_id: str = typer.Argument(..., help="GCP forwarding rule ID"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Run terraform import for a specific GCP forwarding rule."""
    ImportManager(output_dir, "gcp_global_forwarding_rule").find_and_import(rule_id)
