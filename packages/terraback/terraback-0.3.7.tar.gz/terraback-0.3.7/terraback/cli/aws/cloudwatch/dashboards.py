from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_dashboards(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for CloudWatch Dashboards and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    cloudwatch_client = boto_session.client("cloudwatch")
    
    print(f"Scanning for CloudWatch Dashboards in region {region}...")
    
    # Get all dashboards using pagination
    paginator = cloudwatch_client.get_paginator('list_dashboards')
    dashboards = []
    
    for page in paginator.paginate():
        for dashboard_meta in page['DashboardEntries']:
            dashboard_name = dashboard_meta['DashboardName']
            
            try:
                # Get full dashboard details including the body
                dashboard_detail = cloudwatch_client.get_dashboard(
                    DashboardName=dashboard_name
                )
                
                # Combine metadata with detailed info
                dashboard = {
                    'DashboardName': dashboard_name,
                    'DashboardArn': dashboard_meta['DashboardArn'],
                    'LastModified': dashboard_meta['LastModified'],
                    'Size': dashboard_meta['Size'],
                    'DashboardBody': dashboard_detail['DashboardBody']
                }
                
                # Add sanitized name for resource naming
                dashboard['name_sanitized'] = dashboard_name.replace('-', '_').replace(' ', '_').replace('.', '_').lower()
                dashboards.append(dashboard)
                
            except Exception as e:
                print(f"  - Warning: Could not retrieve details for dashboard {dashboard_name}: {e}")
                continue

    output_file = output_dir / "cloudwatch_dashboard.tf"
    generate_tf(dashboards, "cloudwatch_dashboard", output_file)
    print(f"Generated Terraform for {len(dashboards)} CloudWatch Dashboards -> {output_file}")
    generate_imports_file(
        "cloudwatch_dashboard", 
        dashboards, 
        remote_resource_id_key="DashboardName", 
        output_dir=output_dir
    )

def list_dashboards(output_dir: Path):
    """Lists all CloudWatch Dashboard resources previously generated."""
    ImportManager(output_dir, "cloudwatch_dashboard").list_all()

def import_dashboard(dashboard_name: str, output_dir: Path):
    """Runs terraform import for a specific CloudWatch Dashboard by its name."""
    ImportManager(output_dir, "cloudwatch_dashboard").find_and_import(dashboard_name)