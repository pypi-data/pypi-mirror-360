import json
import typer
from pathlib import Path

app = typer.Typer()

DEFAULT_OUTPUT_DIR = Path("generated")

@app.command()
def generated():
    """List all generated Terraform and import files."""
    files = list(DEFAULT_OUTPUT_DIR.glob("*"))
    if not files:
        typer.echo("No generated resources found.")
        raise typer.Exit()

    typer.echo("Generated resources:")
    for f in files:
        typer.echo(f" - {f.name}")

@app.command()
def resource(resource_type: str):
    """
    List import commands for a specific resource type (e.g. ec2, s3)
    by reading from the generated JSON import file.
    
    Example:
      terraback list resource ec2
    """
    import_file_json = DEFAULT_OUTPUT_DIR / f"{resource_type}_import.json"
    if not import_file_json.exists():
        typer.echo(f"No import JSON file found for resource: {resource_type} at {import_file_json}")
        raise typer.Exit(code=1)

    with open(import_file_json) as f:
        try:
            data = json.load(f)
            if not data:
                typer.echo(f"No resources found in {import_file_json}")
                return
            
            typer.echo(f"terraform import commands for '{resource_type}':")
            for entry in data:
                # Reconstruct the import command format for display
                resource_ref = f'{entry.get("resource_type", "unknown_type")}.{entry.get("resource_name", "unknown_name")}'
                remote_id = entry.get("remote_id", "unknown_id")
                typer.echo(f"terraform import {resource_ref} {remote_id}")

        except json.JSONDecodeError:
            typer.echo(f"Error: Could not decode JSON from {import_file_json}")
            raise typer.Exit(code=1)
        except KeyError as e:
            typer.echo(f"Error: Missing expected key {e} in {import_file_json}")
            raise typer.Exit(code=1)