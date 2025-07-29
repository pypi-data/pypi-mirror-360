# terraback/cli/azure/network/__init__.py
import typer
from pathlib import Path
from typing import Optional

from . import vnets, subnets, nsgs, network_interfaces
from .vnets import scan_azure_vnets
from .subnets import scan_azure_subnets
from .nsgs import scan_azure_nsgs
from .network_interfaces import scan_azure_network_interfaces
from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="network",
    help="Work with Azure Networking resources like VNets, Subnets, NSGs, and NICs.",
    no_args_is_help=True
)

def register():
    """Registers the network resources with the cross-scan registry."""
    # Virtual Networks
    register_scan_function("azure_virtual_network", scan_azure_vnets)
    
    # Subnets
    register_scan_function("azure_subnet", scan_azure_subnets)
    
    # Network Security Groups
    register_scan_function("azure_network_security_group", scan_azure_nsgs)
    
    # Network Interfaces
    register_scan_function("azure_network_interface", scan_azure_network_interfaces)
    
    # VNet Dependencies
    cross_scan_registry.register_dependency("azure_virtual_network", "azure_resource_group")
    cross_scan_registry.register_dependency("azure_virtual_network", "azure_subnet")
    
    # Subnet dependencies
    cross_scan_registry.register_dependency("azure_subnet", "azure_virtual_network")
    cross_scan_registry.register_dependency("azure_subnet", "azure_network_security_group")
    cross_scan_registry.register_dependency("azure_subnet", "azure_route_table")
    
    # NSG dependencies  
    cross_scan_registry.register_dependency("azure_network_security_group", "azure_resource_group")
    
    # Network Interface dependencies
    cross_scan_registry.register_dependency("azure_network_interface", "azure_subnet")
    cross_scan_registry.register_dependency("azure_network_interface", "azure_network_security_group")
    cross_scan_registry.register_dependency("azure_network_interface", "azure_lb")

# Add sub-commands
app.add_typer(vnets.app, name="vnet")
app.add_typer(subnets.app, name="subnet")
app.add_typer(nsgs.app, name="nsg")
app.add_typer(network_interfaces.app, name="nic")

# Add convenience command for scanning all network resources
@app.command("scan-all")
def scan_all_network(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies")
):
    """Scan all Azure network resources."""
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
            "azure_virtual_network",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location
        )
    else:
        # Scan VNets
        vnets.scan_vnets(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=location,
            resource_group_name=resource_group_name,
            with_deps=False
        )
        
        # Scan Subnets
        subnets.scan_subnets(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=location,
            resource_group_name=resource_group_name,
            with_deps=False
        )
        
        # Scan NSGs
        nsgs.scan_nsgs(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=location,
            resource_group_name=resource_group_name,
            with_deps=False
        )
        
        # Scan NICs
        network_interfaces.scan_network_interfaces(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=location,
            resource_group_name=resource_group_name,
            with_deps=False
        )