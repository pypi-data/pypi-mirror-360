import typer
from pathlib import Path
from typing import Optional

from . import buckets

app = typer.Typer(
    name="storage",
    help="Work with GCP Storage resources.",
    no_args_is_help=True,
)

def register():
    """Register storage scan functions with cross-scan registry."""
    from terraback.utils.cross_scan_registry import register_scan_function
    from .buckets import scan_gcp_buckets

    register_scan_function("gcp_bucket", scan_gcp_buckets)
    # If you add more storage resource types later, register them here

# Add sub-commands
app.add_typer(buckets.app, name="bucket")

@app.command("scan-all")
def scan_all_storage(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", envvar="GOOGLE_CLOUD_PROJECT"),
    with_deps: bool = typer.Option(False, "--with-deps"),
):
    """Scan all GCP storage resources."""
    from terraback.cli.gcp.session import get_default_project_id

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
            raise typer.Exit(code=1)

    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan("gcp_bucket", output_dir=output_dir, project_id=project_id)
    else:
        from .buckets import scan_gcp_buckets
        scan_gcp_buckets(output_dir=output_dir, project_id=project_id, with_deps=False)
