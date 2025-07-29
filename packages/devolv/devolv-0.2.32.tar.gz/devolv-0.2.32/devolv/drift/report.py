import json
import difflib
from rich.console import Console
from rich.text import Text
import typer

def clean_policy(policy):
    """
    Remove empty statements ({} entries) from the policy's 'Statement' list.
    """
    if isinstance(policy, dict) and "Statement" in policy:
        statements = policy.get("Statement", [])
        if isinstance(statements, list):
            policy["Statement"] = [s for s in statements if s]
    return policy

def detect_drift(local_doc, aws_doc) -> bool:
    """
    Detect removal drift:
    Returns True if AWS has permissions not present in local (local missing permissions).
    """
    local_statements = {json.dumps(s, sort_keys=True) for s in local_doc.get("Statement", [])}
    aws_statements = {json.dumps(s, sort_keys=True) for s in aws_doc.get("Statement", [])}

    missing_in_local = aws_statements - local_statements

    if missing_in_local:
        typer.echo("❌ Drift detected: Local is missing permissions present in AWS.")
        return True

    typer.echo("✅ No removal drift detected (local may have extra permissions; that's fine).")
    return False

def generate_diff_lines(local_doc: dict, aws_doc: dict):
    """
    Generate a unified diff between pretty-printed local and AWS policy JSONs.
    Returns a list of diff lines.
    """
    local_str = json.dumps(clean_policy(local_doc), indent=2, sort_keys=True)
    aws_str = json.dumps(clean_policy(aws_doc), indent=2, sort_keys=True)

    return list(difflib.unified_diff(
        local_str.splitlines(),
        aws_str.splitlines(),
        fromfile="local",
        tofile="aws",
        lineterm=""
    ))

def print_drift_diff(local_doc: dict, aws_doc: dict):
    """
    Pretty-print a unified diff using Rich formatting.
    """
    console = Console()
    diff_lines = generate_diff_lines(local_doc, aws_doc)

    if not diff_lines:
        console.print("✅ No drift detected: Policies match.", style="green")
        return

    console.print("❌ Drift detected — see diff below", style="bold red")

    for line in diff_lines:
        if line.startswith('---') or line.startswith('+++'):
            console.print(Text(line, style="bold"))
        elif line.startswith('@@'):
            console.print(Text(line, style="cyan"))
        elif line.startswith('-'):
            console.print(Text(line, style="red"))
        elif line.startswith('+'):
            console.print(Text(line, style="green"))
        else:
            console.print(Text(line, style="bright_black"))
