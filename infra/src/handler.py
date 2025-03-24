import boto3
import os
import logging
import json
from github import (
    Github,
    GithubException
    )


logger = logging.getLogger()
logger.setLevel("INFO")


def get_environment_variables():
    queue_url = os.environ["QUEUE_URL"]
    gh_token = os.environ["GITHUB_TOKEN"]
    repo_owner = os.environ["REPO_OWNER"]
    repo_name = os.environ["REPO_NAME"]
    return queue_url, gh_token, repo_owner, repo_name


def create_and_merge_pr(message: dict, owner: str, repo: str, token: str) -> None:
    body = json.loads(message["body"])
    database_name = body["DatabaseName"]
    database_engine = body["DatabaseEngine"]
    database_environ = body["Environment"]
    branch_name = f"{database_name}"

    g = Github(token)
    g_repo = g.get_repo(f"{owner}/{repo}")
    master_branch = g_repo.get_branch("master")
    latest_sha = master_branch.commit.sha

    ref = f"refs/heads/{branch_name}"
    try:
        g_repo.create_git_ref(ref=ref, sha=latest_sha)
    except GithubException as e:
        if "422" in e.message:
            logger.error("Branch already exists, stopping execution")
            return

    varfile_path = f"clusters/{database_name}.tfvars"
    varfile_content = f"""
    database_name   = "{database_name}"
    database_engine = "{database_engine}"
    environment     = "{database_environ}"
    """

    try:
        res = g_repo.create_file(
            branch=branch_name,
            path=varfile_path,
            content=varfile_content,
            message=f"RDS cluster {database_name}",
        )
        logger.info(res)
    except GithubException as e:
        if "sha" in e.message:
            logger.error("Trying to update existing files not supported, stopping excecution")
            return
        else:
            logger.error(e.message)

    res = g_repo.create_pull(
        title=f"RDS Cluster for {database_name}",
        body=f"Configuration for RDS cluster {database_name}",
        base="master",
        head=branch_name,
    )

    res.merge(
        delete_branch=True,
    )

    logger.info(res)


def lambda_handler(event, context):
    QUEUE_URL, GITHUB_TOKEN, REPO_OWNER, REPO_NAME = get_environment_variables()
    sqs_client = boto3.client("sqs")

    logger.info(f"EVENT: {event}")
    logger.info(f"Recieved message from SQS {QUEUE_URL}")
    message = event.get("Records")[0]

    # 2. Create PR
    create_and_merge_pr(
        message=message,
        owner=REPO_OWNER,
        repo=REPO_NAME,
        token=GITHUB_TOKEN,
    )

    # 3. DeleteMessage
    receipt_handle = event.get("Records")[0].get("receiptHandle")
    sqs_client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
    logger.info("Deleted message from queue")
