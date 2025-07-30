import typer
from pathlib import Path
from typing import Optional

# --- App Definition ---
app = typer.Typer(
    name="gcp",
    help="Work with Google Cloud Platform resources.",
    no_args_is_help=True,
)

# --- Service Module Imports ---
# Each of these should have their own Typer app and a `register()` function.
from . import compute, network, storage, loadbalancer, sql, pubsub, secrets, gke

# --- Module and Dependency Definitions ---
SERVICE_MODULES = [
    ("Compute", compute),
    ("Network", network),
    ("Storage", storage),
    ("Load Balancer", loadbalancer),
    ("SQL", sql),
    ("PubSub", pubsub),
    ("Secrets", secrets),
    ("GKE", gke),
]

PROFESSIONAL_DEPENDENCIES = [
    ("gcp_instance", "gcp_network"),
    ("gcp_instance", "gcp_subnet"),
    ("gcp_instance", "gcp_disk"),
    ("gcp_instance", "gcp_firewall"),
    ("gcp_instance", "gcp_service_account"),
    ("gcp_disk", "gcp_snapshot"),
    ("gcp_disk", "gcp_image"),
    ("gcp_subnet", "gcp_network"),
    ("gcp_firewall", "gcp_network"),
    ("gcp_router", "gcp_network"),
    ("gcp_vpn_gateway", "gcp_network"),
    ("gcp_backend_service", "gcp_instance_group"),
    ("gcp_backend_service", "gcp_health_check"),
    ("gcp_url_map", "gcp_backend_service"),
    ("gcp_target_https_proxy", "gcp_url_map"),
    ("gcp_global_forwarding_rule", "gcp_target_https_proxy"),
    ("gcp_instance_group", "gcp_instance_template"),
    ("gcp_instance_template", "gcp_network"),
    ("gcp_instance_template", "gcp_subnet"),
    ("gcp_bucket", "gcp_bucket_iam_binding"),
]

# --- Registration Logic ---
_registered = False

def register():
    """
    Register all GCP resources and dependencies with the central cross-scan registry.
    This function is idempotent and will only run once.
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
for service_name_lower, module in [(name.lower().replace(" ", ""), mod) for name, mod in SERVICE_MODULES]:
    if hasattr(module, "app"):
        app.add_typer(module.app, name=service_name_lower, help=f"Work with {service_name_lower.upper()} resources.")

@app.command("scan-all")
def scan_all_gcp(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated files"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="GCP Project ID"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="GCP region"),
    zone: Optional[str] = typer.Option(None, "--zone", "-z", help="GCP zone"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies (Professional feature)"),
    parallel: int = typer.Option(1, "--parallel", help="Number of parallel workers (Professional feature)"),
    check: bool = typer.Option(True, "--check/--skip-check", help="Validate Terraform after scan"),
):
    """
    Scan all available GCP resources based on your license tier.
    """
    register()

    from terraback.core.license import check_feature_access, Tier
    from terraback.core.license import get_active_tier
    from terraback.utils.cross_scan_registry import cross_scan_registry, recursive_scan, get_all_scan_functions
    from terraback.utils.parallel_scan import ParallelScanManager, create_scan_tasks

    # Project ID resolution
    if not project_id:
        from terraback.cli.gcp.session import get_default_project_id
        project_id = get_default_project_id()
    if not project_id:
        typer.echo("Error: No GCP project found. Set GOOGLE_CLOUD_PROJECT or use --project-id", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Scanning GCP resources in project '{project_id}'...")
    if region:
        typer.echo(f"Region: {region}")
    if zone:
        typer.echo(f"Zone: {zone}")

    # 1. Handle Dependency Scanning (--with-deps)
    if with_deps:
        if check_feature_access(Tier.PROFESSIONAL):
            typer.echo("\nScanning with dependency resolution...")
            recursive_scan(
                "gcp_instance",  # or whatever root resource makes sense
                output_dir=output_dir,
                project_id=project_id,
                region=region,
                zone=zone,
            )
            typer.echo("\nScan complete!")
            return
        else:
            typer.echo("\nDependency scanning (--with-deps) requires a Professional license.")
            typer.echo("Falling back to standard scan. To upgrade: terraback license activate <key>\n")

    # 2. Standard Scan (no dependency recursion)
    all_scans = get_all_scan_functions()
    scan_configs = []
    skipped_configs = []

    tier = get_active_tier()

    for name, details in all_scans.items():
        # Only run GCP resources
        if "gcp" in name and check_feature_access(details.get("tier", Tier.COMMUNITY)):
            scan_configs.append({'name': name, 'function': details['function']})
        elif "gcp" in name:
            skipped_configs.append(name)

    if skipped_configs:
        typer.echo(f"\nCommunity Edition: Skipping {len(skipped_configs)} Professional resources.")

    base_kwargs = {
        'output_dir': output_dir, 'project_id': project_id,
        'region': region, 'zone': zone
    }
    tasks = create_scan_tasks(scan_configs, base_kwargs)

    # 3. Execute Scans (Parallel or Sequential)
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
