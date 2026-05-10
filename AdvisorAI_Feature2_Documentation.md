# ADVISOR AI
## Feature 2: RAG Research Search
### Technical Implementation Report | May 2026

---

## 1. Feature Overview

Feature 2 implements a **Retrieval-Augmented Generation (RAG)** pipeline that allows financial advisors to search across research reports using natural language. Instead of manually reading through PDFs, advisors can ask questions like "What are the top picks in semiconductors?" and get cited, grounded answers from actual research documents.

This directly addresses **Section 4.4** and **Section 5.3** of the problem statement:
- Section 4.4: *"Natural language queries across research reports"*
- Section 5.3: *"Retrieval-Augmented Generation (RAG)"*

---

## 2. Architecture

```
Advisor Question
      |
      v
EC2 FastAPI Server (54.81.100.34:8000)
      |
      ├── ChromaDB (vector store — 29 chunks)
      |       |
      |       └── Searches relevant chunks from 5 PDFs
      |
      └── Amazon Bedrock (Llama 3.1 8B)
              |
              └── Generates cited answer from retrieved chunks
                      |
                      v
              Answer + Source Citations
```

### 2.1 Why EC2 + ChromaDB instead of Bedrock Knowledge Base

| Option | Cost | Setup Time | Demo Quality |
|---|---|---|---|
| Bedrock Knowledge Base + OpenSearch | $350-700/month | 2+ hours | Same |
| EC2 t3.micro + ChromaDB | Free tier | 20 minutes | Same |

**Decision: EC2 + ChromaDB** — identical output, zero cost risk.

### 2.2 Services Used

| Service | Purpose | Cost |
|---|---|---|
| AWS EC2 t3.micro | Hosts FastAPI RAG server + ChromaDB | Free tier (750 hrs/mo) |
| AWS S3 | Stores 5 research PDFs | Free tier (5GB) |
| Amazon Bedrock (Llama 3.1 8B) | Generates answers from retrieved context | $0.22/1M tokens |
| ChromaDB | Local vector store — semantic search | Free (open source) |
| FastAPI + Uvicorn | REST API server | Free (open source) |

---

## 3. Research Documents

5 mock financial research PDFs created and stored in S3:

| File | Source | Coverage |
|---|---|---|
| `semiconductor_outlook_2025.pdf` | Goldman Sachs Research | NVIDIA, TSMC, AMD, Micron |
| `banking_sector_report_2025.pdf` | Morgan Stanley Research | HDFC, ICICI, Axis, Kotak |
| `it_sector_outlook_2025.pdf` | JP Morgan Research | TCS, Infosys, HCL, Wipro |
| `fmcg_sector_report_2025.pdf` | UBS Research | HUL, ITC, Dabur, Marico |
| `macro_outlook_india_2025.pdf` | Deutsche Bank Research | India GDP, inflation, markets |

---

## 4. Implementation Steps

### Step 1 — Create S3 Bucket

```bash
aws s3 mb s3://advisor-ai-research-575462906097 \
  --region us-east-1
```

### Step 2 — Generate Research PDFs

```bash
pip install fpdf2
python create_research_docs.py
```

Output:
```
Created: research_docs/semiconductor_outlook_2025.pdf
Created: research_docs/banking_sector_report_2025.pdf
Created: research_docs/it_sector_outlook_2025.pdf
Created: research_docs/fmcg_sector_report_2025.pdf
Created: research_docs/macro_outlook_india_2025.pdf
```

### Step 3 — Upload PDFs to S3

```bash
aws s3 cp research_docs/ s3://advisor-ai-research-575462906097/research/ \
  --recursive \
  --region us-east-1
```

Verify:
```bash
aws s3 ls s3://advisor-ai-research-575462906097/research/
```

Output:
```
2026-05-10 10:35:07  2922  banking_sector_report_2025.pdf
2026-05-10 10:35:07  2923  fmcg_sector_report_2025.pdf
2026-05-10 10:35:07  2980  it_sector_outlook_2025.pdf
2026-05-10 10:35:07  3153  macro_outlook_india_2025.pdf
2026-05-10 10:35:08  2978  semiconductor_outlook_2025.pdf
```

### Step 4 — Launch EC2 Instance

```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name advisor-ai-key \
  --query 'KeyMaterial' \
  --output text \
  --region us-east-1 > advisor-ai-key.pem

chmod 400 advisor-ai-key.pem

# Create security group
aws ec2 create-security-group \
  --group-name advisor-ai-sg \
  --description "Advisor AI security group" \
  --region us-east-1
# Security Group ID: sg-0f26fc1c08b1b4f8b

# Allow SSH (port 22) and RAG server (port 8000)
aws ec2 authorize-security-group-ingress \
  --group-name advisor-ai-sg \
  --protocol tcp --port 22 --cidr 0.0.0.0/0 --region us-east-1

aws ec2 authorize-security-group-ingress \
  --group-name advisor-ai-sg \
  --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region us-east-1

# Launch t3.micro (free tier eligible)
aws ec2 run-instances \
  --image-id ami-0a59ec92177ec3fad \
  --instance-type t3.micro \
  --key-name advisor-ai-key \
  --security-groups advisor-ai-sg \
  --count 1 \
  --region us-east-1 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=advisor-ai-rag}]'
```

Instance ID: `i-069a0fd9edb6c3897`
Public IP: `54.81.100.34`

### Step 5 — Configure EC2

```bash
# SSH into EC2
ssh -i advisor-ai-key.pem ec2-user@54.81.100.34

# Install dependencies
sudo yum update -y
sudo yum install python3-pip git -y
pip3 install chromadb pypdf boto3 fastapi uvicorn

# Configure AWS credentials
aws configure

# Create project folder
mkdir advisor-ai-rag && cd advisor-ai-rag

# Download PDFs from S3
mkdir research_docs
aws s3 cp s3://advisor-ai-research-575462906097/research/ \
  research_docs/ --recursive
```

### Step 6 — Deploy RAG Server

Created `rag_server.py` on EC2 with:
- FastAPI REST API on port 8000
- ChromaDB persistent vector store
- PDF ingestion with 500-character chunks + 100-character overlap
- Bedrock Llama 3.1 8B for answer generation
- Source citation in every response

```bash
# Start server permanently
nohup python3 rag_server.py > rag.log 2>&1 &
```

Server startup output:
```
Loading PDFs into ChromaDB...
Loaded semiconductor_outlook_2025.pdf — 6 chunks
Loaded banking_sector_report_2025.pdf — 6 chunks
Loaded macro_outlook_india_2025.pdf — 6 chunks
Loaded it_sector_outlook_2025.pdf — 6 chunks
Loaded fmcg_sector_report_2025.pdf — 5 chunks
Total chunks in ChromaDB: 29
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## 5. API Reference

### Health Check
```
GET http://54.81.100.34:8000/health
```
Response:
```json
{"status": "ok", "chunks_loaded": 29}
```

### Research Query
```
POST http://54.81.100.34:8000/research
Content-Type: application/json

{
  "question": "What are the top picks in semiconductor sector?",
  "session_id": "advisor-001"
}
```

Response:
```json
{
  "answer": "Based on the Goldman Sachs Research report...",
  "sources": ["semiconductor_outlook_2025.pdf"],
  "session_id": "advisor-001"
}
```

---

## 6. Test Results

### Test 1 — Semiconductor Research
```bash
curl -X POST http://54.81.100.34:8000/research \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the top picks in semiconductor sector?"}'
```

**Result:** Returned NVIDIA ($950 target), TSMC ($180), Broadcom ($1,400), Micron ($130) with BUY ratings, citing `semiconductor_outlook_2025.pdf` ✅

### Test 2 — Banking Sector
```bash
curl -X POST http://54.81.100.34:8000/research \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the outlook for Indian banking sector?"}'
```

**Result:** Returned OVERWEIGHT stance, 14.2% credit growth, HDFC Bank and ICICI Bank as top picks, citing `banking_sector_report_2025.pdf` ✅

### Test 3 — India GDP
```bash
curl -X POST http://54.81.100.34:8000/research \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Indias GDP growth forecast?"}'
```

**Result:** Returned 6.8% FY26 GDP forecast from Deutsche Bank, citing `macro_outlook_india_2025.pdf` ✅

---

## 7. RAG Pipeline Explanation

```
Step 1 — INGESTION (done once at startup)
PDFs → Extract text → Split into 500-char chunks
     → ChromaDB embeds chunks using all-MiniLM-L6-v2
     → 29 chunks stored as vectors

Step 2 — RETRIEVAL (every query)
User question → ChromaDB semantic search
             → Returns top 3 most relevant chunks
             → Includes source filename

Step 3 — GENERATION (every query)
System prompt + retrieved chunks + question
→ Llama 3.1 8B via Bedrock
→ Generates grounded answer with citations
```

---

## 8. Completion Status

| Component | Status | Details |
|---|---|---|
| S3 Bucket | ✅ DONE | advisor-ai-research-575462906097 with 5 PDFs |
| EC2 Instance | ✅ DONE | t3.micro, i-069a0fd9edb6c3897, free tier |
| Security Group | ✅ DONE | Ports 22 and 8000 open |
| ChromaDB | ✅ DONE | 29 chunks from 5 PDFs |
| FastAPI Server | ✅ DONE | Running on port 8000 via nohup |
| Bedrock Integration | ✅ DONE | Llama 3.1 8B generating cited answers |
| IAM Role | ✅ DONE | advisor-ai-kb-role for Bedrock access |
| Health Endpoint | ✅ DONE | GET /health returns chunk count |
| Research Endpoint | ✅ DONE | POST /research returns answer + sources |
| All 3 Tests | ✅ DONE | Semiconductors, Banking, GDP all passing |

---

## 9. Daily Operations

### Shutdown (before sleeping)
```bash
# Stop EC2
aws ec2 stop-instances \
  --instance-ids i-069a0fd9edb6c3897 \
  --region us-east-1

# Delete API Gateway stage
aws apigateway delete-stage \
  --rest-api-id 6jg65j6ajh \
  --stage-name prod \
  --region us-east-1
```

### Startup (every morning)
```bash
# Start EC2
aws ec2 start-instances \
  --instance-ids i-069a0fd9edb6c3897 \
  --region us-east-1

# Get new IP (changes every restart)
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=advisor-ai-rag" \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text --region us-east-1

# SSH in and restart server
ssh -i advisor-ai-key.pem ec2-user@NEW_IP
cd advisor-ai-rag
nohup python3 rag_server.py > rag.log 2>&1 &

# Redeploy API Gateway
aws apigateway create-deployment \
  --rest-api-id 6jg65j6ajh \
  --stage-name prod \
  --region us-east-1
```

---

## 10. Live Endpoint

```
POST http://54.81.100.34:8000/research
```

> Note: IP address changes when EC2 is restarted. Always check current IP using describe-instances command above.

---

*Feature 2 Complete | Next: Feature 3 — Client 360 Meeting Prep*
