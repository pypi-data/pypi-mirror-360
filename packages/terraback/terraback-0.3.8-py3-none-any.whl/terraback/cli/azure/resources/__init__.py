# terraback/cli/azure/resources/__init__.py
import typer
from pathlib import Path
from typing import Optional

from . import resource_groups
from .resource_groups import scan_azure_resource_groups
from terraback.utils.cross_scan_registry import register_scan_function

app = typer.Typer(
    name="resources",
    help="Work with Azure Resource Management resources.",
    no_args_is_help=True
)

def register():
    """Registers the resource management resources with the cross-scan registry."""
    # Resource Groups
    register_scan_function("azure_resource_group", scan_azure_resource_groups)

# Add sub-commands
app.add_typer(resource_groups.app, name="rg")

# Convenience command
@app.command("scan-all")
def scan_all_resources(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION")
):
    """Scan all Azure resource management resources."""
    from terraback.cli.azure.session import get_default_subscription_id
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    # Scan Resource Groups
    resource_groups.scan_resource_groups(
        output_dir=output_dir,
        subscription_id=subscription_id,
        location=location
    )