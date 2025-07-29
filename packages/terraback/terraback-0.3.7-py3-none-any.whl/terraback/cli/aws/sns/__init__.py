from terraback.core.license import require_professional
import typer
from pathlib import Path

from .topics import scan_topics, list_topics, import_topic
from .subscriptions import scan_subscriptions, list_subscriptions, import_subscription

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="sns",
    help="Manage SNS (Simple Notification Service) resources like topics and subscriptions.",
    no_args_is_help=True
)

# --- SNS Topic Commands ---
@app.command(name="scan-topics", help="Scan SNS topics.")
@require_professional
def scan_topics_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    include_subscriptions: bool = typer.Option(True, help="Include subscription scanning")
):
    scan_topics(output_dir, profile, region, include_subscriptions)

@app.command(name="list-topics", help="List scanned SNS topics.")
@require_professional
def list_topics_command(output_dir: Path = typer.Option("generated")):
    list_topics(output_dir)

@app.command(name="import-topic", help="Import an SNS topic by ARN.")
@require_professional
def import_topic_command(
    topic_arn: str,
    output_dir: Path = typer.Option("generated")
):
    import_topic(topic_arn, output_dir)

# --- SNS Subscription Commands ---
@app.command(name="scan-subscriptions", help="Scan SNS subscriptions.")
@require_professional
def scan_subscriptions_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    topic_arn: str = typer.Option(None, help="Filter by specific topic ARN")
):
    scan_subscriptions(output_dir, profile, region, topic_arn)

@app.command(name="list-subscriptions", help="List scanned SNS subscriptions.")
@require_professional
def list_subscriptions_command(output_dir: Path = typer.Option("generated")):
    list_subscriptions(output_dir)

@app.command(name="import-subscription", help="Import an SNS subscription by ARN.")
@require_professional
def import_subscription_command(
    subscription_arn: str,
    output_dir: Path = typer.Option("generated")
):
    import_subscription(subscription_arn, output_dir)

# --- Combined Commands ---
@app.command(name="scan-all", help="Scan all SNS resources (topics and subscriptions).")
@require_professional
def scan_all_sns_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_topics(output_dir, profile, region, include_subscriptions=True)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the SNS module."""
    register_scan_function("sns_topic", scan_topics)
    register_scan_function("sns_subscription", scan_subscriptions)

    # Define SNS dependencies
    # SNS can send messages to SQS queues
    cross_scan_registry.register_dependency("sns_topic", "sqs_queue")
    # SNS can trigger Lambda functions
    cross_scan_registry.register_dependency("sns_topic", "lambda_function")
    # CloudWatch alarms can publish to SNS topics
    cross_scan_registry.register_dependency("cloudwatch_alarm", "sns_topic")
