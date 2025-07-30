# terraback/cli/aws/__init__.py
import typer
from pathlib import Path
from typing import Optional
from . import instances, volumes, snapshots, amis, key_pairs, launch_templates, network_interfaces

app = typer.Typer(
    name="aws",
    help="Work with Amazon Web Services resources.",
    no_args_is_help=True
)

# Registration flag to avoid multiple registrations
_registered = False

def register():
    """Register all AWS resources with cross-scan registry."""
    global _registered
    if _registered:
        return
    _registered = True
    
    # Import and register AWS scan functions
    try:
        from terraback.cli.aws.ec2.instances import scan_ec2
        from terraback.utils.cross_scan_registry import register_scan_function
        register_scan_function("ec2", scan_ec2)
    except ImportError as e:
        typer.echo(f"Warning: Failed to register EC2: {e}", err=True)
    
    try:
        from terraback.cli.aws.vpc import scan_vpcs
        from terraback.utils.cross_scan_registry import register_scan_function
        register_scan_function("vpc", scan_vpcs)
    except ImportError as e:
        typer.echo(f"Warning: Failed to register VPC: {e}", err=True)
    
    try:
        from terraback.cli.aws.s3 import scan_buckets
        from terraback.utils.cross_scan_registry import register_scan_function
        register_scan_function("s3_bucket", scan_buckets)
    except ImportError as e:
        typer.echo(f"Warning: Failed to register S3: {e}", err=True)
    
    # Register dependencies
    from terraback.utils.cross_scan_registry import cross_scan_registry
    cross_scan_registry.register_dependency("ec2", "vpc")
    cross_scan_registry.register_dependency("ec2", "security_group")

@app.command("scan-all")
def scan_all_aws(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies")
):
    """Scan all AWS resources across all services."""
    # Ensure resources are registered
    register()
    
    from terraback.cli.aws.session import get_boto_session
    from terraback.core.license import check_feature_access, Tier
    
    # Get session to validate credentials
    try:
        session = get_boto_session(profile, region or "us-east-1")
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        typer.echo(f"Scanning AWS resources in account {identity['Account']}")
        if region:
            typer.echo(f"Region: {region}")
        else:
            typer.echo("Region: us-east-1 (default)")
    except Exception as e:
        typer.echo(f"Error: AWS authentication failed: {e}", err=True)
        raise typer.Exit(code=1)
    
    if with_deps:
        if check_feature_access(Tier.PROFESSIONAL):
            # Start with EC2 instances as they have the most dependencies
            from terraback.utils.cross_scan_registry import recursive_scan
            
            typer.echo("\nScanning with dependency resolution (Professional feature)...")
            recursive_scan(
                "ec2",
                output_dir=output_dir,
                profile=profile,
                region=region
            )
        else:
            typer.echo("\nDependency scanning (--with-deps) requires a Professional license")
            with_deps = False
    
    if not with_deps:
        # Scan each service independently
        typer.echo("\nScanning EC2 instances...")
        try:
            from terraback.cli.aws.ec2.instances import scan_ec2
            scan_ec2(output_dir, profile or "", region or "us-east-1")
        except ImportError:
            typer.echo("EC2 scanning not available")
        
        typer.echo("\nScanning VPC resources...")
        try:
            from terraback.cli.aws.vpc import scan_vpcs
            scan_vpcs(output_dir, profile or "", region or "us-east-1")
        except ImportError:
            typer.echo("VPC scanning not available")
        
        typer.echo("\nScanning S3 buckets...")
        try:
            from terraback.cli.aws.s3 import scan_buckets
            scan_buckets(output_dir, profile or "", region or "us-east-1")
        except ImportError:
            typer.echo("S3 scanning not available")

@app.command("list-resources")
def list_aws_resources(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import files")
):
    """List all AWS resources previously scanned."""
    from terraback.utils.importer import ImportManager
    
    resource_types = [
        "ec2",
        "vpc", 
        "security_group",
        "s3_bucket",
        "iam_role",
        "iam_policy",
    ]
    
    for resource_type in resource_types:
        import_file = output_dir / f"{resource_type}_import.json"
        if import_file.exists():
            typer.echo(f"\n=== {resource_type} ===")
            ImportManager(output_dir, resource_type).list_all()

@app.command("clean")
def clean_aws_files(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory to clean"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clean all AWS-related generated files."""
    from terraback.utils.cleanup import clean_generated_files
    
    if not yes:
        confirm = typer.confirm(f"This will delete all AWS .tf and _import.json files in {output_dir}. Continue?")
        if not confirm:
            raise typer.Abort()
    
    aws_prefixes = [
        "ec2",
        "vpc",
        "security_group", 
        "s3_bucket",
        "iam_role",
        "iam_policy",
    ]
    
    for prefix in aws_prefixes:
        clean_generated_files(output_dir, prefix)
    
    typer.echo("AWS generated files cleaned successfully!")

# Add individual resource commands
@app.command("ec2")
def ec2_command():
    """Work with EC2 instances."""
    typer.echo("Use 'terraback aws ec2-scan/ec2-list/ec2-import' commands")

@app.command("ec2-scan")
def ec2_scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan with dependencies")
):
    """Scan EC2 instances."""
    try:
        from terraback.cli.aws.ec2.instances import scan_ec2
        scan_ec2(output_dir, profile or "", region or "us-east-1")
    except ImportError:
        typer.echo("Error: EC2 scanning module not found", err=True)
        raise typer.Exit(code=1)

@app.command("ec2-list") 
def ec2_list(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List previously scanned EC2 instances."""
    from terraback.utils.importer import ImportManager
    ImportManager(output_dir, "ec2").list_all()

@app.command("ec2-import")
def ec2_import(
    instance_id: str = typer.Argument(..., help="EC2 instance ID"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific EC2 instance."""
    from terraback.utils.importer import ImportManager
    ImportManager(output_dir, "ec2").find_and_import(instance_id)
