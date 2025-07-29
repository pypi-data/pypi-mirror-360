from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_listener_rules(output_dir: Path, profile: str = None, region: str = "us-east-1", listener_arn: str = None):
    """
    Scans for ALB/NLB Listener Rules and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    elbv2_client = boto_session.client("elbv2")
    
    print(f"Scanning for ELB v2 Listener Rules in region {region}...")
    
    # Get listeners to scan rules for
    listeners = []
    if listener_arn:
        # Scan specific listener
        try:
            response = elbv2_client.describe_listeners(ListenerArns=[listener_arn])
            listeners = response['Listeners']
        except Exception as e:
            print(f"Error finding listener {listener_arn}: {e}")
            return
    else:
        # Get all load balancers first, then their listeners
        lb_paginator = elbv2_client.get_paginator('describe_load_balancers')
        for lb_page in lb_paginator.paginate():
            for lb in lb_page['LoadBalancers']:
                try:
                    listener_response = elbv2_client.describe_listeners(LoadBalancerArn=lb['LoadBalancerArn'])
                    listeners.extend(listener_response['Listeners'])
                except Exception as e:
                    print(f"  - Warning: Could not retrieve listeners for LB {lb['LoadBalancerName']}: {e}")
                    continue
    
    if not listeners:
        print("No listeners found")
        return
    
    # Get rules for each listener
    listener_rules = []
    for listener in listeners:
        listener_arn = listener['ListenerArn']
        listener_port = listener['Port']
        lb_name = listener_arn.split('/')[-3]  # Extract LB name from ARN
        
        try:
            # Get rules for this listener
            rules_response = elbv2_client.describe_rules(ListenerArn=listener_arn)
            
            for rule in rules_response['Rules']:
                # Skip default rules as they're managed by the listener resource
                if rule.get('IsDefault', False):
                    continue
                
                # Add context information for easier template usage
                rule['ListenerArn'] = listener_arn
                rule['ListenerPort'] = listener_port
                rule['LoadBalancerName'] = lb_name
                
                # Add sanitized names for resource naming
                rule_arn = rule['RuleArn']
                rule_arn_parts = rule_arn.split('/')
                rule['name_sanitized'] = f"{lb_name}_{listener_port}_{rule_arn_parts[-1]}".replace('-', '_').replace('.', '_').lower()
                rule['lb_name_sanitized'] = lb_name.replace('-', '_').replace('.', '_').lower()
                rule['listener_port_sanitized'] = str(listener_port)
                
                # Format conditions for easier template usage
                if rule.get('Conditions'):
                    rule['conditions_formatted'] = []
                    for condition in rule['Conditions']:
                        formatted_condition = {
                            'field': condition.get('Field'),
                            'values': condition.get('Values', []),
                            'host_header_config': condition.get('HostHeaderConfig'),
                            'path_pattern_config': condition.get('PathPatternConfig'),
                            'http_header_config': condition.get('HttpHeaderConfig'),
                            'query_string_config': condition.get('QueryStringConfig'),
                            'http_request_method_config': condition.get('HttpRequestMethodConfig'),
                            'source_ip_config': condition.get('SourceIpConfig')
                        }
                        rule['conditions_formatted'].append(formatted_condition)
                else:
                    rule['conditions_formatted'] = []
                
                # Format actions for easier template usage
                if rule.get('Actions'):
                    rule['actions_formatted'] = []
                    for action in rule['Actions']:
                        formatted_action = {
                            'type': action.get('Type'),
                            'order': action.get('Order', 100),
                            'target_group_arn': action.get('TargetGroupArn'),
                            'forward_config': action.get('ForwardConfig'),
                            'redirect_config': action.get('RedirectConfig'),
                            'fixed_response_config': action.get('FixedResponseConfig'),
                            'authenticate_cognito_config': action.get('AuthenticateCognitoConfig'),
                            'authenticate_oidc_config': action.get('AuthenticateOidcConfig')
                        }
                        rule['actions_formatted'].append(formatted_action)
                else:
                    rule['actions_formatted'] = []
                
                # Extract priority for easier access
                rule['priority_value'] = rule.get('Priority', 'default')
                
                listener_rules.append(rule)
                
        except Exception as e:
            print(f"  - Warning: Could not retrieve rules for listener {listener_arn}: {e}")
            continue
    
    output_file = output_dir / "elbv2_listener_rule.tf"
    generate_tf(listener_rules, "elbv2_listener_rule", output_file)
    print(f"Generated Terraform for {len(listener_rules)} ELB v2 Listener Rules -> {output_file}")
    generate_imports_file(
        "elbv2_listener_rule", 
        listener_rules, 
        remote_resource_id_key="RuleArn", 
        output_dir=output_dir
    )

def list_listener_rules(output_dir: Path):
    """Lists all ELB v2 Listener Rule resources previously generated."""
    ImportManager(output_dir, "elbv2_listener_rule").list_all()

def import_listener_rule(rule_arn: str, output_dir: Path):
    """Runs terraform import for a specific ELB v2 Listener Rule by its ARN."""
    ImportManager(output_dir, "elbv2_listener_rule").find_and_import(rule_arn)