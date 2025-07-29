from terraback.core.license import require_professional
import typer
from pathlib import Path

from .queues import scan_queues, list_queues, import_queue
from .dead_letter_queues import scan_dlq, list_dlq, import_dlq

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="sqs",
    help="Manage SQS (Simple Queue Service) resources.",
    no_args_is_help=True
)

# --- SQS Commands ---
@app.command(name="scan-queues", help="Scan SQS queues.")
@require_professional
def scan_queues_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    include_dlq: bool = typer.Option(True, help="Include Dead Letter Queues")
):
    scan_queues(output_dir, profile, region, include_dlq)

@app.command(name="list-queues", help="List scanned SQS queues.")
@require_professional
def list_queues_command(output_dir: Path = typer.Option("generated")):
    list_queues(output_dir)

@app.command(name="import-queue", help="Import an SQS queue by URL.")
@require_professional
def import_queue_command(
    queue_url: str,
    output_dir: Path = typer.Option("generated")
):
    import_queue(queue_url, output_dir)

# --- DLQ Commands ---
@app.command(name="scan-dlq", help="Scan SQS dead letter queue relationships.")
@require_professional
def scan_dlq_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_dlq(output_dir, profile, region)

@app.command(name="list-dlq", help="List scanned DLQ relationships.")
@require_professional
def list_dlq_command(output_dir: Path = typer.Option("generated")):
    list_dlq(output_dir)

@app.command(name="import-dlq", help="Import a DLQ relationship.")
@require_professional
def import_dlq_command(
    relationship_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_dlq(relationship_id, output_dir)

# --- Combined Commands ---
@app.command(name="scan-all", help="Scan all SQS resources.")
@require_professional
def scan_all_sqs_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_queues(output_dir, profile, region, include_dlq=True)
    scan_dlq(output_dir, profile, region)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the SQS module."""
    register_scan_function("sqs_queue", scan_queues)
    register_scan_function("sqs_dlq_relationship", scan_dlq)

    # Define dependencies
    # Lambda functions often use SQS as event sources
    cross_scan_registry.register_dependency("lambda_function", "sqs_queue")
    # SNS topics can send messages to SQS queues
    cross_scan_registry.register_dependency("sns_topic", "sqs_queue")