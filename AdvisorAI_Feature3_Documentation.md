# ADVISOR AI
## Feature 3: Client 360 Meeting Prep
### Technical Implementation Report | May 2026

---

## 1. Feature Overview

Feature 3 implements an AI-powered **Client 360 Meeting Preparation** system. With a single API call containing a client name, advisors receive a complete, personalized meeting brief covering portfolio status, life events, talking points, cross-sell opportunities, and compliance alerts — in seconds.

This directly addresses **Section 4.1** and **Section 4.2** of the problem statement:
- Section 4.1: *"Automated meeting preparation (client 360 summary)"*
- Section 4.2: *"Next-best-action recommendations, Life-event detection"*

**The demo moment:** Advisor types "Prepare for my 3pm with Rahul Mehta" → instant structured brief with compliance flags, cross-sell opportunities, and a personalized opening line.

---

## 2. Architecture

```
Advisor Request: {"client_name": "Rahul"}
        |
        v
API Gateway POST /client360
(secured with x-api-key)
        |
        v
AWS Lambda — advisor-ai-chat
        |
        ├── CLIENT_DATA (embedded CRM mock data)
        |       └── Life events, goals, concerns,
        |           cross-sell opportunities, compliance flags
        |
        └── Amazon Bedrock (Llama 3.1 8B)
                └── Generates structured 6-section brief
                        |
                        v
Response: {client_name, meeting_time, aum,
           risk_profile, compliance_flags, brief}
```

### 2.1 Services Used

| Service | Purpose | Cost |
|---|---|---|
| AWS Lambda | Runs Client 360 logic | Free tier |
| Amazon Bedrock (Llama 3.1 8B) | Generates meeting brief | $0.22/1M tokens |
| Amazon API Gateway | `/client360` HTTPS endpoint | Free tier |
| Amazon DynamoDB | Session memory (shared with Feature 1) | Free tier |

---

## 3. CRM Data Structure

3 mock clients with full CRM profiles embedded in Lambda:

### Client 1 — Priya Sharma
```
Age: 42 | Occupation: Senior Software Engineer at Infosys
AUM: $850,000 | Risk: Moderate | Client Since: 2019
Life Events: Daughter starting college 2026, Home purchase 2027
Goals: Education fund, Retirement at 58, Home purchase
Concerns: Market volatility, Inflation on fixed income
Cross-sell: Term Life Insurance, NPS top-up, SIP increase
Compliance Flags: None
```

### Client 2 — Rahul Mehta
```
Age: 35 | Occupation: Co-founder, TechStartup Pvt Ltd
AUM: $2,100,000 | Risk: Aggressive | Client Since: 2021
Life Events: Series-B funding liquidity event, Getting married Dec 2025
Goals: Wealth accumulation, International diversification, Tax optimization
Concerns: Concentration risk in tech, Currency exposure
Cross-sell: Global ETF Portfolio, ESOP planning, Wedding fund SIP
Compliance Flags: Large cash inflow - KYC refresh required ⚠️
```

### Client 3 — Anita Desai
```
Age: 62 | Occupation: Retired (Former HR Director)
AUM: $450,000 | Risk: Conservative | Client Since: 2015
Life Events: Recently widowed, Son settled abroad
Goals: Capital preservation, Regular income, Medical emergency fund
Concerns: Outliving savings, Rising healthcare costs, Liquidity
Cross-sell: Senior Citizen Savings Scheme, Health Insurance top-up, Monthly Income Plan
Compliance Flags: None
```

---

## 4. Implementation Steps

### Step 1 — Feature Logic (local)

Created `feature3_client360.py` with:
- `get_client_by_name()` — case-insensitive partial name matching
- `generate_meeting_brief()` — builds CRM context and calls Llama
- 6-section brief structure for every client

```bash
python feature3_client360.py
```

Output confirmed both clients (Priya and Rahul) generating complete briefs locally.

### Step 2 — Embed in Lambda

Updated `lambda_handler.py` to include:
- `CLIENT_DATA` dictionary (full CRM data for all 3 clients)
- `find_crm_client()` function
- `handle_client360()` function
- Path-based routing: `/client360` → Feature 3, `/chat` → Feature 1

```python
# Routing logic in lambda_handler
path = event.get("path", "/chat")
if path == "/client360":
    return handle_client360(body)
else:
    return handle_portfolio_chat(body)
```

### Step 3 — Deploy Updated Lambda

```bash
rm lambda.zip
zip lambda.zip lambda_handler.py

aws lambda update-function-code \
  --function-name advisor-ai-chat \
  --zip-file fileb://lambda.zip \
  --region us-east-1
```

CodeSize increased from 2920 → 4249 bytes confirming new code deployed.

### Step 4 — Create API Gateway /client360 Resource

```bash
# Create resource
aws apigateway create-resource \
  --rest-api-id 6jg65j6ajh \
  --parent-id zgzaf353s2 \
  --path-part client360 \
  --region us-east-1
# Resource ID: 24cz6u

# Create POST method
aws apigateway put-method \
  --rest-api-id 6jg65j6ajh \
  --resource-id 24cz6u \
  --http-method POST \
  --authorization-type NONE \
  --api-key-required \
  --region us-east-1

# Connect to Lambda
aws apigateway put-integration \
  --rest-api-id 6jg65j6ajh \
  --resource-id 24cz6u \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:575462906097:function:advisor-ai-chat/invocations \
  --region us-east-1

# Grant permission
aws lambda add-permission \
  --function-name advisor-ai-chat \
  --statement-id apigateway-client360-new \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:575462906097:6jg65j6ajh/*/POST/client360" \
  --region us-east-1

# Deploy
aws apigateway create-deployment \
  --rest-api-id 6jg65j6ajh \
  --stage-name prod \
  --region us-east-1
```

---

## 5. API Reference

### Client 360 Meeting Prep
```
POST https://6jg65j6ajh.execute-api.us-east-1.amazonaws.com/prod/client360
Headers:
  Content-Type: application/json
  x-api-key: YOUR_API_KEY

Body:
{
  "client_name": "Rahul"
}
```

Response:
```json
{
  "client_name": "Rahul Mehta",
  "meeting_time": "2025-05-09 11:00",
  "aum": 2100000,
  "risk_profile": "Aggressive",
  "compliance_flags": ["Large cash inflow - KYC refresh required"],
  "brief": "**MEETING BRIEF FOR RAHUL MEHTA**\n\n**CLIENT SNAPSHOT**..."
}
```

---

## 6. Brief Structure (6 Sections)

Every generated brief contains exactly these sections:

```
1. CLIENT SNAPSHOT
   Key facts: age, occupation, AUM, risk profile

2. MEETING AGENDA
   3 personalized talking points based on life events and concerns

3. PORTFOLIO ACTIONS
   Specific rebalancing or investment suggestions

4. CROSS-SELL OPPORTUNITIES
   Ranked by priority with reasoning

5. COMPLIANCE ALERTS
   Any KYC, regulatory, or policy flags

6. SUGGESTED OPENING LINE
   Personalized conversation starter based on recent life events
```

---

## 7. Test Results

### Test 1 — Priya Sharma (local)
```bash
python feature3_client360.py
```

**Result:**
- Client Snapshot: Age 42, Infosys engineer, $850K AUM ✅
- Meeting Agenda: Market volatility, Education fund, Home purchase planning ✅
- Cross-sell: Term Life Insurance (High), NPS top-up (Medium), SIP increase (Low) ✅
- Compliance: None ✅
- Opening Line: Personalized around market concerns ✅

### Test 2 — Rahul Mehta (local)
**Result:**
- Compliance flag surfaced: "Large cash inflow - KYC refresh required" ✅
- Cross-sell: Global ETF (High), ESOP planning (Medium), Wedding SIP (Low) ✅
- Opening Line: Referenced Series-B funding congratulations ✅

### Test 3 — Rahul Mehta (live API)
```bash
curl -X POST \
  https://6jg65j6ajh.execute-api.us-east-1.amazonaws.com/prod/client360 \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_KEY" \
  -d '{"client_name": "Rahul"}'
```

**Result:** HTTP 200, complete meeting brief returned with all 6 sections ✅

---

## 8. Completion Status

| Component | Status | Details |
|---|---|---|
| feature3_client360.py | ✅ DONE | Local logic with 6-section brief generation |
| CLIENT_DATA embedded | ✅ DONE | All 3 clients with full CRM profiles in Lambda |
| handle_client360() | ✅ DONE | Path-routed function in lambda_handler.py |
| /client360 API resource | ✅ DONE | Resource ID: 24cz6u |
| POST method | ✅ DONE | API key required |
| Lambda integration | ✅ DONE | AWS_PROXY to advisor-ai-chat |
| Lambda permissions | ✅ DONE | apigateway-client360-new statement |
| Compliance flags | ✅ DONE | Surfaced in response and brief |
| Cross-sell ranking | ✅ DONE | Prioritized in brief |
| Local tests | ✅ DONE | Priya and Rahul both passing |
| Live API test | ✅ DONE | Rahul brief confirmed via curl |

---

## 9. API Gateway Structure (all endpoints)

```
advisor-ai-api (6jg65j6ajh)
└── prod stage
    ├── POST /chat        → Feature 1: Portfolio Chat
    └── POST /client360   → Feature 3: Client 360 Meeting Prep
```

Both endpoints secured with `x-api-key` header.

---

## 10. Prompt Engineering

The Client 360 brief uses a two-part prompt:

**System prompt:** Sets the assistant as a professional meeting prep specialist focused on actionable, specific output.

**User prompt:** Contains full CRM context (life events, goals, concerns, opportunities, flags) plus explicit instruction to generate exactly 6 named sections.

This structured prompting ensures consistent, evaluator-ready output every time.

---

*Feature 3 Complete | Next: Feature 4 — Compliance Alerts + Streamlit UI*
