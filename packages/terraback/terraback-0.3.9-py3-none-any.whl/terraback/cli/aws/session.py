import boto3
from functools import lru_cache

@lru_cache(maxsize=None)
def get_boto_session(profile: str = None, region: str = "us-east-1"):
    """
    Get a Boto3 session with caching.
    """
    if profile:
        return boto3.Session(profile_name=profile, region_name=region)
    return boto3.Session(region_name=region)

