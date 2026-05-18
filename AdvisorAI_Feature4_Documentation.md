# ADVISOR AI
## Feature 4: Compliance Alerts + Streamlit UI
### Technical Implementation Report | May 2026

---

## 1. Feature Overview

Feature 4 implements two things in one:

**Part A — Compliance Rule Engine:** A real-time compliance monitoring system that runs 6 automated rules across all client portfolios, flags violations by severity (HIGH/MEDIUM/LOW), and logs every alert to AWS CloudWatch for a full audit trail.

**Part B — Non-Blocking Audit Trail:** Every violation is logged to AWS CloudWatch for a full audit trail. This is done via a non-blocking background thread to ensure zero latency impact on the critical path of generating recommendations.

This directly addresses **Section 4.5** and **Section 5.5** of the problem statement:
- Section 4.5: *"Pre-trade and post-trade compliance checks, Real-time alerts on policy violations, Explainable AI recommendations (audit-ready)"*
- Section 5.5: *"Provide rationale behind recommendations, Audit trail for all AI-driven outputs"*

---

## 2. Architecture

```
Streamlit UI (localhost:8501)
        |
        ├── Feature 1: POST /chat → API Gateway → Lambda → Bedrock
        |
        ├── Feature 2: POST /research → EC2:8000 → ChromaDB → Bedrock
        |
        ├── Feature 3: POST /client360 → API Gateway → Lambda → Bedrock
        |
        └── Feature 4: Local Python rule engine
                └── Violations → AWS CloudWatch Logs (audit trail)
```

### 2.1 Compliance Rule Engine Architecture

```
PORTFOLIO_DATA (embedded)
        |
        v
6 Rule Functions (lambda checks)
        |
        ├── RULE-001: Equity Concentration (Conservative > 70%)
        ├── RULE-002: Aggressive Equity Overweight (> 85%)
        ├── RULE-003: Cash Drag (> 20% cash)
        ├── RULE-004: KYC Refresh Required (compliance flags)
        ├── RULE-005: Fixed Income Underweight (Conservative < 40%)
        └── RULE-006: Large Single Day Loss (equity < -3%)
                |
                v
        Violations found?
                |
        YES → CloudWatch Logs → /advisor-ai/compliance
        |
        v
        Results: {status: ALERT/WARNING/CLEAN, violations[], severity}
```

### 2.2 Services Used

| Service | Purpose | Cost |
|---|---|---|
| Streamlit | Web UI framework | Free (open source) |
| AWS CloudWatch Logs | Audit trail for violations | Free tier (5GB/month) |
| API Gateway | Routes chat + client360 calls | Free tier |
| Amazon Bedrock | Powers all AI responses | $0.22/1M tokens |
| EC2 + ChromaDB | Powers RAG search | Free tier |

---

## 3. Compliance Rules

6 rules implemented as Python lambda functions — zero dependencies, instant execution:

### RULE-001 — Equity Concentration Risk
```python
check: equity_allocation > 70 AND risk_profile == "Conservative"
severity: HIGH
action: "Immediate rebalancing required. Reduce equity to max 40% for Conservative profile."
```

### RULE-002 — Aggressive Equity Overweight
```python
check: equity_allocation > 85 (any profile)
severity: MEDIUM
action: "Review equity concentration. Even aggressive profiles should maintain diversification."
```

### RULE-003 — Cash Drag
```python
check: cash_allocation > 20%
severity: LOW
action: "Review idle cash. Consider deploying into suitable instruments."
```

### RULE-004 — KYC Refresh Required
```python
check: len(compliance_flags) > 0
severity: HIGH
action: "Complete KYC refresh before processing any new transactions."
```

### RULE-005 — Fixed Income Underweight
```python
check: fixed_income_allocation < 40 AND risk_profile == "Conservative"
severity: MEDIUM
action: "Increase fixed income allocation to minimum 40% for Conservative profile."
```

### RULE-006 — Large Single Day Loss
```python
check: equity_day_change < -3.0%
severity: HIGH
action: "Alert advisor immediately. Review stop-loss triggers and client communication."
```

---

## 4. Implementation Steps

### Step 1 — Build Compliance Engine (local)

Created `feature4_compliance.py` with:
- 6 rule definitions as Python dicts with lambda check functions
- `run_compliance_check()` — runs all rules against all clients
- `log_to_cloudwatch()` — logs violations to CloudWatch audit trail
- Results returned as structured JSON with severity levels

```bash
python feature4_compliance.py
```

Output:
```
COMPLIANCE CHECK — ALL CLIENTS
Summary:
  Total clients: 3
  Total violations: 1
  High severity: 1

Client: Priya Sharma (Moderate) — CLEAN ✓
Client: Rahul Mehta (Aggressive) — ALERT
  [HIGH] KYC Refresh Required
    → Complete KYC refresh before processing any new transactions.
Client: Anita Desai (Conservative) — CLEAN ✓
```

### Step 2 — Add CloudWatch permissions

```bash
aws iam attach-role-policy \
  --role-name advisor-ai-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess
```

### Step 3 — Build Streamlit UI

Created `app.py` with 4 feature tabs:

```python
# Sidebar navigation
feature = st.radio("Select Feature", [
    "📊 Portfolio Chat",
    "🔍 Research Search",
    "👤 Client 360",
    "⚠️ Compliance Monitor"
])
```

Each feature section calls the appropriate backend:
- Portfolio Chat → `API_BASE/chat` with API key header
- Research Search → `RAG_URL` (EC2 direct)
- Client 360 → `API_BASE/client360` with API key header
- Compliance → local `run_compliance_check()` + CloudWatch

### Step 4 — Run the app

```bash
cd ~/Desktop/advisor-ai
source .venv/bin/activate
export ADVISOR_AI_KEY=YOUR_API_KEY
export EC2_RAG_IP=EC2_PUBLIC_IP
streamlit run app.py
```

---

## 5. Streamlit UI Features

### Portfolio Chat Tab
- 3 quick action buttons (Summarize book, Top risks, Rebalancing)
- Full chat interface with message history
- Multi-turn conversation memory via DynamoDB
- Clear chat button

### Research Search Tab
- 4 quick search buttons (Semiconductors, Banking, IT, GDP)
- Text input for custom queries
- Answer displayed with source PDF citations
- Report list shown in sidebar

### Client 360 Tab
- 3 client quick-select buttons (Priya, Rahul, Anita)
- Text input for any client name
- 4 metric cards (Name, AUM, Risk, Meeting time)
- Compliance flag alert banner (red if flagged)
- Full 6-section meeting brief

### Compliance Monitor Tab
- "Run Full Book Check" button
- Per-client check with name input
- Summary metrics (clients checked, violations, high severity)
- Per-client expandable cards
- Color-coded severity badges (🔴 HIGH, 🟡 MEDIUM, 🟢 LOW)
- CloudWatch audit confirmation message

---

## 6. Test Results

### Test 1 — Portfolio Chat
**Query:** "Summarize my entire book performance today"
**Result:** Total AUM $3.4M, all 3 clients with YTD returns, risk flags, next steps ✅

### Test 2 — Research Search
**Query:** "Banking outlook"
**Result:** Morgan Stanley report answer with 14.2% credit growth, OVERWEIGHT stance, source PDFs cited ✅

### Test 3 — Client 360
**Client:** Rahul Mehta
**Result:** $2.1M AUM, Aggressive, compliance alert surfaced, full 6-section brief, personalized opening line ✅

### Test 4 — Compliance Monitor
**Check:** Full book
**Result:**
- Priya Sharma → CLEAN ✅
- Rahul Mehta → ALERT 🔴 (KYC Refresh Required — HIGH)
- Anita Desai → CLEAN ✅
- Violations logged to CloudWatch ✅

---

## 7. CloudWatch Audit Trail

Every compliance violation is logged to:
```
Log Group:  /advisor-ai/compliance
Log Stream: compliance-alerts
```

Log entry format:
```json
{
  "timestamp": "2026-05-11T03:05:00",
  "client": "Rahul Mehta",
  "violations_count": 1,
  "violations": [
    {
      "rule_id": "RULE-004",
      "rule_name": "KYC Refresh Required",
      "severity": "HIGH"
    }
  ]
}
```

This provides the **audit-ready** output required by Section 5.5 of the problem statement.

---

## 8. Completion Status

| Component | Status | Details |
|---|---|---|
| feature4_compliance.py | ✅ DONE | 6 rules, CloudWatch logging |
| RULE-001 Equity Concentration | ✅ DONE | Conservative > 70% equity |
| RULE-002 Aggressive Overweight | ✅ DONE | Any profile > 85% equity |
| RULE-003 Cash Drag | ✅ DONE | Cash > 20% |
| RULE-004 KYC Refresh | ✅ DONE | Compliance flags detected |
| RULE-005 Fixed Income | ✅ DONE | Conservative < 40% fixed income |
| RULE-006 Day Loss | ✅ DONE | Equity day change < -3% |
| CloudWatch logging | ✅ DONE | Non-blocking background thread for zero latency |
| CloudWatch permissions | ✅ DONE | CloudWatchFullAccess on Lambda role |
| app.py Streamlit UI | ✅ DONE | 4 features, dark theme, professional |
| Portfolio Chat tab | ✅ DONE | Quick buttons + chat input |
| Research Search tab | ✅ DONE | Quick buttons + text search + citations |
| Client 360 tab | ✅ DONE | Client buttons + brief + compliance banner |
| Compliance Monitor tab | ✅ DONE | Full book check + per client + severity badges |
| AWS status sidebar | ✅ DONE | 5 green indicators |
| All 4 features live tested | ✅ DONE | All passing in browser |

---

## 9. How to Run

```bash
# Terminal setup
cd ~/Desktop/advisor-ai
source .venv/bin/activate

# Set environment variables
export ADVISOR_AI_KEY=YOUR_API_KEY
export EC2_RAG_IP=EC2_PUBLIC_IP  # changes every EC2 restart

# Launch
streamlit run app.py

# Open browser
open http://localhost:8501
```

---

*Feature 4 Complete | All 4 Features Done | Project Ready for Submission*
