from terraback.core.license import require_professional
import typer
from pathlib import Path

from .functions import scan_lambda_functions, list_lambda_functions, import_lambda_function
from .layers import scan_lambda_layers, list_lambda_layers, import_lambda_layer

from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="lambda",
    help="Manage AWS Lambda resources like Functions and Layers.",
    no_args_is_help=True
)

# --- Lambda Function Commands ---
@app.command(name="scan-functions", help="Scan Lambda functions.")
@require_professional
def scan_functions_command(output_dir: Path = typer.Option("generated"), profile: str = typer.Option(None), region: str = typer.Option("us-east-1")):
    scan_lambda_functions(output_dir, profile, region)

@app.command(name="list-functions", help="List scanned Lambda functions.")
@require_professional
def list_functions_command(output_dir: Path = typer.Option("generated")):
    list_lambda_functions(output_dir)

@app.command(name="import-function", help="Import a Lambda function by its name.")
@require_professional
def import_function_command(function_name: str, output_dir: Path = typer.Option("generated")):
    import_lambda_function(function_name, output_dir)


# --- Lambda Layer Commands ---
@app.command(name="scan-layers", help="Scan Lambda Layer Versions.")
@require_professional
def scan_layers_command(output_dir: Path = typer.Option("generated"), profile: str = typer.Option(None), region: str = typer.Option("us-east-1")):
    scan_lambda_layers(output_dir, profile, region)

@app.command(name="list-layers", help="List scanned Lambda Layer Versions.")
@require_professional
def list_layers_command(output_dir: Path = typer.Option("generated")):
    list_lambda_layers(output_dir)

@app.command(name="import-layer", help="Import a Lambda Layer Version by its ARN.")
@require_professional
def import_layer_command(layer_version_arn: str, output_dir: Path = typer.Option("generated")):
    import_lambda_layer(layer_version_arn, output_dir)


# --- Registration ---
def register():
    """Registers scan functions and dependencies for the Lambda module."""
    register_scan_function("lambda_function", scan_lambda_functions)
    register_scan_function("lambda_layer_version", scan_lambda_layers)

    # Define dependencies
    cross_scan_registry.register_dependency("lambda_function", "iam_role")
    cross_scan_registry.register_dependency("lambda_function", "security_group")
    cross_scan_registry.register_dependency("lambda_function", "subnet")
    cross_scan_registry.register_dependency("lambda_function", "lambda_layer_version")
