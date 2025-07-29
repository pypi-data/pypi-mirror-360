from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_ssl_policies(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for ELB SSL Policies and generates Terraform code.
    Note: This scans predefined AWS SSL policies and any custom policies in use.
    """
    boto_session = get_boto_session(profile, region)
    elbv2_client = boto_session.client("elbv2")
    
    print(f"Scanning for ELB SSL Policies in region {region}...")
    
    # First, get all SSL policies
    try:
        response = elbv2_client.describe_ssl_policies()
        all_policies = response['SslPolicies']
    except Exception as e:
        print(f"Error retrieving SSL policies: {e}")
        return
    
    # Get policies actually in use by listeners
    used_policies = set()
    
    # Get all load balancers and their listeners to find used SSL policies
    try:
        lb_paginator = elbv2_client.get_paginator('describe_load_balancers')
        for lb_page in lb_paginator.paginate():
            for lb in lb_page['LoadBalancers']:
                try:
                    listener_response = elbv2_client.describe_listeners(LoadBalancerArn=lb['LoadBalancerArn'])
                    for listener in listener_response['Listeners']:
                        if listener.get('Protocol') in ['HTTPS', 'TLS'] and listener.get('SslPolicy'):
                            used_policies.add(listener['SslPolicy'])
                except Exception as e:
                    print(f"  - Warning: Could not retrieve listeners for LB {lb['LoadBalancerName']}: {e}")
                    continue
    except Exception as e:
        print(f"  - Warning: Could not retrieve load balancers: {e}")
    
    # Filter policies to only include those in use or commonly used AWS managed policies
    important_policies = {
        'ELBSecurityPolicy-TLS-1-2-2017-01',
        'ELBSecurityPolicy-TLS-1-2-Ext-2018-06', 
        'ELBSecurityPolicy-FS-2018-06',
        'ELBSecurityPolicy-FS-1-2-2019-08',
        'ELBSecurityPolicy-FS-1-2-Res-2019-08',
        'ELBSecurityPolicy-FS-1-2-Res-2020-10',
        'ELBSecurityPolicy-TLS-1-1-2017-01',
        'ELBSecurityPolicy-2016-08',
        'ELBSecurityPolicy-TLS13-1-2-2021-06'
    }
    
    # Include policies that are either in use or are important AWS managed policies
    policies_to_include = used_policies.union(important_policies)
    
    ssl_policies = []
    for policy in all_policies:
        policy_name = policy['Name']
        
        # Include if it's in use or is an important AWS managed policy
        if policy_name in policies_to_include:
            # Add sanitized name for resource naming
            policy['name_sanitized'] = policy_name.replace('-', '_').replace('.', '_').lower()
            
            # Determine if it's a custom policy (not AWS managed)
            policy['is_custom'] = not policy_name.startswith('ELBSecurityPolicy-')
            policy['is_aws_managed'] = policy_name.startswith('ELBSecurityPolicy-')
            policy['is_in_use'] = policy_name in used_policies
            
            # Format supported protocols
            if policy.get('SupportedProtocols'):
                policy['supported_protocols_formatted'] = policy['SupportedProtocols']
            else:
                policy['supported_protocols_formatted'] = []
            
            # Format ciphers for easier template usage
            if policy.get('Ciphers'):
                policy['ciphers_formatted'] = []
                for cipher in policy['Ciphers']:
                    formatted_cipher = {
                        'name': cipher.get('Name'),
                        'priority': cipher.get('Priority')
                    }
                    policy['ciphers_formatted'].append(formatted_cipher)
            else:
                policy['ciphers_formatted'] = []
            
            ssl_policies.append(policy)
    
    # Sort by in-use first, then by name
    ssl_policies.sort(key=lambda p: (not p['is_in_use'], p['Name']))
    
    output_file = output_dir / "elbv2_ssl_policy.tf"
    generate_tf(ssl_policies, "elbv2_ssl_policy", output_file)
    print(f"Generated Terraform for {len(ssl_policies)} ELB SSL Policies ({len(used_policies)} in use) -> {output_file}")
    
    # Note: SSL policies are typically not imported as they're AWS managed resources
    # But we'll generate the import file for any custom policies
    custom_policies = [p for p in ssl_policies if p['is_custom']]
    if custom_policies:
        generate_imports_file(
            "elbv2_ssl_policy", 
            custom_policies, 
            remote_resource_id_key="Name", 
            output_dir=output_dir
        )

def list_ssl_policies(output_dir: Path):
    """Lists all ELB SSL Policy resources previously generated."""
    ImportManager(output_dir, "elbv2_ssl_policy").list_all()

def import_ssl_policy(policy_name: str, output_dir: Path):
    """Runs terraform import for a specific ELB SSL Policy by its name."""
    ImportManager(output_dir, "elbv2_ssl_policy").find_and_import(policy_name)