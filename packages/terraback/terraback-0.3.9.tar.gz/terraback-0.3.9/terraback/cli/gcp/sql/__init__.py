import typer
from pathlib import Path
from typing import Optional

from . import instances, databases

app = typer.Typer(
    name="sql",
    help="Work with GCP Cloud SQL resources.",
    no_args_is_help=True,
)

def register():
    """Register SQL scan functions with cross-scan registry."""
    from terraback.utils.cross_scan_registry import register_scan_function

    from .instances import scan_gcp_sql_instances
    from .databases import scan_gcp_sql_databases

    register_scan_function("gcp_sql_instance", scan_gcp_sql_instances)
    register_scan_function("gcp_sql_database", scan_gcp_sql_databases)

# Add sub-commands
app.add_typer(instances.app, name="instance")
app.add_typer(databases.app, name="database")

@app.command("scan-all")
def scan_all_sql(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", envvar="GOOGLE_CLOUD_PROJECT"),
    with_deps: bool = typer.Option(False, "--with-deps"),
):
    """Scan all GCP Cloud SQL resources."""
    from terraback.cli.gcp.session import get_default_project_id

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
            raise typer.Exit(code=1)

    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan("gcp_sql_instance", output_dir=output_dir, project_id=project_id)
    else:
        from .instances import scan_gcp_sql_instances
        from .databases import scan_gcp_sql_databases

        scan_gcp_sql_instances(output_dir=output_dir, project_id=project_id, with_deps=False)
        scan_gcp_sql_databases(output_dir=output_dir, project_id=project_id, with_deps=False)
