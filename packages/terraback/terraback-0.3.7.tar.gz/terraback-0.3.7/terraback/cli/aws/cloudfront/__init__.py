import typer
from pathlib import Path

from .distributions import scan_distributions, list_distributions, import_distribution
from .origin_access_controls import scan_origin_access_controls, list_origin_access_controls, import_origin_access_control
from .cache_policies import scan_cache_policies, list_cache_policies, import_cache_policy
from .origin_request_policies import scan_origin_request_policies, list_origin_request_policies, import_origin_request_policy

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry
from terraback.core.license import require_professional

app = typer.Typer(
    name="cloudfront",
    help="Manage CloudFront CDN resources like distributions and origin access controls (Pro/Enterprise).",
    no_args_is_help=True
)

# --- CloudFront Distribution Commands ---
@app.command(name="scan-distributions", help="Scan CloudFront distributions.")
@require_professional
def scan_distributions_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region (CloudFront is global)")
):
    scan_distributions(output_dir, profile, region)

@app.command(name="list-distributions", help="List scanned CloudFront distributions.")
@require_professional
def list_distributions_command(output_dir: Path = typer.Option("generated")):
    list_distributions(output_dir)

@app.command(name="import-distribution", help="Import a CloudFront distribution by ID.")
@require_professional
def import_distribution_command(
    distribution_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_distribution(distribution_id, output_dir)

# --- Origin Access Control Commands ---
@app.command(name="scan-origin-access-controls", help="Scan CloudFront Origin Access Controls.")
@require_professional
def scan_oac_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region (CloudFront is global)")
):
    scan_origin_access_controls(output_dir, profile, region)

@app.command(name="list-origin-access-controls", help="List scanned Origin Access Controls.")
@require_professional
def list_oac_command(output_dir: Path = typer.Option("generated")):
    list_origin_access_controls(output_dir)

@app.command(name="import-origin-access-control", help="Import an Origin Access Control by ID.")
@require_professional
def import_oac_command(
    oac_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_origin_access_control(oac_id, output_dir)

# --- Cache Policy Commands ---
@app.command(name="scan-cache-policies", help="Scan CloudFront cache policies.")
@require_professional
def scan_cache_policies_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region (CloudFront is global)")
):
    scan_cache_policies(output_dir, profile, region)

@app.command(name="list-cache-policies", help="List scanned cache policies.")
@require_professional
def list_cache_policies_command(output_dir: Path = typer.Option("generated")):
    list_cache_policies(output_dir)

@app.command(name="import-cache-policy", help="Import a cache policy by ID.")
@require_professional
def import_cache_policy_command(
    policy_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_cache_policy(policy_id, output_dir)

# --- Origin Request Policy Commands ---
@app.command(name="scan-origin-request-policies", help="Scan CloudFront origin request policies.")
@require_professional
def scan_origin_request_policies_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region (CloudFront is global)")
):
    scan_origin_request_policies(output_dir, profile, region)

@app.command(name="list-origin-request-policies", help="List scanned origin request policies.")
@require_professional
def list_origin_request_policies_command(output_dir: Path = typer.Option("generated")):
    list_origin_request_policies(output_dir)

@app.command(name="import-origin-request-policy", help="Import an origin request policy by ID.")
@require_professional
def import_origin_request_policy_command(
    policy_id: str,
    output_dir: Path = typer.Option("generated")
):
    import_origin_request_policy(policy_id, output_dir)

# --- Combined Commands ---
@app.command(name="scan-all", help="Scan all CloudFront resources.")
@require_professional
def scan_all_cloudfront_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region (CloudFront is global)")
):
    scan_distributions(output_dir, profile, region)
    scan_origin_access_controls(output_dir, profile, region)
    scan_cache_policies(output_dir, profile, region)
    scan_origin_request_policies(output_dir, profile, region)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the CloudFront module."""
    register_scan_function("cloudfront_distribution", scan_distributions)
    register_scan_function("cloudfront_origin_access_control", scan_origin_access_controls)
    register_scan_function("cloudfront_cache_policy", scan_cache_policies)
    register_scan_function("cloudfront_origin_request_policy", scan_origin_request_policies)

    # CloudFront distributions depend on various AWS services
    cross_scan_registry.register_dependency("cloudfront_distribution", "acm_certificate")
    cross_scan_registry.register_dependency("cloudfront_distribution", "s3_bucket")
    cross_scan_registry.register_dependency("cloudfront_distribution", "elbv2_load_balancer")
    cross_scan_registry.register_dependency("cloudfront_distribution", "cloudfront_origin_access_control")
    cross_scan_registry.register_dependency("cloudfront_distribution", "cloudfront_cache_policy")
    cross_scan_registry.register_dependency("cloudfront_distribution", "cloudfront_origin_request_policy")
    cross_scan_registry.register_dependency("cloudfront_distribution", "lambda_function")
    cross_scan_registry.register_dependency("cloudfront_distribution", "wafv2_web_acl")