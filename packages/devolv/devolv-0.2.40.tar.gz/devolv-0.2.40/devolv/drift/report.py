import json
import difflib
from rich.console import Console
from rich.text import Text

def clean_policy(policy):
    """
    Remove empty statements ({} entries) from the policy's 'Statement' list.
    """
    if isinstance(policy, dict) and "Statement" in policy:
        statements = policy.get("Statement", [])
        if isinstance(statements, list):
            policy["Statement"] = [s for s in statements if s]
    return policy

def normalize_resource(resource):
    """
    Always return a sorted list for the resource field.
    """
    if isinstance(resource, str):
        return [resource]
    if isinstance(resource, list):
        return sorted(resource)
    return resource

def normalize_statement(stmt):
    """
    Return a normalized statement where Resource is always a sorted list.
    """
    stmt = stmt.copy()
    if "Resource" in stmt:
        stmt["Resource"] = normalize_resource(stmt["Resource"])
    return stmt

def normalize_policy(policy):
    """
    Clean and normalize an entire policy.
    """
    cleaned = clean_policy(policy)
    cleaned["Statement"] = [normalize_statement(s) for s in cleaned.get("Statement", [])]
    return cleaned

def generate_diff_lines(local_doc: dict, aws_doc: dict):
    """
    Generate a unified diff between local and AWS policy JSONs.
    """
    local_str = json.dumps(normalize_policy(local_doc), indent=2, sort_keys=True)
    aws_str = json.dumps(normalize_policy(aws_doc), indent=2, sort_keys=True)

    return list(difflib.unified_diff(
        local_str.splitlines(),
        aws_str.splitlines(),
        fromfile="local",
        tofile="aws",
        lineterm=""
    ))

def print_drift_diff(local_doc: dict, aws_doc: dict):
    """
    Pretty-print a unified diff using Rich.
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
