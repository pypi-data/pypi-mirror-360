# terraback/cli/gcp/network/subnets.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.cloud import compute_v1
from google.api_core import exceptions

from terraback.cli.gcp.session import get_default_project_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="subnet", help="Scan and import GCP VPC subnets.")

def get_subnet_data(project_id: str, region: str = None) -> List[Dict[str, Any]]:
    """Fetch subnet data from GCP."""
    client = compute_v1.SubnetworksClient()
    subnets = []
    
    try:
        if region:
            # List subnets in specific region
            request = compute_v1.ListSubnetworksRequest(
                project=project_id,
                region=region
            )
            subnet_list = client.list(request=request)
        else:
            # List all subnets across all regions
            request = compute_v1.AggregatedListSubnetworksRequest(
                project=project_id
            )
            aggregated_list = client.aggregated_list(request=request)
            subnet_list = []
            for region_name, scoped_list in aggregated_list:
                if scoped_list.subnetworks:
                    for subnet in scoped_list.subnetworks:
                        # Extract region from the scoped list key
                        subnet_region = region_name.split('/')[-1]
                        subnet_list.append((subnet, subnet_region))
        
        for item in subnet_list:
            if region:
                subnet = item
                subnet_region = region
            else:
                subnet, subnet_region = item
            
            subnet_data = {
                "name": subnet.name,
                "id": f"{project_id}/{subnet_region}/{subnet.name}",
                "project": project_id,
                "region": subnet_region,
                "network": subnet.network.split('/')[-1] if subnet.network else None,
                "ip_cidr_range": subnet.ip_cidr_range,
                "description": subnet.description or "",
                
                # Secondary ranges
                "secondary_ip_ranges": [],
                
                # Private Google Access
                "private_ip_google_access": subnet.private_ip_google_access if hasattr(subnet, 'private_ip_google_access') else False,
                
                # Flow logs
                "enable_flow_logs": subnet.enable_flow_logs if hasattr(subnet, 'enable_flow_logs') else False,
                
                # For resource naming
                "name_sanitized": subnet.name.replace('-', '_').lower(),
                
                # Purpose (e.g., PRIVATE, INTERNAL_HTTPS_LOAD_BALANCER)
                "purpose": subnet.purpose if hasattr(subnet, 'purpose') else "PRIVATE",
                
                # Stack type (IPV4_ONLY, IPV4_IPV6)
                "stack_type": subnet.stack_type if hasattr(subnet, 'stack_type') else "IPV4_ONLY",
            }
            
            # Process secondary IP ranges
            if subnet.secondary_ip_ranges:
                for secondary_range in subnet.secondary_ip_ranges:
                    subnet_data["secondary_ip_ranges"].append({
                        "range_name": secondary_range.range_name,
                        "ip_cidr_range": secondary_range.ip_cidr_range
                    })
            
            # Log config
            if hasattr(subnet, 'log_config') and subnet.log_config:
                subnet_data["log_config"] = {
                    "aggregation_interval": subnet.log_config.aggregation_interval,
                    "flow_sampling": subnet.log_config.flow_sampling,
                    "metadata": subnet.log_config.metadata,
                    "metadata_fields": list(subnet.log_config.metadata_fields) if subnet.log_config.metadata_fields else [],
                }
            else:
                subnet_data["log_config"] = None
            
            subnets.append(subnet_data)
            
    except exceptions.GoogleAPIError as e:
        typer.echo(f"Error fetching subnets: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return subnets

@app.command("scan")
def scan_subnets(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    with_deps: bool = typer.Option(False, "--with-deps")
):
    """Scans GCP VPC subnets and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning GCP subnets with dependencies...")
        recursive_scan(
            "gcp_subnet",
            output_dir=output_dir,
            project_id=project_id,
            region=region
        )
    else:
        typer.echo(f"Scanning for GCP subnets in project '{project_id}'...")
        if region:
            typer.echo(f"Region: {region}")
        else:
            typer.echo("Region: all regions")
        
        subnet_data = get_subnet_data(project_id, region)
        
        if not subnet_data:
            typer.echo("No subnets found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "gcp_subnet.tf"
        generate_tf(subnet_data, "gcp_subnet", output_file, provider="gcp")
        typer.echo(f"Generated Terraform for {len(subnet_data)} subnets -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "gcp_subnet",
            subnet_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_subnets(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List all GCP subnet resources previously generated."""
    ImportManager(output_dir, "gcp_subnet").list_all()

@app.command("import")
def import_subnet(
    subnet_id: str = typer.Argument(..., help="GCP subnet ID (project/region/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Run terraform import for a specific GCP subnet."""
    ImportManager(output_dir, "gcp_subnet").find_and_import(subnet_id)

# Scan function for cross-scan registry
def scan_gcp_subnets(
    output_dir: Path,
    project_id: str = None,
    region: Optional[str] = None,
    **kwargs
):
    """Scan function to be registered with cross-scan registry."""
    if not project_id:
        project_id = get_default_project_id()
    
    typer.echo(f"[Cross-scan] Scanning GCP subnets in project {project_id}")
    
    subnet_data = get_subnet_data(project_id, region)
    
    if subnet_data:
        output_file = output_dir / "gcp_subnet.tf"
        generate_tf(subnet_data, "gcp_subnet", output_file, provider="gcp")
        generate_imports_file(
            "gcp_subnet",
            subnet_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(subnet_data)} GCP subnets")