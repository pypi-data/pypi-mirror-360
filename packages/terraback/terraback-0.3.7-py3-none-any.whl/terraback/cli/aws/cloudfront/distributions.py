from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_distributions(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for CloudFront distributions and generates Terraform code.
    Note: CloudFront is a global service, but we use the specified region for the session.
    """
    boto_session = get_boto_session(profile, region)
    cloudfront_client = boto_session.client("cloudfront")
    
    print(f"Scanning for CloudFront distributions (global service)...")
    
    # Get all distributions
    distributions = []
    paginator = cloudfront_client.get_paginator('list_distributions')
    
    for page in paginator.paginate():
        if 'Items' not in page['DistributionList']:
            continue
            
        for dist_summary in page['DistributionList']['Items']:
            dist_id = dist_summary['Id']
            
            try:
                # Get detailed distribution configuration
                response = cloudfront_client.get_distribution(Id=dist_id)
                distribution = response['Distribution']
                
                # Add sanitized name for resource naming
                distribution['name_sanitized'] = dist_id.replace('-', '_')
                
                # Get distribution configuration
                config = distribution['DistributionConfig']
                
                # Format origins for easier template usage
                if config.get('Origins') and config['Origins'].get('Items'):
                    config['origins_formatted'] = []
                    for origin in config['Origins']['Items']:
                        formatted_origin = {
                            'domain_name': origin['DomainName'],
                            'origin_id': origin['Id'],
                            'origin_path': origin.get('OriginPath', ''),
                            'connection_attempts': origin.get('ConnectionAttempts', 3),
                            'connection_timeout': origin.get('ConnectionTimeout', 10),
                            'origin_shield': origin.get('OriginShield'),
                            's3_origin_config': origin.get('S3OriginConfig'),
                            'custom_origin_config': origin.get('CustomOriginConfig'),
                            'origin_access_control_id': origin.get('OriginAccessControlId')
                        }
                        config['origins_formatted'].append(formatted_origin)
                else:
                    config['origins_formatted'] = []
                
                # Format origin groups
                if config.get('OriginGroups') and config['OriginGroups'].get('Items'):
                    config['origin_groups_formatted'] = []
                    for group in config['OriginGroups']['Items']:
                        formatted_group = {
                            'origin_id': group['Id'],
                            'failover_criteria': group.get('FailoverCriteria'),
                            'members': group.get('Members', {}).get('Items', [])
                        }
                        config['origin_groups_formatted'].append(formatted_group)
                else:
                    config['origin_groups_formatted'] = []
                
                # Format default cache behavior
                if config.get('DefaultCacheBehavior'):
                    default_behavior = config['DefaultCacheBehavior']
                    config['default_cache_behavior_formatted'] = {
                        'target_origin_id': default_behavior['TargetOriginId'],
                        'viewer_protocol_policy': default_behavior['ViewerProtocolPolicy'],
                        'allowed_methods': default_behavior.get('AllowedMethods', {}).get('Items', []),
                        'cached_methods': default_behavior.get('AllowedMethods', {}).get('CachedMethods', {}).get('Items', []),
                        'compress': default_behavior.get('Compress', False),
                        'cache_policy_id': default_behavior.get('CachePolicyId'),
                        'origin_request_policy_id': default_behavior.get('OriginRequestPolicyId'),
                        'response_headers_policy_id': default_behavior.get('ResponseHeadersPolicyId'),
                        'realtime_log_config_arn': default_behavior.get('RealtimeLogConfigArn'),
                        'field_level_encryption_id': default_behavior.get('FieldLevelEncryptionId'),
                        'function_associations': default_behavior.get('FunctionAssociations', {}).get('Items', []),
                        'lambda_function_associations': default_behavior.get('LambdaFunctionAssociations', {}).get('Items', []),
                        'forwarded_values': default_behavior.get('ForwardedValues'),
                        'min_ttl': default_behavior.get('MinTTL', 0),
                        'default_ttl': default_behavior.get('DefaultTTL'),
                        'max_ttl': default_behavior.get('MaxTTL'),
                        'smooth_streaming': default_behavior.get('SmoothStreaming', False),
                        'trusted_signers': default_behavior.get('TrustedSigners', {}).get('Items', []),
                        'trusted_key_groups': default_behavior.get('TrustedKeyGroups', {}).get('Items', [])
                    }
                else:
                    config['default_cache_behavior_formatted'] = {}
                
                # Format cache behaviors
                if config.get('CacheBehaviors') and config['CacheBehaviors'].get('Items'):
                    config['cache_behaviors_formatted'] = []
                    for behavior in config['CacheBehaviors']['Items']:
                        formatted_behavior = {
                            'path_pattern': behavior['PathPattern'],
                            'target_origin_id': behavior['TargetOriginId'],
                            'viewer_protocol_policy': behavior['ViewerProtocolPolicy'],
                            'allowed_methods': behavior.get('AllowedMethods', {}).get('Items', []),
                            'cached_methods': behavior.get('AllowedMethods', {}).get('CachedMethods', {}).get('Items', []),
                            'compress': behavior.get('Compress', False),
                            'cache_policy_id': behavior.get('CachePolicyId'),
                            'origin_request_policy_id': behavior.get('OriginRequestPolicyId'),
                            'response_headers_policy_id': behavior.get('ResponseHeadersPolicyId'),
                            'realtime_log_config_arn': behavior.get('RealtimeLogConfigArn'),
                            'field_level_encryption_id': behavior.get('FieldLevelEncryptionId'),
                            'function_associations': behavior.get('FunctionAssociations', {}).get('Items', []),
                            'lambda_function_associations': behavior.get('LambdaFunctionAssociations', {}).get('Items', []),
                            'forwarded_values': behavior.get('ForwardedValues'),
                            'min_ttl': behavior.get('MinTTL', 0),
                            'default_ttl': behavior.get('DefaultTTL'),
                            'max_ttl': behavior.get('MaxTTL'),
                            'smooth_streaming': behavior.get('SmoothStreaming', False),
                            'trusted_signers': behavior.get('TrustedSigners', {}).get('Items', []),
                            'trusted_key_groups': behavior.get('TrustedKeyGroups', {}).get('Items', [])
                        }
                        config['cache_behaviors_formatted'].append(formatted_behavior)
                else:
                    config['cache_behaviors_formatted'] = []
                
                # Format custom error responses
                if config.get('CustomErrorResponses') and config['CustomErrorResponses'].get('Items'):
                    config['custom_error_responses_formatted'] = []
                    for error_response in config['CustomErrorResponses']['Items']:
                        formatted_response = {
                            'error_code': error_response['ErrorCode'],
                            'response_page_path': error_response.get('ResponsePagePath'),
                            'response_code': error_response.get('ResponseCode'),
                            'error_caching_min_ttl': error_response.get('ErrorCachingMinTTL', 300)
                        }
                        config['custom_error_responses_formatted'].append(formatted_response)
                else:
                    config['custom_error_responses_formatted'] = []
                
                # Format viewer certificate
                if config.get('ViewerCertificate'):
                    vc = config['ViewerCertificate']
                    config['viewer_certificate_formatted'] = {
                        'acm_certificate_arn': vc.get('ACMCertificateArn'),
                        'iam_certificate_id': vc.get('IAMCertificateId'),
                        'cloudfront_default_certificate': vc.get('CloudFrontDefaultCertificate', False),
                        'ssl_support_method': vc.get('SSLSupportMethod'),
                        'minimum_protocol_version': vc.get('MinimumProtocolVersion'),
                        'certificate_source': vc.get('CertificateSource')
                    }
                else:
                    config['viewer_certificate_formatted'] = {}
                
                # Format aliases (CNAMEs)
                if config.get('Aliases') and config['Aliases'].get('Items'):
                    config['aliases_formatted'] = config['Aliases']['Items']
                else:
                    config['aliases_formatted'] = []
                
                # Format logging configuration
                if config.get('Logging'):
                    logging_config = config['Logging']
                    config['logging_config_formatted'] = {
                        'enabled': logging_config.get('Enabled', False),
                        'include_cookies': logging_config.get('IncludeCookies', False),
                        'bucket': logging_config.get('Bucket'),
                        'prefix': logging_config.get('Prefix', '')
                    }
                else:
                    config['logging_config_formatted'] = {'enabled': False}
                
                # Format web ACL
                config['web_acl_id'] = config.get('WebACLId', '')
                
                # Format restrictions
                if config.get('Restrictions') and config['Restrictions'].get('GeoRestriction'):
                    geo_restriction = config['Restrictions']['GeoRestriction']
                    config['geo_restriction_formatted'] = {
                        'restriction_type': geo_restriction.get('RestrictionType', 'none'),
                        'locations': geo_restriction.get('Items', [])
                    }
                else:
                    config['geo_restriction_formatted'] = {'restriction_type': 'none', 'locations': []}
                
                # Get tags
                try:
                    tags_response = cloudfront_client.list_tags_for_resource(Resource=distribution['ARN'])
                    config['tags_formatted'] = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', {}).get('Items', [])}
                except Exception as e:
                    print(f"  - Warning: Could not retrieve tags for distribution {dist_id}: {e}")
                    config['tags_formatted'] = {}
                
                # Add the formatted config back to the distribution
                distribution['DistributionConfigFormatted'] = config
                
                distributions.append(distribution)
                
            except Exception as e:
                print(f"  - Warning: Could not retrieve details for distribution {dist_id}: {e}")
                continue
    
    output_file = output_dir / "cloudfront_distribution.tf"
    generate_tf(distributions, "cloudfront_distribution", output_file)
    print(f"Generated Terraform for {len(distributions)} CloudFront distributions -> {output_file}")
    generate_imports_file(
        "cloudfront_distribution", 
        distributions, 
        remote_resource_id_key="Id", 
        output_dir=output_dir
    )

def list_distributions(output_dir: Path):
    """Lists all CloudFront distribution resources previously generated."""
    ImportManager(output_dir, "cloudfront_distribution").list_all()

def import_distribution(distribution_id: str, output_dir: Path):
    """Runs terraform import for a specific CloudFront distribution by its ID."""
    ImportManager(output_dir, "cloudfront_distribution").find_and_import(distribution_id)