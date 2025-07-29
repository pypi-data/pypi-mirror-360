import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import AzureError

from terraback.cli.azure.session import get_cached_azure_session, get_default_subscription_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="disk", help="Scan and import Azure Managed Disks.")

def get_disk_data(subscription_id: str = None, resource_group_name: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch Managed Disk data from Azure.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        resource_group_name: Optional resource group filter
        location: Optional location filter
    
    Returns:
        List of disk data dictionaries
    """
    session = get_cached_azure_session(subscription_id)
    compute_client = ComputeManagementClient(**session)
    
    disks = []
    
    try:
        # Get disks either from specific resource group or all
        if resource_group_name:
            disk_list = compute_client.disks.list_by_resource_group(resource_group_name)
        else:
            disk_list = compute_client.disks.list()
        
        for disk in disk_list:
            # Apply location filter if specified
            if location and disk.location != location:
                continue
                
            # Parse resource group from ID
            rg_name = disk.id.split('/')[4] if not resource_group_name else resource_group_name
            
            # Build disk data structure matching Terraform schema
            disk_data = {
                "name": disk.name,
                "id": disk.id,
                "resource_group_name": rg_name,
                "location": disk.location,
                "tags": disk.tags or {},
                
                # Core properties
                "storage_account_type": disk.sku.name if disk.sku else None,
                "create_option": disk.creation_data.create_option if disk.creation_data else None,
                "disk_size_gb": disk.disk_size_gb,
                
                # Source information - safely access nested attributes
                "source_uri": getattr(disk.creation_data, 'source_uri', None) if disk.creation_data else None,
                "source_resource_id": getattr(disk.creation_data, 'source_resource_id', None) if disk.creation_data else None,
                "image_reference_id": None,
                
                # OS information
                "os_type": disk.os_type,
                "hyper_v_generation": getattr(disk, 'hyper_v_generation', None),
                
                # Availability zones
                "zones": disk.zones if disk.zones else None,
                
                # Performance - safely access attributes that might not exist
                "disk_iops_read_write": getattr(disk, 'disk_iops_read_write', None),
                "disk_mbps_read_write": getattr(disk, 'disk_m_bps_read_write', None),  # Note: might be disk_m_bps_read_write
                "tier": getattr(disk, 'tier', None),
                
                # Access policy
                "disk_access_id": getattr(disk, 'disk_access_id', None),
                "network_access_policy": getattr(disk, 'network_access_policy', None),
                
                # Bursting
                "bursting_enabled": getattr(disk, 'bursting_enabled', None),
                
                # Encryption
                "disk_encryption_set_id": None,
                
                # For resource naming
                "name_sanitized": disk.name.replace('-', '_').lower(),
                
                # State
                "disk_state": disk.disk_state,
                "provisioning_state": disk.provisioning_state,
            }
            
            # Handle image reference
            if disk.creation_data and hasattr(disk.creation_data, 'image_reference') and disk.creation_data.image_reference:
                disk_data["image_reference_id"] = disk.creation_data.image_reference.id
            
            # Handle encryption
            if disk.encryption and hasattr(disk.encryption, 'disk_encryption_set_id'):
                disk_data["disk_encryption_set_id"] = disk.encryption.disk_encryption_set_id
            
            # Handle encryption settings if present
            if hasattr(disk, 'encryption_settings_collection') and disk.encryption_settings_collection and disk.encryption_settings_collection.enabled:
                settings = disk.encryption_settings_collection.encryption_settings[0] if disk.encryption_settings_collection.encryption_settings else None
                if settings:
                    disk_data["encryption_settings"] = {
                        "enabled": True,
                        "disk_encryption_key": {
                            "secret_url": settings.disk_encryption_key.secret_url,
                            "source_vault_id": settings.disk_encryption_key.source_vault.id
                        } if settings.disk_encryption_key else None,
                        "key_encryption_key": {
                            "key_url": settings.key_encryption_key.key_url,
                            "source_vault_id": settings.key_encryption_key.source_vault.id
                        } if settings.key_encryption_key else None,
                    }
            else:
                disk_data["encryption_settings"] = None
            
            disks.append(disk_data)
            
    except AzureError as e:
        typer.echo(f"Error fetching disks: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return disks

@app.command("scan")
def scan_disks(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan all dependencies.")
):
    """Scans Azure Managed Disks and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning Azure Managed Disks with dependencies...")
        recursive_scan(
            "azure_managed_disk",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location
        )
    else:
        typer.echo(f"Scanning for Azure Managed Disks in subscription '{subscription_id}'...")
        if resource_group_name:
            typer.echo(f"Filtering by resource group: {resource_group_name}")
        if location:
            typer.echo(f"Filtering by location: {location}")
        
        disk_data = get_disk_data(subscription_id, resource_group_name, location)
        
        if not disk_data:
            typer.echo("No disks found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "azure_managed_disk.tf"
        generate_tf(disk_data, "azure_managed_disk", output_file, provider="azure")
        typer.echo(f"Generated Terraform for {len(disk_data)} disks -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "azure_managed_disk",
            disk_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_disks(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import file")
):
    """List all Azure Managed Disk resources previously generated."""
    ImportManager(output_dir, "azure_managed_disk").list_all()

@app.command("import")
def import_disk(
    disk_id: str = typer.Argument(..., help="Azure Managed Disk resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory with import file")
):
    """Run terraform import for a specific Azure Managed Disk by its resource ID."""
    ImportManager(output_dir, "azure_managed_disk").find_and_import(disk_id)

# Scan function for cross-scan registry
def scan_azure_disks(
    output_dir: Path,
    subscription_id: str = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan function to be registered with cross-scan registry."""
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
    
    typer.echo(f"[Cross-scan] Scanning Azure Managed Disks in subscription {subscription_id}")
    
    disk_data = get_disk_data(subscription_id, resource_group_name, location)
    
    if disk_data:
        output_file = output_dir / "azure_managed_disk.tf"
        generate_tf(disk_data, "azure_managed_disk", output_file, provider="azure")
        generate_imports_file(
            "azure_managed_disk",
            disk_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(disk_data)} Azure Managed Disks")