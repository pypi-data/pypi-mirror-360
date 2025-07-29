# terraback/cli/azure/compute/virtual_machines.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import AzureError

from terraback.cli.azure.session import get_cached_azure_session, get_default_subscription_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="vm", help="Scan and import Azure Virtual Machines.")

def enhance_vm_data(vm_data: Dict[str, Any], vm_details: Any) -> Dict[str, Any]:
    """
    Enhance VM data with OS type detection and SSH key information.
    
    Args:
        vm_data: The basic VM data dictionary
        vm_details: The detailed VM object from Azure API
    
    Returns:
        Enhanced VM data dictionary
    """
    # Detect OS type from various sources
    os_type = None
    
    # Method 1: Check storage profile OS disk
    if hasattr(vm_details, 'storage_profile') and vm_details.storage_profile:
        if hasattr(vm_details.storage_profile, 'os_disk') and vm_details.storage_profile.os_disk:
            if hasattr(vm_details.storage_profile.os_disk, 'os_type'):
                os_type = vm_details.storage_profile.os_disk.os_type
    
    # Method 2: Check image reference for known Windows patterns
    if not os_type and vm_data.get('source_image_reference'):
        publisher = vm_data['source_image_reference'].get('publisher', '').lower()
        offer = vm_data['source_image_reference'].get('offer', '').lower()
        
        # Common Windows image patterns
        windows_patterns = [
            'microsoftwindows', 'windowsserver', 'windows-',
            'win-', 'windows_', 'microsoftsqlserver'
        ]
        
        for pattern in windows_patterns:
            if pattern in publisher or pattern in offer:
                os_type = 'Windows'
                break
        
        # If not Windows, assume Linux
        if not os_type:
            os_type = 'Linux'
    
    # Method 3: Check OS profile for Windows-specific settings
    if not os_type and hasattr(vm_details, 'os_profile') and vm_details.os_profile:
        if hasattr(vm_details.os_profile, 'windows_configuration'):
            os_type = 'Windows'
        elif hasattr(vm_details.os_profile, 'linux_configuration'):
            os_type = 'Linux'
    
    vm_data['os_type'] = os_type or 'Linux'  # Default to Linux if unable to detect
    
    # Extract SSH keys for Linux VMs
    if vm_data['os_type'] == 'Linux':
        ssh_keys = []
        if hasattr(vm_details, 'os_profile') and vm_details.os_profile:
            if hasattr(vm_details.os_profile, 'linux_configuration') and vm_details.os_profile.linux_configuration:
                linux_config = vm_details.os_profile.linux_configuration
                if hasattr(linux_config, 'ssh') and linux_config.ssh:
                    if hasattr(linux_config.ssh, 'public_keys') and linux_config.ssh.public_keys:
                        for key in linux_config.ssh.public_keys:
                            ssh_keys.append({
                                'username': vm_data['admin_username'],
                                'path': key.path if hasattr(key, 'path') else None,
                                'public_key': key.key_data if hasattr(key, 'key_data') else None
                            })
        
        if ssh_keys:
            vm_data['admin_ssh_keys'] = ssh_keys
    
    # Extract Windows-specific settings
    elif vm_data['os_type'] == 'Windows':
        if hasattr(vm_details, 'os_profile') and vm_details.os_profile:
            if hasattr(vm_details.os_profile, 'windows_configuration') and vm_details.os_profile.windows_configuration:
                win_config = vm_details.os_profile.windows_configuration
                
                vm_data['enable_automatic_updates'] = win_config.enable_automatic_updates if hasattr(win_config, 'enable_automatic_updates') else None
                vm_data['timezone'] = win_config.time_zone if hasattr(win_config, 'time_zone') else None
                vm_data['provision_vm_agent'] = win_config.provision_vm_agent if hasattr(win_config, 'provision_vm_agent') else None
                
                # WinRM listeners
                if hasattr(win_config, 'winrm') and win_config.winrm:
                    if hasattr(win_config.winrm, 'listeners') and win_config.winrm.listeners:
                        vm_data['winrm_listeners'] = []
                        for listener in win_config.winrm.listeners:
                            vm_data['winrm_listeners'].append({
                                'protocol': listener.protocol if hasattr(listener, 'protocol') else None,
                                'certificate_url': listener.certificate_url if hasattr(listener, 'certificate_url') else None
                            })
    
    # Extract identity information
    if hasattr(vm_details, 'identity') and vm_details.identity:
        vm_data['identity'] = {
            'type': vm_details.identity.type,
            'principal_id': vm_details.identity.principal_id if hasattr(vm_details.identity, 'principal_id') else None,
            'tenant_id': vm_details.identity.tenant_id if hasattr(vm_details.identity, 'tenant_id') else None,
        }
        
        if hasattr(vm_details.identity, 'user_assigned_identities'):
            vm_data['identity']['identity_ids'] = list(vm_details.identity.user_assigned_identities.keys())
    
    # Extract custom data if present (base64 encoded)
    if hasattr(vm_details, 'os_profile') and vm_details.os_profile:
        if hasattr(vm_details.os_profile, 'custom_data'):
            vm_data['custom_data'] = vm_details.os_profile.custom_data
    
    return vm_data

def get_vm_data(subscription_id: str = None, resource_group_name: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch Virtual Machine data from Azure.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        resource_group_name: Optional resource group filter
        location: Optional location filter
    
    Returns:
        List of VM data dictionaries
    """
    session = get_cached_azure_session(subscription_id)
    compute_client = ComputeManagementClient(**session)
    network_client = NetworkManagementClient(**session)
    
    vms = []
    
    try:
        # Get VMs either from specific resource group or all
        if resource_group_name:
            vm_list = compute_client.virtual_machines.list(resource_group_name)
        else:
            vm_list = compute_client.virtual_machines.list_all()
        
        for vm in vm_list:
            # Apply location filter if specified
            if location and vm.location != location:
                continue
                
            # Parse resource group from ID
            rg_name = vm.id.split('/')[4] if not resource_group_name else resource_group_name
            
            # Get VM details with instance view for status
            vm_details = compute_client.virtual_machines.get(
                resource_group_name=rg_name,
                vm_name=vm.name,
                expand='instanceView'
            )
            
            # Extract network interface IDs
            network_interface_ids = []
            if vm_details.network_profile and vm_details.network_profile.network_interfaces:
                network_interface_ids = [nic.id for nic in vm_details.network_profile.network_interfaces]
            
            # Build VM data structure matching Terraform schema
            vm_data = {
                "name": vm.name,
                "id": vm.id,
                "resource_group_name": rg_name,
                "location": vm.location,
                "size": vm.hardware_profile.vm_size if vm.hardware_profile else None,
                "tags": vm.tags or {},
                
                # Admin credentials
                "admin_username": vm.os_profile.admin_username if vm.os_profile else None,
                
                # Network
                "network_interface_ids": network_interface_ids,
                
                # Availability
                "availability_set_id": vm.availability_set.id if vm.availability_set else None,
                "zone": vm.zones[0] if vm.zones else None,
                
                # OS Disk
                "os_disk": {
                    "caching": vm.storage_profile.os_disk.caching if vm.storage_profile and vm.storage_profile.os_disk else None,
                    "storage_account_type": vm.storage_profile.os_disk.managed_disk.storage_account_type if vm.storage_profile and vm.storage_profile.os_disk and vm.storage_profile.os_disk.managed_disk else None,
                    "disk_size_gb": vm.storage_profile.os_disk.disk_size_gb if vm.storage_profile and vm.storage_profile.os_disk else None,
                    "name": vm.storage_profile.os_disk.name if vm.storage_profile and vm.storage_profile.os_disk else None,
                },
                
                # Source image
                "source_image_reference": None,
                "source_image_id": None,
                
                # Data disks
                "data_disks": [],
                
                # Boot diagnostics
                "boot_diagnostics": None,
                
                # Additional properties
                "computer_name": vm.os_profile.computer_name if vm.os_profile else None,
                "license_type": vm.license_type,
                "priority": vm.priority,
                "eviction_policy": vm.eviction_policy,
                
                # State from instance view
                "power_state": "unknown",
                
                # For resource naming
                "name_sanitized": vm.name.replace('-', '_').lower()
            }
            
            # Extract source image information
            if vm.storage_profile and vm.storage_profile.image_reference:
                if vm.storage_profile.image_reference.id:
                    vm_data["source_image_id"] = vm.storage_profile.image_reference.id
                else:
                    vm_data["source_image_reference"] = {
                        "publisher": vm.storage_profile.image_reference.publisher,
                        "offer": vm.storage_profile.image_reference.offer,
                        "sku": vm.storage_profile.image_reference.sku,
                        "version": vm.storage_profile.image_reference.version,
                    }
            
            # Extract data disks
            if vm.storage_profile and vm.storage_profile.data_disks:
                for disk in vm.storage_profile.data_disks:
                    vm_data["data_disks"].append({
                        "lun": disk.lun,
                        "name": disk.name,
                        "caching": disk.caching,
                        "storage_account_type": disk.managed_disk.storage_account_type if disk.managed_disk else None,
                        "disk_size_gb": disk.disk_size_gb,
                        "create_option": disk.create_option,
                    })
            
            # Extract boot diagnostics
            if vm.diagnostics_profile and vm.diagnostics_profile.boot_diagnostics:
                boot_diag = vm.diagnostics_profile.boot_diagnostics
                vm_data["boot_diagnostics"] = {
                    "enabled": boot_diag.enabled,
                    "storage_account_uri": boot_diag.storage_uri,
                }
            
            # Extract power state from instance view
            if hasattr(vm_details, 'instance_view') and vm_details.instance_view:
                for status in vm_details.instance_view.statuses:
                    if status.code.startswith('PowerState/'):
                        vm_data["power_state"] = status.code.split('/')[-1]
                        break
            
            # Enhance VM data with OS detection and additional properties
            vm_data = enhance_vm_data(vm_data, vm_details)
            
            vms.append(vm_data)
            
    except AzureError as e:
        typer.echo(f"Error fetching VMs: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return vms

@app.command("scan")
def scan_vms(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID.", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location.", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group."),
    include_all_states: bool = typer.Option(False, "--include-all-states", help="Include VMs in all power states (not just running)."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan all dependencies (VNet, Disks, NSGs, NICs).")
):
    """Scans Azure Virtual Machines and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning Azure VMs with dependencies...")
        recursive_scan(
            "azure_virtual_machine",
            output_dir=output_dir,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            location=location,
            include_all_states=include_all_states
        )
    else:
        typer.echo(f"Scanning for Azure VMs in subscription '{subscription_id}'...")
        if resource_group_name:
            typer.echo(f"Filtering by resource group: {resource_group_name}")
        if location:
            typer.echo(f"Filtering by location: {location}")
        
        vm_data = get_vm_data(subscription_id, resource_group_name, location)
        
        if not vm_data:
            typer.echo("No VMs found.")
            return
        
        # Filter by power state if needed
        if not include_all_states:
            vm_data = [vm for vm in vm_data if vm.get("power_state", "").lower() in ["running", "starting"]]
            typer.echo(f"Filtered to {len(vm_data)} running VMs.")
        
        # Generate Terraform files
        output_file = output_dir / "azure_virtual_machine.tf"
        generate_tf(vm_data, "azure_virtual_machine", output_file, provider="azure")
        typer.echo(f"Generated Terraform for {len(vm_data)} VMs -> {output_file}")
        
        # Check if SSH keys are missing and notify
        linux_vms_without_keys = [vm for vm in vm_data if vm.get('os_type') == 'Linux' and not vm.get('admin_ssh_keys')]
        if linux_vms_without_keys:
            typer.echo("\n⚠️  Warning: The following Linux VMs don't have SSH keys configured in Azure:")
            for vm in linux_vms_without_keys:
                typer.echo(f"   - {vm['name']}")
            typer.echo("   You'll need to update the SSH key path in the generated Terraform file.\n")
        
        # Check for Windows VMs and notify about passwords
        windows_vms = [vm for vm in vm_data if vm.get('os_type') == 'Windows']
        if windows_vms:
            typer.echo("\n⚠️  Warning: The following Windows VMs need password configuration:")
            for vm in windows_vms:
                typer.echo(f"   - {vm['name']}")
            typer.echo("   Update the admin_password in the generated Terraform file.\n")
        
        # Generate import file
        generate_imports_file(
            "azure_virtual_machine",
            vm_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_vms(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import file")
):
    """List all Azure VM resources previously generated."""
    ImportManager(output_dir, "azure_virtual_machine").list_all()

@app.command("import")
def import_vm(
    vm_id: str = typer.Argument(..., help="Azure VM resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory with import file")
):
    """Run terraform import for a specific Azure VM by its resource ID."""
    ImportManager(output_dir, "azure_virtual_machine").find_and_import(vm_id)

# Scan function for cross-scan registry
def scan_azure_vms(
    output_dir: Path,
    subscription_id: str = None,
    resource_group_name: Optional[str] = None,
    location: Optional[str] = None,
    include_all_states: bool = False
):
    """Scan function to be registered with cross-scan registry."""
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
    
    typer.echo(f"[Cross-scan] Scanning Azure VMs in subscription {subscription_id}")
    
    vm_data = get_vm_data(subscription_id, resource_group_name, location)
    
    if not include_all_states:
        vm_data = [vm for vm in vm_data if vm.get("power_state", "").lower() in ["running", "starting"]]
    
    if vm_data:
        output_file = output_dir / "azure_virtual_machine.tf"
        generate_tf(vm_data, "azure_virtual_machine", output_file, provider="azure")
        
        generate_imports_file(
            "azure_virtual_machine",
            vm_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(vm_data)} Azure VMs")