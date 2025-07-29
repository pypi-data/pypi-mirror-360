import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import AzureError

from terraback.cli.azure.session import get_cached_azure_session, get_default_subscription_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="subnet", help="Scan and import Azure Subnets.")

def get_subnet_data(subscription_id: str = None, resource_group_name: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch Subnet data from Azure.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        resource_group_name: Optional resource group filter
        location: Optional location filter
    
    Returns:
        List of subnet data dictionaries
    """
    session = get_cached_azure_session(subscription_id)
    network_client = NetworkManagementClient(**session)
    
    subnets = []
    
    try:
        # First get all VNets to iterate through their subnets
        if resource_group_name:
            vnet_list = network_client.virtual_networks.list(resource_group_name)
        else:
            vnet_list = network_client.virtual_networks.list_all()
        
        for vnet in vnet_list:
            # Apply location filter if specified
            if location and vnet.location != location:
                continue
                
            # Parse resource group from VNet ID
            vnet_rg = vnet.id.split('/')[4]
            
            # Get subnets for this VNet
            subnet_list = network_client.subnets.list(
                resource_group_name=vnet_rg,
                virtual_network_name=vnet.name
            )
            
            for subnet in subnet_list:
                # Build subnet data structure matching Terraform schema
                subnet_data = {
                    "name": subnet.name,
                    "id": subnet.id,
                    "resource_group_name": vnet_rg,
                    "virtual_network_name": vnet.name,
                    "address_prefixes": [subnet.address_prefix] if subnet.address_prefix else [],
                    
                    # Service endpoints
                    "service_endpoints": [],
                    "service_endpoint_policy_ids": [],
                    
                    # Delegations
                    "delegation": [],
                    
                    # Security
                    "network_security_group_id": subnet.network_security_group.id if subnet.network_security_group else None,
                    "route_table_id": subnet.route_table.id if subnet.route_table else None,
                    
                    # Private endpoint settings
                    "private_endpoint_network_policies_enabled": getattr(subnet, 'private_endpoint_network_policies', 'Enabled') == 'Enabled',
                    "private_link_service_network_policies_enabled": getattr(subnet, 'private_link_service_network_policies', 'Enabled') == 'Enabled',
                    
                    # NAT Gateway
                    "nat_gateway_id": subnet.nat_gateway.id if hasattr(subnet, 'nat_gateway') and subnet.nat_gateway else None,
                    
                    # For resource naming
                    "name_sanitized": subnet.name.replace('-', '_').lower(),
                    
                    # State
                    "provisioning_state": subnet.provisioning_state,
                }
                
                # Extract service endpoints
                if subnet.service_endpoints:
                    for endpoint in subnet.service_endpoints:
                        subnet_data["service_endpoints"].append({
                            "service": endpoint.service,
                            "locations": endpoint.locations if endpoint.locations else []
                        })
                
                # Extract service endpoint policies
                if hasattr(subnet, 'service_endpoint_policies') and subnet.service_endpoint_policies:
                    subnet_data["service_endpoint_policy_ids"] = [policy.id for policy in subnet.service_endpoint_policies]
                
                # Extract delegations
                if subnet.delegations:
                    for delegation in subnet.delegations:
                        subnet_data["delegation"].append({
                            "name": delegation.name,
                            "service_delegation": {
                                "name": delegation.service_name,
                                "actions": delegation.actions if hasattr(delegation, 'actions') else []
                            }
                        })
                
                subnets.append(subnet_data)
            
    except AzureError as e:
        typer.echo(f"Error fetching subnets: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return subnets

@app.command("scan")
def scan_subnets(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan all dependencies (NSGs, Route Tables).")
):
    """Scans Azure Subnets and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning Azure Subnets with dependencies...")
        recursive_scan(
            "azure_subnet",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location
        )
    else:
        typer.echo(f"Scanning for Azure Subnets in subscription '{subscription_id}'...")
        if resource_group_name:
            typer.echo(f"Filtering by resource group: {resource_group_name}")
        if location:
            typer.echo(f"Filtering by location: {location}")
        
        subnet_data = get_subnet_data(subscription_id, resource_group_name, location)
        
        if not subnet_data:
            typer.echo("No subnets found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "azure_subnet.tf"
        generate_tf(subnet_data, "azure_subnet", output_file, provider="azure")
        typer.echo(f"Generated Terraform for {len(subnet_data)} subnets -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "azure_subnet",
            subnet_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_subnets(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import file")
):
    """List all Azure Subnet resources previously generated."""
    ImportManager(output_dir, "azure_subnet").list_all()

@app.command("import")
def import_subnet(
    subnet_id: str = typer.Argument(..., help="Azure Subnet resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory with import file")
):
    """Run terraform import for a specific Azure Subnet by its resource ID."""
    ImportManager(output_dir, "azure_subnet").find_and_import(subnet_id)

# Scan function for cross-scan registry
def scan_azure_subnets(
    output_dir: Path,
    subscription_id: str = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan function to be registered with cross-scan registry."""
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
    
    typer.echo(f"[Cross-scan] Scanning Azure Subnets in subscription {subscription_id}")
    
    subnet_data = get_subnet_data(subscription_id, resource_group_name, location)
    
    if subnet_data:
        output_file = output_dir / "azure_subnet.tf"
        generate_tf(subnet_data, "azure_subnet", output_file, provider="azure")
        generate_imports_file(
            "azure_subnet",
            subnet_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(subnet_data)} Azure Subnets")
