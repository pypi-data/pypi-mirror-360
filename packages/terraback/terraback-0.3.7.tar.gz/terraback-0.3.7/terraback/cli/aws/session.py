import boto3
from functools import lru_cache
from typing import Optional

@lru_cache(maxsize=None)
def get_boto_session(profile: str = None, region: str = "us-east-1"):
    """
    Get a Boto3 session with caching.
    """
    if profile:
        return boto3.Session(profile_name=profile, region_name=region)
    return boto3.Session(region_name=region)

def get_cached_boto_session(profile: Optional[str] = None, region: str = "us-east-1", 
                           cache = None):
    """
    Get a cached boto session that caches API responses.
    
    Args:
        profile: AWS profile name
        region: AWS region
        cache: ScanCache instance (if None, gets default cache)
    
    Returns:
        CachedBotoSession instance
    """
    # Import here to avoid circular dependencies
    from terraback.utils.scan_cache import get_scan_cache, CachedBotoSession
    
    session = get_boto_session(profile, region)
    
    if cache is None:
        cache = get_scan_cache()
    
    return CachedBotoSession(session, cache)