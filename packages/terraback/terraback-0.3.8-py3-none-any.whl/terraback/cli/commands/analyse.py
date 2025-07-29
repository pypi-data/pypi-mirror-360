"""Analyse Terraform tfstate files and show resource layout."""
import json
from pathlib import Path
from typing import Dict, List, Any

import typer

app = typer.Typer(help="Analyse Terraform state files")


@app.command("state")
def analyse_state(
    tfstate_file: Path = typer.Option(
        "terraform.tfstate", 
        exists=True, 
        help="Path to tfstate file"
    )
):
    """Analyse Terraform tfstate file and display resource/module structure, outputs, and dependencies."""
    try:
        with open(tfstate_file) as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        typer.secho(f"Error parsing tfstate file: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

    resources = state.get("resources", [])
    if not resources:
        typer.echo("No resources found in tfstate file.")
        raise typer.Exit(1)

    # Display resources
    typer.secho("\nResources:", fg=typer.colors.BRIGHT_BLUE, bold=True)
    for res in resources:
        module = res.get("module", "root")
        type_ = res["type"]
        name = res["name"]
        
        if module == "root":
            typer.echo(f"  {type_}.{name}")
        else:
            typer.echo(f"  [{module}] {type_}.{name}")

        # Display dependencies if available
        instances = res.get("instances", [])
        for inst in instances:
            deps = inst.get("dependencies", [])
            if deps:
                for dep in deps:
                    typer.secho(f"    └─ depends on: {dep}", fg=typer.colors.YELLOW)

    # Display outputs if present
    outputs = state.get("outputs", {})
    if outputs:
        typer.secho("\nOutputs:", fg=typer.colors.BRIGHT_BLUE, bold=True)
        for name, details in outputs.items():
            value = details.get("value", "N/A")
            typer.echo(f"  {name}: {value}")

    # Suggest module paths for imports
    typer.secho(
        "\nSuggested module paths for imports:", 
        fg=typer.colors.BRIGHT_BLUE, 
        bold=True
    )
    for res in resources:
        module = res.get("module", "root")
        type_ = res["type"]
        name = res["name"]
        
        if module != "root":
            suggested_path = f"{module}.{type_}.{name}"
        else:
            suggested_path = f"{type_}.{name}"
            
        typer.echo(f"  {type_}.{name} → {suggested_path}")


@app.command("summary")
def analyse_summary(
    tfstate_file: Path = typer.Option(
        "terraform.tfstate", 
        exists=True, 
        help="Path to tfstate file"
    )
):
    """Show a summary of resources in the tfstate file."""
    try:
        with open(tfstate_file) as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        typer.secho(f"Error parsing tfstate file: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

    resources = state.get("resources", [])
    if not resources:
        typer.echo("No resources found in tfstate file.")
        raise typer.Exit(1)

    # Count resources by type
    resource_counts: Dict[str, int] = {}
    module_counts: Dict[str, int] = {}
    
    for res in resources:
        # Count by type
        res_type = res["type"]
        resource_counts[res_type] = resource_counts.get(res_type, 0) + 1
        
        # Count by module
        module = res.get("module", "root")
        module_counts[module] = module_counts.get(module, 0) + 1

    typer.secho("\nResource Summary:", fg=typer.colors.BRIGHT_BLUE, bold=True)
    typer.echo(f"Total resources: {len(resources)}")
    
    typer.secho("\nBy Type:", fg=typer.colors.GREEN)
    for res_type, count in sorted(resource_counts.items()):
        typer.echo(f"  {res_type}: {count}")
    
    typer.secho("\nBy Module:", fg=typer.colors.GREEN)
    for module, count in sorted(module_counts.items()):
        typer.echo(f"  {module}: {count}")


if __name__ == "__main__":
    app()