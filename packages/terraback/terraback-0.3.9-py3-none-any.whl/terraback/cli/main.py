import typer
from pathlib import Path
from typing import Optional
import asyncio

from terraback.utils.logging import setup_logging, get_logger
setup_logging()
logger = get_logger(__name__)

# Clean provider imports
from terraback.cli import aws, azure, gcp

# Import command modules
from terraback.cli.commands.clean import app as clean_app
from terraback.cli.commands.list import app as list_app
from terraback.cli.commands.analyse import app as analyse_app

# Import licensing
from terraback.core.license import (
    activate_license, get_active_license, get_active_tier, get_license_status,
    require_professional, require_enterprise, check_feature_access, Tier,
    start_free_trial, is_trial_active, get_trial_info
)

# Import the updated imports module
from terraback.terraform_generator.imports import read_import_file, validate_import_file
from terraback.import_workflows import import_with_blocks
from terraback.utils.import_workflows import (
    import_with_commands,
    import_with_workspaces,
)
from terraback.utils import terraform_checker
from terraback.terraform_generator.filters import strip_id_prefix, to_terraform_resource_name

cli = typer.Typer(
    name="terraback",
    help=(
        "Terraback: A tool to generate Terraform from existing cloud infrastructure. "
        "Logging is configured using TERRABACK_LOG_LEVEL and TERRABACK_LOG_FILE."
    ),
    no_args_is_help=True,
)

# License Command Group
license_app = typer.Typer(help="Manage your Terraback license.")

@license_app.command("status")
def license_status():
    """Check the current license status and tier with validation details."""
    status = get_license_status()

    typer.echo(f"Active Feature Tier: {typer.style(status['active_tier'].capitalize(), bold=True)}")

    if status['has_license']:
        typer.secho("\nLicense Details:", fg=typer.colors.GREEN)
        typer.echo(f"  - Email: {status.get('email', 'N/A')}")
        typer.echo(f"  - Tier: {status.get('tier', 'N/A').capitalize()}")
        typer.echo(f"  - Expires: {status.get('expires', 'N/A')}")
        if status.get('order_id'):
            typer.echo(f"  - Order ID: {status.get('order_id')}")

        # Show trial info if present
        if status.get('is_trial'):
            typer.secho(f"\n  Free Trial Active! Days remaining: {status.get('days_remaining', 0)}", fg=typer.colors.YELLOW)

        if 'days_since_online_validation' in status:
            days_since = status['days_since_online_validation']
            validation_count = status.get('validation_count', 0)

            typer.echo(f"\nValidation Status:")
            typer.echo(f"  - Days since last online check: {days_since}")
            typer.echo(f"  - Total validations performed: {validation_count}")

            from terraback.core.license import ValidationSettings

            if days_since >= ValidationSettings.MAX_OFFLINE_DAYS:
                typer.secho("  VALIDATION REQUIRED - Connect to internet", fg=typer.colors.RED, bold=True)
            elif days_since >= ValidationSettings.OFFLINE_GRACE_DAYS:
                remaining = ValidationSettings.MAX_OFFLINE_DAYS - days_since
                typer.secho(f"  Please connect to internet soon ({remaining} days remaining)", fg=typer.colors.YELLOW)
            elif days_since >= ValidationSettings.VALIDATION_INTERVAL_DAYS:
                typer.secho("  Validation recommended - connect to internet", fg=typer.colors.YELLOW)
            else:
                typer.secho("  Validation up to date", fg=typer.colors.GREEN)

    else:
        typer.secho("\nNo active license key found.", fg=typer.colors.YELLOW)
        typer.echo("Running in Community mode.")
        typer.echo("\nCommunity Edition includes:")
        typer.echo("  Unlimited core resources (EC2, VPC, S3, VMs, VNets, Storage)")
        typer.echo("  Basic dependency mapping")
        typer.echo("  Multi-cloud support (AWS, Azure, GCP)")
        typer.echo("  Community support via GitHub")
        typer.echo("\nTo unlock advanced services (RDS, Lambda, EKS, etc.):")
        typer.echo("  Get Migration Pass: https://terraback.io/pricing")
        typer.echo("  Activate license: terraback license activate <key>")
        typer.echo("\nOr start your free 30-day Professional trial:")
        typer.echo("  terraback trial start")

@license_app.command("activate")
def license_activate(key: str = typer.Argument(..., help="Your license key.")):
    """Activate a new license key with enhanced security."""
    if activate_license(key):
        typer.secho("License activated successfully!", fg=typer.colors.GREEN, bold=True)
        typer.echo()

        status = get_license_status()
        if status['has_license']:
            typer.echo(f"Licensed to: {status.get('email', 'N/A')}")
            typer.echo(f"Tier: {status.get('tier', 'N/A').capitalize()}")
            typer.echo(f"Expires: {status.get('expires', 'N/A')}")

            from terraback.core.license import _get_machine_fingerprint
            fingerprint = _get_machine_fingerprint()
            typer.echo(f"Machine fingerprint: {fingerprint[:8]}... (for security)")
            typer.echo("\nYour license is now protected with:")
            typer.echo("  Machine fingerprinting")
            typer.echo("  Periodic online validation")
            typer.echo("  Clock tampering detection")

    else:
        typer.secho("License activation failed.", fg=typer.colors.RED, bold=True)
        typer.echo("Please check that:")
        typer.echo("  - The license key is copied correctly")
        typer.echo("  - The license hasn't expired")
        typer.echo("  - You have internet connection")
        typer.echo("  - The license hasn't been activated on another machine")
        typer.echo("\nIf you continue to have issues, contact support@terraback.io")
        raise typer.Exit(code=1)

@license_app.command("refresh")
def license_refresh():
    """Force online license validation to refresh local data."""
    from terraback.core.license import force_license_refresh

    typer.echo("Attempting to refresh license validation...")

    if force_license_refresh():
        typer.secho("License validation refreshed successfully", fg=typer.colors.GREEN)

        status = get_license_status()
        if 'days_since_online_validation' in status:
            typer.echo(f"Last validation: just now")
            typer.echo(f"Total validations: {status.get('validation_count', 0)}")
    else:
        typer.secho("License refresh failed", fg=typer.colors.RED)
        typer.echo("This could be due to:")
        typer.echo("  - No internet connection")
        typer.echo("  - License has expired or been revoked")
        typer.echo("  - Server maintenance")
        typer.echo("\nTry again later or contact support@terraback.io")
        raise typer.Exit(code=1)

@license_app.command("doctor")
def license_doctor():
    """Run comprehensive license diagnostics."""
    from terraback.core.license import (
        get_license_path, get_metadata_path, get_validation_path,
        _is_online, _get_machine_fingerprint, get_validation_info
    )

    typer.echo("Running license diagnostics...\n")

    typer.echo("License Files:")
    license_path = get_license_path()
    metadata_path = get_metadata_path()
    validation_path = get_validation_path()

    files_status = [
        (license_path, "license.jwt"),
        (metadata_path, "license_metadata.json"),
        (validation_path, "license_validation.enc")
    ]

    for path, name in files_status:
        if path.exists():
            size = path.stat().st_size
            typer.echo(f"  Found {name} ({size} bytes)")
        else:
            typer.echo(f"  Missing {name}")

    typer.echo(f"\nConnectivity:")
    is_online = _is_online()
    if is_online:
        typer.echo("  Internet connection available")
    else:
        typer.echo("  No internet connection")

    typer.echo(f"\nLicense Status:")
    license_data = get_active_license()
    if license_data:
        typer.echo("  Valid license found")
        typer.echo(f"  - Tier: {license_data.get('tier', 'unknown')}")
        typer.echo(f"  - Expires: {license_data.get('expiry', 'unknown')}")
    else:
        typer.echo("  No valid license")

    typer.echo(f"\nValidation Status:")
    validation_info = get_validation_info()

    if 'days_since_online' in validation_info:
        days = validation_info['days_since_online']
        typer.echo(f"  - Days since last validation: {days}")
        typer.echo(f"  - Validation count: {validation_info.get('validation_count', 0)}")

        if validation_info.get('validation_status') == 'valid':
            typer.echo("  Validation status: Valid")
        else:
            typer.echo("  Validation status: Expired")
    else:
        typer.echo("  No validation data found")

    typer.echo(f"\nSecurity:")
    fingerprint = _get_machine_fingerprint()
    typer.echo(f"  - Machine fingerprint: {fingerprint[:12]}...")

    typer.echo(f"\nRecommendations:")

    if not license_data:
        typer.echo("  - Activate a license with: terraback license activate <key>")
        typer.echo("  - Or start a free trial: terraback trial start")
    elif validation_info.get('needs_validation') and is_online:
        typer.echo("  - Refresh validation with: terraback license refresh")
    elif validation_info.get('needs_validation') and not is_online:
        typer.echo("  - Connect to internet and run: terraback license refresh")
    elif validation_info.get('in_grace_period'):
        typer.echo("  - Connect to internet soon to avoid service interruption")
    else:
        typer.echo("  - License system is working correctly")

# ----------------------- TRIAL COMMAND GROUP ----------------------
trial_app = typer.Typer(help="Free trial management")

@trial_app.command("start")
def trial_start():
    """Start a free 30-day Professional trial if available."""
    if is_trial_active():
        info = get_trial_info()
        typer.secho("Trial is already active.", fg=typer.colors.YELLOW)
        typer.echo(f"Expires: {info.get('end_date', 'N/A')}")
        typer.echo(f"Days remaining: {info.get('days_remaining', 0)}")
        return
    if start_free_trial():
        typer.secho("Free trial activated!", fg=typer.colors.GREEN)
        info = get_trial_info()
        if info:
            typer.echo(f"Expires: {info.get('end_date', 'N/A')}")
            typer.echo(f"Days remaining: {info.get('days_remaining', 0)}")
    else:
        typer.secho("Could not start free trial.", fg=typer.colors.RED)
# ------------------------------------------------------------------

# Cache Command Group
cache_app = typer.Typer(help="Manage terraback cache")

@cache_app.command("stats")
def cache_stats():
    """Show cache statistics."""
    from terraback.utils.scan_cache import get_scan_cache

    cache = get_scan_cache()
    stats = cache.get_stats()

    typer.echo("\nCache Statistics:")
    typer.echo(f"  Hit Rate: {stats['hit_rate']}")
    typer.echo(f"  Total Hits: {stats['hits']}")
    typer.echo(f"  Total Misses: {stats['misses']}")
    typer.echo(f"  Cache Size: {stats['total_size_kb']} KB")
    typer.echo(f"  Memory Cache Items: {stats['memory_cache_size']}")
    typer.echo(f"  TTL: {stats['ttl_minutes']:.0f} minutes")

@cache_app.command("clear")
def cache_clear(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clear all cached data."""
    from terraback.utils.scan_cache import get_scan_cache

    if not confirm:
        confirm = typer.confirm("Are you sure you want to clear all cached data?")

    if confirm:
        cache = get_scan_cache()
        cache.clear()
        typer.echo("Cache cleared successfully!")
    else:
        typer.echo("Cache clear cancelled.")

@cache_app.command("invalidate")
def cache_invalidate(
    service: Optional[str] = typer.Option(None, help="Cloud service name (e.g., ec2, s3)"),
    operation: Optional[str] = typer.Option(None, help="Operation name (e.g., describe_instances)")
):
    """Invalidate specific cache entries."""
    from terraback.utils.scan_cache import get_scan_cache

    cache = get_scan_cache()
    count = cache.invalidate_pattern(service, operation)

    if service and operation:
        typer.echo(f"Invalidated {count} cache entries for {service}:{operation}")
    elif service:
        typer.echo(f"Invalidated {count} cache entries for service: {service}")
    elif operation:
        typer.echo(f"Invalidated {count} cache entries for operation: {operation}")
    else:
        typer.echo(f"Invalidated {count} cache entries")

# Add command groups to main cli
cli.add_typer(aws.app, name="aws", help="Amazon Web Services resources")
cli.add_typer(azure.app, name="azure", help="Microsoft Azure resources")
cli.add_typer(gcp.app, name="gcp", help="Google Cloud Platform resources")
cli.add_typer(clean_app, name="clean", help="Clean generated files")
cli.add_typer(list_app, name="list", help="List scanned resources")
cli.add_typer(analyse_app, name="analyse", help="Analyse Terraform state")
cli.add_typer(license_app, name="license", help="License management")
cli.add_typer(trial_app, name="trial", help="Free trial management")
cli.add_typer(cache_app, name="cache", help="Cache management")

@cli.command("scan-all")
def scan_all(
    provider: str = typer.Argument(..., help="Cloud provider: 'aws', 'azure', or 'gcp'"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory to save Terraform files"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region, Azure location, or GCP region"),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure subscription ID"),
    project_id: Optional[str] = typer.Option(None, "--project-id", help="GCP project ID"),
    resource_group: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Azure resource group"),
    zone: Optional[str] = typer.Option(None, "--zone", "-z", help="GCP zone"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies (Professional feature)"),
    parallel: int = typer.Option(1, "--parallel", help="Number of parallel workers (1-32)"),
    check: bool = typer.Option(True, "--check/--skip-check", help="Validate Terraform after scan"),
    cache_ttl: int = typer.Option(60, "--cache-ttl", help="Cache TTL in minutes")
):
    """Scan all resources for a specific cloud provider.

    The ``--cache-ttl`` option sets how long scan data is cached (in minutes)
    to speed up repeated scans.
    """
    provider = provider.lower()

    # Initialize cache with custom TTL before any scanning occurs
    from datetime import timedelta
    from terraback.utils.scan_cache import get_scan_cache
    get_scan_cache(ttl=timedelta(minutes=cache_ttl))
    
    # Validate parallel workers
    if parallel < 1:
        typer.echo("Warning: Parallel workers must be at least 1. Setting to 1.", err=True)
        parallel = 1
    elif parallel > 32:
        typer.echo("Warning: Limiting parallel workers to 32 for stability.", err=True)
        parallel = 32
    
    # Show parallel mode if enabled
    if parallel > 1:
        typer.secho(f"Parallel mode enabled with {parallel} workers", fg=typer.colors.BRIGHT_GREEN, bold=True)
    
    # If --with-deps is requested but user doesn't have license, show clear message once
    if with_deps:
        from terraback.core.license import check_feature_access, Tier
        if not check_feature_access(Tier.PROFESSIONAL):
            typer.echo("\nDependency scanning (--with-deps) requires a Professional license")
            typer.echo("Proceeding with independent scanning of each service...")
            typer.echo("To unlock dependency scanning: terraback license activate <key> or terraback trial start\n")

    if provider == "aws":
        aws.register()
        from terraback.cli.aws import scan_all_aws
        scan_all_aws(
            output_dir=output_dir,
            profile=profile,
            region=region,
            with_deps=with_deps,
            parallel=parallel,
            check=check
        )
    elif provider == "azure":
        azure.register()
        from terraback.cli.azure import scan_all_azure
        scan_all_azure(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=region,
            resource_group_name=resource_group,
            with_deps=with_deps,
            parallel=parallel,
            check=check
        )
    elif provider == "gcp":
        gcp.register()
        from terraback.cli.gcp import scan_all_gcp
        scan_all_gcp(
            output_dir=output_dir,
            project_id=project_id,
            region=region,
            zone=zone,
            with_deps=with_deps,
            parallel=parallel,
            check=check
        )
    else:
        typer.echo(f"Error: Unknown provider '{provider}'. Use 'aws', 'azure', or 'gcp'.", err=True)
        raise typer.Exit(code=1) 
    
@cli.command("scan-recursive")
@require_professional
def scan_recursive(
    resource_type: str = typer.Argument(..., help="Initial resource type to scan"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s"),
    project_id: Optional[str] = typer.Option(None, "--project-id"),
    zone: Optional[str] = typer.Option(None, "--zone", "-z"),
    use_cache: bool = typer.Option(True, "--cache/--no-cache"),
    cache_ttl: int = typer.Option(60, "--cache-ttl", help="Cache TTL in minutes")
):
    """(Professional Feature) Recursively scan cloud resources with smart dependency resolution."""
    from datetime import timedelta
    from terraback.utils.scan_cache import get_scan_cache
    from terraback.utils.cross_scan_registry import recursive_scan as base_recursive_scan

    resource_type_map = {
        'vm': 'azure_virtual_machine',
        'vms': 'azure_virtual_machine',
        'disk': 'azure_managed_disk',
        'disks': 'azure_managed_disk',
        'vnet': 'azure_virtual_network',
        'vnets': 'azure_virtual_network',
        'subnet': 'azure_subnet',
        'subnets': 'azure_subnet',
        'nsg': 'azure_network_security_group',
        'nsgs': 'azure_network_security_group',
        'instance': 'ec2',
        'instances': 'ec2',
        'bucket': 's3_bucket',
        'buckets': 's3_bucket',
        'gcp_vm': 'gcp_instance',
        'gcp_vms': 'gcp_instance',
        'gcp_bucket': 'gcp_bucket',
        'gcp_buckets': 'gcp_bucket',
    }

    normalized_type = resource_type_map.get(resource_type.lower(), resource_type.lower())
    typer.echo(f"Starting Professional recursive scan for '{normalized_type}'...")

    is_azure = normalized_type.startswith('azure_')
    is_gcp = normalized_type.startswith('gcp_')

    if is_azure:
        azure.register()
    elif is_gcp:
        gcp.register()
    else:
        aws.register()

    kwargs = {
        'resource_type': normalized_type,
        'output_dir': output_dir
    }

    if is_azure:
        from terraback.cli.azure.session import get_default_subscription_id
        if not subscription_id:
            subscription_id = get_default_subscription_id()
            if not subscription_id:
                typer.echo("Error: No Azure subscription found. Please run 'az login'", err=True)
                raise typer.Exit(code=1)
        kwargs['subscription_id'] = subscription_id
        kwargs['location'] = region
    elif is_gcp:
        from terraback.cli.gcp.session import get_default_project_id
        if not project_id:
            project_id = get_default_project_id()
            if not project_id:
                typer.echo("Error: No GCP project found. Please run 'gcloud config set project'", err=True)
                raise typer.Exit(code=1)
        kwargs['project_id'] = project_id
        kwargs['region'] = region
        kwargs['zone'] = zone
    else:
        from terraback.cli.common.defaults import get_aws_defaults
        defaults = get_aws_defaults()
        kwargs['profile'] = profile or defaults['profile']
        kwargs['region'] = region or defaults['region']

    if use_cache:
        cache = get_scan_cache(
            cache_dir=output_dir / ".terraback" / "cache",
            ttl=timedelta(minutes=cache_ttl)
        )
        typer.echo(f"Caching enabled (TTL: {cache_ttl} minutes)")

    base_recursive_scan(**kwargs)

    if use_cache:
        stats = cache.get_stats()
        typer.echo(f"\nCache Statistics:")
        typer.echo(f"  Hit Rate: {stats['hit_rate']}")
        typer.echo(f"  Cache Size: {stats['total_size_kb']} KB")

@cli.command("auth-check")
def check_auth():
    """Check authentication status for all cloud providers."""
    typer.echo("Checking cloud authentication status...\n")

    try:
        from terraback.cli.aws.session import get_boto_session
        session = get_boto_session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        typer.echo("AWS: Authenticated")
        typer.echo(f"  Account: {identity['Account']}")
        typer.echo(f"  User/Role: {identity['Arn'].split('/')[-1]}")
        typer.echo(f"  Region: {session.region_name}")
    except Exception:
        typer.echo("AWS: Not authenticated (run: aws configure)")

    try:
        from terraback.cli.azure.session import get_default_subscription_id
        sub_id = get_default_subscription_id()
        if sub_id:
            typer.echo("\nAzure: Authenticated")
            typer.echo(f"  Subscription: {sub_id}")
        else:
            typer.echo("\nAzure: Not authenticated (run: az login)")
    except Exception:
        typer.echo("\nAzure: Not authenticated (run: az login)")

    try:
        from terraback.cli.gcp.session import get_default_project_id
        project_id = get_default_project_id()
        if project_id:
            typer.echo("\nGCP: Authenticated")
            typer.echo(f"  Project: {project_id}")
        else:
            typer.echo("\nGCP: Not authenticated (run: gcloud auth application-default login)")
    except Exception:
        typer.echo("\nGCP: Not authenticated (run: gcloud auth application-default login)")

@cli.command("upgrade")
def upgrade_info():
    """Show information about upgrading to Professional features."""
    current_tier = get_active_tier()

    if current_tier == Tier.COMMUNITY:
        typer.echo("Upgrade to Professional for Advanced Features\n")

        typer.echo("Your Current Plan: Community Edition (Free)")
        typer.echo("  - Unlimited core resources (EC2, VPC, S3, VMs, VNets, Storage)")
        typer.echo("  - Multi-cloud support (AWS, Azure, GCP)")
        typer.echo("  - Basic dependency mapping\n")

        typer.echo("Unlock with Migration Pass ($299 for 3 months):")
        typer.echo("  - Advanced AWS services (RDS, Lambda, EKS, ALB, Route53, etc.)")
        typer.echo("  - Recursive dependency scanning (--with-deps)")
        typer.echo("  - Multi-account/subscription support")
        typer.echo("  - Priority email support")
        typer.echo("  - Advanced caching and performance features\n")

        typer.echo("Get Migration Pass: https://terraback.io/pricing")
        typer.echo("Enterprise needs: sales@terraback.io")
        typer.echo("\nOr start your free 30-day trial: terraback trial start")
    elif current_tier == Tier.PROFESSIONAL:
        typer.secho("You have Professional access!", fg=typer.colors.GREEN, bold=True)
        typer.echo("All advanced features are unlocked.")
    elif current_tier == Tier.ENTERPRISE:
        typer.secho("You have Enterprise access!", fg=typer.colors.GREEN, bold=True)
        typer.echo("All features including enterprise support are available.")

def _ensure_resource_blocks(directory: Path, resources):
    """Ensure minimal resource blocks exist for all resources to be imported."""
    import re
    import json
    
    # Define minimal required fields for various resource types
    REQUIRED_FIELDS = {
        'aws_api_gateway_deployment': {
            'rest_api_id': lambda r: r['id'].split('/')[0] if '/' in r['id'] else 'unknown'
        },
        'aws_api_gateway_method': {
            'rest_api_id': lambda r: r['id'].split('/')[0] if '/' in r['id'] else 'unknown',
            'resource_id': lambda r: r['id'].split('/')[1] if '/' in r['id'] else 'unknown',
            'http_method': lambda r: r['id'].split('/')[2] if '/' in r['id'] else 'GET'
        },
        'aws_api_gateway_resource': {
            'rest_api_id': lambda r: r['id'].split('/')[0] if '/' in r['id'] else 'unknown',
            'parent_id': lambda r: 'unknown',
            'path_part': lambda r: 'unknown'
        },
        'aws_api_gateway_rest_api': {
            'name': lambda r: r['name'] if 'name' in r else r['id']
        },
        'aws_route53_record': {
            'zone_id': lambda r: r['id'].split('_')[0] if '_' in r['id'] else 'unknown',
            'name': lambda r: 'unknown',
            'type': lambda r: 'A',
            'records': lambda r: ['127.0.0.1'],
            'ttl': lambda r: 300,
        },
        'aws_route53_zone': {
            'name': lambda r: 'example.com'
        },
        'aws_route_table': {
            'vpc_id': lambda r: 'vpc-unknown'
        },
        'aws_secretsmanager_secret_version': {
            'secret_id': lambda r: r['name'].rsplit('_', 2)[0] if '_' in r['name'] else 'unknown'
        },
        'aws_sns_topic_subscription': {
            'topic_arn': lambda r: 'arn:aws:sns:us-east-1:000000000000:unknown',
            'protocol': lambda r: 'email',
            'endpoint': lambda r: 'example@example.com'
        },
        'aws_acm_certificate': {
            'domain_name': lambda r: 'example.com'
        },
        'aws_instance': {
            'ami': lambda r: 'ami-12345678',
            'instance_type': lambda r: 't2.micro'
        },
        'aws_security_group': {
            'name': lambda r: r['name'] if 'name' in r else 'unknown'
        },
        'aws_subnet': {
            'vpc_id': lambda r: 'vpc-unknown',
            'cidr_block': lambda r: '10.0.0.0/24'
        },
        'aws_vpc': {
            'cidr_block': lambda r: '10.0.0.0/16'
        }
    }
    
    # First, scan all existing .tf files to find what resources already exist
    all_existing_resources = set()
    resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"'
    
    for tf_file in directory.glob("*.tf"):
        try:
            with open(tf_file, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(resource_pattern, content)
                for resource_type, resource_name in matches:
                    all_existing_resources.add(f"{resource_type}.{resource_name}")
        except Exception as e:
            typer.echo(f"Warning: Could not read {tf_file}: {e}")
    
    stub_file = directory / "terraback_import_stubs.tf"
    existing_blocks = set()
    
    # Read existing stubs if any, to avoid duplicates
    if stub_file.exists():
        try:
            with open(stub_file, "r", encoding="utf-8") as f:
                content = f.read()
                matches = re.findall(resource_pattern, content)
                for resource_type, resource_name in matches:
                    existing_blocks.add(f'resource "{resource_type}" "{resource_name}"')
        except Exception as e:
            typer.echo(f"Warning: Could not read {stub_file}: {e}")
    
    stubs = []
    stubs_created = 0
    
    for imp in resources:
        # Handle the key names from all_imports structure
        resource_type = imp.get('type', imp.get('resource_type'))
        resource_name = imp.get('name', imp.get('resource_name'))
        resource_id = imp.get('id', imp.get('remote_id'))
        
        if not resource_type or not resource_name:
            typer.echo(f"Warning: Skipping resource with missing type or name: {imp}")
            continue
        
        # Check if resource already exists in any .tf file
        resource_address = f"{resource_type}.{resource_name}"
        if resource_address in all_existing_resources:
            continue  # Resource already exists
        
        # Compose a minimal resource block
        resource_decl = f'resource "{resource_type}" "{resource_name}"'
        if resource_decl in existing_blocks:
            continue  # skip duplicate
        
        # Build the stub with required fields
        stub_lines = [f'resource "{resource_type}" "{resource_name}" {{']
        
        # Add required fields based on resource type
        if resource_type in REQUIRED_FIELDS:
            fields = REQUIRED_FIELDS[resource_type]
            for field_name, field_func in fields.items():
                try:
                    # Create a resource object with all available data
                    resource_obj = {
                        'id': resource_id,
                        'name': resource_name,
                        'type': resource_type,
                        **imp  # Include all other fields from import data
                    }
                    field_value = field_func(resource_obj)
                    if isinstance(field_value, (list, dict)):
                        serialized = json.dumps(field_value)
                        stub_lines.append(f'  {field_name} = {serialized}')
                    elif isinstance(field_value, bool):
                        stub_lines.append(f'  {field_name} = {str(field_value).lower()}')
                    elif isinstance(field_value, (int, float)):
                        stub_lines.append(f'  {field_name} = {field_value}')
                    else:
                        stub_lines.append(f'  {field_name} = "{field_value}"')
                except Exception as e:
                    typer.echo(f"Warning: Could not determine {field_name} for {resource_type}: {e}")
                    stub_lines.append(f'  {field_name} = "unknown"')
        
        stub_lines.append('  # (auto-generated stub for import - update with actual values)')
        stub_lines.append('}')
        stub_lines.append('')  # Empty line between resources
        
        stubs.append('\n'.join(stub_lines))
        stubs_created += 1
    
    if stubs:
        try:
            with open(stub_file, "a", encoding="utf-8") as f:
                f.write('\n'.join(stubs))
            typer.echo(f"Created {stubs_created} stub resource blocks in {stub_file.name}")
        except Exception as e:
            typer.echo(f"Error writing to {stub_file}: {e}")
    
    return stubs_created


def _verify_import_entries(entries) -> bool:
    """Verify provider metadata for each import entry."""
    from terraback.cli.aws.session import get_boto_session

    aws_sessions = {}
    aws_accounts = {}
    errors = []

    for imp in entries:
        provider = (imp.get('type') or '').split('_')[0]
        meta = imp.get('provider_metadata') or {}

        if provider == 'aws':
            region = meta.get('region') or 'us-east-1'
            session = aws_sessions.get(region)
            account = aws_accounts.get(region)
            if session is None:
                session = get_boto_session(region=region)
                aws_sessions[region] = session
                try:
                    account = session.client('sts').get_caller_identity().get('Account')
                except Exception:
                    account = None
                aws_accounts[region] = account

            expected_account = meta.get('account_id')
            if expected_account and account and expected_account != account:
                errors.append(
                    f"Account mismatch for {imp.get('address', imp.get('id'))}: expected {expected_account}, got {account}"
                )
            expected_region = meta.get('region')
            if expected_region and expected_region != region:
                errors.append(
                    f"Region mismatch for {imp.get('address', imp.get('id'))}: expected {expected_region}, got {region}"
                )

    if errors:
        typer.echo("Verification errors:")
        for err in errors:
            typer.echo(f"  - {err}")
        return False
    return True

@cli.command("import")
def import_resource(
    resource_type: str = typer.Argument(..., help="Resource type (e.g., ec2, vpc, azure_vm, gcp_instance)"),
    resource_id: str = typer.Argument(..., help="Resource ID to import"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing generated files"),
    terraform_dir: Path = typer.Option(None, "--terraform-dir", "-t", help="Terraform directory (defaults to output_dir)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show terraform import command without running it"),
    create_stub: bool = typer.Option(True, "--create-stub/--no-create-stub", help="Create stub resource if missing"),
    verify: bool = typer.Option(False, "--verify", help="Verify resource before importing"),
):
    """Import a specific cloud resource into Terraform state."""
    import subprocess

    if terraform_dir is None:
        terraform_dir = output_dir

    # Find the corresponding import file
    import_file = output_dir / f"{resource_type}_import.json"
    if not import_file.exists():
        typer.echo(f"Error: No import file found for {resource_type}. Run scan first.", err=True)
        raise typer.Exit(code=1)

    # Use the updated read_import_file function
    try:
        resources, read_error = read_import_file(import_file)
    except Exception as e:
        typer.echo(f"Error reading {import_file.name}: {e}", err=True)
        raise typer.Exit(code=1)
    if read_error:
        typer.echo(f"Error reading {import_file.name}: {read_error}", err=True)
        raise typer.Exit(code=1)

    matching_resource = None
    for resource in resources:
        if resource.get('remote_id') == resource_id:
            matching_resource = resource
            break

    if not matching_resource:
        typer.echo(f"Error: Resource {resource_id} not found in {resource_type} import file.", err=True)
        typer.echo("Available resources:")
        for r in resources[:5]:
            typer.echo(f"  - {r.get('remote_id')}")
        if len(resources) > 5:
            typer.echo(f"  ... and {len(resources) - 5} more")
        raise typer.Exit(code=1)

    resource_name = matching_resource.get('resource_name')
    terraform_resource_type = matching_resource.get('resource_type')
    terraform_address = f"{terraform_resource_type}.{resource_name}"

    if verify:
        entry = {
            'type': terraform_resource_type,
            'name': resource_name,
            'id': resource_id,
            'address': terraform_address,
            'provider_metadata': matching_resource.get('provider_metadata'),
        }
        if not _verify_import_entries([entry]):
            raise typer.Exit(code=1)

    # Check if resource exists in Terraform files
    resource_exists = False
    for tf_file in terraform_dir.glob("*.tf"):
        with open(tf_file, 'r') as f:
            if f'resource "{terraform_resource_type}" "{resource_name}"' in f.read():
                resource_exists = True
                break
    
    if not resource_exists and create_stub:
        typer.echo(f"Resource {terraform_address} not found in Terraform files.")
        typer.echo("Creating stub resource...")
        _ensure_resource_blocks(terraform_dir, [matching_resource])

    import_cmd = [
        "terraform",
        "import",
        terraform_address,
        resource_id
    ]

    typer.echo(f"Importing {terraform_resource_type} resource: {resource_id}")
    typer.echo(f"Terraform address: {terraform_address}")

    if dry_run:
        typer.echo("\nDry run - would execute:")
        typer.echo(" ".join(import_cmd))
        return

    if not _check_terraform_installation():
        raise typer.Exit(code=1)

    if not (terraform_dir / ".terraform").exists():
        typer.echo("\nTerraform not initialized. Running 'terraform init'...")
        success, error = _safe_terraform_init(terraform_dir)
        if not success:
            raise typer.Exit(code=1)

    typer.echo("\nRunning terraform import...")
    result = subprocess.run(
        import_cmd,
        cwd=terraform_dir,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        typer.secho("Import successful!", fg=typer.colors.GREEN)
        typer.echo(result.stdout)
    else:
        typer.secho("Import failed!", fg=typer.colors.RED)
        typer.echo(result.stderr)
        
        # Check for common errors and provide guidance
        if "does not exist in the configuration" in result.stderr:
            typer.echo("\nThe resource definition is missing from your .tf files.")
            typer.echo("Run with --create-stub to automatically create it.")
        elif "Cannot import non-existent remote object" in result.stderr:
            typer.echo("\nThe resource no longer exists in your cloud provider.")
            typer.echo("It may have been deleted since the scan was performed.")
        
        raise typer.Exit(code=1)

@cli.command("import-all")
def import_all_resources(
    output_dir: Optional[Path] = typer.Option(None, "-o", "--output-dir", help="Directory containing import files (defaults to current dir)"),
    terraform_dir: Optional[Path] = typer.Option(None, "--terraform-dir", "-t", help="Terraform directory (defaults to output_dir)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be imported without doing it"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
    parallel: int = typer.Option(1, "--parallel", "-p", help="Number of parallel imports"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate import files before processing"),
    create_stubs: bool = typer.Option(True, "--create-stubs/--no-create-stubs", help="Create stub resources for missing definitions"),
    progress: bool = typer.Option(True, "--progress/--no-progress", help="Show progress bar during import"),
    async_mode: bool = typer.Option(False, "--async/--no-async", help="Use asyncio for imports instead of threads"),
    verify: bool = typer.Option(False, "--verify", help="Verify resources before importing"),
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow",
        help="Import workflow: 'import', 'import-blocks', or 'workspaces'",
    ),
    batch_size: Optional[int] = typer.Option(
        1,
        "--batch-size",
        help="Number of resources per workspace when using the 'workspaces' workflow",
    ),
):
    """Import all previously scanned resources into Terraform state.

    By default imports run in a thread pool. Use ``--async`` to execute
    import commands concurrently using :mod:`asyncio` for improved performance.
    The ``--progress`` flag shows a progress bar while resources are imported.
    On Windows with Python versions older than 3.8 the command automatically
    falls back to the threaded implementation when ``--async`` is used.
    """
    import subprocess
    import os
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if not isinstance(async_mode, bool):
        async_mode = bool(async_mode.default)
    if not isinstance(progress, bool):
        progress = bool(progress.default)
    if not isinstance(create_stubs, bool):
        create_stubs = bool(create_stubs.default)

    # Use current working directory if output_dir not specified
    if output_dir is None:
        output_dir = Path(os.getcwd())
    else:
        output_dir = Path(output_dir).resolve()

    # Use output_dir as terraform_dir if not specified
    if terraform_dir is None:
        terraform_dir = output_dir
    else:
        terraform_dir = Path(terraform_dir).resolve()

    typer.echo(f"Looking for import files in: {output_dir}")

    import_files = list(output_dir.glob("*_import.json"))

    if not import_files:
        typer.echo(f"No import files found in {output_dir}")
        typer.echo("Files in directory:")
        try:
            for f in output_dir.iterdir():
                typer.echo(f"  - {f.name}")
        except Exception as e:
            typer.echo(f"Error listing directory: {e}")
        raise typer.Exit(code=1)

    # Validate import files if requested
    if validate:
        typer.echo("Validating import files...")
        validation_errors = []
        for import_file in import_files:
            errors = validate_import_file(import_file)
            if errors:
                validation_errors.extend([f"{import_file.name}: {error}" for error in errors])
        
        if validation_errors:
            typer.echo("Validation errors found:")
            for error in validation_errors[:10]:  # Show first 10 errors
                typer.echo(f"  - {error}")
            if len(validation_errors) > 10:
                typer.echo(f"  ... and {len(validation_errors) - 10} more errors")
            
            if not typer.confirm("Continue with import despite validation errors?"):
                raise typer.Exit(code=1)

    all_imports = []

    for import_file in import_files:
        typer.echo(f"Reading {import_file.name}...")
        try:
            resources, read_error = read_import_file(import_file)
        except Exception as e:
            typer.echo(f"Error reading {import_file.name}: {e}", err=True)
            raise typer.Exit(code=1)

        if read_error:
            typer.echo(f"Error reading {import_file.name}: {read_error}", err=True)
            raise typer.Exit(code=1)
        
        for resource in resources:
            terraform_resource_type = resource.get('resource_type')
            resource_name = resource.get('resource_name')
            remote_id = resource.get('remote_id')

            if not all([terraform_resource_type, resource_name, remote_id]):
                typer.echo(f"Warning: Incomplete resource data in {import_file.name}, skipping")
                continue

            terraform_address = f"{terraform_resource_type}.{resource_name}"

            all_imports.append({
                'type': terraform_resource_type,
                'name': resource_name,
                'id': remote_id,
                'address': terraform_address,
                'file': import_file.name,
                'provider_metadata': resource.get('provider_metadata')
            })

    typer.echo(f"\nFound {len(all_imports)} resources to import")

    valid_workflows = {"import", "import-blocks", "workspaces", "import-commands"}
    if workflow is not None and workflow not in valid_workflows:
        typer.echo(f"Invalid workflow: {workflow}", err=True)
        raise typer.Exit(code=1)
    if workflow == "import-commands":
        workflow = "import"
    if workflow is None:
        version = terraform_checker.TerraformChecker.get_terraform_version()
        if version:
            import re
            m = re.search(r"v(\d+)\.(\d+)", version)
            if m and (int(m.group(1)) > 1 or (int(m.group(1)) == 1 and int(m.group(2)) >= 5)):
                workflow = "import-blocks"
            else:
                workflow = "import"
        else:
            workflow = "import"
    typer.echo(f"Using workflow: {workflow}")

    if workflow == "workspaces" and (
        not isinstance(batch_size, int) or batch_size <= 0
    ):
        typer.echo(
            "Error: --batch-size must be a positive integer when using the 'workspaces' workflow",
            err=True,
        )
        raise typer.Exit(code=1)

    by_type = {}
    for imp in all_imports:
        by_type[imp['type']] = by_type.get(imp['type'], 0) + 1
    for resource_type, count in sorted(by_type.items()):
        typer.echo(f"  {resource_type}: {count}")

    if verify:
        typer.echo("\nVerifying provider metadata...")
        if not _verify_import_entries(all_imports):
            raise typer.Exit(code=1)

    # Create stub resources if requested
    if create_stubs and not dry_run:
        typer.echo("\nChecking for missing resource definitions...")
        stubs_created = _ensure_resource_blocks(terraform_dir, all_imports)
        if stubs_created > 0:
            typer.echo(f"Created {stubs_created} stub resources")

    if workflow == "import-blocks" and not dry_run:
        if not _check_terraform_installation():
            raise typer.Exit(code=1)
        import_with_blocks(terraform_dir, all_imports)
        return

    if workflow == "workspaces" and not dry_run:
        if not _check_terraform_installation():
            raise typer.Exit(code=1)
        import_with_workspaces(terraform_dir, all_imports)
        return

    if dry_run:
        typer.echo("\nDry run - commands that would be executed:")
        for imp in all_imports[:10]:
            typer.echo(f"  terraform import {imp['address']} \"{imp['id']}\"")
        if len(all_imports) > 10:
            typer.echo(f"  ... and {len(all_imports) - 10} more")
        return

    if not yes:
        confirm = typer.confirm(f"\nImport all {len(all_imports)} resources?")
        if not confirm:
            raise typer.Abort()

    # Check if terraform is initialized
    if not (terraform_dir / ".terraform").exists():
        typer.echo("\nTerraform not initialized. Running 'terraform init'...")
        init_result = subprocess.run(
            ["terraform", "init"],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        if init_result.returncode != 0:
            typer.echo(f"Error: terraform init failed: {init_result.stderr}", err=True)
            raise typer.Exit(code=1)

    imported, failed, failed_imports = import_with_commands(
        terraform_dir,
        all_imports,
        parallel=parallel,
        async_mode=async_mode,
        progress=progress,
    )

    typer.echo(f"\nImport complete:")
    typer.secho(f"  ✓ Successful: {imported}", fg=typer.colors.GREEN)
    if failed > 0:
        typer.secho(f"  ✗ Failed: {failed}", fg=typer.colors.RED)
        typer.echo("\nFailed imports:")
        for fail in failed_imports[:5]:
            error_msg = (fail.get('stderr') or '').strip()
            file_name = fail.get('file') or fail['imp'].get('file', '')
            typer.echo(f"  - {file_name}: {error_msg}")
        if len(failed_imports) > 5:
            typer.echo(f"  ... and {len(failed_imports) - 5} more")

        # Provide helpful guidance
        typer.echo("\nTroubleshooting tips:")
        typer.echo("  1. Ensure all .tf files are present in the terraform directory")
        typer.echo("  2. Check that resources still exist in your cloud provider")
        typer.echo("  3. Verify resource IDs are correct")
        typer.echo("  4. Run 'terraform plan' to see current state")

        raise typer.Exit(code=1)
    else:
        typer.echo("\nAll resources imported successfully!")
        typer.echo("Run 'terraform plan' to verify the imported state.")

def _check_terraform_installation() -> bool:
    """Check if Terraform is installed and show helpful error if not."""
    import shutil
    import platform
    
    if shutil.which('terraform') is not None:
        return True
    
    # Show helpful error message
    typer.echo()
    typer.secho("Error: Terraform Not Found", fg="red", bold=True)
    typer.echo()
    typer.echo("Terraback requires Terraform to be installed and available in your PATH.")
    typer.echo()
    typer.secho("Installation Options:", fg="blue", bold=True)
    typer.echo()
    
    # Detection for different operating systems
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        typer.echo("macOS:")
        typer.echo("  brew tap hashicorp/tap")
        typer.echo("  brew install hashicorp/tap/terraform")
    elif system == "linux":
        typer.echo("Linux:")
        typer.echo("  # Ubuntu/Debian:")
        typer.echo("  wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg")
        typer.echo("  sudo apt update && sudo apt install terraform")
        typer.echo()
        typer.echo("  # Or download from: https://www.terraform.io/downloads")
    elif system == "windows":
        typer.echo("Windows:")
        typer.echo("  # Using Chocolatey:")
        typer.echo("  choco install terraform")
        typer.echo()
        typer.echo("  # Or download from: https://www.terraform.io/downloads")
    else:
        typer.echo("Download from: https://www.terraform.io/downloads")
    
    typer.echo()
    typer.secho("Official Download:", fg="cyan")
    typer.echo("  https://www.terraform.io/downloads")
    typer.echo()
    typer.echo("After installation, make sure 'terraform' is available in your PATH.")
    typer.echo("Test with: terraform version")
    typer.echo()
    
    return False

def _safe_terraform_init(directory: Path) -> tuple[bool, str]:
    """Safely run terraform init with proper error handling."""
    import subprocess
    
    try:
        result = subprocess.run(
            ['terraform', 'init'],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            typer.echo("Terraform initialization successful")
            return True, ""
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            typer.secho(f"Terraform init failed:", fg="red")
            typer.echo(error_msg)
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        error_msg = "Terraform init timed out after 5 minutes"
        typer.secho(f"Error: {error_msg}", fg="red")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error running terraform init: {e}"
        typer.secho(f"Error: {error_msg}", fg="red")
        return False, error_msg

def _safe_terraform_fmt(directory: Path) -> bool:
    """Safely run terraform fmt with proper error handling."""
    import subprocess
    
    try:
        result = subprocess.run(
            ['terraform', 'fmt'],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            typer.echo("Terraform formatting successful")
            return True
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            typer.echo(f"Warning: terraform fmt had issues: {error_msg}")
            return False
            
    except subprocess.TimeoutExpired:
        typer.echo("Warning: Terraform fmt timed out")
        return False
    except Exception as e:
        typer.echo(f"Warning: Could not run terraform fmt: {e}")
        return False

def _fix_terraform_files(directory: Path):
    """Fix common Terraform syntax errors in generated files."""
    import re

    for tf_file in directory.glob("*.tf"):
        typer.echo(f"  Fixing {tf_file.name}...")

        with open(tf_file, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Fix resource names with spaces
        content = re.sub(
            r'resource\s+"([^"]+)"\s+"([^"]*)\s+([^"]*)"',
            lambda m: f'resource "{m.group(1)}" "{m.group(2).replace(" ", "_")}{m.group(3)}"',
            content
        )
        
        # Fix resource names starting with numbers
        content = re.sub(
            r'resource\s+"([^"]+)"\s+"(\d[^"]*)"',
            lambda m: f'resource "{m.group(1)}" "res_{m.group(2)}"',
            content
        )
        
        # Fix invalid characters in resource names
        def fix_resource_name(match):
            resource_type = match.group(1)
            resource_name = match.group(2)
            # Replace invalid characters with underscores
            fixed_name = re.sub(r'[^a-zA-Z0-9_]', '_', resource_name)
            # Ensure it doesn't start with a number
            if fixed_name and fixed_name[0].isdigit():
                fixed_name = f'res_{fixed_name}'
            return f'resource "{resource_type}" "{fixed_name}"'
        
        content = re.sub(r'resource\s+"([^"]+)"\s+"([^"]*)"', fix_resource_name, content)

        # Fix multiple arguments on same line
        content = re.sub(
            r'"\s\s+([a-zA-Z_][a-zA-Z0-9_]*\s*=)',
            r'"\n  \1',
            content
        )
        
        # Fix missing newlines before blocks
        content = re.sub(
            r'"\s\s+([a-zA-Z_][a-zA-Z0-9_]*\s*\{)',
            r'"\n  \1',
            content
        )
        
        # Remove backticks and jinja artifacts
        content = re.sub(r'```jinja.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`+', '', content)

        # Fix missing commas in JSON-like structures
        content = re.sub(
            r'(\{"[^"]+"\s*=\s*"[^"]*")([^,}]+)(\})',
            r'\1, \2\3',
            content
        )

        if content != original_content:
            with open(tf_file, 'w', encoding='utf-8') as f:
                f.write(content)

@cli.command("plan")
def terraform_plan(
    terraform_dir: Path = typer.Option("generated", "--terraform-dir", "-t", help="Terraform directory"),
    output: Optional[Path] = typer.Option(None, "--out", help="Save plan to file"),
):
    """Run terraform plan on imported resources."""
    import subprocess

    # Check Terraform installation
    success = _check_terraform_installation()
    if not success:
        raise typer.Exit(code=1)

    if not (terraform_dir / ".terraform").exists():
        typer.echo("Terraform not initialized. Running 'terraform init'...")
        success, error = _safe_terraform_init(terraform_dir)
        if not success:
            typer.secho(f"Error: {error}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    cmd = ["terraform", "plan"]
    if output:
        cmd.extend(["-out", str(output)])

    typer.echo("Running terraform plan...")
    result = subprocess.run(cmd, cwd=terraform_dir)
    if result.returncode != 0:
        raise typer.Exit(code=1)

if __name__ == "__main__":
    cli()
