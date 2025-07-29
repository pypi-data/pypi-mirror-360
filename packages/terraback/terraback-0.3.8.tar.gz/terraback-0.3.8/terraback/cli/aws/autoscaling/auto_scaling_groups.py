from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_auto_scaling_groups(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for Auto Scaling Groups and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    autoscaling_client = boto_session.client("autoscaling")
    
    print(f"Scanning for Auto Scaling Groups in region {region}...")
    
    # Get all Auto Scaling Groups using pagination
    paginator = autoscaling_client.get_paginator('describe_auto_scaling_groups')
    auto_scaling_groups = []
    
    for page in paginator.paginate():
        for asg in page['AutoScalingGroups']:
            # Get tags for the ASG (tags are already included in the response)
            # Convert tag format for easier template usage
            asg['TagsFormatted'] = []
            for tag in asg.get('Tags', []):
                asg['TagsFormatted'].append({
                    'Key': tag['Key'],
                    'Value': tag['Value'],
                    'PropagateAtLaunch': tag.get('PropagateAtLaunch', False)
                })
            
            # Add sanitized name for resource naming
            asg['name_sanitized'] = asg['AutoScalingGroupName'].replace('-', '_').replace(' ', '_').replace('.', '_').lower()
            
            # Extract launch template or launch configuration info for easier template access
            if asg.get('LaunchTemplate'):
                asg['UsesLaunchTemplate'] = True
                asg['UsesLaunchConfiguration'] = False
            elif asg.get('LaunchConfigurationName'):
                asg['UsesLaunchTemplate'] = False
                asg['UsesLaunchConfiguration'] = True
            else:
                asg['UsesLaunchTemplate'] = False
                asg['UsesLaunchConfiguration'] = False
            
            auto_scaling_groups.append(asg)

    output_file = output_dir / "autoscaling_group.tf"
    generate_tf(auto_scaling_groups, "autoscaling_group", output_file)
    print(f"Generated Terraform for {len(auto_scaling_groups)} Auto Scaling Groups -> {output_file}")
    generate_imports_file(
        "autoscaling_group", 
        auto_scaling_groups, 
        remote_resource_id_key="AutoScalingGroupName", 
        output_dir=output_dir
    )

def list_auto_scaling_groups(output_dir: Path):
    """Lists all Auto Scaling Group resources previously generated."""
    ImportManager(output_dir, "autoscaling_group").list_all()

def import_auto_scaling_group(asg_name: str, output_dir: Path):
    """Runs terraform import for a specific Auto Scaling Group by its name."""
    ImportManager(output_dir, "autoscaling_group").find_and_import(asg_name)