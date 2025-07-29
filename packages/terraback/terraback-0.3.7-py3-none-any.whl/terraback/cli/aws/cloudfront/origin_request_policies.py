from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_origin_request_policies(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for CloudFront origin request policies and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    cloudfront_client = boto_session.client("cloudfront")
    
    print(f"Scanning for CloudFront origin request policies (global service)...")
    
    origin_request_policies = []
    
    try:
        # Get custom origin request policies (no pagination support)
        response = cloudfront_client.list_origin_request_policies(Type='custom')
        
        if 'Items' in response['OriginRequestPolicyList']:
            for policy_summary in response['OriginRequestPolicyList']['Items']:
                policy_id = policy_summary['OriginRequestPolicy']['Id']
                
                try:
                    # Get detailed origin request policy configuration
                    response = cloudfront_client.get_origin_request_policy(Id=policy_id)
                    policy = response['OriginRequestPolicy']
                    
                    # Add sanitized name for resource naming
                    policy['name_sanitized'] = policy_id.replace('-', '_')
                    
                    # Format configuration for easier template usage
                    config = policy['OriginRequestPolicyConfig']
                    
                    # Format headers config
                    headers_config = config.get('HeadersConfig', {})
                    config['headers_formatted'] = {
                        'header_behavior': headers_config.get('HeaderBehavior', 'none'),
                        'headers': headers_config.get('Headers', {}).get('Items', [])
                    }
                    
                    # Format query strings config
                    query_strings_config = config.get('QueryStringsConfig', {})
                    config['query_strings_formatted'] = {
                        'query_string_behavior': query_strings_config.get('QueryStringBehavior', 'none'),
                        'query_strings': query_strings_config.get('QueryStrings', {}).get('Items', [])
                    }
                    
                    # Format cookies config
                    cookies_config = config.get('CookiesConfig', {})
                    config['cookies_formatted'] = {
                        'cookie_behavior': cookies_config.get('CookieBehavior', 'none'),
                        'cookies': cookies_config.get('Cookies', {}).get('Items', [])
                    }
                    
                    policy['config_formatted'] = config
                    origin_request_policies.append(policy)
                    
                except Exception as e:
                    print(f"  - Warning: Could not retrieve details for origin request policy {policy_id}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error retrieving origin request policies: {e}")
    
    output_file = output_dir / "cloudfront_origin_request_policy.tf"
    generate_tf(origin_request_policies, "cloudfront_origin_request_policy", output_file)
    print(f"Generated Terraform for {len(origin_request_policies)} CloudFront origin request policies -> {output_file}")
    generate_imports_file(
        "cloudfront_origin_request_policy", 
        origin_request_policies, 
        remote_resource_id_key="Id", 
        output_dir=output_dir
    )

def list_origin_request_policies(output_dir: Path):
    """Lists all CloudFront origin request policy resources previously generated."""
    ImportManager(output_dir, "cloudfront_origin_request_policy").list_all()

def import_origin_request_policy(policy_id: str, output_dir: Path):
    """Runs terraform import for a specific CloudFront origin request policy by its ID."""
    ImportManager(output_dir, "cloudfront_origin_request_policy").find_and_import(policy_id)