import typer
from pathlib import Path
from functools import partial
from typing import Optional

from . import virtual_machines, disks, ssh_keys
from .virtual_machines import scan_azure_vms
from .disks import scan_azure_disks
from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="compute",
    help="Work with Azure Compute resources like VMs, Disks, and SSH Keys.",
    no_args_is_help=True
)

def register():
    """
    Registers the Azure compute resources with the cross-scan registry.
    """
    # Virtual Machines
    scan_vms_core = partial(scan_azure_vms, include_all_states=True)
    register_scan_function("azure_virtual_machine", scan_vms_core)
    
    # VM Dependencies
    cross_scan_registry.register_dependency("azure_virtual_machine", "azure_network_interface")
    cross_scan_registry.register_dependency("azure_virtual_machine", "azure_subnet")
    cross_scan_registry.register_dependency("azure_virtual_machine", "azure_managed_disk")
    cross_scan_registry.register_dependency("azure_virtual_machine", "azure_network_security_group")
    cross_scan_registry.register_dependency("azure_virtual_machine", "azure_availability_set")
    cross_scan_registry.register_dependency("azure_virtual_machine", "azure_image")
    
    # Managed Disks
    register_scan_function("azure_managed_disk", scan_azure_disks)
    cross_scan_registry.register_dependency("azure_managed_disk", "azure_virtual_machine")
    cross_scan_registry.register_dependency("azure_managed_disk", "azure_snapshot")
    
    # TODO: Add SSH Keys when implemented
    # register_scan_function("azure_ssh_key", scan_azure_ssh_keys)

# Add sub-commands
app.add_typer(virtual_machines.app, name="vm")
app.add_typer(disks.app, name="disk")
app.add_typer(ssh_keys.app, name="ssh-key")

# Add convenience command for scanning all compute resources
@app.command("scan-all")
def scan_all_compute(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies")
):
    """Scan all Azure compute resources."""
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
            "azure_virtual_machine",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location
        )
    else:
        # Scan VMs
        virtual_machines.scan_vms(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=location,
            resource_group_name=resource_group_name,
            include_all_states=True
        )
        
        # Scan Disks
        disks.scan_disks(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=location,
            resource_group_name=resource_group_name
        )

# ----------------------------------------------------------------------
# Professional tier scan functions (stubs) - append below existing content
# ----------------------------------------------------------------------

from terraback.core.license import require_professional

@require_professional
def scan_azure_sql_servers(
    output_dir: Path,
    subscription_id: Optional[str] = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan Azure SQL Servers (Professional feature)."""
    
    typer.echo("[Professional] Scanning Azure SQL Servers...")
    # TODO: Implement SQL Server scanning
    typer.echo("Azure SQL Server scanning not yet implemented")


@require_professional
def scan_azure_sql_databases(
    output_dir: Path,
    subscription_id: Optional[str] = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan Azure SQL Databases (Professional feature)."""
    
    typer.echo("[Professional] Scanning Azure SQL Databases...")
    # TODO: Implement SQL Database scanning
    typer.echo("Azure SQL Database scanning not yet implemented")


@require_professional
def scan_azure_app_service_plans(
    output_dir: Path,
    subscription_id: Optional[str] = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan Azure App Service Plans (Professional feature)."""
    
    typer.echo("[Professional] Scanning Azure App Service Plans...")
    # TODO: Implement App Service Plan scanning
    typer.echo("Azure App Service Plan scanning not yet implemented")


@require_professional
def scan_azure_web_apps(
    output_dir: Path,
    subscription_id: Optional[str] = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan Azure Web Apps (Professional feature)."""
    
    typer.echo("[Professional] Scanning Azure Web Apps...")
    # TODO: Implement Web App scanning
    typer.echo("Azure Web App scanning not yet implemented")


@require_professional
def scan_azure_function_apps(
    output_dir: Path,
    subscription_id: Optional[str] = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan Azure Function Apps (Professional feature)."""
    
    typer.echo("[Professional] Scanning Azure Function Apps...")
    # TODO: Implement Function App scanning
    typer.echo("Azure Function App scanning not yet implemented")


@require_professional
def scan_azure_key_vaults(
    output_dir: Path,
    subscription_id: Optional[str] = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan Azure Key Vaults (Professional feature)."""
    
    typer.echo("[Professional] Scanning Azure Key Vaults...")
    # TODO: Implement Key Vault scanning
    typer.echo("Azure Key Vault scanning not yet implemented")


@require_professional
def scan_azure_container_registries(
    output_dir: Path,
    subscription_id: Optional[str] = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan Azure Container Registries (Professional feature)."""
    
    typer.echo("[Professional] Scanning Azure Container Registries...")
    # TODO: Implement Container Registry scanning
    typer.echo("Azure Container Registry scanning not yet implemented")


from terraback.core.license import require_professional

@require_professional
def scan_azure_kubernetes_clusters(
    output_dir: Path,
    subscription_id: Optional[str] = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan Azure Kubernetes Clusters (Professional feature)."""
    
    typer.echo("[Professional] Scanning Azure Kubernetes Clusters...")
    # TODO: Implement AKS scanning
    typer.echo("Azure Kubernetes Service scanning not yet implemented")
