import typer
from pathlib import Path
from typing import Optional

from . import topics, subscriptions

app = typer.Typer(
    name="pubsub",
    help="Work with GCP Pub/Sub resources.",
    no_args_is_help=True,
)

def register():
    """Register Pub/Sub scan functions with cross-scan registry."""
    from terraback.utils.cross_scan_registry import register_scan_function

    from .topics import scan_gcp_pubsub_topics
    from .subscriptions import scan_gcp_pubsub_subscriptions

    register_scan_function("gcp_pubsub_topic", scan_gcp_pubsub_topics)
    register_scan_function("gcp_pubsub_subscription", scan_gcp_pubsub_subscriptions)

# Add sub-commands
app.add_typer(topics.app, name="topic")
app.add_typer(subscriptions.app, name="subscription")

@app.command("scan-all")
def scan_all_pubsub(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", envvar="GOOGLE_CLOUD_PROJECT"),
    with_deps: bool = typer.Option(False, "--with-deps"),
):
    """Scan all GCP Pub/Sub resources."""
    from terraback.cli.gcp.session import get_default_project_id

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
            raise typer.Exit(code=1)

    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan("gcp_pubsub_topic", output_dir=output_dir, project_id=project_id)
    else:
        from .topics import scan_gcp_pubsub_topics
        from .subscriptions import scan_gcp_pubsub_subscriptions

        scan_gcp_pubsub_topics(output_dir=output_dir, project_id=project_id, with_deps=False)
        scan_gcp_pubsub_subscriptions(output_dir=output_dir, project_id=project_id, with_deps=False)
