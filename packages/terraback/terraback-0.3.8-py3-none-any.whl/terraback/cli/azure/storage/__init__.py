# terraback/cli/azure/storage/__init__.py
import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="storage",
    help="Work with Azure Storage resources.",
    no_args_is_help=True
)

@app.command()
def scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies")
):
    """Scan Azure storage accounts."""
    from . import storage_accounts
    storage_accounts.scan_storage_accounts(
        output_dir=output_dir,
        subscription_id=subscription_id,
        location=location,
        resource_group_name=resource_group_name,
        with_deps=with_deps
    )

@app.command("scan-all")
def scan_all(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies")
):
    """Scan all Azure storage resources (currently same as scan)."""
    from terraback.cli.azure.session import get_default_subscription_id
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan(
            "azure_storage_account",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location
        )
    else:
        # Scan Storage Accounts
        from . import storage_accounts
        storage_accounts.scan_storage_accounts(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=location,
            resource_group_name=resource_group_name,
            with_deps=False
        )

@app.command()
def list(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import file")
):
    """List all Azure Storage Account resources previously generated."""
    from .storage_accounts import list_storage_accounts
    list_storage_accounts(output_dir)

@app.command()
def import_(
    account_id: str = typer.Argument(..., help="Azure Storage Account resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory with import file")
):
    """Run terraform import for a specific Azure Storage Account by its resource ID."""
    from .storage_accounts import import_storage_account
    import_storage_account(account_id, output_dir)

def register():
    """Registers the storage resources with the cross-scan registry."""
    try:
        from .storage_accounts import scan_azure_storage_accounts
        from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry
        
        # Storage Accounts
        register_scan_function("azure_storage_account", scan_azure_storage_accounts)
        
        # Storage Account Dependencies
        cross_scan_registry.register_dependency("azure_storage_account", "azure_resource_group")
        cross_scan_registry.register_dependency("azure_storage_account", "azure_virtual_network")
        cross_scan_registry.register_dependency("azure_storage_account", "azure_subnet")
    except ImportError:
        pass  # Silent fail during initial import

# Try to add the nested 'account' subcommand
try:
    from . import storage_accounts
    if hasattr(storage_accounts, 'app'):
        app.add_typer(storage_accounts.app, name="account")
except ImportError:
    pass