# terraback/cli/azure/loadbalancer/load_balancers.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import AzureError

from terraback.cli.azure.session import get_cached_azure_session, get_default_subscription_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="standard", help="Scan and import Azure Load Balancers.")

def get_load_balancer_data(subscription_id: str = None, resource_group_name: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch Load Balancer data from Azure.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        resource_group_name: Optional resource group filter
        location: Optional location filter
    
    Returns:
        List of load balancer data dictionaries
    """
    session = get_cached_azure_session(subscription_id)
    network_client = NetworkManagementClient(**session)
    
    load_balancers = []
    
    try:
        # Get load balancers either from specific resource group or all
        if resource_group_name:
            lb_list = network_client.load_balancers.list(resource_group_name)
        else:
            lb_list = network_client.load_balancers.list_all()
        
        for lb in lb_list:
            # Apply location filter if specified
            if location and lb.location != location:
                continue
                
            # Parse resource group from ID
            rg_name = lb.id.split('/')[4]
            
            # Build load balancer data structure matching Terraform schema
            lb_data = {
                "name": lb.name,
                "id": lb.id,
                "resource_group_name": rg_name,
                "location": lb.location,
                "tags": lb.tags or {},
                
                # SKU
                "sku": lb.sku.name if lb.sku else "Basic",
                "sku_tier": lb.sku.tier if lb.sku else "Regional",
                
                # Frontend IP configurations
                "frontend_ip_configuration": [],
                
                # Backend address pools
                "backend_address_pool": [],
                
                # Health probes
                "probe": [],
                
                # Load balancing rules
                "lb_rule": [],
                
                # Inbound NAT rules
                "inbound_nat_rule": [],
                
                # Outbound rules
                # "outbound_rule": [],
                
                # For resource naming
                "name_sanitized": lb.name.replace('-', '_').lower(),
                
                # State
                "provisioning_state": lb.provisioning_state,
            }
            
            # Extract frontend IP configurations
            if lb.frontend_ip_configurations:
                for frontend in lb.frontend_ip_configurations:
                    frontend_data = {
                        "name": frontend.name,
                        "id": frontend.id,
                        "private_ip_address": frontend.private_ip_address,
                        "private_ip_address_allocation": frontend.private_ip_allocation_method,
                        "private_ip_address_version": frontend.private_ip_address_version or "IPv4",
                        "subnet_id": frontend.subnet.id if frontend.subnet else None,
                        "public_ip_address_id": frontend.public_ip_address.id if frontend.public_ip_address else None,
                        "public_ip_prefix_id": frontend.public_ip_prefix.id if hasattr(frontend, 'public_ip_prefix') and frontend.public_ip_prefix else None,
                        "zones": frontend.zones if hasattr(frontend, 'zones') else [],
                    }
                    lb_data["frontend_ip_configuration"].append(frontend_data)
            
            # Extract backend address pools
            if lb.backend_address_pools:
                for backend in lb.backend_address_pools:
                    backend_data = {
                        "name": backend.name,
                        "id": backend.id,
                    }
                    lb_data["backend_address_pool"].append(backend_data)
            
            # Extract health probes
            if lb.probes:
                for probe in lb.probes:
                    probe_data = {
                        "name": probe.name,
                        "id": probe.id,
                        "protocol": probe.protocol,
                        "port": probe.port,
                        "request_path": probe.request_path if probe.protocol.upper() in ["HTTP", "HTTPS"] else None,
                        "interval_in_seconds": probe.interval_in_seconds,
                        "number_of_probes": probe.number_of_probes,
                    }
                    lb_data["probe"].append(probe_data)
            
            # Extract load balancing rules
            if lb.load_balancing_rules:
                for rule in lb.load_balancing_rules:
                    rule_data = {
                        "name": rule.name,
                        "id": rule.id,
                        "protocol": rule.protocol,
                        "frontend_port": rule.frontend_port,
                        "backend_port": rule.backend_port,
                        "frontend_ip_configuration_id": rule.frontend_ip_configuration.id if rule.frontend_ip_configuration else None,
                        "backend_address_pool_id": rule.backend_address_pool.id if rule.backend_address_pool else None,
                        "probe_id": rule.probe.id if rule.probe else None,
                        "enable_floating_ip": rule.enable_floating_ip,
                        "idle_timeout_in_minutes": rule.idle_timeout_in_minutes,
                        "load_distribution": rule.load_distribution,
                        "disable_outbound_snat": rule.disable_outbound_snat if hasattr(rule, 'disable_outbound_snat') else False,
                        "enable_tcp_reset": rule.enable_tcp_reset if hasattr(rule, 'enable_tcp_reset') else False,
                    }
                    lb_data["lb_rule"].append(rule_data)
            
            # Extract inbound NAT rules
            if lb.inbound_nat_rules:
                for nat_rule in lb.inbound_nat_rules:
                    nat_data = {
                        "name": nat_rule.name,
                        "id": nat_rule.id,
                        "protocol": nat_rule.protocol,
                        "frontend_port": nat_rule.frontend_port,
                        "backend_port": nat_rule.backend_port,
                        "frontend_ip_configuration_id": nat_rule.frontend_ip_configuration.id if nat_rule.frontend_ip_configuration else None,
                        "idle_timeout_in_minutes": nat_rule.idle_timeout_in_minutes,
                        "enable_floating_ip": nat_rule.enable_floating_ip,
                        "enable_tcp_reset": nat_rule.enable_tcp_reset if hasattr(nat_rule, 'enable_tcp_reset') else False,
                    }
                    lb_data["inbound_nat_rule"].append(nat_data)
            
            # Extract outbound rules (for Standard SKU)
            # Outbound rules are not rendered in the template, so this section is removed.
            
            load_balancers.append(lb_data)
            
    except AzureError as e:
        typer.echo(f"Error fetching load balancers: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return load_balancers

@app.command("scan")
def scan_load_balancers(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan all dependencies.")
):
    """Scans Azure Load Balancers and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning Azure Load Balancers with dependencies...")
        recursive_scan(
            "azure_lb",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location
        )
    else:
        typer.echo(f"Scanning for Azure Load Balancers in subscription '{subscription_id}'...")
        if resource_group_name:
            typer.echo(f"Filtering by resource group: {resource_group_name}")
        if location:
            typer.echo(f"Filtering by location: {location}")
        
        lb_data = get_load_balancer_data(subscription_id, resource_group_name, location)
        
        if not lb_data:
            typer.echo("No load balancers found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "azure_lb.tf"
        generate_tf(lb_data, "azure_lb", output_file, provider="azure")
        typer.echo(f"Generated Terraform for {len(lb_data)} load balancers -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "azure_lb",
            lb_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_load_balancers(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import file")
):
    """List all Azure Load Balancer resources previously generated."""
    ImportManager(output_dir, "azure_lb").list_all()

@app.command("import")
def import_load_balancer(
    lb_id: str = typer.Argument(..., help="Azure Load Balancer resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory with import file")
):
    """Run terraform import for a specific Azure Load Balancer by its resource ID."""
    ImportManager(output_dir, "azure_lb").find_and_import(lb_id)

# Scan function for cross-scan registry
def scan_azure_load_balancers(
    output_dir: Path,
    subscription_id: str = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan function to be registered with cross-scan registry."""
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
    
    typer.echo(f"[Cross-scan] Scanning Azure Load Balancers in subscription {subscription_id}")
    
    lb_data = get_load_balancer_data(subscription_id, resource_group_name, location)
    
    if lb_data:
        output_file = output_dir / "azure_lb.tf"
        generate_tf(lb_data, "azure_lb", output_file, provider="azure")
        generate_imports_file(
            "azure_lb",
            lb_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(lb_data)} Azure Load Balancers")