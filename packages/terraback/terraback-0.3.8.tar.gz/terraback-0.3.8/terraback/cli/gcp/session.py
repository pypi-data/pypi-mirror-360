# terraback/cli/gcp/session.py
from google.cloud import compute_v1, storage
from google.auth import default
from google.auth.credentials import Credentials
from functools import lru_cache
from typing import Optional, Dict, Any
import os
import subprocess

@lru_cache(maxsize=None)
def get_gcp_credentials() -> Credentials:
    """Get GCP credentials with caching."""
    credentials, project = default()
    return credentials

@lru_cache(maxsize=None)
def get_default_project_id() -> Optional[str]:
    """Get the default project ID from gcloud or environment."""
    # Try environment variable first
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project_id:
        return project_id
    
    # Try gcloud config
    try:
        result = subprocess.run(
            ['gcloud', 'config', 'get-value', 'project'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip() if result.stdout.strip() else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_compute_client(project_id: str = None) -> compute_v1.InstancesClient:
    """Get a Compute Engine client."""
    if project_id is None:
        project_id = get_default_project_id()
    
    credentials = get_gcp_credentials()
    return compute_v1.InstancesClient(credentials=credentials)