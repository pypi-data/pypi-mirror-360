# terraback/cli/gcp/storage/buckets.py
import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.cloud import storage
from google.api_core import exceptions

from terraback.cli.gcp.session import get_default_project_id, get_gcp_credentials
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

app = typer.Typer(name="bucket", help="Scan and import GCP Storage buckets.")

def get_bucket_data(project_id: str) -> List[Dict[str, Any]]:
    """Fetch storage bucket data from GCP."""
    credentials = get_gcp_credentials()
    client = storage.Client(project=project_id, credentials=credentials)
    buckets = []

    try:
        bucket_list = client.list_buckets()

        for bucket in bucket_list:
            bucket_data = {
                "name": bucket.name,
                "id": bucket.name,
                "project": project_id,
                "location": bucket.location,
                "storage_class": bucket.storage_class,
                "versioning_enabled": bucket.versioning_enabled if hasattr(bucket, 'versioning_enabled') else False,
                "lifecycle_rules": [],
                "cors": [],
                "default_kms_key_name": bucket.default_kms_key_name if hasattr(bucket, 'default_kms_key_name') else None,
                "labels": dict(bucket.labels) if bucket.labels else {},
                "retention_policy": None,
                "uniform_bucket_level_access_enabled": (
                    bucket.iam_configuration.uniform_bucket_level_access.enabled
                    if (
                        hasattr(bucket, 'iam_configuration') and
                        bucket.iam_configuration is not None and
                        hasattr(bucket.iam_configuration, 'uniform_bucket_level_access') and
                        bucket.iam_configuration.uniform_bucket_level_access is not None
                    )
                    else False
                ),
                "public_access_prevention": (
                    bucket.iam_configuration.public_access_prevention
                    if (
                        hasattr(bucket, 'iam_configuration') and
                        bucket.iam_configuration is not None and
                        hasattr(bucket.iam_configuration, 'public_access_prevention')
                    )
                    else "inherited"
                ),
                "name_sanitized": bucket.name.replace('-', '_').replace('.', '_').lower(),
                "website": None,
            }

            # Process lifecycle rules
            if hasattr(bucket, 'lifecycle_rules') and bucket.lifecycle_rules:
                for rule in bucket.lifecycle_rules:
                    lifecycle_rule = {
                        "action": {
                            "type": rule.action.type,
                            "storage_class": rule.action.storage_class if hasattr(rule.action, 'storage_class') else None
                        },
                        "condition": {}
                    }
                    if hasattr(rule.condition, 'age'):
                        lifecycle_rule["condition"]["age"] = rule.condition.age
                    if hasattr(rule.condition, 'created_before'):
                        lifecycle_rule["condition"]["created_before"] = rule.condition.created_before.isoformat()
                    if hasattr(rule.condition, 'is_live'):
                        lifecycle_rule["condition"]["is_live"] = rule.condition.is_live
                    if hasattr(rule.condition, 'matches_storage_class'):
                        lifecycle_rule["condition"]["matches_storage_class"] = list(rule.condition.matches_storage_class)
                    if hasattr(rule.condition, 'num_newer_versions'):
                        lifecycle_rule["condition"]["num_newer_versions"] = rule.condition.num_newer_versions
                    bucket_data["lifecycle_rules"].append(lifecycle_rule)

            # Process CORS configuration
            if bucket.cors:
                for cors_rule in bucket.cors:
                    cors_config = {
                        "origins": list(cors_rule.get('origin', [])),
                        "methods": list(cors_rule.get('method', [])),
                        "response_headers": list(cors_rule.get('responseHeader', [])),
                        "max_age_seconds": cors_rule.get('maxAgeSeconds', 3600)
                    }
                    bucket_data["cors"].append(cors_config)
            
            # Process retention policy safely
            if hasattr(bucket, 'retention_policy') and bucket.retention_policy:
                bucket_data["retention_policy"] = {
                    "retention_period": bucket.retention_policy.retention_period,
                    "is_locked": bucket.retention_policy.is_locked
                }
            
            # Process website configuration
            if hasattr(bucket, 'website') and bucket.website:
                bucket_data["website"] = {
                    "main_page_suffix": bucket.website.get('mainPageSuffix'),
                    "not_found_page": bucket.website.get('notFoundPage')
                }
            
            buckets.append(bucket_data)
            
    except exceptions.GoogleAPIError as e:
        typer.echo(f"Error fetching buckets: {str(e)}", err=True)
        raise typer.Exit(code=1)
    
    return buckets

@app.command("scan")
def scan_buckets(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    with_deps: bool = typer.Option(False, "--with-deps")
):
    """Scans GCP Storage buckets and generates Terraform code."""
    from terraback.utils.cross_scan_registry import recursive_scan
    
    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        typer.echo("Scanning GCP buckets with dependencies...")
        recursive_scan(
            "gcp_bucket",
            output_dir=output_dir,
            project_id=project_id
        )
    else:
        typer.echo(f"Scanning for GCP buckets in project '{project_id}'...")
        
        bucket_data = get_bucket_data(project_id)
        
        if not bucket_data:
            typer.echo("No buckets found.")
            return
        
        # Generate Terraform files
        output_file = output_dir / "gcp_bucket.tf"
        generate_tf(bucket_data, "gcp_bucket", output_file, provider="gcp")
        typer.echo(f"Generated Terraform for {len(bucket_data)} buckets -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "gcp_bucket",
            bucket_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )

@app.command("list")
def list_buckets(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List all GCP bucket resources previously generated."""
    ImportManager(output_dir, "gcp_bucket").list_all()

@app.command("import")
def import_bucket(
    bucket_name: str = typer.Argument(..., help="GCP bucket name"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Run terraform import for a specific GCP bucket."""
    ImportManager(output_dir, "gcp_bucket").find_and_import(bucket_name)

# Scan function for cross-scan registry
def scan_gcp_buckets(
    output_dir: Path,
    project_id: str = None,
    **kwargs
):
    """Scan function to be registered with cross-scan registry."""
    if not project_id:
        project_id = get_default_project_id()
    
    typer.echo(f"[Cross-scan] Scanning GCP buckets in project {project_id}")
    
    bucket_data = get_bucket_data(project_id)
    
    if bucket_data:
        output_file = output_dir / "gcp_bucket.tf"
        generate_tf(bucket_data, "gcp_bucket", output_file, provider="gcp")
        generate_imports_file(
            "gcp_bucket",
            bucket_data,
            remote_resource_id_key="id",
            output_dir=output_dir
        )
        typer.echo(f"[Cross-scan] Generated Terraform for {len(bucket_data)} GCP buckets")