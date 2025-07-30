# terraback/cli/gcp/network/firewalls.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.cloud import compute_v1
from google.api_core import exceptions

from terraback.cli.gcp.session import get_default_project_id
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="firewall", help="Scan and import GCP firewall rules.")

def get_firewall_data(project_id: str) -> List[Dict[str, Any]]:
    """Fetch firewall rule data from GCP."""
    client = compute_v1.FirewallsClient()
    firewalls = []
    
    try:
        request = compute_v1.ListFirewallsRequest(
            project=project_id
        )
        firewall_list = client.list(request=request)
        
        for firewall in firewall_list:
            firewall_data = {
                "name": firewall.name,
                "id": f"{project_id}/{firewall.name}",
                "project": project_id,
                "network": firewall.network.split('/')[-1] if firewall.network else "default",
                "description": firewall.description or "",
                
                # Direction and priority
                "direction": firewall.direction,
                "priority": firewall.priority,
                
                # Rules
                "allow": [],
                "deny": [],
                
                # Sources and targets
                "source_ranges": list(firewall.source_ranges) if firewall.source_ranges else [],
                "source_tags": list(firewall.source_tags) if firewall.source_tags else [],
                "source_service_accounts": list(firewall.source_service_accounts) if firewall.source_service_accounts else [],
                "destination_ranges": list(firewall.destination_ranges) if firewall.destination_ranges else [],
                "target_tags": list(firewall.target_tags) if firewall.target_tags else [],
                "target_service_accounts": list(firewall.target_service_accounts) if firewall.target_service_accounts else [],
                
                # For resource naming
                "name_sanitized": firewall.name.replace('-', '_').lower(),
                
                # Disabled flag
                "disabled": firewall.disabled if hasattr(firewall, 'disabled') else False,
                
                # Log config
                "enable_logging": False,
            }
            
            # Process allowed rules
            if firewall.allowed:
                for rule in firewall.allowed:
                    allow_rule = {
                        "protocol": rule.I_p_protocol,
                        "ports": list(rule.ports) if rule.ports else []
                    }
                    firewall_data["allow"].append(allow_rule)
            
            # Process denied rules
            if firewall.denied:
                for rule in firewall.denied:
                    deny_rule = {
                        "protocol": rule.I_p_protocol,
                        "ports": list(rule.ports) if rule.ports else []
                    }
                    firewall_data["deny"].append(deny_rule)
            
            # Log config
            if hasattr(firewall, 'log_config') and firewall.log_config:
                firewall_data["enable_logging"] = firewall.log_config.enable
            
            firewalls.append(firewall_data)
            
    except exceptions.GoogleAPIError as e:
        typer.echo(f"Error fetching firewall rules: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return firewalls

@app.command("scan")
def scan_firewalls(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    with_deps: bool = typer.Option(False, "--with-deps")
):
    """Scans GCP firewall rules and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning GCP firewall rules with dependencies...")
        recursive_scan(
            "gcp_firewall",
            output_dir=output_dir,
            project_id=project_id
        )
    else:
        typer.echo(f"Scanning for GCP firewall rules in project '{project_id}'...")
        
        firewall_data = get_firewall_data(project_id)
        
        if not firewall_data:
            typer.echo("No firewall rules found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "gcp_firewall.tf"
        generate_tf(firewall_data, "gcp_firewall", output_file, provider="gcp")
        typer.echo(f"Generated Terraform for {len(firewall_data)} firewall rules -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "gcp_firewall",
            firewall_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_firewalls(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List all GCP firewall resources previously generated."""
    ImportManager(output_dir, "gcp_firewall").list_all()

@app.command("import")
def import_firewall(
    firewall_id: str = typer.Argument(..., help="GCP firewall ID (project/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Run terraform import for a specific GCP firewall rule."""
    ImportManager(output_dir, "gcp_firewall").find_and_import(firewall_id)

# Scan function for cross-scan registry
def scan_gcp_firewalls(
    output_dir: Path,
    project_id: Optional[str] = None,
    **kwargs
):
    """Scan function to be registered with cross-scan registry."""
    if not project_id:
        project_id = get_default_project_id()
    if not project_id:
        typer.echo("Error: No GCP project found", err=True)
        raise typer.Exit(code=1)
    
    typer.echo(f"[Cross-scan] Scanning GCP firewall rules in project {project_id}")
    
    firewall_data = get_firewall_data(project_id)
    
    if firewall_data:
        output_file = output_dir / "gcp_firewall.tf"
        generate_tf(firewall_data, "gcp_firewall", output_file, provider="gcp")
        generate_imports_file(
            "gcp_firewall",
            firewall_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(firewall_data)} GCP firewall rules")
