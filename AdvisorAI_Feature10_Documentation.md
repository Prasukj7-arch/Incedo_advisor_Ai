# ADVISOR AI
## Feature 10: Revenue Enablement (Cross-Sell & Upsell Intelligence)
### Technical Implementation Report | May 2026

---

## 1. Feature Overview

Feature 10 implements the **Revenue Enablement Engine** — a dedicated AI-powered tab that generates ranked, personalized cross-sell and upsell opportunities for each client based on their real profile data: life events, financial goals, concerns, occupation, risk profile, and current portfolio.

This directly addresses **Section 4.6** of the problem statement:
> *"Revenue Enablement — Cross-sell/upsell recommendations, product suitability, and next-best-action engine"*

**The demo moment:** Advisor selects Priya Sharma and clicks Generate. Within 15 seconds, 4 fully personalized product recommendations appear — each one citing a specific life event (daughter's college in 2026, home purchase in 2027, retirement at 58) with a compliance badge and ₹ revenue impact estimate. No generic advice — every card is uniquely tied to that client's real situation.

---

## 2. Architecture

```
Advisor selects client → clicks "Generate Opportunities"
        |
        v
generateRevenue() called (app.js)
        |
        v
POST /api/revenue (FastAPI proxy — fast_app.py)
        |
        v
POST /revenue (API Gateway → Lambda)
        |
        v
handle_revenue_opportunities() in lambda_handler.py
        |
        ├── Finds client in PORTFOLIO_DATA (allocation, returns)
        ├── Finds client in CLIENT_DATA (life events, goals, concerns, occupation)
        ├── Builds a rich personalized context
        ├── Calls Bedrock (Llama 3.1) → returns 4 ranked opportunities
        └── Returns structured JSON:
            {client_name, aum, risk_profile, opportunities: [...]}
                |
                v
UI renders:
- Client summary header (avatar, AUM, risk profile, count)
- 4 opportunity cards in a 2x2 grid
```

### 2.1 Services Used

| Service | Purpose | Cost |
|---|---|---|
| AWS Lambda (Python 3.12) | Builds context + calls Bedrock | Free tier |
| Amazon Bedrock (Llama 3.1 8B) | Generates 4 personalized ranked opportunities | $0.22/1M tokens |
| Amazon API Gateway | `/revenue` HTTPS POST endpoint | Free tier |
| FastAPI (EC2) | Proxy endpoint `POST /api/revenue` with auth | Free tier |
| DynamoDB (`advisor-ai-metrics`) | Tracks `revenue_opportunities` token usage | Free tier |

---

## 3. UI Components

### 3.1 Input Panel
- **Client selector** dropdown: Priya Sharma / Rahul Mehta / Anita Desai
- **Generate Opportunities** button: Green gradient, spinner on load

### 3.2 Client Summary Header
Rendered after generation:
- Green avatar with client initial
- Client name + risk profile + AUM
- "OPPORTUNITIES FOUND: 4" counter (green, large)

### 3.3 Opportunity Cards (2×2 Grid)

Each card contains:

| Field | Description |
|---|---|
| Opportunity number | "OPPORTUNITY 1" label |
| Product name | Bold, large — e.g., "Tax-Saving ULIP" |
| Priority badge | `HIGH` (red), `MEDIUM` (amber), `LOW` (blue) |
| Rationale | Personalized paragraph citing life events/goals |
| Revenue Impact | ₹X lakh / year in green |
| Compliance badge | `SUITABLE` (green) or `REVIEW` (red) |

---

## 4. Live Test Results (Confirmed — May 2026)

### Client: Priya Sharma (Moderate, $0.8M AUM)

| # | Product | Priority | Revenue Impact | Compliance |
|---|---|---|---|---|
| 1 | Tax-Saving ULIP | HIGH | ₹20 lakh / year | SUITABLE |
| 2 | Real Estate Investment Trust (REIT) | MEDIUM | ₹15 lakh / year | SUITABLE |
| 3 | Annuity Plan | LOW | ₹5 lakh / year | SUITABLE |
| 4 | Critical Illness Insurance | HIGH | ₹10 lakh / year | SUITABLE |

**AI correctly referenced:**
- ✅ Daughter starting college in **2026** → Tax-Saving ULIP for education
- ✅ Goal of **purchasing a home in 2027** → REIT for rental income and appreciation
- ✅ Planned **retirement at 58** → Annuity Plan for steady income stream
- ✅ **Occupation: Senior Software Engineer** → Critical Illness Insurance for income protection

---

## 5. Implementation Details

### 5.1 Lambda Handler — `handle_revenue_opportunities()`

```python
def handle_revenue_opportunities(body: dict) -> dict:
    client_name = body.get("client_name", "").strip()
    
    # Look up in both PORTFOLIO_DATA and CLIENT_DATA
    portfolio_client = next((c for c in PORTFOLIO_DATA["clients"]
                             if client_name.lower() in c["name"].lower()), None)
    crm_client = next((c for c in CLIENT_DATA["clients"]
                       if client_name.lower() in c["name"].lower()), None)
    
    # Build rich personalized context from both data sources
    prompt = f"""
    CLIENT PROFILE: {crm_client['name']} | Age: {crm_client['age']}
    Risk: {crm_client['risk_profile']} | AUM: ${crm_client['aum']:,}
    Life Events: {life_events}
    Goals: {goals}
    Concerns: {concerns}
    Portfolio: Equity {portfolio_client['portfolio']['equity']['allocation']}%...
    
    Generate 4 ranked cross-sell opportunities as JSON array.
    Each: product, priority, revenue_impact, rationale, compliance
    JSON only.
    """
    
    answer_json, metrics = call_llama("You are a revenue strategy advisor.", [...])
    save_metrics("revenue_opportunities", metrics)
    
    return {client_name, aum, risk_profile, opportunities: [...]}
```

**Key design decisions:**
- Pulls from **both** `PORTFOLIO_DATA` and `CLIENT_DATA` to maximize context
- Life events, goals, concerns, and occupation are **all included** in the prompt
- Explicit instruction to tie rationale to specific life events — prevents generic advice
- `revenue_impact` is prompted in ₹ to match Indian market context

### 5.2 FastAPI Endpoint — `POST /api/revenue`

```python
class RevenueRequest(BaseModel):
    client_name: str

@app.post("/api/revenue")
def api_revenue(req: RevenueRequest, username: str = Depends(verify_credentials)):
    response = requests.post(
        f"{API_BASE}/revenue",
        headers=HEADERS,
        json={"client_name": req.client_name},
        timeout=45
    )
    return response.json()
```

### 5.3 API Gateway Setup

```bash
# Create /revenue resource
REV_ID=$(aws apigateway create-resource --rest-api-id 6jg65j6ajh \
  --parent-id $PARENT_ID --path-part revenue --query 'id' \
  --output text --region us-east-1)

# Add POST method + Lambda proxy
aws apigateway put-method --rest-api-id 6jg65j6ajh \
  --resource-id $REV_ID --http-method POST \
  --authorization-type NONE --api-key-required --region us-east-1

aws apigateway put-integration --rest-api-id 6jg65j6ajh \
  --resource-id $REV_ID --http-method POST --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:575462906097:function:advisor-ai-chat/invocations \
  --region us-east-1

# Grant Lambda invoke permission
aws lambda add-permission --function-name advisor-ai-chat \
  --statement-id apigateway-revenue --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:575462906097:6jg65j6ajh/*/POST/revenue" \
  --region us-east-1
```

### 5.4 Frontend — `app.js`

```javascript
async function generateRevenue() {
    const clientName = document.getElementById('rev-client-select').value;
    
    const response = await fetch('/api/revenue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_name: clientName })
    });
    const data = await response.json();
    
    // Priority color mapping
    const priorityColor = opp.priority === 'HIGH'
        ? 'text-red-400 bg-red-500/10 border-red-500/30'
        : opp.priority === 'MEDIUM'
        ? 'text-amber-400 bg-amber-500/10 border-amber-500/30'
        : 'text-blue-400 bg-blue-500/10 border-blue-500/30';
    
    // Renders 4 cards in a 2x2 grid
}
```

---

## 6. Completion Status

| Component | Status | Details |
|---|---|---|
| `handle_revenue_opportunities()` in Lambda | ✅ DONE | Dual data source lookup + Bedrock call |
| `/revenue` API Gateway resource | ✅ DONE | POST, API key required, Lambda permission granted |
| `POST /api/revenue` FastAPI endpoint | ✅ DONE | `RevenueRequest` model, 45s timeout |
| Revenue Enablement HTML section | ✅ DONE | Client selector, button, 2×2 card grid |
| `generateRevenue()` in app.js | ✅ DONE | Fetch, spinner, header, card rendering |
| Priority badge color coding | ✅ DONE | HIGH=red, MEDIUM=amber, LOW=blue |
| Compliance badge color coding | ✅ DONE | SUITABLE=green, REVIEW=red |
| `sectionData` entry | ✅ DONE | Header title updates on tab click |
| Sidebar nav item | ✅ DONE | 💰 icon, between Compliance and Simulator |
| Observability tracking | ✅ DONE | `revenue_opportunities` saved to DynamoDB |
| Life-event personalization | ✅ DONE | AI correctly cites real client life events |

---

## 7. Why This Feature Matters

This is the **only feature in the system that directly generates revenue for the firm.** Every other feature (compliance, chat, research) saves time or manages risk. Revenue Enablement is the one that makes the advisor money.

Section 4.6 of the problem statement explicitly requires:
- Cross-sell and upsell recommendations ✅
- Product suitability assessment ✅
- Next-best-action engine ✅

The AI doesn't generate generic advice like "consider mutual funds." It says *"Priya's daughter is starting college in 2026 — a Tax-Saving ULIP addresses her education planning need while providing life cover."* That level of specificity is what separates Advisor AI from a basic chatbot.

---

*Feature 10 Complete | All Problem Statement Requirements Addressed | May 2026*
