from terraback.core.license import require_professional
import typer
from pathlib import Path

from .log_groups import scan_log_groups, list_log_groups, import_log_group
from .alarms import scan_alarms, list_alarms, import_alarm
from .dashboards import scan_dashboards, list_dashboards, import_dashboard

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="cloudwatch",
    help="Manage CloudWatch resources like Log Groups, Alarms, and Dashboards.",
    no_args_is_help=True
)

# --- Log Group Commands ---
@app.command(name="scan-log-groups", help="Scan CloudWatch Log Groups.")
@require_professional
def scan_log_groups_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_log_groups(output_dir, profile, region)

@app.command(name="list-log-groups", help="List scanned CloudWatch Log Groups.")
@require_professional
def list_log_groups_command(output_dir: Path = typer.Option("generated")):
    list_log_groups(output_dir)

@app.command(name="import-log-group", help="Import a CloudWatch Log Group by name.")
@require_professional
def import_log_group_command(
    log_group_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_log_group(log_group_name, output_dir)

# --- Alarm Commands ---
@app.command(name="scan-alarms", help="Scan CloudWatch Alarms.")
@require_professional
def scan_alarms_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_alarms(output_dir, profile, region)

@app.command(name="list-alarms", help="List scanned CloudWatch Alarms.")
@require_professional
def list_alarms_command(output_dir: Path = typer.Option("generated")):
    list_alarms(output_dir)

@app.command(name="import-alarm", help="Import a CloudWatch Alarm by name.")
@require_professional
def import_alarm_command(
    alarm_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_alarm(alarm_name, output_dir)

# --- Dashboard Commands ---
@app.command(name="scan-dashboards", help="Scan CloudWatch Dashboards.")
@require_professional
def scan_dashboards_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_dashboards(output_dir, profile, region)

@app.command(name="list-dashboards", help="List scanned CloudWatch Dashboards.")
@require_professional
def list_dashboards_command(output_dir: Path = typer.Option("generated")):
    list_dashboards(output_dir)

@app.command(name="import-dashboard", help="Import a CloudWatch Dashboard by name.")
@require_professional
def import_dashboard_command(
    dashboard_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_dashboard(dashboard_name, output_dir)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the CloudWatch module."""
    register_scan_function("cloudwatch_log_group", scan_log_groups)
    register_scan_function("cloudwatch_alarm", scan_alarms)
    register_scan_function("cloudwatch_dashboard", scan_dashboards)

    # Define dependencies - CloudWatch resources are often dependencies for other services
    # Lambda functions typically create log groups automatically
    cross_scan_registry.register_dependency("lambda_function", "cloudwatch_log_group")
    # ECS services also use CloudWatch logs
    cross_scan_registry.register_dependency("ecs_service", "cloudwatch_log_group")
    # API Gateway uses CloudWatch logs
    cross_scan_registry.register_dependency("api_gateway_rest_api", "cloudwatch_log_group")
    # RDS instances often have CloudWatch alarms
    cross_scan_registry.register_dependency("rds_instance", "cloudwatch_alarm")
    # Load balancers often have CloudWatch alarms
    cross_scan_registry.register_dependency("elbv2_load_balancer", "cloudwatch_alarm")