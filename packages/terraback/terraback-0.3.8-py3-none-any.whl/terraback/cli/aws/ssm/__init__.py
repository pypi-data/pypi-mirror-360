from terraback.core.license import require_professional
import typer
from pathlib import Path

from .parameters import scan_parameters, list_parameters, import_parameter
from .documents import scan_documents, list_documents, import_document
from .maintenance_windows import scan_maintenance_windows, list_maintenance_windows, import_maintenance_window

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="ssm",
    help="Manage AWS Systems Manager resources like parameters, documents, and maintenance windows.",
    no_args_is_help=True
)

# --- Parameter Store Commands ---
@app.command(name="scan-parameters", help="Scan Systems Manager parameters.")
@require_professional
def scan_parameters_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    parameter_filters: str = typer.Option(None, help="Parameter name filters (comma-separated)"),
    include_secure: bool = typer.Option(True, help="Include SecureString parameters"),
    max_results: int = typer.Option(50, help="Maximum number of parameters to scan")
):
    filters = parameter_filters.split(',') if parameter_filters else None
    scan_parameters(output_dir, profile, region, filters, include_secure, max_results)

@app.command(name="list-parameters", help="List scanned Systems Manager parameters.")
@require_professional
def list_parameters_command(output_dir: Path = typer.Option("generated")):
    list_parameters(output_dir)

@app.command(name="import-parameter", help="Import a Systems Manager parameter by name.")
@require_professional
def import_parameter_command(
    parameter_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_parameter(parameter_name, output_dir)

# --- Document Commands ---
@app.command(name="scan-documents", help="Scan Systems Manager documents.")
@require_professional
def scan_documents_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    owner_filter: str = typer.Option("Self", help="Document owner filter (Self, Amazon, Public)"),
    document_type: str = typer.Option(None, help="Document type filter")
):
    scan_documents(output_dir, profile, region, owner_filter, document_type)

@app.command(name="list-documents", help="List scanned Systems Manager documents.")
@require_professional
def list_documents_command(output_dir: Path = typer.Option("generated")):
    list_documents(output_dir)

@app.command(name="import-document", help="Import a Systems Manager document by name.")
@require_professional
def import_document_command(
    document_name: str,
    output_dir: Path = typer.Option("generated")
):
    import_document(document_name, output_dir)

# --- Maintenance Window Commands ---
@app.command(name="scan-maintenance-windows", help="Scan Systems Manager maintenance windows.")
@require_professional
def scan_maintenance_windows_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region")
):
    scan_maintenance_windows(output_dir, profile, region)

@app.command(name="list-maintenance-windows", help="List scanned maintenance windows.")
@require_professional
def list_maintenance_windows_command(output_dir: Path = typer.Option("generated")):
    list_maintenance_windows(output_dir)

@app.command(name="import-maintenance-window", help="Import a maintenance window by ID.")
@require_professional
def import_maintenance_window_command(
    window_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_maintenance_window(window_id, output_dir)

# --- Combined Commands ---
@app.command(name="scan-all", help="Scan all Systems Manager resources.")
@require_professional
def scan_all_ssm_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    max_parameters: int = typer.Option(50, help="Maximum number of parameters to scan")
):
    scan_parameters(output_dir, profile, region, max_results=max_parameters)
    scan_documents(output_dir, profile, region)
    scan_maintenance_windows(output_dir, profile, region)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the Systems Manager module."""
    register_scan_function("ssm_parameter", scan_parameters)
    register_scan_function("ssm_document", scan_documents)
    register_scan_function("ssm_maintenance_window", scan_maintenance_windows)

    # Define Systems Manager dependencies
    # EC2 instances may use SSM parameters and documents
    cross_scan_registry.register_dependency("ec2", "ssm_parameter")
    cross_scan_registry.register_dependency("ec2", "ssm_document")
    # Lambda functions may use SSM parameters
    cross_scan_registry.register_dependency("lambda_function", "ssm_parameter")
    # ECS task definitions may use SSM parameters
    cross_scan_registry.register_dependency("ecs_task_definition", "ssm_parameter")