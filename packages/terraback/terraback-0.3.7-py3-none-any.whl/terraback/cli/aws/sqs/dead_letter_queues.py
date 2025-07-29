from pathlib import Path
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_dlq(output_dir: Path, profile: str = None, region: str = "us-east-1"):
    """
    Dedicated scan for dead letter queues and their redrive policies.
    """
    boto_session = get_boto_session(profile, region)
    sqs_client = boto_session.client("sqs")
    
    print(f"Scanning for SQS dead letter queues in region {region}...")
    
    # Get all queue URLs
    response = sqs_client.list_queues()
    queue_urls = response.get('QueueUrls', [])
    
    dlq_relationships = []
    
    for queue_url in queue_urls:
        try:
            queue_name = queue_url.split('/')[-1]
            
            # Get queue attributes
            attributes_response = sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['RedrivePolicy']
            )
            attributes = attributes_response.get('Attributes', {})
            
            redrive_policy = attributes.get('RedrivePolicy')
            if redrive_policy:
                import json
                try:
                    policy_data = json.loads(redrive_policy)
                    dlq_relationship = {
                        'source_queue_url': queue_url,
                        'source_queue_name': queue_name,
                        'dlq_arn': policy_data.get('deadLetterTargetArn'),
                        'max_receive_count': policy_data.get('maxReceiveCount', 3)
                    }
                    dlq_relationships.append(dlq_relationship)
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            print(f"  - Warning: Could not check DLQ policy for queue {queue_url}: {e}")
            continue
    
    if dlq_relationships:
        output_file = output_dir / "sqs_dlq_relationships.tf"
        generate_tf(dlq_relationships, "sqs_dlq_relationship", output_file)
        print(f"Generated Terraform for {len(dlq_relationships)} DLQ relationships -> {output_file}")

def list_dlq(output_dir: Path):
    """Lists all SQS DLQ relationship resources previously generated."""
    ImportManager(output_dir, "sqs_dlq_relationship").list_all()

def import_dlq(relationship_id: str, output_dir: Path):
    """Runs terraform import for a specific DLQ relationship."""
    ImportManager(output_dir, "sqs_dlq_relationship").find_and_import(relationship_id)