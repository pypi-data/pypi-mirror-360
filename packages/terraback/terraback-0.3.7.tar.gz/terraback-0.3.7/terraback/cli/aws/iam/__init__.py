import typer
from pathlib import Path

from .roles import scan_roles, list_roles, import_role
from .policies import scan_policies, list_policies, import_policy
from terraback.utils.cross_scan_registry import register_scan_function

app = typer.Typer(
    name="iam",
    help="Manage IAM resources like Roles and Policies.",
    no_args_is_help=True
)

# --- Role Commands ---
@app.command(name="scan-roles")
def scan_roles_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_roles(output_dir, profile, region)

# --- Policy Commands ---
@app.command(name="scan-policies")
def scan_policies_command(
    output_dir: Path = typer.Option("generated", help="Directory..."),
    profile: str = typer.Option(None, help="AWS CLI profile..."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_policies(output_dir, profile, region)

# --- Registration Function ---
def register():
    """Registers the scan functions for the IAM module."""
    register_scan_function("iam_roles", scan_roles)
    register_scan_function("iam_policies", scan_policies)