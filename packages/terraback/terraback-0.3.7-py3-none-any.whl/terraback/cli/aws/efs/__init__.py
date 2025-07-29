from terraback.core.license import require_professional
import typer
from pathlib import Path

from .file_systems import scan_file_systems, list_file_systems, import_file_system
from .mount_targets import scan_mount_targets, list_mount_targets, import_mount_target
from .access_points import scan_access_points, list_access_points, import_access_point

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="efs",
    help="Manage EFS (Elastic File System) resources like file systems, mount targets, and access points.",
    no_args_is_help=True
)

# --- EFS File System Commands ---
@app.command(name="scan-file-systems", help="Scan EFS file systems.")
@require_professional
def scan_file_systems_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_file_systems(output_dir, profile, region)

@app.command(name="list-file-systems", help="List scanned EFS file systems.")
@require_professional
def list_file_systems_command(output_dir: Path = typer.Option("generated")):
    list_file_systems(output_dir)

@app.command(name="import-file-system", help="Import an EFS file system by ID.")
@require_professional
def import_file_system_command(
    file_system_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_file_system(file_system_id, output_dir)

# --- EFS Mount Target Commands ---
@app.command(name="scan-mount-targets", help="Scan EFS mount targets.")
@require_professional
def scan_mount_targets_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_mount_targets(output_dir, profile, region)

@app.command(name="list-mount-targets", help="List scanned EFS mount targets.")
@require_professional
def list_mount_targets_command(output_dir: Path = typer.Option("generated")):
    list_mount_targets(output_dir)

@app.command(name="import-mount-target", help="Import an EFS mount target by ID.")
@require_professional
def import_mount_target_command(
    mount_target_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_mount_target(mount_target_id, output_dir)

# --- EFS Access Point Commands ---
@app.command(name="scan-access-points", help="Scan EFS access points.")
@require_professional
def scan_access_points_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_access_points(output_dir, profile, region)

@app.command(name="list-access-points", help="List scanned EFS access points.")
@require_professional
def list_access_points_command(output_dir: Path = typer.Option("generated")):
    list_access_points(output_dir)

@app.command(name="import-access-point", help="Import an EFS access point by ID.")
@require_professional
def import_access_point_command(
    access_point_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_access_point(access_point_id, output_dir)

# --- Combined Commands ---
@app.command(name="scan-all", help="Scan all EFS resources (file systems, mount targets, access points).")
@require_professional
def scan_all_efs_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_file_systems(output_dir, profile, region)
    scan_mount_targets(output_dir, profile, region)
    scan_access_points(output_dir, profile, region)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the EFS module."""
    register_scan_function("efs_file_system", scan_file_systems)
    register_scan_function("efs_mount_target", scan_mount_targets)
    register_scan_function("efs_access_point", scan_access_points)

    # Define EFS dependencies
    # Mount targets depend on file systems and subnets
    cross_scan_registry.register_dependency("efs_mount_target", "efs_file_system")
    cross_scan_registry.register_dependency("efs_mount_target", "subnets")
    cross_scan_registry.register_dependency("efs_mount_target", "security_groups")
    
    # Access points depend on file systems
    cross_scan_registry.register_dependency("efs_access_point", "efs_file_system")
    
    # ECS task definitions may use EFS file systems
    cross_scan_registry.register_dependency("ecs_task_definition", "efs_file_system")
    cross_scan_registry.register_dependency("ecs_task_definition", "efs_access_point")