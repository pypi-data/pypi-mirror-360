# terraback/cli/gcp/loadbalancer/backend_services.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.cloud import compute_v1
from google.api_core import exceptions

from terraback.cli.gcp.session import get_default_project_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="backend-service", help="Scan and import GCP backend services.")

def get_backend_service_data(project_id: str, region: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch backend service data from GCP."""
    # TODO: Implement actual GCP API calls
    # This is a placeholder implementation
    backend_services = []
    
    try:
        # Global backend services
        if not region:
            # client = compute_v1.BackendServicesClient()
            # request = compute_v1.ListBackendServicesRequest(project=project_id)
            # service_list = client.list(request=request)
            pass
        else:
            # Regional backend services
            # client = compute_v1.RegionBackendServicesClient()
            # request = compute_v1.ListRegionBackendServicesRequest(
            #     project=project_id,
            #     region=region
            # )
            # service_list = client.list(request=request)
            pass
        
        typer.echo("[TODO] Backend service scanning not yet implemented")
        
    except exceptions.GoogleAPIError as e:
        typer.echo(f"Error fetching backend services: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return backend_services

@app.command("scan")
def scan_backend_services(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    with_deps: bool = typer.Option(False, "--with-deps")
):
    """Scans GCP backend services and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning GCP backend services with dependencies...")
        recursive_scan(
            "gcp_backend_service",
            output_dir=output_dir,
            project_id=project_id,
            region=region
        )
    else:
        typer.echo(f"Scanning for GCP backend services in project '{project_id}'...")
        if region:
            typer.echo(f"Region: {region}")
        else:
            typer.echo("Scope: Global")
        
        backend_service_data = get_backend_service_data(project_id, region)
        
        if not backend_service_data:
            typer.echo("No backend services found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "gcp_backend_service.tf"
        generate_tf(backend_service_data, "gcp_backend_service", output_file, provider="gcp")
        typer.echo(f"Generated Terraform for {len(backend_service_data)} backend services -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "gcp_backend_service",
            backend_service_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_backend_services(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List all GCP backend service resources previously generated."""
    ImportManager(output_dir, "gcp_backend_service").list_all()

@app.command("import")
def import_backend_service(
    backend_service_id: str = typer.Argument(..., help="GCP backend service ID"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Run terraform import for a specific GCP backend service."""
    ImportManager(output_dir, "gcp_backend_service").find_and_import(backend_service_id)

# Scan function for cross-scan registry
def scan_gcp_backend_services(
    output_dir: Path,
    project_id: Optional[str] = None,
    region: Optional[str] = None,
    **kwargs
):
    """Scan function to be registered with cross-scan registry."""
    if not project_id:
        project_id = get_default_project_id()
    if not project_id:
        typer.echo("Error: No GCP project found", err=True)
        raise typer.Exit(code=1)
    
    typer.echo(f"[Cross-scan] Scanning GCP backend services in project {project_id}")
    
    backend_service_data = get_backend_service_data(project_id, region)
    
    if backend_service_data:
        output_file = output_dir / "gcp_backend_service.tf"
        generate_tf(backend_service_data, "gcp_backend_service", output_file, provider="gcp")
        generate_imports_file(
            "gcp_backend_service",
            backend_service_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(backend_service_data)} GCP backend services")
