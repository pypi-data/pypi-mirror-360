from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

from typing import Optional

def scan_certificates(
    output_dir: Path, 
    profile: Optional[str] = None, 
    region: str = "us-east-1",
    include_imported: bool = True,
    include_issued: bool = True
):
    """
    Scans for ACM certificates and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    acm_client = boto_session.client("acm")
    
    print(f"Scanning for ACM certificates in region {region}...")
    
    # Build certificate status filters based on options
    certificate_statuses = []
    if include_issued:
        certificate_statuses.extend(['ISSUED'])
    if include_imported:
        certificate_statuses.extend(['ISSUED'])  # Imported certs also show as ISSUED
    
    if not certificate_statuses:
        print("No certificate types selected for scanning")
        return
    
    # Get all certificates using pagination
    paginator = acm_client.get_paginator('list_certificates')
    certificates = []
    
    for page in paginator.paginate(CertificateStatuses=certificate_statuses):
        for cert_summary in page['CertificateSummaryList']:
            cert_arn = cert_summary['CertificateArn']
            
            try:
                # Get detailed certificate information
                cert_detail = acm_client.describe_certificate(CertificateArn=cert_arn)
                certificate = cert_detail['Certificate']
                
                # Add computed fields for easier template usage
                certificate['arn_sanitized'] = cert_arn.split('/')[-1].replace('-', '_').lower()
                certificate['domain_sanitized'] = certificate['DomainName'].replace('.', '_').replace('*', 'wildcard').replace('-', '_').lower()
                
                # Determine certificate type (ACM-issued vs imported)
                if certificate.get('Type') == 'IMPORTED':
                    certificate['is_imported'] = True
                    certificate['is_acm_issued'] = False
                else:
                    certificate['is_imported'] = False
                    certificate['is_acm_issued'] = True
                
                # Format subject alternative names for easier template usage
                if certificate.get('SubjectAlternativeNames'):
                    certificate['sans_formatted'] = certificate['SubjectAlternativeNames']
                else:
                    certificate['sans_formatted'] = []
                
                # Format domain validation options
                if certificate.get('DomainValidationOptions'):
                    certificate['domain_validation_formatted'] = []
                    for dvo in certificate['DomainValidationOptions']:
                        formatted_dvo = {
                            'DomainName': dvo['DomainName'],
                            'ValidationDomain': dvo.get('ValidationDomain'),
                            'ValidationStatus': dvo.get('ValidationStatus'),
                            'ValidationMethod': dvo.get('ValidationMethod')
                        }
                        # Add DNS validation records if present
                        if dvo.get('ResourceRecord'):
                            formatted_dvo['ResourceRecord'] = dvo['ResourceRecord']
                        certificate['domain_validation_formatted'].append(formatted_dvo)
                else:
                    certificate['domain_validation_formatted'] = []
                
                # Get certificate tags
                try:
                    tags_response = acm_client.list_tags_for_certificate(CertificateArn=cert_arn)
                    certificate['Tags'] = tags_response.get('Tags', [])
                except Exception as e:
                    print(f"  - Warning: Could not retrieve tags for certificate {cert_arn}: {e}")
                    certificate['Tags'] = []
                
                certificates.append(certificate)
                
            except Exception as e:
                print(f"  - Warning: Could not retrieve details for certificate {cert_arn}: {e}")
                continue

    # Filter certificates based on type if needed
    if not include_imported:
        certificates = [cert for cert in certificates if not cert['is_imported']]
    if not include_issued:
        certificates = [cert for cert in certificates if not cert['is_acm_issued']]

    output_file = output_dir / "acm_certificate.tf"
    generate_tf(certificates, "acm_certificate", output_file)
    print(f"Generated Terraform for {len(certificates)} ACM certificates -> {output_file}")
    generate_imports_file(
        "acm_certificate", 
        certificates, 
        remote_resource_id_key="CertificateArn", 
        output_dir=output_dir
    )

def list_certificates(output_dir: Path):
    """Lists all ACM certificate resources previously generated."""
    ImportManager(output_dir, "acm_certificate").list_all()

def import_certificate(certificate_arn: str, output_dir: Path):
    """Runs terraform import for a specific ACM certificate by its ARN."""
    ImportManager(output_dir, "acm_certificate").find_and_import(certificate_arn)
