from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_scaling_policies(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for Auto Scaling Policies and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    autoscaling_client = boto_session.client("autoscaling")
    
    print(f"Scanning for Auto Scaling Policies in region {region}...")
    
    # Get all Scaling Policies using pagination
    paginator = autoscaling_client.get_paginator('describe_policies')
    scaling_policies = []
    
    for page in paginator.paginate():
        for policy in page['ScalingPolicies']:
            # Add sanitized name for resource naming
            policy['name_sanitized'] = policy['PolicyName'].replace('-', '_').replace(' ', '_').replace('.', '_').lower()
            
            # Add ASG name sanitized for cross-referencing
            policy['asg_name_sanitized'] = policy['AutoScalingGroupName'].replace('-', '_').replace(' ', '_').replace('.', '_').lower()
            
            # Format step adjustments if present
            if policy.get('StepAdjustments'):
                policy['StepAdjustmentsFormatted'] = []
                for step in policy['StepAdjustments']:
                    formatted_step = {
                        'MetricIntervalLowerBound': step.get('MetricIntervalLowerBound'),
                        'MetricIntervalUpperBound': step.get('MetricIntervalUpperBound'),
                        'ScalingAdjustment': step['ScalingAdjustment']
                    }
                    policy['StepAdjustmentsFormatted'].append(formatted_step)
            else:
                policy['StepAdjustmentsFormatted'] = []
            
            # Format target tracking configuration if present
            if policy.get('TargetTrackingConfiguration'):
                ttc = policy['TargetTrackingConfiguration']
                policy['TargetTrackingFormatted'] = {
                    'TargetValue': ttc['TargetValue'],
                    'DisableScaleIn': ttc.get('DisableScaleIn', False)
                }
                
                # Handle predefined metric specification
                if ttc.get('PredefinedMetricSpecification'):
                    pms = ttc['PredefinedMetricSpecification']
                    policy['TargetTrackingFormatted']['PredefinedMetricSpecification'] = {
                        'PredefinedMetricType': pms['PredefinedMetricType']
                    }
                    if pms.get('ResourceLabel'):
                        policy['TargetTrackingFormatted']['PredefinedMetricSpecification']['ResourceLabel'] = pms['ResourceLabel']
                
                # Handle custom metric specification
                if ttc.get('CustomizedMetricSpecification'):
                    cms = ttc['CustomizedMetricSpecification']
                    policy['TargetTrackingFormatted']['CustomizedMetricSpecification'] = {
                        'MetricName': cms['MetricName'],
                        'Namespace': cms['Namespace'],
                        'Statistic': cms['Statistic']
                    }
                    if cms.get('Dimensions'):
                        policy['TargetTrackingFormatted']['CustomizedMetricSpecification']['Dimensions'] = cms['Dimensions']
                    if cms.get('Unit'):
                        policy['TargetTrackingFormatted']['CustomizedMetricSpecification']['Unit'] = cms['Unit']
            else:
                policy['TargetTrackingFormatted'] = None
            
            scaling_policies.append(policy)

    output_file = output_dir / "autoscaling_policy.tf"
    generate_tf(scaling_policies, "autoscaling_policy", output_file)
    print(f"Generated Terraform for {len(scaling_policies)} Auto Scaling Policies -> {output_file}")
    generate_imports_file(
        "autoscaling_policy", 
        scaling_policies, 
        remote_resource_id_key="PolicyARN", 
        output_dir=output_dir
    )

def list_scaling_policies(output_dir: Path):
    """Lists all Auto Scaling Policy resources previously generated."""
    ImportManager(output_dir, "autoscaling_policy").list_all()

def import_scaling_policy(policy_arn: str, output_dir: Path):
    """Runs terraform import for a specific Auto Scaling Policy by its ARN."""
    ImportManager(output_dir, "autoscaling_policy").find_and_import(policy_arn)