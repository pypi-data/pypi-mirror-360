from terraback.core.license import require_professional
import typer
from pathlib import Path

# Import functions for all RDS resources
from .instances import scan_rds_instances, list_rds_instances, import_rds_instance
from .subnet_groups import scan_db_subnet_groups, list_db_subnet_groups, import_db_subnet_group
from .parameter_groups import scan_db_parameter_groups, list_db_parameter_groups, import_db_parameter_group

# Import registry utilities
from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="rds",
    help="Manage RDS resources like DB Instances, Subnet Groups, and Parameter Groups.",
    no_args_is_help=True
)

# --- DB Instance Commands ---
@app.command(name="scan-instances", help="Scan RDS DB Instances and generate Terraform code.")
@require_professional
def scan_rds_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_rds_instances(output_dir, profile, region)

@app.command(name="list-instances", help="List all RDS DB Instance resources previously generated.")
@require_professional
def list_rds_command(output_dir: Path = typer.Option("generated", help="Directory...")):
    list_rds_instances(output_dir)

@app.command(name="import-instance", help="Run terraform import for a specific RDS DB Instance.")
@require_professional
def import_rds_command(
    db_instance_id: str,
    output_dir: Path = typer.Option("generated", help="Directory...")
):
    import_rds_instance(db_instance_id, output_dir)

# --- DB Subnet Group Commands ---
@app.command(name="scan-subnet-groups", help="Scan RDS DB Subnet Groups and generate Terraform code.")
@require_professional
def scan_sng_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_db_subnet_groups(output_dir, profile, region)

@app.command(name="list-subnet-groups", help="List all RDS DB Subnet Group resources previously generated.")
@require_professional
def list_sng_command(output_dir: Path = typer.Option("generated", help="Directory...")):
    list_db_subnet_groups(output_dir)

@app.command(name="import-subnet-group", help="Run terraform import for a specific RDS DB Subnet Group.")
@require_professional
def import_sng_command(
    subnet_group_name: str,
    output_dir: Path = typer.Option("generated", help="Directory...")
):
    import_db_subnet_group(subnet_group_name, output_dir)

# --- DB Parameter Group Commands ---
@app.command(name="scan-parameter-groups", help="Scan RDS DB Parameter Groups and generate Terraform code.")
@require_professional
def scan_pg_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_db_parameter_groups(output_dir, profile, region)

@app.command(name="list-parameter-groups", help="List all RDS DB Parameter Group resources previously generated.")
@require_professional
def list_pg_command(output_dir: Path = typer.Option("generated", help="Directory...")):
    list_db_parameter_groups(output_dir)

@app.command(name="import-parameter-group", help="Run terraform import for a specific RDS DB Parameter Group.")
@require_professional
def import_pg_command(
    parameter_group_name: str,
    output_dir: Path = typer.Option("generated", help="Directory...")
):
    import_db_parameter_group(parameter_group_name, output_dir)


# --- Registration Function ---
def register():
    """Registers the scan functions for the RDS module."""
    # DB Instances
    register_scan_function("rds_instance", scan_rds_instances)
    cross_scan_registry.register_dependency("rds_instance", "db_subnet_group")
    cross_scan_registry.register_dependency("rds_instance", "db_parameter_group") # An instance uses a parameter group

    # DB Subnet Groups
    register_scan_function("db_subnet_group", scan_db_subnet_groups)
    cross_scan_registry.register_dependency("db_subnet_group", "subnet")

    # DB Parameter Groups
    register_scan_function("db_parameter_group", scan_db_parameter_groups)