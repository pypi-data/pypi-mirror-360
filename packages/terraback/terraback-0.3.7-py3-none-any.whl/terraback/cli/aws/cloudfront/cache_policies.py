from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_cache_policies(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for CloudFront cache policies and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    cloudfront_client = boto_session.client("cloudfront")
    
    print(f"Scanning for CloudFront cache policies (global service)...")
    
    cache_policies = []
    
    try:
        # Get custom cache policies
        paginator = cloudfront_client.get_paginator('list_cache_policies')
        
        for page in paginator.paginate(Type='custom'):
            if 'Items' not in page['CachePolicyList']:
                continue
                
            for policy_summary in page['CachePolicyList']['Items']:
                policy_id = policy_summary['CachePolicy']['Id']
                
                try:
                    # Get detailed cache policy configuration
                    response = cloudfront_client.get_cache_policy(Id=policy_id)
                    policy = response['CachePolicy']
                    
                    # Add sanitized name for resource naming
                    policy['name_sanitized'] = policy_id.replace('-', '_')
                    
                    # Format configuration for easier template usage
                    config = policy['CachePolicyConfig']
                    
                    # Format parameters in key value headers
                    if config.get('ParametersInCacheKeyAndForwardedToOrigin'):
                        params = config['ParametersInCacheKeyAndForwardedToOrigin']
                        
                        # Format headers
                        headers_config = params.get('HeadersConfig', {})
                        config['headers_formatted'] = {
                            'header_behavior': headers_config.get('HeaderBehavior', 'none'),
                            'headers': headers_config.get('Headers', {}).get('Items', [])
                        }
                        
                        # Format query strings
                        query_strings_config = params.get('QueryStringsConfig', {})
                        config['query_strings_formatted'] = {
                            'query_string_behavior': query_strings_config.get('QueryStringBehavior', 'none'),
                            'query_strings': query_strings_config.get('QueryStrings', {}).get('Items', [])
                        }
                        
                        # Format cookies
                        cookies_config = params.get('CookiesConfig', {})
                        config['cookies_formatted'] = {
                            'cookie_behavior': cookies_config.get('CookieBehavior', 'none'),
                            'cookies': cookies_config.get('Cookies', {}).get('Items', [])
                        }
                        
                        config['enable_accept_encoding_gzip'] = params.get('EnableAcceptEncodingGzip', False)
                        config['enable_accept_encoding_brotli'] = params.get('EnableAcceptEncodingBrotli', False)
                    
                    policy['config_formatted'] = config
                    cache_policies.append(policy)
                    
                except Exception as e:
                    print(f"  - Warning: Could not retrieve details for cache policy {policy_id}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error retrieving cache policies: {e}")
    
    output_file = output_dir / "cloudfront_cache_policy.tf"
    generate_tf(cache_policies, "cloudfront_cache_policy", output_file)
    print(f"Generated Terraform for {len(cache_policies)} CloudFront cache policies -> {output_file}")
    generate_imports_file(
        "cloudfront_cache_policy", 
        cache_policies, 
        remote_resource_id_key="Id", 
        output_dir=output_dir
    )

def list_cache_policies(output_dir: Path):
    """Lists all CloudFront cache policy resources previously generated."""
    ImportManager(output_dir, "cloudfront_cache_policy").list_all()

def import_cache_policy(policy_id: str, output_dir: Path):
    """Runs terraform import for a specific CloudFront cache policy by its ID."""
    ImportManager(output_dir, "cloudfront_cache_policy").find_and_import(policy_id)