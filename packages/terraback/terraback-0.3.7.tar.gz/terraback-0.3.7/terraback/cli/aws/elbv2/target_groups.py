from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_target_groups(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for ELBv2 Target Groups and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    elbv2_client = boto_session.client("elbv2")
    
    print(f"Scanning for Target Groups in region {region}...")
    paginator = elbv2_client.get_paginator('describe_target_groups')
    target_groups = []
    for page in paginator.paginate():
        for tg in page['TargetGroups']:
            # Fetch tags for each target group
            tags_response = elbv2_client.describe_tags(ResourceArns=[tg['TargetGroupArn']])
            tg['Tags'] = tags_response['TagDescriptions'][0]['Tags']
            
            # Fetch target group attributes
            try:
                attrs_response = elbv2_client.describe_target_group_attributes(
                    TargetGroupArn=tg['TargetGroupArn']
                )
                tg['Attributes'] = {}
                for attr in attrs_response.get('Attributes', []):
                    tg['Attributes'][attr['Key']] = attr['Value']
            except Exception as e:
                print(f"  - Warning: Could not retrieve attributes for TG {tg['TargetGroupName']}: {e}")
                tg['Attributes'] = {}
            
            # Add sanitized name for resource naming
            tg['name_sanitized'] = tg['TargetGroupName'].replace('-', '_').replace('.', '_').lower()
            
            # Format stickiness configuration
            if tg['Attributes'].get('stickiness.enabled') == 'true':
                tg['stickiness_config'] = {
                    'enabled': True,
                    'type': tg['Attributes'].get('stickiness.type', 'lb_cookie'),
                    'cookie_duration': tg['Attributes'].get('stickiness.lb_cookie.duration_seconds', '86400'),
                    'cookie_name': tg['Attributes'].get('stickiness.app_cookie.cookie_name'),
                    'app_cookie_duration': tg['Attributes'].get('stickiness.app_cookie.duration_seconds')
                }
            else:
                tg['stickiness_config'] = None
            
            target_groups.append(tg)

    output_file = output_dir / "elbv2_target_group.tf"
    generate_tf(target_groups, "elbv2_target_group", output_file)
    print(f"Generated Terraform for {len(target_groups)} Target Groups -> {output_file}")
    generate_imports_file("elbv2_target_group", target_groups, remote_resource_id_key="TargetGroupArn", output_dir=output_dir)

def list_target_groups(output_dir: Path):
    ImportManager(output_dir, "elbv2_target_group").list_all()

def import_target_group(tg_arn: str, output_dir: Path):
    ImportManager(output_dir, "elbv2_target_group").find_and_import(tg_arn)