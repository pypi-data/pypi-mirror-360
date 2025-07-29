# terraback/cli/azure/resources/resource_groups.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import AzureError

from terraback.cli.azure.session import get_cached_azure_session, get_default_subscription_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="rg", help="Scan and import Azure Resource Groups.")

def get_resource_group_data(subscription_id: str = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch Resource Group data from Azure.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        location: Optional location filter
    
    Returns:
        List of resource group data dictionaries
    """
    session = get_cached_azure_session(subscription_id)
    resource_client = ResourceManagementClient(**session)
    
    resource_groups = []
    
    try:
        # Get all resource groups
        rg_list = resource_client.resource_groups.list()
        
        for rg in rg_list:
            # Apply location filter if specified
            if location and rg.location != location:
                continue
            
            # Build resource group data structure matching Terraform schema
            rg_data = {
                "name": rg.name,
                "id": rg.id,
                "location": rg.location,
                "tags": rg.tags or {},
                
                # Managed by (for managed resource groups)
                "managed_by": rg.managed_by if hasattr(rg, 'managed_by') else None,
                
                # For resource naming
                "name_sanitized": rg.name.replace('-', '_').lower(),
                
                # State
                "provisioning_state": rg.properties.provisioning_state if rg.properties else None,
            }
            
            resource_groups.append(rg_data)
            
    except AzureError as e:
        typer.echo(f"Error fetching resource groups: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return resource_groups

@app.command("scan")
def scan_resource_groups(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION")
):
    """Scans Azure Resource Groups and generates Terraform code."""
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    typer.echo(f"Scanning for Azure Resource Groups in subscription '{subscription_id}'...")
    if location:
        typer.echo(f"Filtering by location: {location}")
    
    rg_data = get_resource_group_data(subscription_id, location)
    
    if not rg_data:
        typer.echo("No resource groups found.")
        return
    
    # Generate Terraform files
    output_file = output_dir / "azure_resource_group.tf"
    generate_tf(rg_data, "azure_resource_group", output_file, provider="azure")
    typer.echo(f"Generated Terraform for {len(rg_data)} resource groups -> {output_file}")
    
    # Generate import file
    generate_imports_file(
        "azure_resource_group",
        rg_data,
        remote_resource_id_key="id",
        output_dir=output_dir
    )

@app.command("list")
def list_resource_groups(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import file")
):
    """List all Azure Resource Group resources previously generated."""
    ImportManager(output_dir, "azure_resource_group").list_all()

@app.command("import")
def import_resource_group(
    rg_id: str = typer.Argument(..., help="Azure Resource Group resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory with import file")
):
    """Run terraform import for a specific Azure Resource Group by its resource ID."""
    ImportManager(output_dir, "azure_resource_group").find_and_import(rg_id)

# Scan function for cross-scan registry
def scan_azure_resource_groups(
    output_dir: Path,
    subscription_id: str = None,
    location: Optional[str] = None
):
    """Scan function to be registered with cross-scan registry."""
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
    
    typer.echo(f"[Cross-scan] Scanning Azure Resource Groups in subscription {subscription_id}")
    
    rg_data = get_resource_group_data(subscription_id, location)
    
    if rg_data:
        output_file = output_dir / "azure_resource_group.tf"
        generate_tf(rg_data, "azure_resource_group", output_file, provider="azure")
        generate_imports_file(
            "azure_resource_group",
            rg_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(rg_data)} Azure Resource Groups")