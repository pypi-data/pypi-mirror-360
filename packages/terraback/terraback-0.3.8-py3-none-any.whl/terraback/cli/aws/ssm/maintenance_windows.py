from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_maintenance_windows(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for Systems Manager maintenance windows and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ssm_client = boto_session.client("ssm")
    
    print(f"Scanning for Systems Manager maintenance windows in region {region}...")
    
    maintenance_windows = []
    
    try:
        # Get maintenance windows
        response = ssm_client.describe_maintenance_windows()
        
        for mw_summary in response.get('WindowIdentities', []):
            window_id = mw_summary['WindowId']
            
            try:
                # Get detailed maintenance window information
                window_detail = ssm_client.get_maintenance_window(WindowId=window_id)
                
                # Create maintenance window object
                maintenance_window = {
                    'WindowId': window_id,
                    'Name': window_detail.get('Name'),
                    'Description': window_detail.get('Description', ''),
                    'Schedule': window_detail.get('Schedule'),
                    'ScheduleTimezone': window_detail.get('ScheduleTimezone'),
                    'ScheduleOffset': window_detail.get('ScheduleOffset'),
                    'Duration': window_detail.get('Duration'),
                    'Cutoff': window_detail.get('Cutoff'),
                    'AllowUnassociatedTargets': window_detail.get('AllowUnassociatedTargets', False),
                    'Enabled': window_detail.get('Enabled', True),
                    'CreatedDate': window_detail.get('CreatedDate'),
                    'ModifiedDate': window_detail.get('ModifiedDate'),
                    'StartDate': window_detail.get('StartDate'),
                    'EndDate': window_detail.get('EndDate'),
                    'NextExecutionTime': window_detail.get('NextExecutionTime')
                }
                
                # Add sanitized name for resource naming
                window_name = maintenance_window.get('Name', window_id)
                maintenance_window['name_sanitized'] = window_name.replace('-', '_').replace(' ', '_').replace('.', '_').lower()
                
                # Get maintenance window targets
                try:
                    targets_response = ssm_client.describe_maintenance_window_targets(
                        WindowId=window_id
                    )
                    maintenance_window['targets'] = targets_response.get('Targets', [])
                    maintenance_window['targets_formatted'] = []
                    
                    for target in maintenance_window['targets']:
                        formatted_target = {
                            'WindowId': target.get('WindowId'),
                            'WindowTargetId': target.get('WindowTargetId'),
                            'ResourceType': target.get('ResourceType'),
                            'Targets': target.get('Targets', []),
                            'OwnerInformation': target.get('OwnerInformation'),
                            'Name': target.get('Name'),
                            'Description': target.get('Description', '')
                        }
                        maintenance_window['targets_formatted'].append(formatted_target)
                        
                except Exception as e:
                    print(f"  - Warning: Could not retrieve targets for maintenance window {window_id}: {e}")
                    maintenance_window['targets'] = []
                    maintenance_window['targets_formatted'] = []
                
                # Get maintenance window tasks
                try:
                    tasks_response = ssm_client.describe_maintenance_window_tasks(
                        WindowId=window_id
                    )
                    maintenance_window['tasks'] = tasks_response.get('Tasks', [])
                    maintenance_window['tasks_formatted'] = []
                    
                    for task in maintenance_window['tasks']:
                        formatted_task = {
                            'WindowId': task.get('WindowId'),
                            'WindowTaskId': task.get('WindowTaskId'),
                            'TaskArn': task.get('TaskArn'),
                            'Type': task.get('Type'),
                            'Targets': task.get('Targets', []),
                            'TaskParameters': task.get('TaskParameters', {}),
                            'Priority': task.get('Priority', 1),
                            'ServiceRoleArn': task.get('ServiceRoleArn'),
                            'MaxConcurrency': task.get('MaxConcurrency'),
                            'MaxErrors': task.get('MaxErrors'),
                            'Name': task.get('Name'),
                            'Description': task.get('Description', ''),
                            'CutoffBehavior': task.get('CutoffBehavior')
                        }
                        maintenance_window['tasks_formatted'].append(formatted_task)
                        
                except Exception as e:
                    print(f"  - Warning: Could not retrieve tasks for maintenance window {window_id}: {e}")
                    maintenance_window['tasks'] = []
                    maintenance_window['tasks_formatted'] = []
                
                # Calculate derived properties
                maintenance_window['has_targets'] = len(maintenance_window['targets_formatted']) > 0
                maintenance_window['has_tasks'] = len(maintenance_window['tasks_formatted']) > 0
                maintenance_window['is_enabled'] = maintenance_window.get('Enabled', False)
                
                # Format schedule timezone
                if maintenance_window.get('ScheduleTimezone'):
                    maintenance_window['has_timezone'] = True
                else:
                    maintenance_window['has_timezone'] = False
                
                # Get tags
                try:
                    tags_response = ssm_client.list_tags_for_resource(
                        ResourceType='MaintenanceWindow',
                        ResourceId=window_id
                    )
                    maintenance_window['tags_formatted'] = {
                        tag['Key']: tag['Value'] 
                        for tag in tags_response.get('TagList', [])
                    }
                except Exception as e:
                    print(f"  - Warning: Could not retrieve tags for maintenance window {window_id}: {e}")
                    maintenance_window['tags_formatted'] = {}
                
                maintenance_windows.append(maintenance_window)
                
            except Exception as e:
                print(f"  - Warning: Could not retrieve details for maintenance window {window_id}: {e}")
                continue
    
    except Exception as e:
        print(f"Error scanning maintenance windows: {e}")
        return
    
    # Generate maintenance windows
    if maintenance_windows:
        output_file = output_dir / "ssm_maintenance_window.tf"
        generate_tf(maintenance_windows, "ssm_maintenance_window", output_file)
        print(f"Generated Terraform for {len(maintenance_windows)} Systems Manager maintenance windows -> {output_file}")
        generate_imports_file(
            "ssm_maintenance_window", 
            maintenance_windows, 
            remote_resource_id_key="WindowId", 
            output_dir=output_dir
        )

def list_maintenance_windows(output_dir: Path):
    """Lists all Systems Manager maintenance window resources previously generated."""
    ImportManager(output_dir, "ssm_maintenance_window").list_all()

def import_maintenance_window(window_id: str, output_dir: Path):
    """Runs terraform import for a specific Systems Manager maintenance window by its ID."""
    ImportManager(output_dir, "ssm_maintenance_window").find_and_import(window_id)