from terraback.core.license import require_professional
import typer
from pathlib import Path

from .certificates import scan_certificates, list_certificates, import_certificate

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="acm",
    help="Manage AWS Certificate Manager (ACM) resources like SSL/TLS certificates.",
    no_args_is_help=True
)

# --- Certificate Commands ---
@app.command(name="scan-certificates", help="Scan ACM SSL/TLS certificates.")
@require_professional
def scan_certificates_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    include_imported: bool = typer.Option(True, help="Include imported certificates"),
    include_issued: bool = typer.Option(True, help="Include ACM-issued certificates")
):
    scan_certificates(output_dir, profile, region, include_imported, include_issued)

@app.command(name="list-certificates", help="List scanned ACM certificates.")
@require_professional
def list_certificates_command(output_dir: Path = typer.Option("generated")):
    list_certificates(output_dir)

@app.command(name="import-certificate", help="Import an ACM certificate by ARN.")
@require_professional
def import_certificate_command(
    certificate_arn: str,
    output_dir: Path = typer.Option("generated")
):
    import_certificate(certificate_arn, output_dir)

# --- Registration ---
def register():
    """Registers scan functions and dependencies for the ACM module."""
    register_scan_function("acm_certificate", scan_certificates)

    # ACM certificates are dependencies for other services
    # Load balancers use ACM certificates for HTTPS listeners
    cross_scan_registry.register_dependency("elbv2_listener", "acm_certificate")
    # Classic load balancers can also use ACM certificates
    cross_scan_registry.register_dependency("classic_load_balancer", "acm_certificate")
    # API Gateway can use ACM certificates for custom domains
    cross_scan_registry.register_dependency("api_gateway_rest_api", "acm_certificate")
    # CloudFront distributions use ACM certificates (when we add CloudFront)
    cross_scan_registry.register_dependency("cloudfront_distribution", "acm_certificate")