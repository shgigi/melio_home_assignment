import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel("INFO")

def get_environment_variables():
    queue_url = os.environ["QUEUE_URL"]
    timeout = int(os.environ["TIMEOUT"])
    return queue_url, timeout

def lambda_handler(event, context):

    QUEUE_URL, TIMEOUT = get_environment_variables()
    sqs_client = boto3.client("sqs")

    logger.info(f"EVENT: {event}")

    logger.info(f"Recieved message from SQS {QUEUE_URL}")

    
    # 2. Create PR


    # 3. DeleteMessage

    receipt_handle = event.get("Records")[0].get("receiptHandle")
    sqs_client.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle
    )
    logger.info("Deleted message from queue")