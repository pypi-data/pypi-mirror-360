from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_waf_associations(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for WAF WebACL associations with ALBs and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    elbv2_client = boto_session.client("elbv2")
    wafv2_client = boto_session.client("wafv2")
    
    print(f"Scanning for WAF WebACL associations with ALBs in region {region}...")
    
    # Get all ALBs first
    alb_arns = []
    lb_paginator = elbv2_client.get_paginator('describe_load_balancers')
    for page in lb_paginator.paginate():
        for lb in page['LoadBalancers']:
            if lb['Type'] == 'application':  # WAF only works with ALBs
                alb_arns.append({
                    'arn': lb['LoadBalancerArn'],
                    'name': lb['LoadBalancerName']
                })
    
    if not alb_arns:
        print("No Application Load Balancers found")
        return
    
    # Check WAF associations
    associations = []
    for alb in alb_arns:
        try:
            # Check if ALB has WAF WebACL associated
            response = wafv2_client.get_web_acl_for_resource(
                ResourceArn=alb['arn']
            )
            
            if response.get('WebACL'):
                web_acl = response['WebACL']
                association = {
                    'ResourceArn': alb['arn'],
                    'ResourceName': alb['name'],
                    'WebACLArn': web_acl['ARN'],
                    'WebACLName': web_acl['Name'],
                    'WebACLId': web_acl['Id'],
                    'name_sanitized': f"{alb['name'].replace('-', '_')}_{web_acl['Name'].replace('-', '_')}".lower()
                }
                associations.append(association)
        except wafv2_client.exceptions.WAFNonexistentItemException:
            # No WAF association for this ALB
            continue
        except Exception as e:
            print(f"  - Warning: Could not check WAF association for ALB {alb['name']}: {e}")
            continue
    
    if associations:
        output_file = output_dir / "wafv2_web_acl_association.tf"
        generate_tf(associations, "wafv2_web_acl_association", output_file)
        print(f"Generated Terraform for {len(associations)} WAF WebACL associations -> {output_file}")
        
        # Generate import file
        generate_imports_file(
            "wafv2_web_acl_association",
            associations,
            remote_resource_id_key="ResourceArn",  # Will be formatted specially
            output_dir=output_dir
        )
    else:
        print("No WAF WebACL associations found")

def list_waf_associations(output_dir: Path):
    """Lists all WAF WebACL Association resources previously generated."""
    ImportManager(output_dir, "wafv2_web_acl_association").list_all()

def import_waf_association(resource_arn: str, web_acl_arn: str, output_dir: Path):
    """
    Runs terraform import for a specific WAF WebACL Association.
    Import format: <resource_arn>,<web_acl_arn>
    """
    import_id = f"{resource_arn},{web_acl_arn}"
    ImportManager(output_dir, "wafv2_web_acl_association").find_and_import(import_id)