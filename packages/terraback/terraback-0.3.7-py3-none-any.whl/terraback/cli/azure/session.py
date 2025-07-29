# terraback/cli/azure/session.py
from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from functools import lru_cache
from typing import Optional
import os

@lru_cache(maxsize=None)
def get_azure_credential(use_cli: bool = True):
    """
    Get Azure credentials with caching.
    
    Args:
        use_cli: If True, uses Azure CLI credentials. Otherwise uses DefaultAzureCredential.
    
    Returns:
        Azure credential object
    """
    if use_cli or os.getenv("AZURE_USE_CLI_AUTH", "true").lower() == "true":
        return AzureCliCredential()
    return DefaultAzureCredential()

@lru_cache(maxsize=None)
def get_default_subscription_id():
    """Get the default subscription ID from Azure CLI."""
    try:
        credential = get_azure_credential()
        subscription_client = SubscriptionClient(credential)
        
        # Get the first (default) subscription
        for sub in subscription_client.subscriptions.list():
            return sub.subscription_id
            
    except Exception:
        # Fall back to environment variable
        return os.getenv("AZURE_SUBSCRIPTION_ID")
    
    return None

@lru_cache(maxsize=None)
def get_resource_client(subscription_id: str = None, credential=None):
    """
    Get a cached Resource Management client.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        credential: Optional credential object
    
    Returns:
        ResourceManagementClient instance
    """
    if subscription_id is None:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            raise ValueError("No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID")
    
    if credential is None:
        credential = get_azure_credential()
    
    return ResourceManagementClient(
        credential=credential,
        subscription_id=subscription_id
    )

def get_cached_azure_session(subscription_id: str = None, credential=None):
    """
    Get a cached Azure session that can cache API responses.
    
    Args:
        subscription_id: Azure subscription ID (optional)
        credential: Optional credential object
    
    Returns:
        Dictionary with credential and subscription_id for use by service clients
    """
    if subscription_id is None:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            raise ValueError("No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID")
    
    if credential is None:
        credential = get_azure_credential()
    
    return {
        "credential": credential,
        "subscription_id": subscription_id
    }