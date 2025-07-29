from pathlib import Path
from typing import List, Dict, Any
import concurrent.futures
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager


def _get_layer_versions(lambda_client, layer_name: str) -> List[Dict[str, Any]]:
    """Fetch all versions for a specific layer."""
    version_paginator = lambda_client.get_paginator('list_layer_versions')
    layer_versions = []
    
    for version_page in version_paginator.paginate(LayerName=layer_name):
        for layer_version in version_page.get('LayerVersions', []):
            layer_version['ImportId'] = layer_version['LayerVersionArn']
            layer_versions.append(layer_version)
    
    return layer_versions


def _get_all_layer_names(lambda_client) -> List[str]:
    """Fetch all layer names."""
    layer_paginator = lambda_client.get_paginator('list_layers')
    layer_names = []
    
    for page in layer_paginator.paginate():
        layer_names.extend([layer['LayerName'] for layer in page.get('Layers', [])])
    
    return layer_names


def _fetch_layer_versions_parallel(lambda_client, layer_names: List[str], max_workers: int = 10) -> List[Dict[str, Any]]:
    """Fetch layer versions in parallel for better performance."""
    all_layer_versions = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all layer version fetching tasks
        future_to_layer = {
            executor.submit(_get_layer_versions, lambda_client, layer_name): layer_name 
            for layer_name in layer_names
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_layer):
            layer_name = future_to_layer[future]
            try:
                layer_versions = future.result()
                all_layer_versions.extend(layer_versions)
                print(f"  - Found {len(layer_versions)} versions for layer: {layer_name}")
            except Exception as exc:
                print(f"  - Error fetching versions for layer {layer_name}: {exc}")
    
    return all_layer_versions


def scan_lambda_layers(output_dir: Path, profile: str = None, region: str = "us-east-1", max_workers: int = 10):
    """
    Scans for AWS Lambda Layers and their versions, generating Terraform code.
    Uses parallel processing for improved performance.
    
    Args:
        output_dir: Directory to write Terraform files
        profile: AWS profile to use
        region: AWS region to scan
        max_workers: Maximum number of parallel workers for API calls
    """
    boto_session = get_boto_session(profile, region)
    lambda_client = boto_session.client("lambda")
    
    print(f"Scanning for Lambda Layers in region {region}...")
    
    # Step 1: Get all layer names
    layer_names = _get_all_layer_names(lambda_client)
    print(f"Found {len(layer_names)} layers to process")
    
    if not layer_names:
        print("No layers found in the region")
        return
    
    # Step 2: Fetch all layer versions in parallel
    all_layer_versions = _fetch_layer_versions_parallel(lambda_client, layer_names, max_workers)
    
    # Step 3: Generate Terraform files
    if all_layer_versions:
        output_file = output_dir / "lambda_layer_version.tf"
        generate_tf(all_layer_versions, "lambda_layer_version", output_file)
        print(f"Generated Terraform for {len(all_layer_versions)} Lambda Layer Versions -> {output_file}")
        
        generate_imports_file(
            "lambda_layer_version", 
            all_layer_versions, 
            remote_resource_id_key="ImportId", 
            output_dir=output_dir
        )
    else:
        print("No layer versions found to generate Terraform code")


def list_lambda_layers(output_dir: Path):
    """Lists all Lambda Layer Version resources previously generated."""
    ImportManager(output_dir, "lambda_layer_version").list_all()


def import_lambda_layer(layer_version_arn: str, output_dir: Path):
    """Runs terraform import for a specific Lambda Layer Version by its ARN."""
    ImportManager(output_dir, "lambda_layer_version").find_and_import(layer_version_arn)