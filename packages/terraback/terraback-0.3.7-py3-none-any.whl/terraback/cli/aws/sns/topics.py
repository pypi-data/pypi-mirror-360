from pathlib import Path
import json
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_topics(output_dir: Path, profile: str = None, region: str = "us-east-1", include_subscriptions: bool = True):
    """
    Scans for SNS topics and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    sns_client = boto_session.client("sns")
    
    print(f"Scanning for SNS topics in region {region}...")
    
    # Get all topics
    topics = []
    paginator = sns_client.get_paginator('list_topics')
    
    for page in paginator.paginate():
        for topic in page.get('Topics', []):
            topic_arn = topic['TopicArn']
            
            try:
                # Get topic attributes
                attributes_response = sns_client.get_topic_attributes(TopicArn=topic_arn)
                attributes = attributes_response.get('Attributes', {})
                
                # Extract topic name from ARN
                topic_name = topic_arn.split(':')[-1]
                
                # Create topic object
                topic_data = {
                    'TopicArn': topic_arn,
                    'TopicName': topic_name,
                    'Attributes': attributes
                }
                
                # Add sanitized name for resource naming
                topic_data['name_sanitized'] = topic_name.replace('-', '_').replace('.', '_').lower()
                
                # Determine topic type
                topic_data['is_fifo'] = topic_name.endswith('.fifo')
                topic_data['is_standard'] = not topic_data['is_fifo']
                
                # Format display name
                topic_data['display_name'] = attributes.get('DisplayName', '')
                
                # Format delivery policy
                delivery_policy = attributes.get('DeliveryPolicy')
                if delivery_policy:
                    try:
                        topic_data['delivery_policy'] = json.loads(delivery_policy)
                    except json.JSONDecodeError:
                        topic_data['delivery_policy'] = None
                else:
                    topic_data['delivery_policy'] = None
                
                # Format policy
                policy = attributes.get('Policy')
                if policy:
                    try:
                        topic_data['policy'] = json.loads(policy)
                    except json.JSONDecodeError:
                        topic_data['policy'] = None
                else:
                    topic_data['policy'] = None
                
                # Handle KMS encryption
                kms_master_key_id = attributes.get('KmsMasterKeyId')
                if kms_master_key_id:
                    topic_data['kms_encrypted'] = True
                    topic_data['kms_master_key_id'] = kms_master_key_id
                else:
                    topic_data['kms_encrypted'] = False
                    topic_data['kms_master_key_id'] = None
                
                # FIFO specific attributes
                if topic_data['is_fifo']:
                    topic_data['content_based_deduplication'] = attributes.get('ContentBasedDeduplication', 'false').lower() == 'true'
                    topic_data['fifo_throughput_limit'] = attributes.get('FifoThroughputLimit', 'perTopic')
                else:
                    topic_data['content_based_deduplication'] = None
                    topic_data['fifo_throughput_limit'] = None
                
                # Handle signature version
                topic_data['signature_version'] = attributes.get('SignatureVersion', '1')
                
                # Handle tracing config
                topic_data['tracing_config'] = attributes.get('TracingConfig', 'PassThrough')
                
                # Get effective delivery policy
                effective_delivery_policy = attributes.get('EffectiveDeliveryPolicy')
                if effective_delivery_policy:
                    try:
                        topic_data['effective_delivery_policy'] = json.loads(effective_delivery_policy)
                    except json.JSONDecodeError:
                        topic_data['effective_delivery_policy'] = None
                else:
                    topic_data['effective_delivery_policy'] = None
                
                # Get tags
                try:
                    tags_response = sns_client.list_tags_for_resource(ResourceArn=topic_arn)
                    topic_data['tags_formatted'] = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
                except Exception as e:
                    print(f"  - Warning: Could not retrieve tags for topic {topic_name}: {e}")
                    topic_data['tags_formatted'] = {}
                
                # Get subscription count
                topic_data['subscriptions_confirmed'] = int(attributes.get('SubscriptionsConfirmed', 0))
                topic_data['subscriptions_pending'] = int(attributes.get('SubscriptionsPending', 0))
                topic_data['subscriptions_deleted'] = int(attributes.get('SubscriptionsDeleted', 0))
                
                topics.append(topic_data)
                
            except Exception as e:
                print(f"  - Warning: Could not retrieve attributes for topic {topic_arn}: {e}")
                continue
    
    # Generate topics
    if topics:
        output_file = output_dir / "sns_topic.tf"
        generate_tf(topics, "sns_topic", output_file)
        print(f"Generated Terraform for {len(topics)} SNS topics -> {output_file}")
        generate_imports_file(
            "sns_topic", 
            topics, 
            remote_resource_id_key="TopicArn", 
            output_dir=output_dir
        )
    
    # Scan subscriptions if requested
    if include_subscriptions:
        from .subscriptions import scan_subscriptions
        scan_subscriptions(output_dir, profile, region)

def list_topics(output_dir: Path):
    """Lists all SNS topic resources previously generated."""
    ImportManager(output_dir, "sns_topic").list_all()

def import_topic(topic_arn: str, output_dir: Path):
    """Runs terraform import for a specific SNS topic by its ARN."""
    ImportManager(output_dir, "sns_topic").find_and_import(topic_arn)
