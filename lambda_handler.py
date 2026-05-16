import json
import boto3
from datetime import datetime
from decimal import Decimal
from feature4_compliance import check_compliance, log_audit_trail

MODEL_ID = "us.meta.llama3-1-8b-instruct-v1:0"
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
SESSION_TABLE = "advisor-ai-sessions"
SUPERVISION_TABLE = "advisor-ai-supervision"

PORTFOLIO_DATA = {
  "clients": [
    {
      "id": "C001", "name": "Priya Sharma", "risk_profile": "Moderate",
      "aum": 850000, "ytd_return": 12.4, "last_rebalanced": "2025-02-15",
      "portfolio": {
        "equity": {"allocation": 55, "value": 467500, "day_change": 1.2},
        "fixed_income": {"allocation": 30, "value": 255000, "day_change": -0.3},
        "cash": {"allocation": 10, "value": 85000, "day_change": 0},
        "alternatives": {"allocation": 5, "value": 42500, "day_change": 0.8}
      },
      "top_holdings": [
        {"ticker": "AAPL", "value": 95000, "day_change": 2.1},
        {"ticker": "MSFT", "value": 88000, "day_change": 0.9},
        {"ticker": "GOOGL", "value": 72000, "day_change": 1.4},
        {"ticker": "HDFC Bank", "value": 65000, "day_change": -0.5},
        {"ticker": "Infosys", "value": 58000, "day_change": 1.8}
      ]
    },
    {
      "id": "C002", "name": "Rahul Mehta", "risk_profile": "Aggressive",
      "aum": 2100000, "ytd_return": 22.7, "last_rebalanced": "2025-03-01",
      "portfolio": {
        "equity": {"allocation": 80, "value": 1680000, "day_change": 2.3},
        "fixed_income": {"allocation": 10, "value": 210000, "day_change": -0.1},
        "cash": {"allocation": 5, "value": 105000, "day_change": 0},
        "alternatives": {"allocation": 5, "value": 105000, "day_change": 1.5}
      },
      "top_holdings": [
        {"ticker": "NVDA", "value": 320000, "day_change": 3.8},
        {"ticker": "TSLA", "value": 280000, "day_change": -1.2},
        {"ticker": "META", "value": 240000, "day_change": 2.6},
        {"ticker": "AMZN", "value": 195000, "day_change": 1.1},
        {"ticker": "TCS", "value": 180000, "day_change": 0.7}
      ]
    },
    {
      "id": "C003", "name": "Anita Desai", "risk_profile": "Conservative",
      "aum": 450000, "ytd_return": 6.1, "last_rebalanced": "2025-01-20",
      "portfolio": {
        "equity": {"allocation": 25, "value": 112500, "day_change": 0.4},
        "fixed_income": {"allocation": 60, "value": 270000, "day_change": -0.2},
        "cash": {"allocation": 12, "value": 54000, "day_change": 0},
        "alternatives": {"allocation": 3, "value": 13500, "day_change": 0.2}
      },
      "top_holdings": [
        {"ticker": "Govt Bond 2030", "value": 120000, "day_change": -0.1},
        {"ticker": "SBI Fixed Deposit", "value": 90000, "day_change": 0},
        {"ticker": "Reliance", "value": 55000, "day_change": 0.6},
        {"ticker": "Gold ETF", "value": 45000, "day_change": 0.3},
        {"ticker": "HDFC Balanced Fund", "value": 40000, "day_change": 0.2}
      ]
    }
  ]
}

CLIENT_DATA = {
  "clients": [
    {
      "id": "C001", "name": "Priya Sharma", "age": 42,
      "occupation": "Senior Software Engineer at Infosys",
      "risk_profile": "Moderate", "aum": 850000,
      "since": "2019-06-01", "last_meeting": "2025-03-12",
      "next_meeting": "2025-05-15 15:00",
      "life_events": ["Daughter starting college in 2026", "Planning home purchase in 2027"],
      "goals": ["Daughter education fund", "Retirement at 58", "Home purchase"],
      "concerns": ["Market volatility", "Inflation impact on fixed income"],
      "last_interaction_notes": "Discussed rebalancing equity exposure. Concerned about US tech valuations.",
      "cross_sell_opportunities": ["Term Life Insurance", "NPS top-up", "SIP increase"],
      "compliance_flags": []
    },
    {
      "id": "C002", "name": "Rahul Mehta", "age": 35,
      "occupation": "Co-founder, TechStartup Pvt Ltd",
      "risk_profile": "Aggressive", "aum": 2100000,
      "since": "2021-01-15", "last_meeting": "2025-04-02",
      "next_meeting": "2025-05-09 11:00",
      "life_events": ["Recent liquidity event from startup funding round", "Getting married in Dec 2025"],
      "goals": ["Wealth accumulation", "International diversification", "Tax optimization"],
      "concerns": ["Concentration risk in tech", "Currency exposure"],
      "last_interaction_notes": "Post Series-B funding, has fresh capital to deploy. Interested in global ETFs.",
      "cross_sell_opportunities": ["Global ETF Portfolio", "ESOP planning", "Wedding fund SIP"],
      "compliance_flags": ["Large cash inflow - KYC refresh required"]
    },
    {
      "id": "C003", "name": "Anita Desai", "age": 62,
      "occupation": "Retired (Former HR Director)",
      "risk_profile": "Conservative", "aum": 450000,
      "since": "2015-08-20", "last_meeting": "2025-02-28",
      "next_meeting": "2025-05-20 10:00",
      "life_events": ["Recently widowed", "Son settled abroad"],
      "goals": ["Capital preservation", "Regular income", "Medical emergency fund"],
      "concerns": ["Outliving savings", "Rising healthcare costs", "Liquidity"],
      "last_interaction_notes": "Discussed increasing fixed income allocation. Wants monthly income stream.",
      "cross_sell_opportunities": ["Senior Citizen Savings Scheme", "Health Insurance top-up", "Monthly Income Plan"],
      "compliance_flags": []
    }
  ]
}

PORTFOLIO_SYSTEM_PROMPT = """You are an expert AI financial advisor assistant for a broker-dealer firm.
You have real-time client portfolio data. Be concise, professional, and specific with numbers.
Always mention values, percentages, and changes. Flag risks clearly. Suggest actionable next steps."""

CLIENT360_SYSTEM_PROMPT = """You are an expert financial advisor assistant preparing meeting briefs.
Generate a comprehensive, professional meeting preparation brief.
Be specific, actionable, and concise. Use the exact data provided.
Format the brief clearly with sections. Focus on what the advisor needs to know."""

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,x-api-key",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
    "Content-Type": "application/json"
}


def find_crm_client(name: str):
    name_lower = name.lower()
    for c in CLIENT_DATA["clients"]:
        if name_lower in c["name"].lower():
            return c
    return None


def build_portfolio_context(question: str) -> str:
    for c in PORTFOLIO_DATA["clients"]:
        if c["name"].split()[0].lower() in question.lower() or \
           c["name"].lower() in question.lower():
            holdings = "\n".join([
                f"  - {h['ticker']}: ${h['value']:,} ({h['day_change']}%)"
                for h in c["top_holdings"]
            ])
            return f"""
CLIENT: {c['name']} | Risk: {c['risk_profile']} | AUM: ${c['aum']:,}
YTD Return: {c['ytd_return']}% | Last Rebalanced: {c['last_rebalanced']}
ALLOCATION:
- Equity: {c['portfolio']['equity']['allocation']}% = ${c['portfolio']['equity']['value']:,} (Day: {c['portfolio']['equity']['day_change']}%)
- Fixed Income: {c['portfolio']['fixed_income']['allocation']}% = ${c['portfolio']['fixed_income']['value']:,}
- Cash: {c['portfolio']['cash']['allocation']}% = ${c['portfolio']['cash']['value']:,}
- Alternatives: {c['portfolio']['alternatives']['allocation']}% = ${c['portfolio']['alternatives']['value']:,}
TOP HOLDINGS:
{holdings}"""
    total_aum = sum(c["aum"] for c in PORTFOLIO_DATA["clients"])
    lines = [f"TOTAL BOOK AUM: ${total_aum:,}\n"]
    for c in PORTFOLIO_DATA["clients"]:
        lines.append(
            f"- {c['name']} | AUM: ${c['aum']:,} | Risk: {c['risk_profile']} "
            f"| YTD: {c['ytd_return']}% | Equity: {c['portfolio']['equity']['allocation']}%"
        )
    return "\n".join(lines)


def get_session(session_id: str) -> list:
    try:
        table = dynamodb.Table(SESSION_TABLE)
        resp = table.get_item(Key={"session_id": session_id})
        return resp.get("Item", {}).get("history", [])
    except Exception:
        return []


def save_session(session_id: str, history: list):
    try:
        table = dynamodb.Table(SESSION_TABLE)
        table.put_item(Item={
            "session_id": session_id,
            "history": history,
            "updated_at": datetime.utcnow().isoformat()
        })
    except Exception:
        pass


def call_llama(system_prompt: str, messages: list) -> tuple:
    """Returns (answer, metrics_dict)"""
    conversation = ""
    for msg in messages:
        role = "user" if msg["role"] == "user" else "assistant"
        conversation += f"<|start_header_id|>{role}<|end_header_id|>\n{msg['content']}\n<|eot_id|>"

    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_prompt}
<|eot_id|>{conversation}<|start_header_id|>assistant<|end_header_id|>"""

    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 1000,
        "temperature": 0.7,
        "top_p": 0.9
    })

    import time
    start_time = time.time()
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=body,
        trace="ENABLED"
    )
    latency_ms = int((time.time() - start_time) * 1000)

    result = json.loads(response["body"].read())
    answer = result["generation"].strip()

    # Extract Bedrock metrics from response metadata
    metadata = response.get("ResponseMetadata", {})
    http_headers = metadata.get("HTTPHeaders", {})

    input_tokens = int(http_headers.get("x-amzn-bedrock-input-token-count", 0))
    output_tokens = int(http_headers.get("x-amzn-bedrock-output-token-count", 0))

    # Llama 3.1 8B pricing: $0.22/1M input, $0.22/1M output
    cost_usd = ((input_tokens + output_tokens) / 1_000_000) * 0.22

    metrics = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "latency_ms": latency_ms,
        "cost_usd": Decimal(str(round(cost_usd, 6))),
        "model_id": MODEL_ID,
        "timestamp": datetime.utcnow().isoformat()
    }

    return answer, metrics


def save_metrics(feature: str, metrics: dict):
    """Save invocation metrics to DynamoDB for observability."""
    try:
        table = dynamodb.Table("advisor-ai-metrics")
        table.put_item(Item={
            "metric_id": f"{feature}-{datetime.utcnow().isoformat()}",
            "feature": feature,
            **metrics
        })
    except Exception:
        pass


def send_to_supervision(client_profile: dict, feature: str, recommendation: str, violations: list, metrics: dict):
    """Saves a flagged recommendation to the supervision queue for human review."""
    try:
        table = dynamodb.Table(SUPERVISION_TABLE)
        review_id = f"REV-{int(datetime.utcnow().timestamp())}"
        table.put_item(Item={
            "review_id": review_id,
            "status": "PENDING",
            "client_id": client_profile.get("id", "UNKNOWN"),
            "client_name": client_profile.get("name", "Unknown"),
            "feature": feature,
            "recommendation": recommendation,
            "violations": violations,
            "metrics": metrics,
            "created_at": datetime.utcnow().isoformat(),
            "decision": None,
            "supervisor_notes": None
        })
        return review_id
    except Exception as e:
        print(f"Supervision queue error: {e}")
        return None


def handle_portfolio_chat(body: dict) -> dict:
    question = body.get("question", "").strip()
    if question == "health_check":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"status": "active"})}
        
    session_id = body.get("session_id", "default-session")
    if not question:
        return {"statusCode": 400, "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Question is required"})}
    history = get_session(session_id)
    context_data = build_portfolio_context(question)
    user_message = f"PORTFOLIO DATA:\n{context_data}\n\nQUESTION: {question}"
    history.append({"role": "user", "content": user_message})
    answer, metrics = call_llama(PORTFOLIO_SYSTEM_PROMPT, history)
    save_metrics("portfolio_chat", metrics)
    
    # --- COMPLIANCE RULE ENGINE ---
    client_profile = None
    for c in PORTFOLIO_DATA["clients"]:
        if c["name"].split()[0].lower() in question.lower() or c["name"].lower() in question.lower():
            client_profile = c
            break
            
    violations = []
    if client_profile:
        violations = check_compliance(client_profile, answer)
        log_audit_trail(client_profile["id"], "portfolio_chat", answer, violations)
    else:
        log_audit_trail("UNKNOWN_CLIENT", "portfolio_chat", answer, [])
        
    if violations:
        review_id = send_to_supervision(client_profile, "portfolio_chat", answer, violations, metrics)
        status_msg = f"🛡️ ADVICE SUSPENDED: This recommendation triggered {len(violations)} compliance violations and has been sent to the Supervision Queue (ID: {review_id}) for human approval. It will NOT be visible to the client until approved."
        answer = status_msg
        status_code = "PENDING_REVIEW"
    else:
        status_code = "APPROVED"

    history.append({"role": "assistant", "content": answer})
    save_session(session_id, history)
    return {
        "statusCode": 200, "headers": CORS_HEADERS,
        "body": json.dumps({
            "answer": answer,
            "session_id": session_id,
            "status_code": status_code,
            "turn": len(history) // 2,
            "metrics": metrics
        }, default=float)
    }


def handle_client360(body: dict) -> dict:
    client_name = body.get("client_name", "").strip()
    if not client_name:
        return {"statusCode": 400, "headers": CORS_HEADERS,
                "body": json.dumps({"error": "client_name is required"})}
    client = find_crm_client(client_name)
    if not client:
        return {"statusCode": 404, "headers": CORS_HEADERS,
                "body": json.dumps({"error": f"Client '{client_name}' not found"})}
    life_events = "\n".join([f"  - {e}" for e in client["life_events"]])
    goals = "\n".join([f"  - {g}" for g in client["goals"]])
    concerns = "\n".join([f"  - {c}" for c in client["concerns"]])
    opportunities = "\n".join([f"  - {o}" for o in client["cross_sell_opportunities"]])
    flags = "\n".join([f"  - {f}" for f in client["compliance_flags"]]) \
        if client["compliance_flags"] else "  - None"
    user_message = f"""
CLIENT 360 DATA:
- Name: {client['name']} | Age: {client['age']} | Occupation: {client['occupation']}
- Client Since: {client['since']} | Risk Profile: {client['risk_profile']} | AUM: ${client['aum']:,}
- Last Meeting: {client['last_meeting']} | Next Meeting: {client['next_meeting']}
- Last Interaction: {client['last_interaction_notes']}

Life Events:
{life_events}

Financial Goals:
{goals}

Current Concerns:
{concerns}

Cross-sell Opportunities:
{opportunities}

Compliance Flags:
{flags}

Generate a professional meeting preparation brief for {client['name']} with these sections:
1. CLIENT SNAPSHOT (3-4 key bullet points)
2. MEETING AGENDA (3 suggested talking points)
3. PORTFOLIO ACTIONS (specific suggestions)
4. CROSS-SELL OPPORTUNITIES (ranked by priority)
5. COMPLIANCE ALERTS (flags to be aware of)
6. SUGGESTED OPENING LINE (personalized conversation starter)
"""
    answer, metrics = call_llama(CLIENT360_SYSTEM_PROMPT, [{"role": "user", "content": user_message}])
    save_metrics("client360_brief", metrics)
    
    # --- COMPLIANCE RULE ENGINE ---
    violations = check_compliance(client, answer)
    log_audit_trail(client["id"], "client360_brief", answer, violations)
    
    if violations:
        review_id = send_to_supervision(client, "client360_brief", answer, violations, metrics)
        status_msg = f"🛡️ BRIEF SUSPENDED: This brief triggered {len(violations)} compliance violations and has been sent to the Supervision Queue (ID: {review_id}) for review."
        answer = status_msg
        status_code = "PENDING_REVIEW"
    else:
        status_code = "APPROVED"

    return {
        "statusCode": 200, "headers": CORS_HEADERS,
        "body": json.dumps({
            "client_name": client["name"],
            "meeting_time": client["next_meeting"],
            "aum": client["aum"],
            "risk_profile": client["risk_profile"],
            "compliance_flags": client["compliance_flags"],
            "brief": answer,
            "status_code": status_code,
            "metrics": {k: float(v) if isinstance(v, Decimal) else v for k, v in metrics.items()}
        })
    }


def handle_scenario_simulation(body: dict) -> dict:
    client_name = body.get("client_name", "").strip()
    scenario = body.get("scenario", "").strip()
    
    if not client_name or not scenario:
        return {"statusCode": 400, "headers": CORS_HEADERS,
                "body": json.dumps({"error": "client_name and scenario are required"})}
                
    client_portfolio = None
    for c in PORTFOLIO_DATA["clients"]:
        if client_name.lower() in c["name"].lower():
            client_portfolio = c
            break
            
    if not client_portfolio:
        return {"statusCode": 404, "headers": CORS_HEADERS,
                "body": json.dumps({"error": f"Client '{client_name}' not found"})}

    prompt = f"""You are a senior portfolio risk analyst. 
Simulate the following scenario for {client_portfolio['name']}'s portfolio.

CURRENT PORTFOLIO:
{json.dumps(client_portfolio['portfolio'], indent=2)}

REQUESTED SCENARIO:
"{scenario}"

TASK:
1. Calculate the new weights (%) for Equity, Fixed Income, Cash, and Alternatives after the scenario is applied.
2. Estimate the impact on 'Estimated Annual Return' and 'Risk Level' (Low, Medium, High).
3. Provide a professional analysis of the changes.
4. Format the output as a JSON object strictly following this structure:
{{
    "current": {{ "equity": {client_portfolio['portfolio']['equity']['allocation']}, "fixed_income": {client_portfolio['portfolio']['fixed_income']['allocation']}, "cash": {client_portfolio['portfolio']['cash']['allocation']}, "alternatives": {client_portfolio['portfolio']['alternatives']['allocation']}, "return": {client_portfolio['ytd_return']}, "risk": "{client_portfolio['risk_profile']}" }},
    "simulated": {{ "equity": 0, "fixed_income": 0, "cash": 0, "alternatives": 0, "return": 0, "risk": "" }},
    "analysis": "string rationale",
    "compliance_status": "PASS/FAIL/WARNING",
    "compliance_details": "string"
}}

JSON only. No other text."""

    answer_json, metrics = call_llama("You are a financial simulation engine.", [{"role": "user", "content": prompt}])
    save_metrics("scenario_simulation", metrics)
    
    try:
        # Clean potential markdown wrapping from AI
        clean_json = answer_json.replace('```json', '').replace('```', '').strip()
        simulation_data = json.loads(clean_json)
        return {
            "statusCode": 200, "headers": CORS_HEADERS,
            "body": json.dumps(simulation_data)
        }
    except Exception as e:
        return {
            "statusCode": 500, "headers": CORS_HEADERS,
            "body": json.dumps({"error": f"Failed to parse simulation: {str(e)}", "raw": answer_json})
        }


def handle_dashboard_data(body: dict) -> dict:
    """Aggregates book-wide data and generates proactive AI insights."""
    total_aum = sum(c["aum"] for c in PORTFOLIO_DATA["clients"])
    avg_return = sum(c["ytd_return"] for c in PORTFOLIO_DATA["clients"]) / len(PORTFOLIO_DATA["clients"])
    
    # Generate Proactive Insights via AI
    book_summary = "\n".join([
        f"- {c['name']}: ${c['aum']:,} | YTD: {c['ytd_return']}% | Risk: {c['risk_profile']}"
        for c in PORTFOLIO_DATA["clients"]
    ])
    
    prompt = f"""You are a senior investment strategist.
Analyze this advisor's book of business and provide 3 high-impact, proactive insights for today.

BOOK SUMMARY:
{book_summary}

TASK:
Identify rebalancing needs, risk concentrations, or client engagement opportunities.
Format each insight as a JSON object inside an array:
[
  {{ "type": "warning/info/success", "text": "Short actionable insight", "client": "Name" }},
  ...
]

JSON only."""

    answer_json, metrics = call_llama("You are a proactive advisor concierge.", [{"role": "user", "content": prompt}])
    save_metrics("dashboard_insights", metrics)
    
    try:
        clean_json = answer_json.replace('```json', '').replace('```', '').strip()
        insights = json.loads(clean_json)
        return {
            "statusCode": 200, "headers": CORS_HEADERS,
            "body": json.dumps({
                "total_aum": f"${total_aum/1000000:.1f}M",
                "avg_return": f"{avg_return:.1f}%",
                "client_count": len(PORTFOLIO_DATA["clients"]),
                "insights": insights
            })
        }
    except Exception as e:
        return {
            "statusCode": 200, "headers": CORS_HEADERS,
            "body": json.dumps({
                "total_aum": f"${total_aum/1000000:.1f}M",
                "avg_return": f"{avg_return:.1f}%",
                "client_count": len(PORTFOLIO_DATA["clients"]),
                "insights": [
                    {"type": "info", "text": "Review today's top research reports for market shifts.", "client": "All"},
                    {"type": "warning", "text": "Check equity concentration in aggressive portfolios.", "client": "Rahul Mehta"}
                ]
            })
        }


def lambda_handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}
    try:
        path = event.get("path", "/chat")
        if path == "/health":
            return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"status": "active"})}
            
        body = json.loads(event.get("body", "{}"))
        if path == "/client360":
            return handle_client360(body)
        elif path == "/simulate":
            return handle_scenario_simulation(body)
        elif path == "/dashboard":
            return handle_dashboard_data(body)
        else:
            return handle_portfolio_chat(body)
    except Exception as e:
        return {
            "statusCode": 500, "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }