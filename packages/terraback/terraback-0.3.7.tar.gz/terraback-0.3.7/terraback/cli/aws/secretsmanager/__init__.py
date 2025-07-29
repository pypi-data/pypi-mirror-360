from terraback.core.license import require_professional
import typer
from pathlib import Path

from .secrets import scan_secrets, list_secrets, import_secret
from .secret_versions import scan_secret_versions, list_secret_versions, import_secret_version

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="secretsmanager",
    help="Manage AWS Secrets Manager resources like secrets and secret versions.",
    no_args_is_help=True
)

# --- Secrets Commands ---
@app.command(name="scan-secrets", help="Scan Secrets Manager secrets.")
@require_professional
def scan_secrets_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    include_versions: bool = typer.Option(False, help="Include secret versions scanning"),
    include_deleted: bool = typer.Option(False, help="Include deleted secrets")
):
    scan_secrets(output_dir, profile, region, include_versions, include_deleted)

@app.command(name="list-secrets", help="List scanned Secrets Manager secrets.")
@require_professional
def list_secrets_command(output_dir: Path = typer.Option("generated")):
    list_secrets(output_dir)

@app.command(name="import-secret", help="Import a Secrets Manager secret by ARN.")
@require_professional
def import_secret_command(
    secret_arn: str,
    output_dir: Path = typer.Option("generated")
):
    import_secret(secret_arn, output_dir)

# --- Secret Versions Commands ---
@app.command(name="scan-secret-versions", help="Scan secret versions.")
@require_professional
def scan_secret_versions_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    secret_arn: str = typer.Option(None, help="Filter by specific secret ARN")
):
    scan_secret_versions(output_dir, profile, region, secret_arn)

@app.command(name="list-secret-versions", help="List scanned secret versions.")
@require_professional
def list_secret_versions_command(output_dir: Path = typer.Option("generated")):
    list_secret_versions(output_dir)

@app.command(name="import-secret-version", help="Import a secret version by composite ID.")
@require_professional
def import_secret_version_command(
    composite_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_secret_version(composite_id, output_dir)

# --- Combined Commands ---
@app.command(name="scan-all", help="Scan all Secrets Manager resources.")
@require_professional
def scan_all_secrets_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    include_deleted: bool = typer.Option(False, help="Include deleted secrets")
):
    scan_secrets(output_dir, profile, region, include_versions=True, include_deleted=include_deleted)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the Secrets Manager module."""
    register_scan_function("secretsmanager_secret", scan_secrets)
    register_scan_function("secretsmanager_secret_version", scan_secret_versions)

    # Define Secrets Manager dependencies
    # RDS instances often use Secrets Manager for credentials
    cross_scan_registry.register_dependency("rds_instance", "secretsmanager_secret")
    # Lambda functions may use secrets
    cross_scan_registry.register_dependency("lambda_function", "secretsmanager_secret")
    # ECS task definitions may use secrets
    cross_scan_registry.register_dependency("ecs_task_definition", "secretsmanager_secret")

