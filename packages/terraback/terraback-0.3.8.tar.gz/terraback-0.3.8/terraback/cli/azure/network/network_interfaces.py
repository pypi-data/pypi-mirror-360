# terraback/cli/azure/network/network_interfaces.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import AzureError

from terraback.cli.azure.session import get_cached_azure_session, get_default_subscription_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="nic", help="Scan and import Azure Network Interfaces.")

def get_network_interface_data(subscription_id: str = None, resource_group_name: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch Network Interface data from Azure.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        resource_group_name: Optional resource group filter
        location: Optional location filter
    
    Returns:
        List of network interface data dictionaries
    """
    session = get_cached_azure_session(subscription_id)
    network_client = NetworkManagementClient(**session)
    
    network_interfaces = []
    
    try:
        # Get network interfaces either from specific resource group or all
        if resource_group_name:
            nic_list = network_client.network_interfaces.list(resource_group_name)
        else:
            nic_list = network_client.network_interfaces.list_all()
        
        for nic in nic_list:
            # Apply location filter if specified
            if location and nic.location != location:
                continue
                
            # Parse resource group from ID
            rg_name = nic.id.split('/')[4]
            
            # Build network interface data structure matching Terraform schema
            nic_data = {
                "name": nic.name,
                "id": nic.id,
                "resource_group_name": rg_name,
                "location": nic.location,
                "tags": nic.tags or {},
                
                # IP configurations
                "ip_configuration": [],
                
                # DNS settings
                "dns_servers": nic.dns_settings.dns_servers if nic.dns_settings else [],
                "internal_dns_name_label": nic.dns_settings.internal_dns_name_label if nic.dns_settings else None,
                
                # Security
                "enable_accelerated_networking": nic.enable_accelerated_networking,
                "enable_ip_forwarding": nic.enable_ip_forwarding,
                
                # Associated VM
                "virtual_machine_id": nic.virtual_machine.id if nic.virtual_machine else None,
                
                # Associated NSG
                "network_security_group_id": nic.network_security_group.id if nic.network_security_group else None,
                
                # For resource naming
                "name_sanitized": nic.name.replace('-', '_').lower(),
                
                # State
                "provisioning_state": nic.provisioning_state,
                
                # MAC address (read-only)
                "mac_address": nic.mac_address,
                
                # Primary NIC flag
                "primary": nic.primary if hasattr(nic, 'primary') else None,
            }
            
            # Extract IP configurations
            if nic.ip_configurations:
                for ip_config in nic.ip_configurations:
                    config_data = {
                        "name": ip_config.name,
                        "subnet_id": ip_config.subnet.id if ip_config.subnet else None,
                        "private_ip_address_allocation": ip_config.private_ip_address_allocation_method,
                        "private_ip_address": ip_config.private_ip_address,
                        "primary": ip_config.primary,
                        "private_ip_address_version": ip_config.private_ip_address_version or "IPv4",
                        "public_ip_address_id": ip_config.public_ip_address.id if ip_config.public_ip_address else None,
                    }
                    
                    # Application Gateway Backend Pools
                    if hasattr(ip_config, 'application_gateway_backend_address_pools') and ip_config.application_gateway_backend_address_pools:
                        config_data["application_gateway_backend_address_pool_ids"] = [pool.id for pool in ip_config.application_gateway_backend_address_pools]
                    
                    # Load Balancer Backend Pools
                    if hasattr(ip_config, 'load_balancer_backend_address_pools') and ip_config.load_balancer_backend_address_pools:
                        config_data["load_balancer_backend_address_pool_ids"] = [pool.id for pool in ip_config.load_balancer_backend_address_pools]
                    
                    # Load Balancer Inbound NAT Rules
                    if hasattr(ip_config, 'load_balancer_inbound_nat_rules') and ip_config.load_balancer_inbound_nat_rules:
                        config_data["load_balancer_inbound_nat_rule_ids"] = [rule.id for rule in ip_config.load_balancer_inbound_nat_rules]
                    
                    nic_data["ip_configuration"].append(config_data)
            
            network_interfaces.append(nic_data)
            
    except AzureError as e:
        typer.echo(f"Error fetching network interfaces: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return network_interfaces

@app.command("scan")
def scan_network_interfaces(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan all dependencies.")
):
    """Scans Azure Network Interfaces and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning Azure Network Interfaces with dependencies...")
        recursive_scan(
            "azure_network_interface",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location
        )
    else:
        typer.echo(f"Scanning for Azure Network Interfaces in subscription '{subscription_id}'...")
        if resource_group_name:
            typer.echo(f"Filtering by resource group: {resource_group_name}")
        if location:
            typer.echo(f"Filtering by location: {location}")
        
        nic_data = get_network_interface_data(subscription_id, resource_group_name, location)
        
        if not nic_data:
            typer.echo("No network interfaces found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "azure_network_interface.tf"
        generate_tf(nic_data, "azure_network_interface", output_file, provider="azure")
        typer.echo(f"Generated Terraform for {len(nic_data)} network interfaces -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "azure_network_interface",
            nic_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_network_interfaces(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import file")
):
    """List all Azure Network Interface resources previously generated."""
    ImportManager(output_dir, "azure_network_interface").list_all()

@app.command("import")
def import_network_interface(
    nic_id: str = typer.Argument(..., help="Azure Network Interface resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory with import file")
):
    """Run terraform import for a specific Azure Network Interface by its resource ID."""
    ImportManager(output_dir, "azure_network_interface").find_and_import(nic_id)

# Scan function for cross-scan registry
def scan_azure_network_interfaces(
    output_dir: Path,
    subscription_id: str = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan function to be registered with cross-scan registry."""
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
    
    typer.echo(f"[Cross-scan] Scanning Azure Network Interfaces in subscription {subscription_id}")
    
    nic_data = get_network_interface_data(subscription_id, resource_group_name, location)
    
    if nic_data:
        output_file = output_dir / "azure_network_interface.tf"
        generate_tf(nic_data, "azure_network_interface", output_file, provider="azure")
        generate_imports_file(
            "azure_network_interface",
            nic_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(nic_data)} Azure Network Interfaces")