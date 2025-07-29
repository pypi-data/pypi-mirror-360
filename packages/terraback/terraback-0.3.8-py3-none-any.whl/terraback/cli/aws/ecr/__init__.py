from terraback.core.license import require_professional
import typer
from pathlib import Path

from .repositories import scan_repositories, list_repositories, import_repository

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="ecr",
    help="Manage ECR (Elastic Container Registry) resources like repositories.",
    no_args_is_help=True
)

# --- ECR Repository Commands ---
@app.command(name="scan-repositories", help="Scan ECR repositories.")
@require_professional
def scan_repositories_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_repositories(output_dir, profile, region)

@app.command(name="list-repositories", help="List scanned ECR repositories.")
@require_professional
def list_repositories_command(output_dir: Path = typer.Option("generated")):
    list_repositories(output_dir)

@app.command(name="import-repository", help="Import an ECR repository by name.")
@require_professional
def import_repository_command(
    repository_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_repository(repository_name, output_dir)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the ECR module."""
    register_scan_function("ecr_repository", scan_repositories)

    # ECR repositories are dependencies for ECS task definitions
    # (Task definitions reference ECR images)
    cross_scan_registry.register_dependency("ecs_task_definition", "ecr_repository")