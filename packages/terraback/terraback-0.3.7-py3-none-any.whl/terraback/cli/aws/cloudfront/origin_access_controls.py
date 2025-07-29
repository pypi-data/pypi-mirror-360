from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_origin_access_controls(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Scans for CloudFront Origin Access Controls and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    cloudfront_client = boto_session.client("cloudfront")
    
    print(f"Scanning for CloudFront Origin Access Controls (global service)...")
    
    # Get all origin access controls
    origin_access_controls = []
    
    try:
        # No pagination support for list_origin_access_controls
        response = cloudfront_client.list_origin_access_controls()
        
        if 'Items' in response['OriginAccessControlList']:
            for oac_summary in response['OriginAccessControlList']['Items']:
                oac_id = oac_summary['Id']
                
                try:
                    # Get detailed OAC configuration
                    response = cloudfront_client.get_origin_access_control(Id=oac_id)
                    oac = response['OriginAccessControl']
                    
                    # Add sanitized name for resource naming
                    oac['name_sanitized'] = oac_id.replace('-', '_')
                    
                    # Format configuration for easier template usage
                    if oac.get('OriginAccessControlConfig'):
                        config = oac['OriginAccessControlConfig']
                        oac['config_formatted'] = {
                            'name': config.get('Name'),
                            'description': config.get('Description', ''),
                            'origin_access_control_origin_type': config.get('OriginAccessControlOriginType'),
                            'signing_behavior': config.get('SigningBehavior'),
                            'signing_protocol': config.get('SigningProtocol')
                        }
                    else:
                        oac['config_formatted'] = {}
                    
                    origin_access_controls.append(oac)
                    
                except Exception as e:
                    print(f"  - Warning: Could not retrieve details for OAC {oac_id}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error retrieving Origin Access Controls: {e}")
        return
    
    output_file = output_dir / "cloudfront_origin_access_control.tf"
    generate_tf(origin_access_controls, "cloudfront_origin_access_control", output_file)
    print(f"Generated Terraform for {len(origin_access_controls)} CloudFront Origin Access Controls -> {output_file}")
    generate_imports_file(
        "cloudfront_origin_access_control", 
        origin_access_controls, 
        remote_resource_id_key="Id", 
        output_dir=output_dir
    )

def list_origin_access_controls(output_dir: Path):
    """Lists all CloudFront Origin Access Control resources previously generated."""
    ImportManager(output_dir, "cloudfront_origin_access_control").list_all()

def import_origin_access_control(oac_id: str, output_dir: Path):
    """Runs terraform import for a specific CloudFront Origin Access Control by its ID."""
    ImportManager(output_dir, "cloudfront_origin_access_control").find_and_import(oac_id)