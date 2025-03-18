import boto3
import os

def get_environment_variables():
    queue_url = os.environ["QUEUE_URL"]
    timeout = int(os.environ["TIMEOUT"])
    return queue_url, timeout

def lambda_handler(event, context):

    QUEUE_URL, TIMEOUT = get_environment_variables()
    sqs_client = boto3.client("sqs")

    # 1. RecieveMessage
    message = sqs_client.recieve_message(
        queueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        VisibilityTimeout=TIMEOUT
    )
    
    # 2. Create PR


    # 3. DeleteMessage

    receipt_handle = message.get("Messages")[0].get("ReceiptHandle")
    sqs_client.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle
    )