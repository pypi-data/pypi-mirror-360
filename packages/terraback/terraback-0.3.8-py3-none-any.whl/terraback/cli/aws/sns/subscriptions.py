from pathlib import Path
import json
from terraback.cli.aws.session import get_boto_session
from terraback.terraform_generator.writer import generate_tf
from terraback.terraform_generator.imports import generate_imports_file
from terraback.utils.importer import ImportManager

def scan_subscriptions(output_dir: Path, profile: str = None, region: str = "us-east-1", topic_arn: str = None):
    """
    Scans for SNS subscriptions and generates Terraform code.
    """
    boto_session = get_boto_session(profile, region)
    sns_client = boto_session.client("sns")
    
    print(f"Scanning for SNS subscriptions in region {region}...")
    
    subscriptions = []
    
    if topic_arn:
        # Scan subscriptions for a specific topic
        try:
            paginator = sns_client.get_paginator('list_subscriptions_by_topic')
            for page in paginator.paginate(TopicArn=topic_arn):
                subscriptions.extend(page.get('Subscriptions', []))
        except Exception as e:
            print(f"Error scanning subscriptions for topic {topic_arn}: {e}")
            return
    else:
        # Scan all subscriptions
        paginator = sns_client.get_paginator('list_subscriptions')
        for page in paginator.paginate():
            subscriptions.extend(page.get('Subscriptions', []))
    
    processed_subscriptions = []
    
    for subscription in subscriptions:
        try:
            subscription_arn = subscription.get('SubscriptionArn')
            
            # Skip pending confirmations
            if subscription_arn == 'PendingConfirmation':
                continue
            
            topic_arn = subscription.get('TopicArn')
            protocol = subscription.get('Protocol')
            endpoint = subscription.get('Endpoint')
            
            # Get subscription attributes
            try:
                attributes_response = sns_client.get_subscription_attributes(
                    SubscriptionArn=subscription_arn
                )
                attributes = attributes_response.get('Attributes', {})
            except Exception as e:
                print(f"  - Warning: Could not get attributes for subscription {subscription_arn}: {e}")
                attributes = {}
            
            # Create subscription object
            subscription_data = {
                'SubscriptionArn': subscription_arn,
                'TopicArn': topic_arn,
                'Protocol': protocol,
                'Endpoint': endpoint,
                'Attributes': attributes
            }
            
            # Add sanitized name for resource naming
            subscription_id = subscription_arn.split(':')[-1] if subscription_arn else 'unknown'
            subscription_data['name_sanitized'] = subscription_id.replace('-', '_').lower()
            
            # Extract topic name for easier referencing
            topic_name = topic_arn.split(':')[-1] if topic_arn else 'unknown'
            subscription_data['topic_name'] = topic_name
            subscription_data['topic_name_sanitized'] = topic_name.replace('-', '_').replace('.', '_').lower()
            
            # Format confirmation status
            subscription_data['confirmation_was_authenticated'] = attributes.get('ConfirmationWasAuthenticated', 'false').lower() == 'true'
            
            # Format delivery policy
            delivery_policy = attributes.get('DeliveryPolicy')
            if delivery_policy:
                try:
                    subscription_data['delivery_policy'] = json.loads(delivery_policy)
                except json.JSONDecodeError:
                    subscription_data['delivery_policy'] = None
            else:
                subscription_data['delivery_policy'] = None
            
            # Format effective delivery policy
            effective_delivery_policy = attributes.get('EffectiveDeliveryPolicy')
            if effective_delivery_policy:
                try:
                    subscription_data['effective_delivery_policy'] = json.loads(effective_delivery_policy)
                except json.JSONDecodeError:
                    subscription_data['effective_delivery_policy'] = None
            else:
                subscription_data['effective_delivery_policy'] = None
            
            # Format filter policy
            filter_policy = attributes.get('FilterPolicy')
            if filter_policy:
                try:
                    subscription_data['filter_policy'] = json.loads(filter_policy)
                except json.JSONDecodeError:
                    subscription_data['filter_policy'] = None
            else:
                subscription_data['filter_policy'] = None
            
            # Format filter policy scope
            subscription_data['filter_policy_scope'] = attributes.get('FilterPolicyScope', 'MessageAttributes')
            
            # Format pending confirmation
            subscription_data['pending_confirmation'] = attributes.get('PendingConfirmation', 'false').lower() == 'true'
            
            # Format raw message delivery (for SQS and HTTP/S)
            subscription_data['raw_message_delivery'] = attributes.get('RawMessageDelivery', 'false').lower() == 'true'
            
            # Format redrive policy
            redrive_policy = attributes.get('RedrivePolicy')
            if redrive_policy:
                try:
                    subscription_data['redrive_policy'] = json.loads(redrive_policy)
                except json.JSONDecodeError:
                    subscription_data['redrive_policy'] = None
            else:
                subscription_data['redrive_policy'] = None
            
            # Format subscription role ARN (for Kinesis Data Firehose)
            subscription_data['subscription_role_arn'] = attributes.get('SubscriptionRoleArn')
            
            # Protocol-specific formatting
            if protocol == 'email':
                subscription_data['email_address'] = endpoint
            elif protocol == 'email-json':
                subscription_data['email_address'] = endpoint
                subscription_data['json_format'] = True
            elif protocol == 'sms':
                subscription_data['phone_number'] = endpoint
            elif protocol == 'http' or protocol == 'https':
                subscription_data['http_endpoint'] = endpoint
            elif protocol == 'sqs':
                subscription_data['sqs_queue_arn'] = endpoint
            elif protocol == 'lambda':
                subscription_data['lambda_function_arn'] = endpoint
            elif protocol == 'application':
                subscription_data['mobile_app_arn'] = endpoint
            elif protocol == 'firehose':
                subscription_data['firehose_delivery_stream_arn'] = endpoint
            
            processed_subscriptions.append(subscription_data)
            
        except Exception as e:
            print(f"  - Warning: Could not process subscription: {e}")
            continue
    
    # Generate subscriptions
    if processed_subscriptions:
        output_file = output_dir / "sns_subscription.tf"
        generate_tf(processed_subscriptions, "sns_subscription", output_file)
        print(f"Generated Terraform for {len(processed_subscriptions)} SNS subscriptions -> {output_file}")
        generate_imports_file(
            "sns_subscription", 
            processed_subscriptions, 
            remote_resource_id_key="SubscriptionArn", 
            output_dir=output_dir
        )

def list_subscriptions(output_dir: Path):
    """Lists all SNS subscription resources previously generated."""
    ImportManager(output_dir, "sns_subscription").list_all()

def import_subscription(subscription_arn: str, output_dir: Path):
    """Runs terraform import for a specific SNS subscription by its ARN."""
    ImportManager(output_dir, "sns_subscription").find_and_import(subscription_arn)