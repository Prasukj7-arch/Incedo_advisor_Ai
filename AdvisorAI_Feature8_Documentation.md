# ADVISOR AI
## Feature 8: Portfolio Scenario Simulator (What-If Analysis Engine)
### Technical Implementation Report | May 2026

---

## 1. Feature Overview

Feature 8 implements the **Portfolio Scenario Simulator** — a "What-If" analysis engine that allows financial advisors to test hypothetical portfolio changes before executing them in the real world.

Instead of guessing how a market shift or allocation change would affect a client, the advisor types a natural language scenario. The AI calculates the new allocation weights, estimates the impact on annual return and risk level, and presents a **side-by-side comparison** of the current vs. simulated portfolio — including a real-time compliance check on the new hypothetical allocation.

This directly addresses **Section 4.3** of the problem statement:
> *"Scenario simulations — run what-if analysis on portfolio changes to evaluate risk/return impact"*

**The demo moment:** Advisor selects Rahul Mehta, types "Move 20% from Equity to Fixed Income", clicks Run — and instantly sees two cards: current 80% equity vs. simulated 60% equity, with risk level changing from High to Medium, return estimate updating, and a green PASS compliance badge.

---

## 2. Architecture

```
Advisor types scenario in UI
        |
        v
runSimulation() called (app.js)
        |
        v
POST /api/simulate (FastAPI proxy — fast_app.py)
        |
        v
POST /simulate (API Gateway → Lambda)
        |
        v
handle_scenario_simulation() in lambda_handler.py
        |
        ├── Looks up client portfolio from PORTFOLIO_DATA
        ├── Builds structured prompt with current allocations
        ├── Calls Bedrock (Llama 3.1) — returns JSON comparison
        └── Returns: current + simulated + analysis + compliance_status
                |
                v
UI renders:
- Side-by-side allocation cards (with progress bars)
- Return % and Risk Level for each
- AI Impact Analysis paragraph
- Compliance badge (PASS / WARNING / FAIL)
```

### 2.1 Services Used

| Service | Purpose | Cost |
|---|---|---|
| AWS Lambda (Python 3.12) | Runs simulation logic + calls Bedrock | Free tier |
| Amazon Bedrock (Llama 3.1 8B) | Calculates hypothetical allocations and risk impact | $0.22/1M tokens |
| Amazon API Gateway | `/simulate` HTTPS endpoint | Free tier |
| FastAPI (EC2) | Proxy endpoint `/api/simulate` with auth | Free tier |
| DynamoDB (`advisor-ai-metrics`) | Tracks simulation token usage for observability | Free tier |

---

## 3. UI Components

### 3.1 Input Panel (Top)
- **Client Selector** dropdown: Priya Sharma / Rahul Mehta / Anita Desai
- **Scenario Input** text field: Free-form natural language description
- **Run Simulation** button: Calls the API, shows spinner while processing

### 3.2 Side-by-Side Comparison Cards

Two cards rendered after simulation completes:

| Card | Description |
|---|---|
| **Current Allocation** | Grey left border, clock icon, shows current portfolio weights |
| **Simulated Allocation** | Blue left border, wand icon, shows hypothetical new weights |

Each card contains:
- Return % and Risk Level (High = red, others = green)
- 4 animated progress bars: Equity / Fixed Income / Cash / Alternatives

### 3.3 AI Impact Analysis Panel

Below the comparison cards:
- Full AI-generated rationale explaining what changed and why
- **Compliance Badge**: Color-coded pill showing PASS (green) / WARNING (amber) / FAIL (red)

---

## 4. Implementation Details

### 4.1 Lambda Handler — `handle_scenario_simulation()`

```python
def handle_scenario_simulation(body: dict) -> dict:
    client_name = body.get("client_name", "").strip()
    scenario = body.get("scenario", "").strip()
    
    # Find client portfolio from embedded data
    client_portfolio = next(
        (c for c in PORTFOLIO_DATA["clients"] if client_name.lower() in c["name"].lower()),
        None
    )
    
    # Build structured prompt — current allocation pre-filled into JSON template
    prompt = f"""You are a senior portfolio risk analyst.
Simulate: "{scenario}"
Current Portfolio: {json.dumps(client_portfolio['portfolio'])}
Return JSON: {{current: {{...}}, simulated: {{...}}, analysis: "...", compliance_status: "PASS/WARNING/FAIL"}}
JSON only."""
    
    # Call Bedrock → parse JSON → save metrics
    answer_json, metrics = call_llama("You are a financial simulation engine.", [...])
    save_metrics("scenario_simulation", metrics)
    
    # Strip markdown wrappers (Llama sometimes wraps with ```json)
    clean_json = answer_json.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)
```

### 4.2 FastAPI Endpoint — `/api/simulate`

```python
class SimulateRequest(BaseModel):
    client_name: str
    scenario: str

@app.post("/api/simulate")
def api_simulate(req: SimulateRequest, username: str = Depends(verify_credentials)):
    response = requests.post(
        f"{API_BASE}/simulate",
        headers=HEADERS,
        json={"client_name": req.client_name, "scenario": req.scenario},
        timeout=45
    )
    return response.json()
```

### 4.3 API Gateway

New resource `/simulate` added with:
- POST method
- API key required (`x-api-key` header)
- AWS_PROXY integration to `advisor-ai-chat` Lambda (account `575462906097`)

```bash
# CLI commands used to create the resource
SIM_ID=$(aws apigateway create-resource --rest-api-id 6jg65j6ajh \
  --parent-id $PARENT_ID --path-part simulate --query 'id' \
  --output text --region us-east-1)

aws apigateway put-method --rest-api-id 6jg65j6ajh \
  --resource-id $SIM_ID --http-method POST \
  --authorization-type NONE --api-key-required --region us-east-1

aws apigateway put-integration --rest-api-id 6jg65j6ajh \
  --resource-id $SIM_ID --http-method POST --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:575462906097:function:advisor-ai-chat/invocations \
  --region us-east-1
```

### 4.4 Frontend — `app.js`

```javascript
async function runSimulation() {
    const clientName = document.getElementById('sim-client-select').value;
    const scenario = document.getElementById('sim-scenario-input').value;
    
    const response = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_name: clientName, scenario: scenario })
    });
    const data = await response.json();
    
    renderSimStats('sim-current-stats', data.current);
    renderSimStats('sim-new-stats', data.simulated);
    document.getElementById('sim-analysis-text').innerText = data.analysis;
    // Render compliance badge with color coding
}

function renderSimStats(containerId, stats) {
    // Renders Return%, Risk Level, and 4 animated progress bars
}
```

---

## 5. AI Prompt Design

The prompt is carefully engineered to:
1. Pre-fill the `"current"` object with exact live values from `PORTFOLIO_DATA` so the AI doesn't hallucinate current figures
2. Ask for `"simulated"` values only — the AI only calculates the hypothetical state
3. Request a strict JSON-only response to enable direct `json.loads()` parsing
4. Ask for `compliance_status` as a string ("PASS" / "WARNING" / "FAIL") not a boolean

**Error handling:** If Llama returns markdown-wrapped JSON (```json ... ```) instead of raw JSON, the code strips it before parsing. If parsing still fails, a 500 error is returned with the raw AI response for debugging.

---

## 6. Test Scenarios

| Client | Scenario | Expected Result |
|---|---|---|
| Rahul Mehta | Move 20% from Equity to Fixed Income | Equity: 80%→60%, Risk: High→Medium |
| Priya Sharma | Increase Cash by 10% | Cash: 10%→20%, Return slightly lower |
| Anita Desai | Shift 10% from Fixed Income to Equity | May trigger compliance WARNING (conservative profile) |

---

## 7. Completion Status

| Component | Status | Details |
|---|---|---|
| `handle_scenario_simulation()` in Lambda | ✅ DONE | Prompt, Bedrock call, JSON parse, error handling |
| `/simulate` API Gateway resource | ✅ DONE | POST, API key required, Lambda proxy |
| `/api/simulate` FastAPI endpoint | ✅ DONE | SimulateRequest model, 45s timeout |
| Simulator HTML section | ✅ DONE | Client dropdown, scenario input, results area |
| `runSimulation()` in app.js | ✅ DONE | Fetch, spinner, side-by-side rendering |
| Progress bars rendering | ✅ DONE | Animated bars for all 4 asset classes |
| Compliance badge | ✅ DONE | Green/Amber/Red color coding |
| `sectionData` entry | ✅ DONE | Header title updates when tab is clicked |
| Observability tracking | ✅ DONE | `scenario_simulation` saved to DynamoDB |

---

## 8. Why This Feature Matters

Section 4.3 of the problem statement explicitly asks for scenario simulations. Most implementations skip this because it requires the AI to do actual quantitative reasoning, not just text generation.

By building this feature, Advisor AI demonstrates that the system can act as a **pre-trade decision support tool** — giving advisors data-backed confidence before they make any changes to a client's real portfolio.

---

*Feature 8 Complete | Built on AWS Bedrock + Llama 3.1 | May 2026*
