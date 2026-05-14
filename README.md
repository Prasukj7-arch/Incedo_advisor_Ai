# 💼 Advisor AI — Intelligent Financial Concierge
### Built on AWS | Incedo University Mini Project | May 2026

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Features Built](#features-built)
4. [Architecture](#architecture)
5. [Technology Decisions](#technology-decisions)
6. [AWS Services Used](#aws-services-used)
7. [What Changed and Why](#what-changed-and-why)
8. [Project Structure](#project-structure)
9. [API Reference](#api-reference)
10. [How to Run Locally](#how-to-run-locally)
11. [Live Deployment](#live-deployment)
12. [Cost Summary](#cost-summary)
13. [Security](#security)
14. [Documentation](#documentation)

---

## Project Overview

Advisor AI is an **AI-powered financial advisor concierge** built entirely on AWS managed services. It allows financial advisors at broker-dealer firms to interact with client portfolio data, search research reports, prepare for client meetings, and monitor compliance — all through a single, conversational natural language interface.

This project was built as part of the **Incedo University AI-First initiative** and the AWS AI Practitioner certification program.

**Total AWS cost:** ~$0.05 (₹4) for the entire project  
**Live URL:** `https://strained-aletha-easeled.ngrok-free.dev` (wraps `http://EC2_IP:8080` with secure HTTPS)

---

## Problem Statement

Financial advisors in broker-dealer firms operate in a highly fragmented ecosystem — client data, portfolios, research, compliance rules, and market insights are spread across multiple systems. This leads to:

- Delayed client responses
- Inefficient research and portfolio insights generation
- Inconsistent compliance adherence
- Missed revenue opportunities (cross-sell/upsell)
- High dependency on manual workflows

**Objective:** Build an AI-powered Advisor Concierge that acts as a real-time intelligent assistant to advisors — enhancing productivity, decision-making, and client engagement while ensuring compliance.

---

## Features Built

### Feature 1 — Portfolio Chat (Advisor Productivity)
**Problem statement reference:** Section 4.1

Advisors can ask natural language questions about their client portfolios:
- "Summarize my entire book performance today"
- "What are the top risks in Rahul's portfolio?"
- "Which clients need rebalancing?"

The AI responds with specific numbers, percentages, risk flags, and actionable recommendations. Multi-turn conversation memory means advisors can ask follow-up questions naturally.

**AWS services:** Lambda, API Gateway, Bedrock (Llama 3.1), DynamoDB

---

### Feature 2 — RAG Research Search (Conversational Search)
**Problem statement reference:** Section 4.4, Section 5.3

Advisors can search across 5 financial research reports using natural language:
- "What are the top picks in semiconductor sector?"
- "What is the outlook for Indian banking?"
- "What is India's GDP growth forecast?"

The AI retrieves relevant chunks from actual PDFs and generates grounded, cited answers — not hallucinations.

**Research reports indexed:**
- Goldman Sachs — Semiconductor Sector Outlook 2025
- Morgan Stanley — Indian Banking Sector Q1 2025
- JP Morgan — Indian IT Sector Outlook FY2026
- UBS — FMCG Sector Analysis India 2025
- Deutsche Bank — India Macro Outlook 2025-2026

**AWS services:** EC2 (t3.micro), S3, Bedrock (Llama 3.1), ChromaDB

---

### Feature 3 — Client 360 Meeting Prep (Client Intelligence)
**Problem statement reference:** Section 4.1, Section 4.2

One click generates a complete meeting preparation brief for any client:
- Client snapshot (age, AUM, risk profile, occupation)
- Meeting agenda (3 personalized talking points)
- Portfolio actions (specific rebalancing suggestions)
- Cross-sell opportunities (ranked by priority)
- Compliance alerts (any flags to be aware of)
- Suggested opening line (personalized conversation starter)

**AWS services:** Lambda, API Gateway, Bedrock (Llama 3.1)

---

### Feature 4 — Compliance Monitor (Governance & Risk Controls)
**Problem statement reference:** Section 4.5, Section 5.5

A real-time rule engine runs 6 automated compliance checks across all client portfolios:

| Rule | Check | Severity |
|---|---|---|
| Equity Concentration | Conservative client > 70% equity | HIGH |
| Aggressive Overweight | Any client > 85% equity | MEDIUM |
| Cash Drag | Cash > 20% | LOW |
| KYC Refresh | Pending compliance flags | HIGH |
| Fixed Income Underweight | Conservative client < 40% fixed income | MEDIUM |
| Large Day Loss | Equity day change < -3% | HIGH |

Every violation is logged to **AWS CloudWatch** for a complete audit trail — making the system audit-ready as required by Section 5.5.

**AWS services:** CloudWatch Logs, Lambda (IAM policy)

---

### Feature 5 — AI Observability (Telemetry & Cost Controls)
**Internal Use Only**

Real-time monitoring of LLM usage across the entire platform:
- **Token Tracking:** Monitoring input/output token counts per session.
- **Cost Metrics:** Live calculation of USD cost based on Bedrock pricing models.
- **Latency Monitoring:** Tracking AI response times to ensure high advisor productivity.

**AWS services:** CloudWatch, Lambda, Custom UI Telemetry

---

### Feature 6 — Voice Concierge (Accessibility & Efficiency)
**Problem statement reference:** Section 4.6

Hands-free interaction for busy advisors using native browser speech APIs:
- **Voice-to-Text:** Click-to-speak functionality for natural language queries.
- **Text-to-Voice:** Professional AI-generated audio for reading back portfolio summaries and research.
- **Auto-Speak:** Toggleable setting for seamless conversational feedback.

**AWS services:** Browser Web Speech API, Bedrock (Llama 3.1)

---

### Feature 7 — Human-in-the-Loop Supervision (HITL Compliance)
**Problem statement reference:** Section 10 (Strict Oversight)

A secondary layer of human verification for high-risk AI recommendations:
- **Advice Suspension:** Risky recommendations are blocked and sent to a "Pending Review" queue.
- **Supervisor Dashboard:** Management can Approve or Override AI advice with mandatory audit notes.
- **Audit Persistence:** Every human decision is logged permanently to DynamoDB for regulatory review.

**AWS services:** DynamoDB, Lambda, FastAPI, CloudWatch

---

## Architecture

```
User Browser (Voice-Enabled)
    |
    v
FastAPI Server (EC2:8080) ← HTTP Basic Auth (username + password)
    |
    ├── /api/chat ──────────────→ API Gateway → Lambda → Bedrock (Llama 3.1)
    |                                                          ↕
    |                                                      DynamoDB (History)
    |
    ├── /api/supervision ────────→ DynamoDB (Review Queue) ← Supervisor Approval
    |
    ├── /api/rag ───────────────→ RAG Server (EC2:8000)
    |                                   ↕
    |                              ChromaDB (29 chunks)
    |                                   ↕
    |                              Bedrock (Llama 3.1)
    |
    ├── /api/client360 ──────────→ API Gateway → Lambda → Bedrock (Llama 3.1)
    |
    └── /api/observability ──────→ CloudWatch Metrics + Telemetry Console
```

---

## Technology Decisions

### Why Llama 3.1 8B (not Claude)?
- Claude on Bedrock requires AWS Marketplace subscription which needs a Visa/Mastercard credit card
- Llama 3.1 8B is non-legacy, serverless, cross-region inference ready
- Cost: $0.22/1M tokens vs $0.80+ for Claude equivalents
- Quality: More than sufficient for financial advisory Q&A

### Why FastAPI + HTML/CSS/JS (not Streamlit)?
- Streamlit is rigid and looks basic — unsuitable for an executive demo
- Custom HTML/Tailwind/JS gives glassmorphism UI, animations, typing indicators
- FastAPI acts as a secure proxy — API keys never exposed to browser
- Addresses Section 5.6 (Security & Access Control) of problem statement

### Why ChromaDB on EC2 (not Bedrock Knowledge Base)?
- Bedrock Knowledge Base requires OpenSearch Serverless: **$350-700/month minimum**
- ChromaDB on EC2 t3.micro: **$0 (free tier)**
- Identical RAG output — same chunking, embedding, retrieval concept
- Saved approximately 90% infrastructure cost with zero quality loss

### Why embed data in Lambda (not S3)?
- Lambda reading from S3 on every request adds 200-400ms latency
- Embedded JSON data loads instantly with zero cold-start overhead
- For a demo with 3 mock clients, embedded data is faster and more reliable
- S3 is already used where it makes sense: research PDFs storage

---

## AWS Services Used

| Service | Purpose | Cost |
|---|---|---|
| Amazon Bedrock (Llama 3.1 8B) | LLM inference for all 4 features | $0.22/1M tokens |
| AWS Lambda (Python 3.12) | Serverless compute for chat + client360 | Free tier |
| Amazon API Gateway | HTTPS endpoints with API key auth | Free tier |
| Amazon DynamoDB | Multi-turn conversation memory | Free tier |
| Amazon EC2 (t3.micro) | Hosts RAG server + Web frontend | Free tier |
| Amazon S3 | Stores 5 research PDFs | Free tier |
| AWS CloudWatch Logs | Compliance violation audit trail | Free tier |
| AWS IAM | Role-based access control | Free |

**Total project cost: ~$0.05 (₹4)**

---

## What Changed and Why

### Change 1: LLM Model
| Original Plan | What We Built | Reason |
|---|---|---|
| Claude 3.5 Haiku | Llama 3.1 8B | Claude requires marketplace subscription needing credit card. Llama works immediately with no subscription. |

### Change 2: Vector Database
| Original Plan | What We Built | Reason |
|---|---|---|
| Bedrock Knowledge Base + OpenSearch Serverless | ChromaDB on EC2 | OpenSearch costs $350-700/month idle. ChromaDB is free, identical RAG output. |

### Change 3: Frontend
| Original Plan | What We Built | Reason |
|---|---|---|
| Streamlit dashboard | HTML/Tailwind/JS + FastAPI | Streamlit too rigid for professional demo. Custom UI gives glassmorphism design, animations, proper security proxy. |

### Change 4: Data Storage
| Original Plan | What We Built | Reason |
|---|---|---|
| Mock data in S3 | Embedded in Lambda | S3 reads add latency. Embedded data loads instantly. S3 used for research PDFs where it makes sense. |

### Change 5: Models tested and rejected
- `anthropic.claude-3-haiku-20240307-v1:0` — Legacy, blocked after first call
- `anthropic.claude-haiku-4-5-20251001-v1:0` — Marketplace subscription required
- `amazon.titan-text-express-v1` — End of life, deprecated
- `amazon.titan-text-premier-v1:0` — Not available in account region

---

## Project Structure

```
advisor-ai/
├── static/                          # Frontend (served by FastAPI)
│   ├── index.html                   # Main UI — HTML + Tailwind CSS
│   ├── styles.css                   # Custom CSS (glassmorphism, animations)
│   └── app.js                       # Vanilla JS (all 4 feature interactions)
│
├── data/                            # Mock data
│   ├── portfolios.json              # 3 client portfolios with holdings
│   └── clients.json                 # CRM data (life events, goals, flags)
│
├── research_docs/                   # 5 financial research PDFs (also on S3)
│
├── fast_app.py                      # FastAPI server (secure proxy + auth)
├── lambda_handler.py                # AWS Lambda (Feature 1 + Feature 3)
├── feature1_portfolio.py            # Portfolio chat local test
├── feature2_rag.py                  # RAG search local wrapper
├── feature3_client360.py            # Client 360 local test
├── feature4_compliance.py           # Compliance rule engine
├── bedrock_client.py                # Local Bedrock wrapper
├── create_research_docs.py          # Script to generate research PDFs
├── requirements.txt                 # Python dependencies
├── .env                             # Secrets (gitignored)
├── .gitignore                       # Excludes .env, .pem, .venv, etc.
│
├── AdvisorAI_Feature1_Documentation.md
├── AdvisorAI_Feature2_Documentation.md
├── AdvisorAI_Feature3_Documentation.md
├── AdvisorAI_Feature4_Documentation.md
├── AdvisorAI_Feature5_Documentation.md
├── AdvisorAI_Feature6_Documentation.md
└── AdvisorAI_Feature7_Documentation.md
```

### EC2 Structure (separate machine)
```
advisor-ai-rag/
├── rag_server.py                    # FastAPI RAG server (port 8000)
├── research_docs/                   # 5 PDFs downloaded from S3
└── chroma_db/                       # ChromaDB vector store (29 chunks)
```

---

## API Reference

### Feature 1 — Portfolio Chat
```
POST https://API_GATEWAY_URL/chat
Headers: x-api-key: YOUR_KEY
Body: {"question": "Summarize my book today", "session_id": "session-001"}
```

### Feature 2 — Research Search
```
POST http://EC2_IP:8000/research
Body: {"question": "What are semiconductor top picks?"}
```

### Feature 3 — Client 360
```
POST https://API_GATEWAY_URL/client360
Headers: x-api-key: YOUR_KEY
Body: {"client_name": "Rahul"}
```

### Feature 4 — Compliance Check
```
# Runs locally via Python rule engine
# Logs violations to CloudWatch: /advisor-ai/compliance
```

---

## How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/Prasukj7-arch/Incedo_advisor_Ai.git
cd Incedo_advisor_Ai

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install fastapi uvicorn requests python-dotenv boto3 fpdf2 pypdf chromadb

# 4. Create .env file
cat > .env << EOF
ADVISOR_AI_KEY=your_api_key_here
EC2_RAG_IP=your_ec2_ip_here
WEB_USERNAME=incedo
WEB_PASSWORD=advisor2026
EOF

# 5. Run the app
uvicorn fast_app:app --reload --port 8080

# 6. Open browser
open http://localhost:8080
# Login: incedo / advisor2026
```

---

## Live Deployment

The app is deployed on AWS EC2 (t3.micro, free tier).

### Morning startup routine
```bash
# 1. Start EC2
aws ec2 start-instances \
  --instance-ids i-069a0fd9edb6c3897 --region us-east-1

# 2. Get new IP (changes every restart)
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=advisor-ai-rag" \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text --region us-east-1

# 3. SSH in
ssh -i ~/Desktop/advisor-ai-key.pem ec2-user@NEW_IP

# 4. Start RAG server
cd advisor-ai-rag
nohup python3 rag_server.py > rag.log 2>&1 &

# 5. Start web frontend
cd Incedo_advisor_Ai
nohup python3 fast_app.py > web.log 2>&1 &
exit

# 6. Redeploy API Gateway
aws apigateway create-deployment \
  --rest-api-id 6jg65j6ajh --stage-name prod --region us-east-1

aws apigateway update-usage-plan \
  --usage-plan-id jyzpkv \
  --patch-operations '[{"op":"add","path":"/apiStages","value":"6jg65j6ajh:prod"}]' \
  --region us-east-1
```

### Securing with HTTPS (Ngrok for Demo Submission)
To provide evaluation panels with a highly professional, secure HTTPS URL that avoids mixed-content blocks:
```bash
# On EC2 terminal
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz

# Authenticate with your free account token (gives 1 permanent static domain)
./ngrok config add-authtoken <your_auth_token>

# Launch HTTPS tunnel pointing to local FastAPI server
./ngrok http --url=your-static-domain.ngrok-free.app 8080
```

### Nightly shutdown routine
```bash
# Stop EC2
aws ec2 stop-instances \
  --instance-ids i-069a0fd9edb6c3897 --region us-east-1

# Delete API Gateway stage
aws apigateway delete-stage \
  --rest-api-id 6jg65j6ajh --stage-name prod --region us-east-1

# Unlink usage plan
aws apigateway update-usage-plan \
  --usage-plan-id jyzpkv \
  --patch-operations '[{"op":"remove","path":"/apiStages","value":"6jg65j6ajh:prod"}]' \
  --region us-east-1
```

---

## Cost Summary

| Service | Monthly Cost | Notes |
|---|---|---|
| EC2 t3.micro | $0 | Free tier (750 hrs/month) |
| Lambda | $0 | Free tier (1M requests/month) |
| API Gateway | $0 | Free tier (1M calls/month) |
| DynamoDB | $0 | Free tier (25GB) |
| S3 | $0 | Free tier (5GB) |
| CloudWatch | $0 | Free tier (5GB logs) |
| Bedrock Llama 3.1 | ~$0.30 | For the entire project duration |
| **TOTAL** | **~₹25** | **For the entire project** |

---

## Security

- **Web access:** HTTP Basic Authentication (username + password required)
- **API access:** API Gateway API key (`x-api-key` header required)
- **AWS credentials:** Never in code — loaded from `.env` (gitignored)
- **SSH keys:** `.pem` file stored locally, gitignored
- **EC2 security group:** Ports 22 (SSH), 8000 (RAG), 8080 (Web) only
- **API throttling:** 5 requests/second, 1000 requests/month limit
- **Zero trust:** FastAPI proxy ensures browser never sees AWS credentials
- **Audit trail:** All compliance violations logged to CloudWatch

---

## Documentation

Each feature has a detailed technical implementation document:

| Document | Contents |
|---|---|
| `AdvisorAI_Feature1_Documentation.md` | Lambda setup, API Gateway, DynamoDB, all CLI commands |
| `AdvisorAI_Feature2_Documentation.md` | S3, EC2 setup, ChromaDB, RAG pipeline, PDF ingestion |
| `AdvisorAI_Feature3_Documentation.md` | CRM data, Client 360 brief generation, meeting prep |
| `AdvisorAI_Feature4_Documentation.md` | Compliance rules, CloudWatch audit, Streamlit → FastAPI pivot |
| `AdvisorAI_Feature5_Documentation.md` | AI Observability, latency tracking, cost monitoring |
| `AdvisorAI_Feature6_Documentation.md` | Voice concierge, Web Speech API, TTS implementation |
| `AdvisorAI_Feature7_Documentation.md` | Human-in-the-loop, DynamoDB Queue, Supervisor workflow |

---

## KPIs Addressed

From Section 12 of the problem statement:

| KPI | How Addressed |
|---|---|
| Advisor productivity improvement | Portfolio chat reduces research time from hours to seconds |
| Reduction in client response time | Client 360 generates meeting brief in < 5 seconds |
| Compliance violations reduction | Real-time rule engine catches violations before meetings |
| User adoption and engagement | Professional glassmorphism UI designed for daily use |

---

## Acknowledgements

Built as part of **Incedo University — Incedo 4.0 AI-First Initiative**

Courses completed:
- Prompt Engineering Practical Course (Udemy)
- AWS AI Practitioner Certification (AWS Skill Builder)
- Microsoft Copilot Training

*This project demonstrates practical application of GenAI, AWS Bedrock, RAG pipelines, serverless architecture, and secure web deployment — all within AWS free tier limits.*

---

*Advisor AI | May 2026 | Built with AWS Bedrock + Llama 3.1 + EC2 + Lambda + DynamoDB*
