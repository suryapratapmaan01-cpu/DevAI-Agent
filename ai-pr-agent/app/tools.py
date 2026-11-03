import os
import docker
from github import Github
from app.config import settings

# Initialize GitHub Client
gh = Github(settings.GITHUB_TOKEN)
docker_client = docker.from_env()

def fetch_pr_diff(repo_name: str, pr_number: int) -> str:
    """Gets the raw patch files from the PR to identify modifications."""
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    # Fetch list of modified files and chunks
    diff_text = ""
    for f in pr.get_files():
        diff_text += f"File: {f.filename}\nPatch:\n{f.patch}\n\n"
    return diff_text

def run_in_sandbox(commands: list, code_files: dict) -> dict:
    """
    Mounts transient code files into the built Docker sandbox container, 
    runs linting/testing engines, and intercepts outputs safely.
    """
    import tempfile
    import shutil
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write files into host-mapped transient directory
        for filename, content in code_files.items():
            filepath = os.path.join(tmpdir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(content)
                
        # Run container mounting the transient folder
        volumes = {tmpdir: {"bind": "/workspace", "mode": "rw"}}
        logs = []
        exit_codes = []
        
        container = docker_client.containers.run(
            "ai-agent-sandbox:latest",
            command="tail -f /dev/null",
            volumes=volumes,
            detach=True,
            network_mode="none" # Isolate network execution layers
        )
        
        try:
            for cmd in commands:
                exec_res = container.exec_run(cmd, workdir="/workspace")
                logs.append(f"Command: {cmd}\nExit Code: {exec_res.exit_code}\nOutput:\n{exec_res.output.decode()}")
                exit_codes.append(exec_res.exit_code)
        finally:
            container.stop()
            container.remove()
            
    success = all(code == 0 for code in exit_codes)
    return {"success": success, "log": "\n".join(logs)}

def post_pr_review_comment(repo_name: str, pr_number: int, comment: str):
    """Posts analytical reviews or change request logs back onto GitHub."""
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(comment)
