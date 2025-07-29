"""Common defaults and utilities for cloud providers."""
import os
import subprocess
from typing import Optional, Dict, Any

def get_aws_defaults() -> Dict[str, Any]:
    """Get AWS defaults from environment or boto3 session."""
    try:
        import boto3
        session = boto3.Session()
        return {
            'profile': os.getenv('AWS_PROFILE'),
            'region': session.region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        }
    except ImportError:
        return {
            'profile': os.getenv('AWS_PROFILE'),
            'region': os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        }

def get_azure_defaults() -> Dict[str, Any]:
    """Get Azure defaults from Azure CLI."""
    from terraback.cli.azure.session import get_default_subscription_id
    
    # Try to get default location from Azure CLI config
    default_location = os.getenv('AZURE_LOCATION')
    if not default_location:
        try:
            # Try to get from Azure CLI config
            result = subprocess.run(
                ['az', 'configure', '--list-defaults'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                # Parse the output to find location
                for line in result.stdout.splitlines():
                    if 'location' in line:
                        # Extract location value
                        parts = line.split('=')
                        if len(parts) > 1:
                            default_location = parts[1].strip()
                            break
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    # Fall back to common default
    if not default_location:
        default_location = 'eastus'
    
    return {
        'subscription_id': get_default_subscription_id(),
        'location': default_location
    }

def get_gcp_defaults() -> Dict[str, Any]:
    """Get GCP defaults from gcloud CLI."""
    defaults = {
        'project': os.getenv('GOOGLE_CLOUD_PROJECT'),
        'region': os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
    }
    
    # Try to get from gcloud CLI
    try:
        # Get project
        if not defaults['project']:
            result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                capture_output=True,
                text=True,
                stderr=subprocess.DEVNULL,
                check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                defaults['project'] = result.stdout.strip()
        
        # Get region
        result = subprocess.run(
            ['gcloud', 'config', 'get-value', 'compute/region'],
            capture_output=True,
            text=True,
            stderr=subprocess.DEVNULL,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            defaults['region'] = result.stdout.strip()
            
    except FileNotFoundError:
        # gcloud CLI not installed
        pass
    
    return defaults

def get_cloud_defaults(provider: str) -> Dict[str, Any]:
    """Get defaults for a specific cloud provider."""
    if provider.lower() == 'aws':
        return get_aws_defaults()
    elif provider.lower() == 'azure':
        return get_azure_defaults()
    elif provider.lower() == 'gcp':
        return get_gcp_defaults()
    else:
        raise ValueError(f"Unknown cloud provider: {provider}")

def validate_cloud_auth(provider: str) -> bool:
    """Check if the user is authenticated with the cloud provider."""
    if provider.lower() == 'aws':
        try:
            import boto3
            # Try to get caller identity
            client = boto3.client('sts')
            client.get_caller_identity()
            return True
        except Exception:
            return False
            
    elif provider.lower() == 'azure':
        try:
            # Check if user is logged in to Azure CLI
            result = subprocess.run(
                ['az', 'account', 'show'],
                capture_output=True,
                stderr=subprocess.DEVNULL,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
            
    elif provider.lower() == 'gcp':
        try:
            # Check if user is logged in to gcloud
            result = subprocess.run(
                ['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'],
                capture_output=True,
                stderr=subprocess.DEVNULL,
                check=False
            )
            return result.returncode == 0 and result.stdout.strip()
        except FileNotFoundError:
            return False
    
    return False