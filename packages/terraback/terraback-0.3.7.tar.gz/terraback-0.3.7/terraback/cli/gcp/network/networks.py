# terraback/cli/gcp/network/networks.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.cloud import compute_v1
from google.api_core import exceptions

from terraback.cli.gcp.session import get_default_project_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="network", help="Scan and import GCP VPC networks.")

def get_network_data(project_id: str) -> List[Dict[str, Any]]:
    """Fetch VPC network data from GCP."""
    client = compute_v1.NetworksClient()
    networks = []
    
    try:
        request = compute_v1.ListNetworksRequest(
            project=project_id
        )
        network_list = client.list(request=request)
        
        for network in network_list:
            network_data = {
                "name": network.name,
                "id": f"{project_id}/{network.name}",
                "project": project_id,
                "description": network.description or "",
                
                # Network settings
                "auto_create_subnetworks": network.auto_create_subnetworks,
                "routing_mode": network.routing_config.routing_mode if network.routing_config else "REGIONAL",
                "mtu": network.mtu if hasattr(network, 'mtu') else 1460,
                
                # Subnets (just references)
                "subnetworks": [subnet.split('/')[-1] for subnet in network.subnetworks] if network.subnetworks else [],
                
                # For resource naming
                "name_sanitized": network.name.replace('-', '_').lower(),
                
                # Creation timestamp
                "creation_timestamp": network.creation_timestamp,
            }
            
            networks.append(network_data)
            
    except exceptions.GoogleAPIError as e:
        typer.echo(f"Error fetching networks: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return networks

@app.command("scan")
def scan_networks(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    with_deps: bool = typer.Option(False, "--with-deps")
):
    """Scans GCP VPC networks and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning GCP networks with dependencies...")
        recursive_scan(
            "gcp_network",
            output_dir=output_dir,
            project_id=project_id
        )
    else:
        typer.echo(f"Scanning for GCP networks in project '{project_id}'...")
        
        network_data = get_network_data(project_id)
        
        if not network_data:
            typer.echo("No networks found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "gcp_network.tf"
        generate_tf(network_data, "gcp_network", output_file, provider="gcp")
        typer.echo(f"Generated Terraform for {len(network_data)} networks -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "gcp_network",
            network_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_networks(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List all GCP network resources previously generated."""
    ImportManager(output_dir, "gcp_network").list_all()

@app.command("import")
def import_network(
    network_id: str = typer.Argument(..., help="GCP network ID (project/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Run terraform import for a specific GCP network."""
    ImportManager(output_dir, "gcp_network").find_and_import(network_id)

# Scan function for cross-scan registry
def scan_gcp_networks(
    output_dir: Path,
    project_id: str = None,
    **kwargs
):
    """Scan function to be registered with cross-scan registry."""
    if not project_id:
        project_id = get_default_project_id()
    
    typer.echo(f"[Cross-scan] Scanning GCP networks in project {project_id}")
    
    network_data = get_network_data(project_id)
    
    if network_data:
        output_file = output_dir / "gcp_network.tf"
        generate_tf(network_data, "gcp_network", output_file, provider="gcp")
        generate_imports_file(
            "gcp_network",
            network_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(network_data)} GCP networks")