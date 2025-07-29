from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_launch_configurations(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for Launch Configurations and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    autoscaling_client = boto_session.client("autoscaling")
    
    print(f"Scanning for Launch Configurations in region {region}...")
    
    # Get all Launch Configurations using pagination
    paginator = autoscaling_client.get_paginator('describe_launch_configurations')
    launch_configurations = []
    
    for page in paginator.paginate():
        for lc in page['LaunchConfigurations']:
            # Add sanitized name for resource naming
            lc['name_sanitized'] = lc['LaunchConfigurationName'].replace('-', '_').replace(' ', '_').replace('.', '_').lower()
            
            # Format security groups for easier template usage
            if lc.get('SecurityGroups'):
                lc['SecurityGroupsFormatted'] = lc['SecurityGroups']
            else:
                lc['SecurityGroupsFormatted'] = []
            
            # Format block device mappings for easier template usage
            if lc.get('BlockDeviceMappings'):
                lc['BlockDeviceMappingsFormatted'] = []
                for bdm in lc['BlockDeviceMappings']:
                    formatted_bdm = {
                        'DeviceName': bdm['DeviceName'],
                        'VirtualName': bdm.get('VirtualName'),
                        'NoDevice': bdm.get('NoDevice')
                    }
                    if bdm.get('Ebs'):
                        formatted_bdm['Ebs'] = bdm['Ebs']
                    lc['BlockDeviceMappingsFormatted'].append(formatted_bdm)
            else:
                lc['BlockDeviceMappingsFormatted'] = []
            
            launch_configurations.append(lc)

    output_file = output_dir / "launch_configuration.tf"
    generate_tf(launch_configurations, "launch_configuration", output_file)
    print(f"Generated Terraform for {len(launch_configurations)} Launch Configurations -> {output_file}")
    generate_imports_file(
        "launch_configuration", 
        launch_configurations, 
        remote_resource_id_key="LaunchConfigurationName", 
        output_dir=output_dir
    )

def list_launch_configurations(output_dir: Path):
    """Lists all Launch Configuration resources previously generated."""
    ImportManager(output_dir, "launch_configuration").list_all()

def import_launch_configuration(lc_name: str, output_dir: Path):
    """Runs terraform import for a specific Launch Configuration by its name."""
    ImportManager(output_dir, "launch_configuration").find_and_import(lc_name)