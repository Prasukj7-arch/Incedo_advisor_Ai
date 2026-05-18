import os
import secrets
import requests
import boto3
from typing import Optional
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException, Depends, status
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse, HTMLResponse
# pyrefly: ignore [missing-import]
from fastapi.security import HTTPBasic, HTTPBasicCredentials
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from feature4_compliance import run_compliance_check

# ── Config ─────────────────────────────────────────────────────────────────────
API_BASE = "https://6jg65j6ajh.execute-api.us-east-1.amazonaws.com/prod"
API_KEY  = os.environ.get("ADVISOR_AI_KEY", "")
EC2_IP   = os.environ.get("EC2_RAG_IP", "localhost")
RAG_URL  = f"http://{EC2_IP}:8000/research"

# ── Auth credentials (set in .env or environment) ─────────────────────────────
WEB_USERNAME = os.environ.get("WEB_USERNAME", "")
WEB_PASSWORD = os.environ.get("WEB_PASSWORD", "")

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

class SimulateRequest(BaseModel):
    client_name: str
    scenario: str

class RevenueRequest(BaseModel):
    client_name: str

class SupervisionActionRequest(BaseModel):
    review_id: str
    action: str  # 'APPROVE' or 'OVERRIDE'
    notes: str

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

@app.post("/api/simulate")
def api_simulate(req: SimulateRequest, username: str = Depends(verify_credentials)):
    try:
        response = requests.post(
            f"{API_BASE}/simulate",
            headers=HEADERS,
            json={"client_name": req.client_name, "scenario": req.scenario},
            timeout=45
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/revenue")
def api_revenue(req: RevenueRequest, username: str = Depends(verify_credentials)):
    try:
        response = requests.post(
            f"{API_BASE}/revenue",
            headers=HEADERS,
            json={"client_name": req.client_name},
            timeout=45
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compliance")
def api_compliance(req: dict, username: str = Depends(verify_credentials)):
    try:
        response = requests.post(
            f"{API_BASE}/compliance",
            headers=HEADERS,
            json=req,
            timeout=30
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
def api_dashboard(username: str = Depends(verify_credentials)):
    try:
        response = requests.post(
            f"{API_BASE}/dashboard",
            headers=HEADERS,
            json={},
            timeout=30
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
def api_status(username: str = Depends(verify_credentials)):
    status_apigw = "offline"
    status_ec2 = "offline"

    # 1. Check API Gateway / Lambda Health via /chat
    try:
        res = requests.post(
            f"{API_BASE}/chat",
            headers=HEADERS,
            json={"question": "health_check"},
            timeout=2
        )
        if res.status_code == 200:
            status_apigw = "active"
    except Exception:
        pass

    # 2. Check EC2 RAG Server Health (using /docs as it always exists in FastAPI)
    try:
        res = requests.get("http://localhost:8000/docs", timeout=2)
        if res.status_code == 200:
            status_ec2 = "active"
    except Exception:
        pass

    return {
        "api_gateway": status_apigw,
        "ec2_rag": status_ec2,
        "bedrock": status_apigw
    }

@app.get("/api/observability")
def api_observability(username: str = Depends(verify_credentials)):
    try:
        table = dynamodb.Table("advisor-ai-metrics")
        # Scan full history of metrics (100% Free on AWS)
        response = table.scan()
        items = response.get("Items", [])
        
        # Calculate aggregates
        total_calls = len(items)
        total_tokens = sum(int(i.get("total_tokens", 0)) for i in items)
        total_cost = sum(float(i.get("cost_usd", 0)) for i in items)
        avg_latency = sum(int(i.get("latency_ms", 0)) for i in items) / max(total_calls, 1)
        
        # Per feature breakdown
        features = {}
        for item in items:
            f = item.get("feature", "unknown")
            if f not in features:
                features[f] = {"calls": 0, "tokens": 0, "cost": 0}
            features[f]["calls"] += 1
            features[f]["tokens"] += int(item.get("total_tokens", 0))
            features[f]["cost"] += float(item.get("cost_usd", 0))
        
        # Recent 10 calls for timeline
        recent = sorted(items, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        
        return {
            "summary": {
                "total_calls": total_calls,
                "total_tokens": total_tokens,
                "total_cost_usd": round(total_cost, 6),
                "total_cost_inr": round(total_cost * 83.5, 4),
                "avg_latency_ms": round(avg_latency),
                "model_id": "us.meta.llama3-1-8b-instruct-v1:0"
            },
            "by_feature": features,
            "recent_calls": [
                {
                    "feature": i.get("feature"),
                    "tokens": i.get("total_tokens"),
                    "latency_ms": i.get("latency_ms"),
                    "cost_usd": i.get("cost_usd"),
                    "timestamp": i.get("timestamp")
                } for i in recent
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/supervision/pending")
def get_pending_supervision(username: str = Depends(verify_credentials)):
    try:
        table = dynamodb.Table("advisor-ai-supervision")
        # Use a scan for simplicity in this demo, filtered by status
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("status").eq("PENDING")
        )
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/supervision/action")
def take_supervision_action(req: SupervisionActionRequest, username: str = Depends(verify_credentials)):
    try:
        table = dynamodb.Table("advisor-ai-supervision")
        from datetime import datetime
        
        table.update_item(
            Key={"review_id": req.review_id},
            UpdateExpression="SET #s = :status, decision = :dec, supervisor_notes = :notes, reviewed_at = :time",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":status": "REVIEWED",
                ":dec": req.action,
                ":notes": req.notes,
                ":time": datetime.utcnow().isoformat()
            }
        )
        
        # Log to CloudWatch (Simulated via print for EC2 logs, but usually a CloudWatch call)
        print(f"COMPLIANCE AUDIT: Supervisor {username} performed {req.action} on {req.review_id}. Notes: {req.notes}")
        
        return {"status": "success", "review_id": req.review_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
