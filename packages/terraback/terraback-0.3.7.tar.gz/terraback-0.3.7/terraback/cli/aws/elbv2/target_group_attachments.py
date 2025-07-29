from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_target_group_attachments(output_dir: Path, profile: str = None, region: str = "us-east-1", target_group_arn: str = None):
    """
    Scans for Target Group Attachments (registered targets) and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    elbv2_client = boto_session.client("elbv2")
    
    print(f"Scanning for Target Group Attachments in region {region}...")
    
    # Get target groups to scan
    target_groups = []
    if target_group_arn:
        # Scan specific target group
        try:
            response = elbv2_client.describe_target_groups(TargetGroupArns=[target_group_arn])
            target_groups = response['TargetGroups']
        except Exception as e:
            print(f"Error finding target group {target_group_arn}: {e}")
            return
    else:
        # Get all target groups
        tg_paginator = elbv2_client.get_paginator('describe_target_groups')
        for page in tg_paginator.paginate():
            target_groups.extend(page['TargetGroups'])
    
    if not target_groups:
        print("No target groups found")
        return
    
    # Get targets for each target group
    attachments = []
    for tg in target_groups:
        tg_arn = tg['TargetGroupArn']
        tg_name = tg['TargetGroupName']
        target_type = tg.get('TargetType', 'instance')
        
        try:
            # Get registered targets
            targets_response = elbv2_client.describe_target_health(TargetGroupArn=tg_arn)
            
            for target_health in targets_response.get('TargetHealthDescriptions', []):
                target = target_health['Target']
                
                # Create attachment resource
                attachment = {
                    'TargetGroupArn': tg_arn,
                    'TargetGroupName': tg_name,
                    'TargetType': target_type,
                    'TargetId': target['Id'],
                    'Port': target.get('Port'),
                    'AvailabilityZone': target.get('AvailabilityZone'),
                    'HealthCheckPort': target_health.get('HealthCheckPort'),
                    'State': target_health.get('TargetHealth', {}).get('State'),
                    'Reason': target_health.get('TargetHealth', {}).get('Reason'),
                    'Description': target_health.get('TargetHealth', {}).get('Description')
                }
                
                # Create sanitized names for resource naming
                if target_type == 'instance':
                    attachment['name_sanitized'] = f"{tg_name}_{target['Id'].replace('-', '_')}"
                elif target_type == 'ip':
                    attachment['name_sanitized'] = f"{tg_name}_{target['Id'].replace('.', '_')}"
                elif target_type == 'lambda':
                    # Lambda ARN: arn:aws:lambda:region:account:function:name
                    lambda_name = target['Id'].split(':')[-1]
                    attachment['name_sanitized'] = f"{tg_name}_{lambda_name.replace('-', '_')}"
                else:
                    attachment['name_sanitized'] = f"{tg_name}_{target['Id'].replace('-', '_').replace(':', '_')}"
                
                attachment['tg_name_sanitized'] = tg_name.replace('-', '_').replace('.', '_').lower()
                attachment['target_id_sanitized'] = target['Id'].replace('-', '_').replace('.', '_').replace(':', '_').lower()
                
                attachments.append(attachment)
                
        except Exception as e:
            print(f"  - Warning: Could not retrieve targets for target group {tg_name}: {e}")
            continue
    
    output_file = output_dir / "elbv2_target_group_attachment.tf"
    generate_tf(attachments, "elbv2_target_group_attachment", output_file)
    print(f"Generated Terraform for {len(attachments)} Target Group Attachments -> {output_file}")
    
    # Generate import file
    generate_imports_file(
        "elbv2_target_group_attachment",
        attachments,
        remote_resource_id_key="TargetGroupArn",  # Will be formatted specially
        output_dir=output_dir
    )

def list_target_group_attachments(output_dir: Path):
    """Lists all Target Group Attachment resources previously generated."""
    ImportManager(output_dir, "elbv2_target_group_attachment").list_all()

def import_target_group_attachment(target_group_arn: str, target_id: str, port: str, output_dir: Path):
    """
    Runs terraform import for a specific Target Group Attachment.
    Import format: <target_group_arn>/<target_id>/<port>
    """
    import_id = f"{target_group_arn}/{target_id}/{port}"
    ImportManager(output_dir, "elbv2_target_group_attachment").find_and_import(import_id)