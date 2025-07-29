from pathlib import Path
import json
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_sqs_queues(output_dir: Path, profile: str = None, region: str = "us-east-1", 
                   include_fifo: bool = True, include_dlq: bool = True):
    """
    Scans for SQS queues and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    sqs_client = boto_session.client("sqs")
    
    print(f"Scanning for SQS queues in region {region}...")
    
    # Get all queue URLs
    try:
        response = sqs_client.list_queues()
        queue_urls = response.get('QueueUrls', [])
    except Exception as e:
        print(f"Error listing queues: {e}")
        return
    
    if not queue_urls:
        print("No SQS queues found")
        return
    
    queues = []
    
    for queue_url in queue_urls:
        try:
            # Extract queue name from URL
            queue_name = queue_url.split('/')[-1]
            
            # Skip FIFO queues if not requested
            if queue_name.endswith('.fifo') and not include_fifo:
                continue
                
            # Skip DLQ queues if not requested
            if any(dlq_indicator in queue_name.lower() for dlq_indicator in ['-dlq', '-dead-letter', '-deadletter']) and not include_dlq:
                continue
            
            # Get queue attributes
            attributes_response = sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['All']
            )
            attributes = attributes_response.get('Attributes', {})
            
            # Create queue object
            queue = {
                'QueueUrl': queue_url,
                'QueueName': queue_name,
                'Attributes': attributes
            }
            
            # Add sanitized name for resource naming
            queue['name_sanitized'] = queue_name.replace('-', '_').replace('.', '_').lower()
            
            # Determine queue type
            queue['is_fifo'] = queue_name.endswith('.fifo')
            queue['is_standard'] = not queue['is_fifo']
            
            # Format visibility timeout
            queue['visibility_timeout'] = int(attributes.get('VisibilityTimeout', 30))
            
            # Format message retention period
            queue['message_retention_period'] = int(attributes.get('MessageRetentionPeriod', 345600))
            
            # Format max message size
            queue['max_message_size'] = int(attributes.get('MaxMessageSize', 262144))
            
            # Format delay seconds
            queue['delay_seconds'] = int(attributes.get('DelaySeconds', 0))
            
            # Format receive wait time (long polling)
            queue['receive_wait_time'] = int(attributes.get('ReceiveMessageWaitTimeSeconds', 0))
            
            # Handle redrive policy (Dead Letter Queue)
            redrive_policy = attributes.get('RedrivePolicy')
            if redrive_policy:
                try:
                    policy_data = json.loads(redrive_policy)
                    queue['redrive_policy_formatted'] = {
                        'deadLetterTargetArn': policy_data.get('deadLetterTargetArn'),
                        'maxReceiveCount': policy_data.get('maxReceiveCount', 3)
                    }
                    # Extract DLQ name from ARN for easier reference
                    dlq_arn = policy_data.get('deadLetterTargetArn', '')
                    if dlq_arn:
                        queue['dlq_name'] = dlq_arn.split(':')[-1]
                except json.JSONDecodeError:
                    queue['redrive_policy_formatted'] = None
            else:
                queue['redrive_policy_formatted'] = None
            
            # Handle KMS encryption
            kms_master_key_id = attributes.get('KmsMasterKeyId')
            if kms_master_key_id:
                queue['kms_encrypted'] = True
                queue['kms_master_key_id'] = kms_master_key_id
                # Format data key reuse period
                queue['kms_data_key_reuse_period'] = int(attributes.get('KmsDataKeyReusePeriodSeconds', 300))
            else:
                queue['kms_encrypted'] = False
                queue['kms_master_key_id'] = None
                queue['kms_data_key_reuse_period'] = None
            
            # FIFO specific attributes
            if queue['is_fifo']:
                queue['content_based_deduplication'] = attributes.get('ContentBasedDeduplication', 'false').lower() == 'true'
                queue['fifo_throughput_limit'] = attributes.get('FifoThroughputLimit', 'perQueue')
                queue['deduplication_scope'] = attributes.get('DeduplicationScope', 'queue')
            else:
                queue['content_based_deduplication'] = None
                queue['fifo_throughput_limit'] = None
                queue['deduplication_scope'] = None
            
            # Get queue policy
            policy = attributes.get('Policy')
            if policy:
                queue['policy'] = policy
            else:
                queue['policy'] = None
            
            # Get tags
            try:
                tags_response = sqs_client.list_queue_tags(QueueUrl=queue_url)
                queue['tags_formatted'] = tags_response.get('Tags', {})
            except Exception as e:
                print(f"  - Warning: Could not retrieve tags for queue {queue_name}: {e}")
                queue['tags_formatted'] = {}
            
            queues.append(queue)
                
        except Exception as e:
            print(f"  - Warning: Could not retrieve attributes for queue {queue_url}: {e}")
            continue
    
    # Generate queues
    if queues:
        output_file = output_dir / "sqs_queue.tf"
        generate_tf(queues, "sqs_queue", output_file)
        print(f"Generated Terraform for {len(queues)} SQS queues -> {output_file}")
        generate_imports_file(
            "sqs_queue", 
            queues, 
            remote_resource_id_key="QueueUrl", 
            output_dir=output_dir
        )

def list_sqs_queues(output_dir: Path):
    """Lists all SQS queue resources previously generated."""
    ImportManager(output_dir, "sqs_queue").list_all()

def import_sqs_queue(queue_url: str, output_dir: Path):
    """Runs terraform import for a specific SQS queue by its URL."""
    ImportManager(output_dir, "sqs_queue").find_and_import(queue_url)