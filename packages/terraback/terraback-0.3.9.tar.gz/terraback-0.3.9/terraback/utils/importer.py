import json
import subprocess
from pathlib import Path
import typer
from terraback.utils.logging import get_logger

logger = get_logger(__name__)

class ImportManager:
    """
    Handles the logic for listing and importing resources from generated JSON files.
    """
    def __init__(self, output_dir: Path, resource_type_in_file: str):
        """
        Args:
            output_dir (Path): The directory containing the generated files.
            resource_type_in_file (str): The resource type key used in the import file name (e.g., "ec2", "iam_roles").
        """
        self.output_dir = output_dir
        self.import_file = output_dir / f"{resource_type_in_file}_import.json"
        self.data = self._load()

    def _load(self):
        if not self.import_file.is_file():
            return None
        try:
            with open(self.import_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def list_all(self):
        """Lists all resources found in the import file."""
        if not self.data:
            logger.warning("No import data found for '%s'. Run a scan first.", self.import_file.name)
            raise typer.Exit(code=1)

        logger.info("Listing resources from %s:", self.import_file)
        for entry in self.data:
            # Use .get() for safety in case a key is missing
            tf_address = f'{entry.get("resource_type", "?")}.{entry.get("resource_name", "?")}'
            remote_id = entry.get("remote_id", "N/A")
            logger.info("  > %s  (ID: %s)", tf_address, remote_id)

    def find_and_import(self, remote_id: str):
        """Finds a resource by its remote ID and runs 'terraform import'."""
        if not self.data:
            logger.warning("No import data found in '%s'. Run a scan first.", self.import_file.name)
            raise typer.Exit(code=1)

        entry_to_import = None
        for entry in self.data:
            if entry.get("remote_id") == remote_id:
                entry_to_import = entry
                break
        
        if not entry_to_import:
            logger.error("Resource with ID '%s' not found in %s", remote_id, self.import_file.name)
            raise typer.Exit(code=1)

        tf_address = f'{entry_to_import["resource_type"]}.{entry_to_import["resource_name"]}'
        
        logger.info("Preparing to import '%s' into '%s'...", remote_id, tf_address)
        
        try:
            # Execute terraform import in the output directory
            subprocess.run(
                ["terraform", "import", tf_address, remote_id],
                check=True,
                cwd=self.output_dir
            )
            logger.info("Successfully imported %s!", tf_address)
        except FileNotFoundError:
            logger.error("'terraform' command not found. Is Terraform installed and in your PATH?")
            raise typer.Exit(code=1)
        except subprocess.CalledProcessError as e:
            logger.error("Error during terraform import: %s", e)
            raise typer.Exit(code=1)
