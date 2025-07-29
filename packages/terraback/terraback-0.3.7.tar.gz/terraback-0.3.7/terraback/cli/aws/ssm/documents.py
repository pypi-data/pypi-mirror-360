from pathlib import Path
import json
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_documents(output_dir: Path, profile: str = None, region: str = "us-east-1", 
                  owner_filter: str = "Self", document_type: str = None):
    """
    Scans for Systems Manager documents and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    ssm_client = boto_session.client("ssm")
    
    print(f"Scanning for Systems Manager documents in region {region}...")
    
    # Build document filters
    filters = [
        {
            'Key': 'Owner',
            'Values': [owner_filter]
        }
    ]
    
    if document_type:
        filters.append({
            'Key': 'DocumentType',
            'Values': [document_type]
        })
    
    documents = []
    
    try:
        # Get documents using pagination
        paginator = ssm_client.get_paginator('list_documents')
        
        for page in paginator.paginate(DocumentFilterList=filters):
            for doc_identifier in page.get('DocumentIdentifiers', []):
                document_name = doc_identifier['Name']
                
                try:
                    # Get document details
                    document_detail = ssm_client.describe_document(Name=document_name)
                    doc_info = document_detail['Document']
                    
                    # Get document content
                    try:
                        content_response = ssm_client.get_document(Name=document_name)
                        document_content = content_response.get('Content', '')
                        document_format = content_response.get('DocumentFormat', 'JSON')
                    except Exception as e:
                        print(f"  - Warning: Could not retrieve content for document {document_name}: {e}")
                        document_content = ''
                        document_format = 'JSON'
                    
                    # Create document object
                    document = {
                        'Name': document_name,
                        'DocumentType': doc_info['DocumentType'],
                        'DocumentFormat': document_format,
                        'DocumentVersion': doc_info.get('DocumentVersion', '$LATEST'),
                        'Content': document_content,
                        'Description': doc_info.get('Description', ''),
                        'Owner': doc_info.get('Owner'),
                        'CreatedDate': doc_info.get('CreatedDate'),
                        'Status': doc_info.get('Status'),
                        'StatusInformation': doc_info.get('StatusInformation', ''),
                        'VersionName': doc_info.get('VersionName'),
                        'PlatformTypes': doc_info.get('PlatformTypes', []),
                        'Parameters': doc_info.get('Parameters', []),
                        'TargetType': doc_info.get('TargetType'),
                        'SchemaVersion': doc_info.get('SchemaVersion'),
                        'LatestVersion': doc_info.get('LatestVersion'),
                        'DefaultVersion': doc_info.get('DefaultVersion')
                    }
                    
                    # Add sanitized name for resource naming
                    document['name_sanitized'] = document_name.replace('-', '_').replace(' ', '_').replace('.', '_').lower()
                    
                    # Format document type for easier template usage
                    doc_type = document['DocumentType']
                    document['is_command'] = doc_type == 'Command'
                    document['is_policy'] = doc_type == 'Policy'
                    document['is_automation'] = doc_type == 'Automation'
                    document['is_session'] = doc_type == 'Session'
                    document['is_package'] = doc_type == 'Package'
                    document['is_application_configuration'] = doc_type == 'ApplicationConfiguration'
                    document['is_application_configuration_schema'] = doc_type == 'ApplicationConfigurationSchema'
                    document['is_deployment_strategy'] = doc_type == 'DeploymentStrategy'
                    document['is_change_calendar'] = doc_type == 'ChangeCalendar'
                    
                    # Format platform types
                    document['platform_types_formatted'] = document['PlatformTypes']
                    document['supports_windows'] = 'Windows' in document['PlatformTypes']
                    document['supports_linux'] = 'Linux' in document['PlatformTypes']
                    document['supports_macos'] = 'MacOS' in document['PlatformTypes']
                    
                    # Format parameters for easier template usage
                    document['parameters_formatted'] = []
                    for param in document.get('Parameters', []):
                        formatted_param = {
                            'Name': param.get('Name'),
                            'Type': param.get('Type'),
                            'Description': param.get('Description', ''),
                            'DefaultValue': param.get('DefaultValue'),
                            'AllowedValues': param.get('AllowedValues', []),
                            'AllowedPattern': param.get('AllowedPattern')
                        }
                        document['parameters_formatted'].append(formatted_param)
                    
                    # Parse content if it's JSON to extract more metadata
                    if document_format == 'JSON' and document_content:
                        try:
                            content_data = json.loads(document_content)
                            document['schema_version'] = content_data.get('schemaVersion')
                            document['description_from_content'] = content_data.get('description', '')
                            
                            # Extract main steps/actions
                            if 'mainSteps' in content_data:
                                document['main_steps_count'] = len(content_data['mainSteps'])
                            elif 'steps' in content_data:
                                document['main_steps_count'] = len(content_data['steps'])
                            else:
                                document['main_steps_count'] = 0
                                
                        except json.JSONDecodeError:
                            document['schema_version'] = None
                            document['description_from_content'] = ''
                            document['main_steps_count'] = 0
                    else:
                        document['schema_version'] = None
                        document['description_from_content'] = ''
                        document['main_steps_count'] = 0
                    
                    # Get document permissions
                    try:
                        permissions_response = ssm_client.describe_document_permission(
                            Name=document_name,
                            PermissionType='Share'
                        )
                        document['account_sharing_info'] = permissions_response.get('AccountIds', [])
                        document['is_shared'] = len(document['account_sharing_info']) > 0
                    except Exception:
                        # Most documents don't have sharing permissions
                        document['account_sharing_info'] = []
                        document['is_shared'] = False
                    
                    # Get tags
                    try:
                        tags_response = ssm_client.list_tags_for_resource(
                            ResourceType='Document',
                            ResourceId=document_name
                        )
                        document['tags_formatted'] = {
                            tag['Key']: tag['Value'] 
                            for tag in tags_response.get('TagList', [])
                        }
                    except Exception as e:
                        print(f"  - Warning: Could not retrieve tags for document {document_name}: {e}")
                        document['tags_formatted'] = {}
                    
                    # Determine document category
                    if 'aws-' in document_name.lower():
                        document['category'] = 'aws_managed'
                    elif document['is_automation']:
                        document['category'] = 'automation'
                    elif document['is_command']:
                        document['category'] = 'command'
                    elif document['is_policy']:
                        document['category'] = 'policy'
                    else:
                        document['category'] = 'custom'
                    
                    documents.append(document)
                    
                except Exception as e:
                    print(f"  - Warning: Could not retrieve details for document {document_name}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error scanning documents: {e}")
        return
    
    # Generate documents
    if documents:
        output_file = output_dir / "ssm_document.tf"
        generate_tf(documents, "ssm_document", output_file)
        print(f"Generated Terraform for {len(documents)} Systems Manager documents -> {output_file}")
        generate_imports_file(
            "ssm_document", 
            documents, 
            remote_resource_id_key="Name", 
            output_dir=output_dir
        )

def list_documents(output_dir: Path):
    """Lists all Systems Manager document resources previously generated."""
    ImportManager(output_dir, "ssm_document").list_all()

def import_document(document_name: str, output_dir: Path):
    """Runs terraform import for a specific Systems Manager document by its name."""
    ImportManager(output_dir, "ssm_document").find_and_import(document_name)