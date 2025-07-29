import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from azure.mgmt.storage import StorageManagementClient
from azure.core.exceptions import AzureError

from terraback.cli.azure.session import get_cached_azure_session, get_default_subscription_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="account", help="Scan and import Azure Storage Accounts.")

def get_storage_account_data(subscription_id: str = None, resource_group_name: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch Storage Account data from Azure.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        resource_group_name: Optional resource group filter
        location: Optional location filter
    
    Returns:
        List of storage account data dictionaries
    """
    session = get_cached_azure_session(subscription_id)
    storage_client = StorageManagementClient(**session)
    
    storage_accounts = []
    
    try:
        # Get storage accounts either from specific resource group or all
        if resource_group_name:
            account_list = storage_client.storage_accounts.list_by_resource_group(resource_group_name)
        else:
            account_list = storage_client.storage_accounts.list()
        
        for account in account_list:
            # Apply location filter if specified
            if location and account.location != location:
                continue
                
            # Parse resource group from ID
            rg_name = account.id.split('/')[4]
            
            # Get detailed properties including access keys
            account_details = storage_client.storage_accounts.get_properties(
                resource_group_name=rg_name,
                account_name=account.name
            )
            
            # Build storage account data structure matching Terraform schema
            account_data = {
                "name": account.name,
                "id": account.id,
                "resource_group_name": rg_name,
                "location": account.location,
                "tags": account.tags or {},
                
                # Account settings
                "account_tier": account.sku.tier.value if account.sku and account.sku.tier else "Standard",
                "account_replication_type": account.sku.name.split('_')[1] if account.sku else "LRS",
                "account_kind": account.kind.value if account.kind else "StorageV2",
                "access_tier": getattr(account_details, 'access_tier', 'Hot'),
                
                # Security settings
                "enable_https_traffic_only": getattr(account_details, 'enable_https_traffic_only', True),
                "min_tls_version": getattr(account_details, 'minimum_tls_version', 'TLS1_2'),
                "allow_blob_public_access": getattr(account_details, 'allow_blob_public_access', False),
                "shared_access_key_enabled": getattr(account_details, 'allow_shared_key_access', True),
                
                # Network settings
                "network_rules": None,
                "public_network_access_enabled": True,
                
                # Encryption
                "infrastructure_encryption_enabled": False,
                
                # Identity
                "identity": None,
                
                # Blob properties
                "blob_properties": None,
                
                # Static website
                "static_website": None,
                
                # For resource naming
                "name_sanitized": account.name.replace('-', '_').lower(),
                
                # State
                "provisioning_state": account_details.provisioning_state.value if account_details.provisioning_state else None,
                
                # Primary endpoints
                "primary_endpoints": {
                    "blob": account_details.primary_endpoints.blob if account_details.primary_endpoints else None,
                    "file": account_details.primary_endpoints.file if account_details.primary_endpoints else None,
                    "queue": account_details.primary_endpoints.queue if account_details.primary_endpoints else None,
                    "table": account_details.primary_endpoints.table if account_details.primary_endpoints else None,
                    "web": account_details.primary_endpoints.web if account_details.primary_endpoints else None,
                }
            }
            
            # Extract network rules
            if hasattr(account_details, 'network_rule_set') and account_details.network_rule_set:
                network_rules = account_details.network_rule_set
                account_data["network_rules"] = {
                    "default_action": network_rules.default_action.value if network_rules.default_action else "Allow",
                    "bypass": list(network_rules.bypass) if network_rules.bypass else ["AzureServices"],
                    "ip_rules": [rule.ip_address_or_range for rule in network_rules.ip_rules] if network_rules.ip_rules else [],
                    "virtual_network_subnet_ids": [rule.virtual_network_resource_id for rule in network_rules.virtual_network_rules] if network_rules.virtual_network_rules else [],
                }
                
                # Check if public network access is disabled
                if network_rules.default_action and network_rules.default_action.value == "Deny":
                    account_data["public_network_access_enabled"] = False
            
            # Extract identity information
            if hasattr(account_details, 'identity') and account_details.identity:
                account_data["identity"] = {
                    "type": account_details.identity.type.value if account_details.identity.type else "None",
                    "principal_id": account_details.identity.principal_id,
                    "tenant_id": account_details.identity.tenant_id,
                }
                
                if hasattr(account_details.identity, 'user_assigned_identities') and account_details.identity.user_assigned_identities:
                    account_data["identity"]["identity_ids"] = list(account_details.identity.user_assigned_identities.keys())
            
            # Extract blob properties
            if hasattr(account_details, 'blob_properties') and account_details.blob_properties:
                blob_props = account_details.blob_properties
                account_data["blob_properties"] = {
                    "versioning_enabled": blob_props.is_versioning_enabled if hasattr(blob_props, 'is_versioning_enabled') else False,
                    "change_feed_enabled": blob_props.change_feed.enabled if hasattr(blob_props, 'change_feed') and blob_props.change_feed else False,
                    "last_access_time_enabled": blob_props.last_access_time_tracking_policy.enable if hasattr(blob_props, 'last_access_time_tracking_policy') and blob_props.last_access_time_tracking_policy else False,
                    "delete_retention_policy": {
                        "days": blob_props.delete_retention_policy.days if hasattr(blob_props, 'delete_retention_policy') and blob_props.delete_retention_policy and blob_props.delete_retention_policy.enabled else 0
                    },
                    "container_delete_retention_policy": {
                        "days": blob_props.container_delete_retention_policy.days if hasattr(blob_props, 'container_delete_retention_policy') and blob_props.container_delete_retention_policy and blob_props.container_delete_retention_policy.enabled else 0
                    }
                }
            
            # Check for static website
            if hasattr(account_details, 'static_website') and account_details.static_website and account_details.static_website.enabled:
                account_data["static_website"] = {
                    "index_document": account_details.static_website.index_document,
                    "error_404_document": account_details.static_website.error_404_document,
                }
            
            # Check infrastructure encryption
            if hasattr(account_details, 'encryption') and account_details.encryption:
                if hasattr(account_details.encryption, 'require_infrastructure_encryption'):
                    account_data["infrastructure_encryption_enabled"] = account_details.encryption.require_infrastructure_encryption
            
            storage_accounts.append(account_data)
            
    except AzureError as e:
        typer.echo(f"Error fetching storage accounts: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return storage_accounts

@app.command("scan")
def scan_storage_accounts(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan all dependencies.")
):
    """Scans Azure Storage Accounts and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning Azure Storage Accounts with dependencies...")
        recursive_scan(
            "azure_storage_account",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location
        )
    else:
        typer.echo(f"Scanning for Azure Storage Accounts in subscription '{subscription_id}'...")
        if resource_group_name:
            typer.echo(f"Filtering by resource group: {resource_group_name}")
        if location:
            typer.echo(f"Filtering by location: {location}")
        
        account_data = get_storage_account_data(subscription_id, resource_group_name, location)
        
        if not account_data:
            typer.echo("No storage accounts found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "azure_storage_account.tf"
        generate_tf(account_data, "azure_storage_account", output_file, provider="azure")
        typer.echo(f"Generated Terraform for {len(account_data)} storage accounts -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "azure_storage_account",
            account_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_storage_accounts(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import file")
):
    """List all Azure Storage Account resources previously generated."""
    ImportManager(output_dir, "azure_storage_account").list_all()

@app.command("import")
def import_storage_account(
    account_id: str = typer.Argument(..., help="Azure Storage Account resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory with import file")
):
    """Run terraform import for a specific Azure Storage Account by its resource ID."""
    ImportManager(output_dir, "azure_storage_account").find_and_import(account_id)

# Scan function for cross-scan registry
def scan_azure_storage_accounts(
    output_dir: Path,
    subscription_id: str = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None
):
    """Scan function to be registered with cross-scan registry."""
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
    
    typer.echo(f"[Cross-scan] Scanning Azure Storage Accounts in subscription {subscription_id}")
    
    account_data = get_storage_account_data(subscription_id, resource_group_name, location)
    
    if account_data:
        output_file = output_dir / "azure_storage_account.tf"
        generate_tf(account_data, "azure_storage_account", output_file, provider="azure")
        generate_imports_file(
            "azure_storage_account",
            account_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(account_data)} Azure Storage Accounts")