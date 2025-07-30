from terraback.core.license import require_professional
import typer
from pathlib import Path
from .rest_apis import scan_rest_apis

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="apigateway",
    help="Manage API Gateway REST API resources.",
    no_args_is_help=True
)

@app.command(name="scan-rest-apis", help="Scan REST APIs and all their sub-resources.")
@require_professional
def scan_apis_command(output_dir: Path = typer.Option("generated"), profile: str = typer.Option(None), region: str = typer.Option("us-east-1")):
    scan_rest_apis(output_dir, profile, region)

# Note: list and import commands are omitted for now due to the complexity of nested resources.

def register():
    """Registers scan functions and dependencies for the API Gateway module."""
    register_scan_function("api_gateway_rest_api", scan_rest_apis)

    # Define dependencies
    cross_scan_registry.register_dependency("api_gateway_integration", "lambda_function")
    cross_scan_registry.register_dependency("lambda_function", "api_gateway_rest_api")
