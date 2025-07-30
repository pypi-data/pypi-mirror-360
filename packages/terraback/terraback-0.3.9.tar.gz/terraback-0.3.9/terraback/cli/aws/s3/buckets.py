from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_buckets(output_dir: Path, profile: str = "", region: str = "us-east-1"):
    """
    Scans for S3 buckets and their configurations, then generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    s3_client = boto_session.client("s3")
    
    # Get the initial list of all buckets
    all_buckets_meta = s3_client.list_buckets()["Buckets"]
    
    detailed_buckets = []
    print(f"Scanning {len(all_buckets_meta)} S3 buckets for details...")

    for bucket in all_buckets_meta:
        bucket_name = bucket["Name"]
        bucket_details = {"Name": bucket_name} # Start with the name

        try:
            # Get bucket versioning configuration
            versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
            if versioning.get('Status'):
                bucket_details['Versioning'] = versioning
            
            # Get public access block configuration
            try:
                pab = s3_client.get_public_access_block(Bucket=bucket_name)
                bucket_details['PublicAccessBlock'] = pab['PublicAccessBlockConfiguration']
            except s3_client.exceptions.ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchPublicAccessBlockConfiguration':
                    raise e
            
            detailed_buckets.append(bucket_details)
        except Exception as e:
            # Buckets in other regions can cause permission errors, skip them gracefully.
            print(f"  - Could not get details for bucket '{bucket_name}' (possibly in another region): {e}")

    output_file = output_dir / "s3_bucket.tf"
    generate_tf(detailed_buckets, "s3_bucket", output_file) # Use a specific template key
    print(f"Generated Terraform for {len(detailed_buckets)} S3 Buckets -> {output_file}")
    generate_imports_file("s3_bucket", detailed_buckets, remote_resource_id_key="Name", output_dir=output_dir)

def list_buckets(output_dir: Path):
    """Lists all S3 bucket resources previously generated."""
    ImportManager(output_dir, "s3_bucket").list_all()

def import_bucket(bucket_name: str, output_dir: Path):
    """Runs terraform import for a specific S3 bucket by name."""
    ImportManager(output_dir, "s3_bucket").find_and_import(bucket_name)
