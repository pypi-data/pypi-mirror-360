import typer
from pathlib import Path
from typing import Optional

from . import backend_services, url_maps, target_proxies, forwarding_rules

app = typer.Typer(
    name="loadbalancer",
    help="Work with GCP Load Balancer resources.",
    no_args_is_help=True,
)

def register():
    """Register load balancer scan functions with cross-scan registry."""
    from terraback.utils.cross_scan_registry import register_scan_function

    from .backend_services import scan_gcp_backend_services
    from .url_maps import scan_gcp_url_maps
    from .target_proxies import scan_gcp_target_proxies
    from .forwarding_rules import scan_gcp_forwarding_rules

    register_scan_function("gcp_backend_service", scan_gcp_backend_services)
    register_scan_function("gcp_url_map", scan_gcp_url_maps)
    register_scan_function("gcp_target_https_proxy", scan_gcp_target_proxies)
    register_scan_function("gcp_global_forwarding_rule", scan_gcp_forwarding_rules)

# Add sub-commands
app.add_typer(backend_services.app, name="backend-service")
app.add_typer(url_maps.app, name="url-map")
app.add_typer(target_proxies.app, name="target-proxy")
app.add_typer(forwarding_rules.app, name="forwarding-rule")

@app.command("scan-all")
def scan_all_loadbalancer(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", envvar="GOOGLE_CLOUD_PROJECT"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    with_deps: bool = typer.Option(False, "--with-deps"),
):
    """Scan all GCP load balancer resources."""
    from terraback.cli.gcp.session import get_default_project_id

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
            raise typer.Exit(code=1)

    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan("gcp_backend_service", output_dir=output_dir, project_id=project_id, region=region)
    else:
        from .backend_services import scan_gcp_backend_services
        from .url_maps import scan_gcp_url_maps
        from .target_proxies import scan_gcp_target_proxies
        from .forwarding_rules import scan_gcp_forwarding_rules

        scan_gcp_backend_services(output_dir=output_dir, project_id=project_id, region=region, with_deps=False)
        scan_gcp_url_maps(output_dir=output_dir, project_id=project_id, with_deps=False)
        scan_gcp_target_proxies(output_dir=output_dir, project_id=project_id, with_deps=False)
        scan_gcp_forwarding_rules(output_dir=output_dir, project_id=project_id, region=region, with_deps=False)
