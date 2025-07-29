# terraback/cli/clean.py

import typer
from pathlib import Path
import shutil
from terraback.utils.cross_scan_registry import cross_scan_registry 

app = typer.Typer()

DEFAULT_OUTPUT_DIR = Path("generated")


@app.command("all")
def clean_all_generated_files(
    output_dir: Path = typer.Option(DEFAULT_OUTPUT_DIR, help="Directory containing generated files", writable=True, file_okay=False, dir_okay=True, resolve_path=True),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation")
):
    """Remove all files and subdirectories within the generated output directory."""
    if not output_dir.exists() or not output_dir.is_dir():
        typer.echo(f"Directory not found or is not a directory: {output_dir}")
        raise typer.Exit(code=1)

    if not any(output_dir.iterdir()):
        typer.echo(f"Directory is already empty: {output_dir}")
        return

    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete all contents of '{output_dir}'?")
        if not confirm:
            typer.echo("Clean operation cancelled.")
            raise typer.Exit()

    try:
        for item in output_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        typer.echo(f"Successfully cleaned all contents of '{output_dir}'.")
    except Exception as e:
        typer.echo(f"Error cleaning directory '{output_dir}': {e}", err=True)
        raise typer.Exit(code=1)


@app.command("dependencies")
def clean_dependency_registry():
    """Clear the saved cross-scan dependency registry."""
    cross_scan_registry.clear()
    typer.echo("Cross-scan dependency registry cleared.")
