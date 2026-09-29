import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from app.config import settings
from app.agent import agent_executor

app = FastAPI(title="AI Agentic PR Reviewer Server")

async def verify_signature(request: Request):
    """Enforces secure webhook handshakes from GitHub."""
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=403, detail="Missing signature header.")
    
    body = await request.body()
    secret = bytes(settings.GITHUB_WEBHOOK_SECRET, "utf-8")
    hash_hex = hmac.new(secret, body, hashlib.sha256).hexdigest()
    expected_signature = f"sha256={hash_hex}"
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=403, detail="Invalid signature authentication payload.")

@app.post("/webhooks/github")
async def github_webhook_receiver(request: Request, background_tasks: BackgroundTasks):
    await verify_signature(request)
    payload = await request.json()
    
    # We execute when a new pull request opens or commits push into branches
    if "pull_request" in payload and payload.get("action") in ["opened", "synchronize"]:
        pr_data = payload["pull_request"]
        repo_name = payload["repository"]["full_name"]
        pr_number = pr_data["number"]
        
        # Trigger async workflow using FastAPI background tasks
        background_tasks.add_task(
            agent_executor.invoke, 
            {"repo_name": repo_name, "pr_number": pr_number}
        )
        return {"status": "processing", "message": f"Agent dispatched to review PR #{pr_number}"}
        
    return {"status": "ignored", "message": "Event is not an actionable PR pipeline modification target."}

@app.get("/health")
def health():
    return {"status": "online"}
