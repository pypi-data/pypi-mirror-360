import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="compute",
    help="Work with GCP Compute Engine resources.",
    no_args_is_help=True,
)

def register():
    """Register compute scan functions with cross-scan registry."""
    from terraback.utils.cross_scan_registry import register_scan_function

    from .instances import scan_gcp_instances
    from .disks import scan_gcp_disks

    register_scan_function("gcp_instance", scan_gcp_instances)
    register_scan_function("gcp_disk", scan_gcp_disks)
    # (No inter-service dependencies here: that's handled in gcp/__init__.py)

# Add sub-commands (do not import at top-level to avoid circular imports)
@app.command("instance")
def instance_cmd():
    """Work with GCP instances."""
    from . import instances
    return instances.app

@app.command("disk")
def disk_cmd():
    """Work with GCP disks."""
    from . import disks
    return disks.app

@app.command("scan-all")
def scan_all_compute(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", envvar="GOOGLE_CLOUD_PROJECT"),
    zone: Optional[str] = typer.Option(None, "--zone", "-z"),
    with_deps: bool = typer.Option(False, "--with-deps"),
):
    """
    Scan all compute resources (instances, disks) for this project.
    """
    from terraback.cli.gcp.session import get_default_project_id

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
            raise typer.Exit(code=1)

    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan("gcp_instance", output_dir=output_dir, project_id=project_id, zone=zone)
    else:
        from .instances import scan_gcp_instances
        from .disks import scan_gcp_disks

        scan_gcp_instances(output_dir=output_dir, project_id=project_id, zone=zone, with_deps=False)
        scan_gcp_disks(output_dir=output_dir, project_id=project_id, zone=zone, with_deps=False)
