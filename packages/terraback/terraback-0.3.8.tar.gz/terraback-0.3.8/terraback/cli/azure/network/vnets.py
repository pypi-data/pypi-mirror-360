# terraback/cli/azure/network/vnets.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import AzureError

from terraback.cli.azure.session import get_cached_azure_session, get_default_subscription_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="vnet", help="Scan and import Azure Virtual Networks.")

def get_vnet_data(subscription_id: str = None, resource_group_name: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch Virtual Network data from Azure.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        resource_group_name: Optional resource group filter
        location: Optional location filter
    
    Returns:
        List of VNet data dictionaries
    """
    session = get_cached_azure_session(subscription_id)
    network_client = NetworkManagementClient(**session)
    
    vnets = []
    
    try:
        # Get VNets either from specific resource group or all
        if resource_group_name:
            vnet_list = network_client.virtual_networks.list(resource_group_name)
        else:
            vnet_list = network_client.virtual_networks.list_all()
        
        for vnet in vnet_list:
            # Apply location filter if specified
            if location and vnet.location != location:
                continue
                
            # Parse resource group from ID
            rg_name = vnet.id.split('/')[4]
            
            # Build VNet data structure matching Terraform schema
            vnet_data = {
                "name": vnet.name,
                "id": vnet.id,
                "resource_group_name": rg_name,
                "location": vnet.location,
                "tags": vnet.tags or {},
                
                # Address space
                "address_space": vnet.address_space.address_prefixes if vnet.address_space else [],
                
                # DNS servers
                "dns_servers": vnet.dhcp_options.dns_servers if vnet.dhcp_options and vnet.dhcp_options.dns_servers else [],
                
                # Subnets (basic info, full subnet scan is separate)
                "subnet_names": [subnet.name for subnet in vnet.subnets] if vnet.subnets else [],
                "subnet_count": len(vnet.subnets) if vnet.subnets else 0,
                
                # DDoS protection
                "ddos_protection_plan": {
                    "id": vnet.ddos_protection_plan.id,
                    "enable": True
                } if vnet.ddos_protection_plan else None,
                
                # BGP community
                "bgp_community": vnet.bgp_communities.virtual_network_community if hasattr(vnet, 'bgp_communities') and vnet.bgp_communities else None,
                
                # VM protection
                "vm_protection_enabled": vnet.enable_vm_protection if hasattr(vnet, 'enable_vm_protection') else None,
                
                # For resource naming
                "name_sanitized": vnet.name.replace('-', '_').lower(),
                
                # Provisioning state
                "provisioning_state": vnet.provisioning_state,
                
                # Flow timeout
                "flow_timeout_in_minutes": vnet.flow_timeout_in_minutes if hasattr(vnet, 'flow_timeout_in_minutes') else None,
            }
            
            # Add subnet details for reference (but not full subnet resources)
            if vnet.subnets:
                vnet_data["subnet_details"] = []
                for subnet in vnet.subnets:
                    vnet_data["subnet_details"].append({
                        "name": subnet.name,
                        "address_prefix": subnet.address_prefix,
                        "id": subnet.id,
                    })
            
            vnets.append(vnet_data)
            
    except AzureError as e:
        typer.echo(f"Error fetching VNets: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return vnets

@app.command("scan")
def scan_vnets(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan all dependencies (Subnets, NSGs, etc.).")
):
    """Scans Azure Virtual Networks and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning Azure VNets with dependencies...")
        recursive_scan(
            "azure_virtual_network",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location
        )
    else:
        typer.echo(f"Scanning for Azure VNets in subscription '{subscription_id}'...")
        if resource_group_name:
            typer.echo(f"Filtering by resource group: {resource_group_name}")
        if location:
            typer.echo(f"Filtering by location: {location}")
        
        vnet_data = get_vnet_data(subscription_id, resource_group_name, location)
        
        if not vnet_data:
            typer.echo("No VNets found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "azure_virtual_network.tf"
        generate_tf(vnet_data, "azure_virtual_network", output_file, provider="azure")
        typer.echo(f"Generated Terraform for {len(vnet_data)} VNets -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "azure_virtual_network",
            vnet_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_vnets(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import file")
):
    """List all Azure VNet resources previously generated."""
    ImportManager(output_dir, "azure_virtual_network").list_all()

@app.command("import")
def import_vnet(
    vnet_id: str = typer.Argument(..., help="Azure VNet resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory with import file")
):
    """Run terraform import for a specific Azure VNet by its resource ID."""
    ImportManager(output_dir, "azure_virtual_network").find_and_import(vnet_id)

# Scan function for cross-scan registry
def scan_azure_vnets(
    output_dir: Path,
    subscription_id: str = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan function to be registered with cross-scan registry."""
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
    
    typer.echo(f"[Cross-scan] Scanning Azure VNets in subscription {subscription_id}")
    
    vnet_data = get_vnet_data(subscription_id, resource_group_name, location)
    
    if vnet_data:
        output_file = output_dir / "azure_virtual_network.tf"
        generate_tf(vnet_data, "azure_virtual_network", output_file, provider="azure")
        generate_imports_file(
            "azure_virtual_network",
            vnet_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(vnet_data)} Azure VNets")