from pathlib import Path

def clean_generated_files(output_dir: Path, resource_prefix: str):
    """
    Deletes generated .tf and _import.json files for a given resource.
    Example: "ec2" → deletes ec2.tf and ec2_import.json
    """
    filenames = [
        f"{resource_prefix}.tf",
        f"{resource_prefix}_import.json",
    ]
    for filename in filenames:
        file_path = output_dir / filename
        if file_path.exists():
            file_path.unlink()