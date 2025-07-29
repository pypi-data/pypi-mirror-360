import json
import boto3
import typer
import os
import subprocess

from devolv.drift.aws_fetcher import get_aws_policy_document, merge_policy_documents
from devolv.drift.issues import create_approval_issue, wait_for_sync_choice
from devolv.drift.github_approvals import create_github_pr
from devolv.drift.report import detect_and_print_drift

app = typer.Typer()

def push_branch(branch_name: str):
    """
    Create and push a branch with committed changes.
    """
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Update policy from AWS: {branch_name}"], check=True)
        subprocess.run(["git", "push", "--set-upstream", "origin", branch_name], check=True)
        typer.echo(f"✅ Pushed branch {branch_name} to origin.")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Git command failed: {e}")
        raise typer.Exit(1)

@app.command()
def drift(
    policy_name: str = typer.Option(..., "--policy-name", help="Name of the IAM policy"),
    policy_file: str = typer.Option(..., "--file", help="Path to local policy file"),
    account_id: str = typer.Option(None, "--account-id", help="AWS Account ID (optional, auto-detected if not provided)"),
    approvers: str = typer.Option("", help="Comma-separated GitHub usernames for approval"),
    approval_anyway: bool = typer.Option(False, "--approval-anyway", help="Request approval even if no drift"),
    repo_full_name: str = typer.Option(None, "--repo", help="GitHub repo full name (e.g., org/repo)")
):
    """
    Detect drift between local policy (file) and AWS policy (ARN),
    create GitHub issue for approval, and perform sync based on comment.
    """
    if not account_id:
        sts = boto3.client("sts")
        account_id = sts.get_caller_identity()["Account"]

    policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"

    try:
        with open(policy_file) as f:
            local_doc = json.load(f)
    except FileNotFoundError:
        typer.echo(f"❌ Local policy file {policy_file} not found.")
        raise typer.Exit(1)

    aws_doc = get_aws_policy_document(policy_arn)
    drift = detect_and_print_drift(local_doc, aws_doc)

    if not drift and not approval_anyway:
        typer.echo("✅ No drift detected. Use --approval-anyway to force approval.")
        raise typer.Exit()

    if not repo_full_name:
        repo_full_name = os.getenv("GITHUB_REPOSITORY")

    if not repo_full_name:
        typer.echo("❌ GitHub repo not specified. Use --repo or set GITHUB_REPOSITORY.")
        raise typer.Exit(1)

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        typer.echo("❌ GITHUB_TOKEN not set in environment.")
        raise typer.Exit(1)

    issue_num = create_approval_issue(repo_full_name, token, policy_name)
    typer.echo(f"Issue #{issue_num} created for approval.")

    choice = wait_for_sync_choice(repo_full_name, issue_num, token)

    if choice == "local->aws":
        merged_doc = merge_policy_documents(local_doc, aws_doc)
        iam = boto3.client("iam")
        versions = iam.list_policy_versions(PolicyArn=policy_arn)['Versions']
        if len(versions) >= 5:
            oldest = sorted((v for v in versions if not v['IsDefaultVersion']),
                            key=lambda v: v['CreateDate'])[0]
            iam.delete_policy_version(PolicyArn=policy_arn, VersionId=oldest['VersionId'])
        iam.create_policy_version(
            PolicyArn=policy_arn,
            PolicyDocument=json.dumps(merged_doc),
            SetAsDefault=True
        )
        typer.echo(f"✅ AWS policy {policy_arn} updated with local changes (append-only).")

    elif choice == "aws->local":
        new_content = json.dumps(aws_doc, indent=2)
        with open(policy_file, "w") as f:
            f.write(new_content)

        branch = f"update-policy-{policy_name}"
        pr_title = f"Update {policy_file} from AWS policy"
        pr_body = "This PR updates the local policy file with the AWS default version."

        push_branch(branch)
        pr_num = create_github_pr(repo_full_name, branch, pr_title, pr_body)
        typer.echo(f"✅ Created PR #{pr_num}: updated {policy_file} from AWS policy.")

    else:
        typer.echo("⏭ No synchronization performed (skip).")
