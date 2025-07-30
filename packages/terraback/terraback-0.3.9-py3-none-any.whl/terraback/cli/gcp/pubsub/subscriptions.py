# terraback/cli/gcp/pubsub/subscriptions.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any

from terraback.cli.gcp.session import get_default_project_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="subscription", help="Scan and import GCP Pub/Sub subscriptions.")

def get_pubsub_subscription_data(project_id: str) -> List[Dict[str, Any]]:
    """Fetch Pub/Sub subscription data from GCP."""
    # TODO: Implement actual GCP API calls
    subscriptions = []
    typer.echo("[TODO] Pub/Sub subscription scanning not yet implemented")
    return subscriptions

@app.command("scan")
def scan_pubsub_subscriptions(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    with_deps: bool = typer.Option(False, "--with-deps")
):
    """Scans GCP Pub/Sub subscriptions and generates Terraform code."""
    typer.echo("GCP Pub/Sub subscription scanning not yet implemented.")

# Scan function for cross-scan registry
def scan_gcp_pubsub_subscriptions(output_dir: Path, project_id: Optional[str] = None, **kwargs):
    """Scan function to be registered with cross-scan registry."""
    if not project_id:
        project_id = get_default_project_id()
    typer.echo(f"[Cross-scan] Pub/Sub subscription scanning not yet implemented for project {project_id}")

@app.command("list")
def list_pubsub_subscriptions(output_dir: Path = typer.Option("generated", "-o", "--output-dir")):
    """List all GCP Pub/Sub subscription resources previously generated."""
    ImportManager(output_dir, "gcp_pubsub_subscription").list_all()

@app.command("import")
def import_pubsub_subscription(
    subscription_id: str = typer.Argument(..., help="GCP Pub/Sub subscription ID"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Run terraform import for a specific GCP Pub/Sub subscription."""
    ImportManager(output_dir, "gcp_pubsub_subscription").find_and_import(subscription_id)
