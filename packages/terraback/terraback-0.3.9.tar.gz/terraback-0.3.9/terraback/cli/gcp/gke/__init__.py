import typer
from pathlib import Path
from typing import Optional

from . import clusters, node_pools

app = typer.Typer(
    name="gke",
    help="Work with Google Kubernetes Engine resources.",
    no_args_is_help=True,
)

def register():
    """Register GKE scan functions with cross-scan registry."""
    from terraback.utils.cross_scan_registry import register_scan_function

    from .clusters import scan_gcp_gke_clusters
    from .node_pools import scan_gcp_gke_node_pools

    register_scan_function("gcp_gke_cluster", scan_gcp_gke_clusters)
    register_scan_function("gcp_gke_node_pool", scan_gcp_gke_node_pools)

# Add sub-commands
app.add_typer(clusters.app, name="cluster")
app.add_typer(node_pools.app, name="node-pool")

@app.command("scan-all")
def scan_all_gke(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", envvar="GOOGLE_CLOUD_PROJECT"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    zone: Optional[str] = typer.Option(None, "--zone", "-z"),
    with_deps: bool = typer.Option(False, "--with-deps"),
):
    """Scan all GKE resources."""
    from terraback.cli.gcp.session import get_default_project_id

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
            raise typer.Exit(code=1)

    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan("gcp_gke_cluster", output_dir=output_dir, project_id=project_id, region=region, zone=zone)
    else:
        from .clusters import scan_gcp_gke_clusters
        from .node_pools import scan_gcp_gke_node_pools

        scan_gcp_gke_clusters(output_dir=output_dir, project_id=project_id, region=region, zone=zone, with_deps=False)
        scan_gcp_gke_node_pools(output_dir=output_dir, project_id=project_id, region=region, zone=zone, with_deps=False)
