import json
import boto3
import os

def connect_to_aws(region, service):
    client = boto3.client(service, region_name = region)
    return client


def publish_to_sns(message, subject, topic_arn):
    client = connect_to_aws("us-east-1", "sns")

    response = client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject,
    )
    print(response)


def lambda_handler(event, context):
    topic_arn = os.getenv("TOPIC_ARN", "")

    object_name = event["Records"][0]["s3"]["object"]["key"]
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]

    message_subject = "Proximity detected!"
    message_body = f"Proximity detected in Bucket: {bucket_name} and Object: {object_name}"

    try:
        publish_to_sns(message_body, message_subject, topic_arn)
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    except Exception as e:
        return f"Error {str(e)}"