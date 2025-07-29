from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_alarms(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for CloudWatch Alarms and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    cloudwatch_client = boto_session.client("cloudwatch")
    
    print(f"Scanning for CloudWatch Alarms in region {region}...")
    
    # Get all alarms using pagination
    paginator = cloudwatch_client.get_paginator('describe_alarms')
    alarms = []
    
    for page in paginator.paginate():
        for alarm in page['MetricAlarms']:
            # Get tags for each alarm
            try:
                tags_response = cloudwatch_client.list_tags_for_resource(
                    ResourceARN=alarm['AlarmArn']
                )
                # Convert tag format to match other services
                alarm['Tags'] = [
                    {'Key': tag['Key'], 'Value': tag['Value']} 
                    for tag in tags_response.get('Tags', [])
                ]
            except Exception as e:
                print(f"  - Warning: Could not retrieve tags for alarm {alarm['AlarmName']}: {e}")
                alarm['Tags'] = []
            
            # Add sanitized name for resource naming
            alarm['name_sanitized'] = alarm['AlarmName'].replace('-', '_').replace(' ', '_').replace('.', '_').lower()
            alarms.append(alarm)

    # Also get composite alarms if they exist
    try:
        composite_paginator = cloudwatch_client.get_paginator('describe_alarms')
        for page in composite_paginator.paginate(AlarmTypes=['CompositeAlarm']):
            for alarm in page['CompositeAlarms']:
                # Get tags for composite alarms
                try:
                    tags_response = cloudwatch_client.list_tags_for_resource(
                        ResourceARN=alarm['AlarmArn']
                    )
                    alarm['Tags'] = [
                        {'Key': tag['Key'], 'Value': tag['Value']} 
                        for tag in tags_response.get('Tags', [])
                    ]
                except Exception as e:
                    print(f"  - Warning: Could not retrieve tags for composite alarm {alarm['AlarmName']}: {e}")
                    alarm['Tags'] = []
                
                alarm['name_sanitized'] = alarm['AlarmName'].replace('-', '_').replace(' ', '_').replace('.', '_').lower()
                alarm['AlarmType'] = 'CompositeAlarm'  # Mark as composite
                alarms.append(alarm)
    except Exception as e:
        print(f"  - Note: Could not retrieve composite alarms (may not be available in this region): {e}")

    output_file = output_dir / "cloudwatch_alarm.tf"
    generate_tf(alarms, "cloudwatch_alarm", output_file)
    print(f"Generated Terraform for {len(alarms)} CloudWatch Alarms -> {output_file}")
    generate_imports_file(
        "cloudwatch_alarm", 
        alarms, 
        remote_resource_id_key="AlarmName", 
        output_dir=output_dir
    )

def list_alarms(output_dir: Path):
    """Lists all CloudWatch Alarm resources previously generated."""
    ImportManager(output_dir, "cloudwatch_alarm").list_all()

def import_alarm(alarm_name: str, output_dir: Path):
    """Runs terraform import for a specific CloudWatch Alarm by its name."""
    ImportManager(output_dir, "cloudwatch_alarm").find_and_import(alarm_name)