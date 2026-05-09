import json
import boto3
import os
from datetime import datetime

# ── Bedrock client ────────────────────────────────────────────────────────────
MODEL_ID = "us.meta.llama3-1-8b-instruct-v1:0"
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

# DynamoDB table name (we'll create this on AWS next)
SESSION_TABLE = "advisor-ai-sessions"

# ── Mock portfolio data (embedded so Lambda is self-contained) ────────────────
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

SYSTEM_PROMPT = """You are an expert AI financial advisor assistant for a broker-dealer firm.
You have real-time client portfolio data. Be concise, professional, and specific with numbers.
Always mention values, percentages, and changes. Flag risks clearly. Suggest actionable next steps."""

# ── Helper: find client by name ─────────────────────────────────────────────────
def find_client(name: str):
    name_lower = name.lower()
    for c in PORTFOLIO_DATA["clients"]:
        if name_lower in c["name"].lower():
            return c
    return None

# ── Helper: build portfolio context string ─────────────────────────────────────
def build_context(question: str) -> str:
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
•⁠  ⁠Equity: {c['portfolio']['equity']['allocation']}% = ${c['portfolio']['equity']['value']:,} (Day: {c['portfolio']['equity']['day_change']}%)
•⁠  ⁠Fixed Income: {c['portfolio']['fixed_income']['allocation']}% = ${c['portfolio']['fixed_income']['value']:,} (Day: {c['portfolio']['fixed_income']['day_change']}%)
•⁠  ⁠Cash: {c['portfolio']['cash']['allocation']}% = ${c['portfolio']['cash']['value']:,}
•⁠  ⁠Alternatives: {c['portfolio']['alternatives']['allocation']}% = ${c['portfolio']['alternatives']['value']:,}
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

# ── Helper: get + save session history in DynamoDB ────────────────────────────
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

# ── Helper: call Bedrock with conversation history ─────────────────────────────
def call_bedrock(messages: list) -> str:
    conversation = ""
    for msg in messages:
        role = "user" if msg["role"] == "user" else "assistant"
        conversation += f"<|start_header_id|>{role}<|end_header_id|>\n{msg['content']}\n<|eot_id|>"

    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{SYSTEM_PROMPT}
<|eot_id|>{conversation}<|start_header_id|>assistant<|end_header_id|>"""

    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 1000,
        "temperature": 0.7,
        "top_p": 0.9
    })
    response = bedrock.invoke_model(modelId=MODEL_ID, body=body)
    result = json.loads(response["body"].read())
    return result["generation"].strip()

# ── CORS headers for API Gateway ─────────────────────────────────────────────
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
    "Content-Type": "application/json"
}

# ── MAIN Lambda handler ───────────────────────────────────────────────────────
def lambda_handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    try:
        body = json.loads(event.get("body", "{}"))
        question = body.get("question", "").strip()
        session_id = body.get("session_id", "default-session")

        if not question:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Question is required"})
            }

        history = get_session(session_id)
        context_data = build_context(question)
        user_message = f"PORTFOLIO DATA:\n{context_data}\n\nQUESTION: {question}"

        history.append({"role": "user", "content": user_message})
        answer = call_bedrock(history)
        history.append({"role": "assistant", "content": answer})
        save_session(session_id, history)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "answer": answer,
                "session_id": session_id,
                "turn": len(history) // 2
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }
