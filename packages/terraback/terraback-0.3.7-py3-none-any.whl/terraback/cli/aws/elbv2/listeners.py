from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_listeners(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for ELBv2 Listeners and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    elbv2_client = boto_session.client("elbv2")

    print(f"Scanning for Listeners in region {region}...")
    # First, find all load balancers to then find their listeners
    lb_paginator = elbv2_client.get_paginator('describe_load_balancers')
    all_listeners = []
    for page in lb_paginator.paginate():
        for lb in page['LoadBalancers']:
            try:
                listener_paginator = elbv2_client.get_paginator('describe_listeners')
                for listener_page in listener_paginator.paginate(LoadBalancerArn=lb['LoadBalancerArn']):
                    for listener in listener_page['Listeners']:
                        # Add load balancer context
                        listener['LoadBalancerName'] = lb['LoadBalancerName']
                        listener['LoadBalancerType'] = lb['Type']
                        
                        # Add sanitized name for resource naming
                        lb_name_clean = lb['LoadBalancerName'].replace('-', '_').replace('.', '_').lower()
                        listener['name_sanitized'] = f"{lb_name_clean}_{listener['Port']}_{listener['Protocol'].lower()}"
                        
                        # Get additional listener certificates if any
                        if listener.get('Certificates') and len(listener['Certificates']) > 1:
                            try:
                                cert_response = elbv2_client.describe_listener_certificates(
                                    ListenerArn=listener['ListenerArn']
                                )
                                # Merge additional certificates
                                additional_certs = cert_response.get('Certificates', [])
                                if additional_certs:
                                    # Keep the default cert first, add others
                                    all_certs = [listener['Certificates'][0]]
                                    for cert in additional_certs:
                                        if cert['CertificateArn'] != listener['Certificates'][0]['CertificateArn']:
                                            all_certs.append(cert)
                                    listener['Certificates'] = all_certs
                            except Exception as e:
                                print(f"  - Warning: Could not retrieve additional certificates for listener: {e}")
                        
                        all_listeners.append(listener)
            except Exception as e:
                print(f"  - Warning: Could not retrieve listeners for LB {lb['LoadBalancerName']}: {e}")
                continue
    
    output_file = output_dir / "elbv2_listener.tf"
    generate_tf(all_listeners, "elbv2_listener", output_file)
    print(f"Generated Terraform for {len(all_listeners)} Listeners -> {output_file}")
    generate_imports_file("elbv2_listener", all_listeners, remote_resource_id_key="ListenerArn", output_dir=output_dir)

def list_listeners(output_dir: Path):
    ImportManager(output_dir, "elbv2_listener").list_all()

def import_listener(listener_arn: str, output_dir: Path):
    ImportManager(output_dir, "elbv2_listener").find_and_import(listener_arn)