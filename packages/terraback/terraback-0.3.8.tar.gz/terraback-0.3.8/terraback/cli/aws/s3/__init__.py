import typer
from pathlib import Path
from .buckets import scan_buckets, list_buckets, import_bucket
from terraback.utils.cross_scan_registry import register_scan_function

app = typer.Typer(
    name="s3",
    help="Manage S3 resources like buckets.",
    no_args_is_help=True
)

@app.command(name="scan", help="Scan S3 buckets and their configurations.")
def scan_s3_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files."),
    profile: str = typer.Option(None, help="AWS CLI profile to use."),
    region: str = typer.Option("us-east-1", help="AWS region...")
):
    scan_buckets(output_dir, profile, region)

@app.command(name="list", help="List all S3 bucket resources previously generated.")
def list_s3_command(output_dir: Path = typer.Option("generated", help="Directory containing generated files.")):
    list_buckets(output_dir)

@app.command(name="import", help="Run terraform import for a specific S3 bucket by name.")
def import_s3_command(
    bucket_name: str,
    output_dir: Path = typer.Option("generated", help="Directory with import file.")
):
    import_bucket(bucket_name, output_dir)

def register():
    """Registers the scan function for the S3 module."""
    register_scan_function("s3_bucket", scan_buckets)