import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import AzureError

from terraback.cli.azure.session import get_cached_azure_session, get_default_subscription_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="nsg", help="Scan and import Azure Network Security Groups.")

def get_nsg_data(subscription_id: str = None, resource_group_name: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch Network Security Group data from Azure.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        resource_group_name: Optional resource group filter
        location: Optional location filter
    
    Returns:
        List of NSG data dictionaries
    """
    session = get_cached_azure_session(subscription_id)
    network_client = NetworkManagementClient(**session)
    
    nsgs = []
    
    try:
        # Get NSGs either from specific resource group or all
        if resource_group_name:
            nsg_list = network_client.network_security_groups.list(resource_group_name)
        else:
            nsg_list = network_client.network_security_groups.list_all()
        
        for nsg in nsg_list:
            # Apply location filter if specified
            if location and nsg.location != location:
                continue
                
            # Parse resource group from ID
            rg_name = nsg.id.split('/')[4]
            
            # Build NSG data structure matching Terraform schema
            nsg_data = {
                "name": nsg.name,
                "id": nsg.id,
                "resource_group_name": rg_name,
                "location": nsg.location,
                "tags": nsg.tags or {},
                
                # Security rules
                "security_rules": [],
                
                # Associated resources
                "subnet_ids": [],
                "network_interface_ids": [],
                
                # For resource naming
                "name_sanitized": nsg.name.replace('-', '_').lower(),
                
                # State
                "provisioning_state": nsg.provisioning_state,
            }
            
            # Extract security rules
            if nsg.security_rules:
                for rule in nsg.security_rules:
                    rule_data = {
                        "name": rule.name,
                        "priority": rule.priority,
                        "direction": rule.direction,
                        "access": rule.access,
                        "protocol": rule.protocol,
                        "source_port_range": rule.source_port_range,
                        "source_port_ranges": rule.source_port_ranges if rule.source_port_ranges else [],
                        "destination_port_range": rule.destination_port_range,
                        "destination_port_ranges": rule.destination_port_ranges if rule.destination_port_ranges else [],
                        "source_address_prefix": rule.source_address_prefix,
                        "source_address_prefixes": rule.source_address_prefixes if rule.source_address_prefixes else [],
                        "source_application_security_group_ids": [],
                        "destination_address_prefix": rule.destination_address_prefix,
                        "destination_address_prefixes": rule.destination_address_prefixes if rule.destination_address_prefixes else [],
                        "destination_application_security_group_ids": [],
                        "description": rule.description if rule.description else "",
                    }
                    
                    # Extract ASG references
                    if rule.source_application_security_groups:
                        rule_data["source_application_security_group_ids"] = [asg.id for asg in rule.source_application_security_groups]
                    if rule.destination_application_security_groups:
                        rule_data["destination_application_security_group_ids"] = [asg.id for asg in rule.destination_application_security_groups]
                    
                    nsg_data["security_rules"].append(rule_data)
            
            # Extract associated subnets
            if hasattr(nsg, 'subnets') and nsg.subnets:
                nsg_data["subnet_ids"] = [subnet.id for subnet in nsg.subnets]
            
            # Extract associated network interfaces
            if hasattr(nsg, 'network_interfaces') and nsg.network_interfaces:
                nsg_data["network_interface_ids"] = [nic.id for nic in nsg.network_interfaces]
            
            # Sort rules by priority for cleaner output
            nsg_data["security_rules"].sort(key=lambda x: x["priority"])
            
            nsgs.append(nsg_data)
            
    except AzureError as e:
        typer.echo(f"Error fetching NSGs: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return nsgs

@app.command("scan")
def scan_nsgs(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan all dependencies.")
):
    """Scans Azure Network Security Groups and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning Azure NSGs with dependencies...")
        recursive_scan(
            "azure_network_security_group",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location
        )
    else:
        typer.echo(f"Scanning for Azure NSGs in subscription '{subscription_id}'...")
        if resource_group_name:
            typer.echo(f"Filtering by resource group: {resource_group_name}")
        if location:
            typer.echo(f"Filtering by location: {location}")
        
        nsg_data = get_nsg_data(subscription_id, resource_group_name, location)
        
        if not nsg_data:
            typer.echo("No NSGs found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "azure_network_security_group.tf"
        generate_tf(nsg_data, "azure_network_security_group", output_file, provider="azure")
        typer.echo(f"Generated Terraform for {len(nsg_data)} NSGs -> {output_file}")
        
        # Count total rules
        total_rules = sum(len(nsg["security_rules"]) for nsg in nsg_data)
        typer.echo(f"Total security rules: {total_rules}")
        
        # Generate import file
        generate_imports_file(
            "azure_network_security_group",
            nsg_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_nsgs(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import file")
):
    """List all Azure NSG resources previously generated."""
    ImportManager(output_dir, "azure_network_security_group").list_all()

@app.command("import")
def import_nsg(
    nsg_id: str = typer.Argument(..., help="Azure NSG resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory with import file")
):
    """Run terraform import for a specific Azure NSG by its resource ID."""
    ImportManager(output_dir, "azure_network_security_group").find_and_import(nsg_id)

# Scan function for cross-scan registry
def scan_azure_nsgs(
    output_dir: Path,
    subscription_id: str = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan function to be registered with cross-scan registry."""
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
    
    typer.echo(f"[Cross-scan] Scanning Azure NSGs in subscription {subscription_id}")
    
    nsg_data = get_nsg_data(subscription_id, resource_group_name, location)
    
    if nsg_data:
        output_file = output_dir / "azure_network_security_group.tf"
        generate_tf(nsg_data, "azure_network_security_group", output_file, provider="azure")
        generate_imports_file(
            "azure_network_security_group",
            nsg_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(nsg_data)} Azure NSGs")