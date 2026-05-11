import os
import requests
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException, Request
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Import local compliance module
from feature4_compliance import run_compliance_check

load_dotenv()

API_BASE = os.environ.get("API_GATEWAY_URL", "")
API_KEY = os.environ.get("ADVISOR_AI_KEY", "")
EC2_IP = os.environ.get("EC2_RAG_IP", "")
RAG_URL = f"http://{EC2_IP}:8000/research" if EC2_IP else ""

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

app = FastAPI(title="Advisor AI Backend")

# We will serve static files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")

from typing import Optional

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

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

@app.post("/api/chat")
def api_chat(req: ChatRequest):
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag")
def api_rag(req: RagRequest):
    try:
        response = requests.post(
            RAG_URL,
            json={"question": req.question, "session_id": req.session_id},
            timeout=30
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/client360")
def api_client360(req: ClientRequest):
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
def api_compliance(req: ComplianceRequest):
    try:
        # Run local compliance check
        result = run_compliance_check(req.client_filter)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
def api_status():
    status_apigw = "offline"
    status_ec2 = "offline"
    
    try:
        res = requests.options(f"{API_BASE}/chat", headers=HEADERS, timeout=2)
        if res.status_code == 200: 
            status_apigw = "active"
    except Exception:
        pass
        
    try:
        res = requests.get(f"http://{EC2_IP}:8000/docs", timeout=2)
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
    # pyrefly: ignore [missing-import]
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
