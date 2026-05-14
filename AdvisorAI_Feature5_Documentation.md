# ADVISOR AI
## Feature 5: AI Observability Console
### Technical Implementation Report | May 2026

---

## 1. Feature Overview

Feature 5 implements a production-grade **AI Observability Console**. It provides real-time visibility into the system's performance, resource consumption, and financial costs. This addresses the "Day 2" operations requirements of an enterprise AI application.

This directly addresses **Section 6.5** of the problem statement:
- Section 6.5: *"End-to-end monitoring (logs, traces, metrics), AI model performance tracking"*

---

## 2. Architecture

Feature 5 uses a telemetry-capture pattern that intercepts metadata from every Bedrock call.

```
   AWS Lambda / EC2
         |
         ├── Call Bedrock (Llama 3.1)
         ├── Intercept Metadata (Token counts, Latency)
         ├── Calculate Cost (USD & INR)
         └── Write to DynamoDB (advisor-ai-metrics)
               |
               v
         Dashboard UI (FastAPI + JS)
         (Aggregates and visualizes metrics)
```

### 2.1 Metrics Captured

| Metric | Source | Purpose |
|---|---|---|
| Input Tokens | Bedrock Headers | Track prompt size and context usage |
| Output Tokens | Bedrock Headers | Track AI response length |
| Latency (ms) | Python `time` | Monitor system responsiveness |
| Cost (USD) | Formula | Financial tracking ($0.22 per 1M tokens) |
| Feature ID | App Logic | Attribution (which feature is costing more?) |

---

## 3. Implementation Details

### 3.1 Telemetry Collection (Lambda/EC2)

Every time the AI is invoked, the following logic captures the metrics:

```python
# Extract from Bedrock response headers
headers = response.get("ResponseMetadata", {}).get("HTTPHeaders", {})
input_tokens = int(headers.get("x-amzn-bedrock-input-token-count", 0))
output_tokens = int(headers.get("x-amzn-bedrock-output-token-count", 0))

# Calculate cost
cost_usd = ((input_tokens + output_tokens) / 1_000_000) * 0.22

# Save to DynamoDB
save_metrics(feature_name, {
    "tokens": input_tokens + output_tokens,
    "latency_ms": latency_ms,
    "cost_usd": Decimal(str(round(cost_usd, 6)))
})
```

### 3.2 Storage (DynamoDB)

A dedicated table `advisor-ai-metrics` was created to store every single invocation's telemetry data.

### 3.3 Dashboard (Frontend)

The UI was updated with a new "AI Observability" section that displays:
- **Real-time Counters:** Total tokens used, total cost in USD/INR.
- **Performance:** Average latency per call.
- **Feature Breakdown:** Pie chart/progress bars showing which feature (Chat vs Research) uses the most resources.
- **Timeline:** A "Recent Invocations" table showing the most recent 10 calls.

---

## 4. Completion Status

| Component | Status | Details |
|---|---|---|
| Metrics Capture | ✅ DONE | Integrated into Lambda and EC2 RAG Server |
| DynamoDB Table | ✅ DONE | `advisor-ai-metrics` live in us-east-1 |
| Cost Calculator | ✅ DONE | Automated USD to INR conversion (83.5 rate) |
| Dashboard UI | ✅ DONE | Real-time visualization with charts and tables |
| Cross-Feature Tracking| ✅ DONE | Tracks Chat, Client 360, and Research Search |

---

*Feature 5 Complete | Next: Feature 6 — Voice Concierge*
