# terraback/cli/gcp/compute/disks.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.cloud import compute_v1
from google.api_core import exceptions

from terraback.cli.gcp.session import get_default_project_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="disk", help="Scan and import GCP Compute Engine disks.")

def get_disk_data(project_id: str, zone: str = None) -> List[Dict[str, Any]]:
    """Fetch disk data from GCP."""
    client = compute_v1.DisksClient()
    disks = []
    
    try:
        if zone:
            # List disks in specific zone
            request = compute_v1.ListDisksRequest(
                project=project_id,
                zone=zone
            )
            disk_list = client.list(request=request)
        else:
            # List all disks across all zones
            request = compute_v1.AggregatedListDisksRequest(
                project=project_id
            )
            aggregated_list = client.aggregated_list(request=request)
            disk_list = []
            for zone_name, scoped_list in aggregated_list:
                if scoped_list.disks:
                    for disk in scoped_list.disks:
                        # Extract zone from the scoped list key
                        disk_zone = zone_name.split('/')[-1]
                        disk_list.append((disk, disk_zone))
        
        for item in disk_list:
            if zone:
                disk = item
                disk_zone = zone
            else:
                disk, disk_zone = item
            
            disk_data = {
                "name": disk.name,
                "id": f"{project_id}/{disk_zone}/{disk.name}",
                "project": project_id,
                "zone": disk_zone,
                "size_gb": disk.size_gb,
                "type": disk.type.split('/')[-1] if disk.type else "pd-standard",
                
                # Source information
                "source_image": disk.source_image.split('/')[-1] if disk.source_image else None,
                "source_snapshot": disk.source_snapshot.split('/')[-1] if disk.source_snapshot else None,
                
                # Labels
                "labels": dict(disk.labels) if disk.labels else {},
                
                # Encryption
                "disk_encryption_key": None,
                
                # Physical block size
                "physical_block_size_bytes": disk.physical_block_size_bytes if hasattr(disk, 'physical_block_size_bytes') else 4096,
                
                # State
                "status": disk.status,
                
                # For resource naming
                "name_sanitized": disk.name.replace('-', '_').lower()
            }
            
            # Handle encryption
            if disk.disk_encryption_key:
                if disk.disk_encryption_key.raw_key:
                    disk_data["disk_encryption_key"] = {
                        "raw_key": "REDACTED",  # Don't expose keys
                        "kms_key_self_link": None
                    }
                elif disk.disk_encryption_key.kms_key_name:
                    disk_data["disk_encryption_key"] = {
                        "raw_key": None,
                        "kms_key_self_link": disk.disk_encryption_key.kms_key_name
                    }
            
            disks.append(disk_data)
            
    except exceptions.GoogleAPIError as e:
        typer.echo(f"Error fetching disks: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return disks

@app.command("scan")
def scan_disks(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    zone: Optional[str] = typer.Option(None, "--zone", "-z"),
    with_deps: bool = typer.Option(False, "--with-deps")
):
    """Scans GCP Compute Engine disks and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning GCP disks with dependencies...")
        recursive_scan(
            "gcp_disk",
            output_dir=output_dir,
            project_id=project_id,
            zone=zone
        )
    else:
        typer.echo(f"Scanning for GCP disks in project '{project_id}'...")
        if zone:
            typer.echo(f"Zone: {zone}")
        else:
            typer.echo("Zone: all zones")
        
        disk_data = get_disk_data(project_id, zone)
        
        if not disk_data:
            typer.echo("No disks found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "gcp_disk.tf"
        generate_tf(disk_data, "gcp_disk", output_file, provider="gcp")
        typer.echo(f"Generated Terraform for {len(disk_data)} disks -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "gcp_disk",
            disk_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_disks(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List all GCP disk resources previously generated."""
    ImportManager(output_dir, "gcp_disk").list_all()

@app.command("import")
def import_disk(
    disk_id: str = typer.Argument(..., help="GCP disk ID (project/zone/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Run terraform import for a specific GCP disk."""
    ImportManager(output_dir, "gcp_disk").find_and_import(disk_id)

# Scan function for cross-scan registry
def scan_gcp_disks(
    output_dir: Path,
    project_id: str = None,
    zone: Optional[str] = None,
    **kwargs
):
    """Scan function to be registered with cross-scan registry."""
    if not project_id:
        project_id = get_default_project_id()
    
    typer.echo(f"[Cross-scan] Scanning GCP disks in project {project_id}")
    
    disk_data = get_disk_data(project_id, zone)
    
    if disk_data:
        output_file = output_dir / "gcp_disk.tf"
        generate_tf(disk_data, "gcp_disk", output_file, provider="gcp")
        generate_imports_file(
            "gcp_disk",
            disk_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(disk_data)} GCP disks")