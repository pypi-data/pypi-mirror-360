from terraback.core.license import require_professional
import typer
from pathlib import Path

from .clusters import scan_clusters, list_clusters, import_cluster
from .services import scan_services, list_services, import_service
from .task_definitions import scan_task_definitions, list_task_definitions, import_task_definition

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="ecs",
    help="Manage ECS (Elastic Container Service) resources like Clusters, Services, and Task Definitions.",
    no_args_is_help=True
)

# --- ECS Cluster Commands ---
@app.command(name="scan-clusters", help="Scan ECS Clusters.")
@require_professional
def scan_clusters_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_clusters(output_dir, profile, region)

@app.command(name="list-clusters", help="List scanned ECS Clusters.")
@require_professional
def list_clusters_command(output_dir: Path = typer.Option("generated")):
    list_clusters(output_dir)

@app.command(name="import-cluster", help="Import an ECS Cluster by name.")
@require_professional
def import_cluster_command(
    cluster_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_cluster(cluster_name, output_dir)

# --- ECS Service Commands ---
@app.command(name="scan-services", help="Scan ECS Services.")
@require_professional
def scan_services_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    cluster_name: str = typer.Option(None, help="Filter by specific cluster name")
):
    scan_services(output_dir, profile, region, cluster_name)

@app.command(name="list-services", help="List scanned ECS Services.")
@require_professional
def list_services_command(output_dir: Path = typer.Option("generated")):
    list_services(output_dir)

@app.command(name="import-service", help="Import an ECS Service by ARN.")
@require_professional
def import_service_command(
    service_arn: str,
    output_dir: Path = typer.Option("generated")
):
    import_service(service_arn, output_dir)

# --- ECS Task Definition Commands ---
@app.command(name="scan-task-definitions", help="Scan ECS Task Definitions.")
@require_professional
def scan_task_definitions_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    family_prefix: str = typer.Option(None, help="Filter by task definition family prefix"),
    include_inactive: bool = typer.Option(False, help="Include INACTIVE task definitions")
):
    scan_task_definitions(output_dir, profile, region, family_prefix, include_inactive)

@app.command(name="list-task-definitions", help="List scanned ECS Task Definitions.")
@require_professional
def list_task_definitions_command(output_dir: Path = typer.Option("generated")):
    list_task_definitions(output_dir)

@app.command(name="import-task-definition", help="Import an ECS Task Definition by ARN.")
@require_professional
def import_task_definition_command(
    task_definition_arn: str,
    output_dir: Path = typer.Option("generated")
):
    import_task_definition(task_definition_arn, output_dir)

# --- Combined Commands ---
@app.command(name="scan-all", help="Scan all ECS resources (clusters, services, task definitions).")
@require_professional
def scan_all_ecs_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    include_inactive: bool = typer.Option(False, help="Include INACTIVE task definitions")
):
    scan_clusters(output_dir, profile, region)
    scan_services(output_dir, profile, region)
    scan_task_definitions(output_dir, profile, region, include_inactive=include_inactive)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the ECS module."""
    register_scan_function("ecs_cluster", scan_clusters)
    register_scan_function("ecs_service", scan_services)
    register_scan_function("ecs_task_definition", scan_task_definitions)

    # Define ECS dependencies
    # ECS Services depend on clusters and task definitions
    cross_scan_registry.register_dependency("ecs_service", "ecs_cluster")
    cross_scan_registry.register_dependency("ecs_service", "ecs_task_definition")
    
    # ECS Services depend on networking components
    cross_scan_registry.register_dependency("ecs_service", "subnets")
    cross_scan_registry.register_dependency("ecs_service", "security_groups")
    cross_scan_registry.register_dependency("ecs_service", "elbv2_target_group")
    
    # Task definitions depend on IAM roles and ECR images
    cross_scan_registry.register_dependency("ecs_task_definition", "iam_role")
    cross_scan_registry.register_dependency("ecs_task_definition", "ecr_repository")
    cross_scan_registry.register_dependency("ecs_task_definition", "efs_file_system")
    
    # Task definitions may use CloudWatch log groups
    cross_scan_registry.register_dependency("ecs_task_definition", "cloudwatch_log_group")