import os
import secrets
import requests
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from feature4_compliance import run_compliance_check

# ── Config ─────────────────────────────────────────────────────────────────────
API_BASE = "https://6jg65j6ajh.execute-api.us-east-1.amazonaws.com/prod"
API_KEY  = os.environ.get("ADVISOR_AI_KEY", "")
EC2_IP   = os.environ.get("EC2_RAG_IP", "localhost")
RAG_URL  = f"http://{EC2_IP}:8000/research"

# ── Auth credentials (set in .env or environment) ─────────────────────────────
WEB_USERNAME = os.environ.get("WEB_USERNAME", "incedo")
WEB_PASSWORD = os.environ.get("WEB_PASSWORD", "advisor2026")

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

app = FastAPI(title="Advisor AI", docs_url=None, redoc_url=None)
security = HTTPBasic()

# ── Auth dependency ────────────────────────────────────────────────────────────
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, WEB_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, WEB_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ── Static files ───────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
def serve_index(username: str = Depends(verify_credentials)):
    return FileResponse("static/index.html")

# ── Request models ─────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str
    session_id: str = "fastapi-session"

class RagRequest(BaseModel):
    question: str
    session_id: str = "rag-session"

class ClientRequest(BaseModel):
    client_name: str

class ComplianceRequest(BaseModel):
    client_filter: Optional[str] = None

# ── API endpoints (all protected) ─────────────────────────────────────────────
@app.post("/api/chat")
def api_chat(req: ChatRequest, username: str = Depends(verify_credentials)):
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            headers=HEADERS,
            json={"question": req.question, "session_id": req.session_id},
            timeout=30
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag")
def api_rag(req: RagRequest, username: str = Depends(verify_credentials)):
    try:
        response = requests.post(
            RAG_URL,
            json={"question": req.question, "session_id": req.session_id},
            timeout=30
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/client360")
def api_client360(req: ClientRequest, username: str = Depends(verify_credentials)):
    try:
        response = requests.post(
            f"{API_BASE}/client360",
            headers=HEADERS,
            json={"client_name": req.client_name},
            timeout=30
        )
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Client not found")
        elif response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compliance")
def api_compliance(req: ComplianceRequest, username: str = Depends(verify_credentials)):
    try:
        result = run_compliance_check(req.client_filter)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
def api_status(username: str = Depends(verify_credentials)):
    status_apigw = "offline"
    status_ec2 = "offline"
    
    try:
        res = requests.options(f"{API_BASE}/chat", headers=HEADERS, timeout=2)
        if res.status_code == 200: 
            status_apigw = "active"
    except Exception:
        pass
        
    try:
        # Note: using localhost since this app runs on the EC2 instance now
        res = requests.get("http://localhost:8000/docs", timeout=2)
        if res.status_code in [200, 404, 405]:
            status_ec2 = "active"
    except Exception:
        pass

    return {
        "api_gateway": status_apigw,
        "ec2_rag": status_ec2,
        "bedrock": status_apigw
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
