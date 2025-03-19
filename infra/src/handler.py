import boto3
import os
import logging
import json
from github import Github
from datetime import datetime


logger = logging.getLogger()
logger.setLevel("INFO")


def get_environment_variables():
    queue_url = os.environ["QUEUE_URL"]
    gh_token = os.environ["GITHUB_TOKEN"]
    return queue_url, gh_token


def create_pr(message: dict, owner: str, repo: str, token: str) -> None:
    body = json.loads(message["body"])
    database_name = body["DatabaseName"]
    database_engine = body["DatabaseEngine"]
    database_environ = body["Environment"]
    now = datetime.now().strftime("%Y-%m-%d-%H:%M")
    branch_name = f"{database_name}-{now}"

    g = Github(token)
    g_repo = g.get_repo(f"{owner}/{repo}")
    master_branch = g_repo.get_branch("master")
    latest_sha = master_branch.commit.sha

    ref = f"refs/heads/{branch_name}"
    g_repo.create_git_ref(ref=ref, sha=latest_sha)

    varfile_path = f"clusters/{database_name}"
    varfile_content = f"""
    database_name   = "{database_name}"
    database_engine = "{database_engine}"
    environment     = "{database_environ}"
    """

    g_repo.create_file(
        branch=branch_name,
        path=varfile_path,
        content=varfile_content,
        message=f"RDS cluster {database_name}",
    )

    g_repo.create_pull(
        title=f"RDS Cluster for {database_name}",
        body=f"Configuration for RDS cluster {database_name}",
        base=master_branch,
        head=branch_name,
    )


def lambda_handler(event, context):
    QUEUE_URL, GITHUB_TOKEN = get_environment_variables()
    sqs_client = boto3.client("sqs")

    logger.info(f"EVENT: {event}")
    logger.info(f"Recieved message from SQS {QUEUE_URL}")
    message = event.get("Records")[0]

    # 2. Create PR
    create_pr(
        message=message,
        owner="shgigi",
        repo="melio_home_assignment",
        token=GITHUB_TOKEN,
    )

    # 3. DeleteMessage
    receipt_handle = event.get("Records")[0].get("receiptHandle")
    sqs_client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
    logger.info("Deleted message from queue")
