import typer
from pathlib import Path
from typing import Optional

from . import secrets

app = typer.Typer(
    name="secrets",
    help="Work with GCP Secret Manager resources.",
    no_args_is_help=True,
)

def register():
    """Register Secret Manager scan functions with cross-scan registry."""
    from terraback.utils.cross_scan_registry import register_scan_function

    from .secrets import scan_gcp_secrets

    register_scan_function("gcp_secret", scan_gcp_secrets)

# Add sub-command
app.add_typer(secrets.app, name="secret")

@app.command("scan-all")
def scan_all_secrets(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", envvar="GOOGLE_CLOUD_PROJECT"),
    with_deps: bool = typer.Option(False, "--with-deps"),
):
    """Scan all GCP Secret Manager resources."""
    from terraback.cli.gcp.session import get_default_project_id

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
            raise typer.Exit(code=1)

    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan("gcp_secret", output_dir=output_dir, project_id=project_id)
    else:
        from .secrets import scan_gcp_secrets
        scan_gcp_secrets(output_dir=output_dir, project_id=project_id, with_deps=False)
