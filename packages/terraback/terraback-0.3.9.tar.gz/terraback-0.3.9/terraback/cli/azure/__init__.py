import typer
from pathlib import Path
from typing import Optional

# --- App Definition ---
app = typer.Typer(
    name="azure",
    help="Work with Microsoft Azure resources.",
    no_args_is_help=True,
)

# --- Service Module Imports ---
from . import compute, network, storage, loadbalancer, resources

# --- Module and Dependency Definitions ---
SERVICE_MODULES = [
    ("Compute", compute),
    ("Network", network),
    ("Storage", storage),
    ("Load Balancer", loadbalancer),
    ("Resources", resources),
]

PROFESSIONAL_DEPENDENCIES = [
    ("azure_virtual_machine", "azure_resource_group"),
    ("azure_virtual_machine", "azure_virtual_network"),
    ("azure_virtual_machine", "azure_network_interface"),
    ("azure_network_interface", "azure_subnet"),
    ("azure_network_interface", "azure_resource_group"),
    ("azure_subnet", "azure_virtual_network"),
    ("azure_lb", "azure_resource_group"),
    ("azure_storage_account", "azure_resource_group"),
]

# --- Registration Logic ---
_registered = False

def register():
    """
    Register all Azure resources and dependencies with the central cross-scan registry.
    """
    global _registered
    if _registered:
        return
    _registered = True

    from terraback.core.license import check_feature_access, Tier
    from terraback.utils.cross_scan_registry import cross_scan_registry

    with cross_scan_registry.autosave_mode(False):
        for service_name, module in SERVICE_MODULES:
            try:
                if hasattr(module, "register"):
                    module.register()
            except Exception as e:
                typer.echo(f"Warning: Failed to register {service_name}: {e}", err=True)

        if check_feature_access(Tier.PROFESSIONAL):
            for source, target in PROFESSIONAL_DEPENDENCIES:
                cross_scan_registry.register_dependency(source, target)

        cross_scan_registry.flush()

# --- CLI Command Definitions ---

# Add each service's Typer app as a subcommand.
app.add_typer(compute.app, name="compute", help="VMs, disks, and compute resources")
app.add_typer(network.app, name="network", help="VNets, subnets, and network interfaces")
app.add_typer(storage.app, name="storage", help="Storage accounts and related resources")
app.add_typer(loadbalancer.app, name="lb", help="Load balancers")
app.add_typer(resources.app, name="resources", help="Resource groups")

@app.command("scan-all")
def scan_all_azure(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files"),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies (Professional feature)"),
    parallel: int = typer.Option(1, "--parallel", help="Number of parallel workers (Professional feature)"),
    check: bool = typer.Option(True, "--check/--skip-check", help="Validate Terraform after scan"),
):
    """Scan all available Azure resources based on your license tier."""
    register()

    from terraback.cli.azure.session import get_default_subscription_id
    from terraback.core.license import check_feature_access, Tier
    # Import the new function here
    from terraback.utils.cross_scan_registry import cross_scan_registry, recursive_scan, get_all_scan_functions
    from terraback.utils.parallel_scan import ParallelScanManager, create_scan_tasks

    # 1. Authenticate with Azure
    if not subscription_id:
        subscription_id = get_default_subscription_id()
    if not subscription_id:
        typer.echo("Error: No Azure subscription found. Run 'az login' or set AZURE_SUBSCRIPTION_ID.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Scanning Azure resources in subscription '{subscription_id}'...")
    if location:
        typer.echo(f"Filtering by location: {location}")
    if resource_group_name:
        typer.echo(f"Filtering by resource group: {resource_group_name}")

    # 2. Handle Dependency Scanning (--with-deps)
    if with_deps:
        if check_feature_access(Tier.PROFESSIONAL):
            typer.echo("\nScanning with dependency resolution...")
            recursive_scan("azure_resource_group", output_dir=output_dir, subscription_id=subscription_id, location=location, resource_group_name=resource_group_name)
            typer.echo("\nScan complete!")
            return
        else:
            typer.echo("\nDependency scanning (--with-deps) requires a Professional license.")
            typer.echo("Falling back to standard scan. To upgrade: terraback license activate <key>\n")

    # 3. Perform Standard Scan

    all_scans = get_all_scan_functions() 
    scan_configs = []
    skipped_configs = []

    for name, details in all_scans.items():
        if "azure" in name and check_feature_access(details.get("tier", Tier.COMMUNITY)):
            scan_configs.append({'name': name, 'function': details['function']})
        elif "azure" in name:
            skipped_configs.append(name)
    
    if skipped_configs:
        typer.echo(f"\nCommunity Edition: Skipping {len(skipped_configs)} Professional resources.")

    base_kwargs = {
        'output_dir': output_dir, 'subscription_id': subscription_id,
        'location': location, 'resource_group_name': resource_group_name
    }
    tasks = create_scan_tasks(scan_configs, base_kwargs)

    # 4. Execute Scans
    use_parallel = parallel > 1 and check_feature_access(Tier.PROFESSIONAL)

    if use_parallel:
        typer.echo(f"\nScanning {len(tasks)} resource types in parallel with {parallel} workers...")
        manager = ParallelScanManager(max_workers=parallel)
        manager.scan_parallel(tasks)
    else:
        if parallel > 1:
            typer.echo("\nParallel scanning requires a Professional license. Using sequential scan.")
        typer.echo(f"\nScanning {len(tasks)} resource types sequentially...")
        for task in tasks:
            typer.echo(f"--- Scanning {task.name} ---")
            task.function(**task.kwargs)

    typer.echo("\nScan complete!")
    typer.echo(f"Results saved to: {output_dir}/")

    if check:
        from terraback.utils.terraform_checker import check_and_fix_terraform_files
        check_and_fix_terraform_files(output_dir)


@app.command("list-resources")
def list_azure_resources(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import files")
):
    """List all Azure resources previously scanned."""
    from terraback.utils.importer import ImportManager
    resource_types = [
        "azure_resource_group", "azure_virtual_machine", "azure_managed_disk",
        "azure_virtual_network", "azure_subnet", "azure_network_security_group",
        "azure_network_interface", "azure_storage_account", "azure_lb",
    ]
    for resource_type in resource_types:
        import_file = output_dir / f"{resource_type}_import.json"
        if import_file.exists():
            typer.echo(f"\n=== {resource_type} ===")
            ImportManager(output_dir, resource_type).list_all()

@app.command("clean")
def clean_azure_files(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory to clean"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clean all Azure-related generated files."""
    from terraback.utils.cleanup import clean_generated_files
    if not yes:
        confirm = typer.confirm(f"This will delete all Azure .tf and _import.json files in {output_dir}. Continue?")
        if not confirm:
            raise typer.Abort()
    azure_prefixes = [
        "azure_resource_group", "azure_virtual_machine", "azure_managed_disk",
        "azure_virtual_network", "azure_subnet", "azure_network_security_group",
        "azure_network_interface", "azure_storage_account", "azure_lb",
    ]
    for prefix in azure_prefixes:
        clean_generated_files(output_dir, prefix)
    typer.echo("Azure generated files cleaned successfully!")
