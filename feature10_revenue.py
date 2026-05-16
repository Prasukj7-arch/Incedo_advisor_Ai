import json
import boto3

def handle_revenue_opportunities(body, portfolio_data, client_data, call_llama_fn, save_metrics_fn, cors_headers):
    """Refactored logic for Feature 10: Revenue Enablement."""
    client_name = body.get("client_name", "").strip()
    if not client_name:
        return {"statusCode": 400, "headers": cors_headers,
                "body": json.dumps({"error": "client_name is required"})}

    # Find in both datasets
    portfolio_client = next((c for c in portfolio_data["clients"] if client_name.lower() in c["name"].lower()), None)
    crm_client = next((c for c in client_data["clients"] if client_name.lower() in c["name"].lower()), None)

    if not portfolio_client or not crm_client:
        return {"statusCode": 404, "headers": cors_headers,
                "body": json.dumps({"error": f"Client '{client_name}' not found"})}

    life_events = "\n".join([f"  - {e}" for e in crm_client["life_events"]])
    goals = "\n".join([f"  - {g}" for g in crm_client["goals"]])
    concerns = "\n".join([f"  - {c}" for c in crm_client["concerns"]])
    existing_opps = "\n".join([f"  - {o}" for o in crm_client["cross_sell_opportunities"]])

    prompt = f"""You are a senior financial advisor revenue strategist.
Analyze this client and generate 4 ranked revenue opportunities.

CLIENT PROFILE:
- Name: {crm_client['name']} | Age: {crm_client['age']} | Risk: {crm_client['risk_profile']}
- AUM: ${crm_client['aum']:,} | Since: {crm_client['since']}
- Occupation: {crm_client['occupation']}

LIFE EVENTS:
{life_events}

GOALS:
{goals}

CONCERNS:
{concerns}

CURRENT PORTFOLIO:
- Equity: {portfolio_client['portfolio']['equity']['allocation']}%
- Fixed Income: {portfolio_client['portfolio']['fixed_income']['allocation']}%
- Cash: {portfolio_client['portfolio']['cash']['allocation']}%
- YTD Return: {portfolio_client['ytd_return']}%

EXISTING OPPORTUNITIES IDENTIFIED:
{existing_opps}

TASK:
Generate 4 ranked cross-sell/upsell opportunities. For each:
1. Recommend a specific financial product
2. Assign priority: HIGH, MEDIUM, or LOW
3. Estimate potential AUM/revenue impact
4. Give a short personalized rationale tied to their life events or goals
5. State if it is compliant with their risk profile

Return ONLY a JSON array:
[
  {{
    "product": "Product Name",
    "priority": "HIGH",
    "revenue_impact": "₹X lakh / year",
    "rationale": "Personalized reason based on their situation",
    "compliance": "SUITABLE"
  }}
]
JSON only. No other text."""

    answer_json, metrics = call_llama_fn("You are a revenue strategy advisor.", [{"role": "user", "content": prompt}])
    save_metrics_fn("revenue_opportunities", metrics)

    try:
        clean_json = answer_json.replace('```json', '').replace('```', '').strip()
        opportunities = json.loads(clean_json)
        return {
            "statusCode": 200, "headers": cors_headers,
            "body": json.dumps({
                "client_name": crm_client["name"],
                "aum": crm_client["aum"],
                "risk_profile": crm_client["risk_profile"],
                "opportunities": opportunities
            })
        }
    except Exception as e:
        return {
            "statusCode": 500, "headers": cors_headers,
            "body": json.dumps({"error": f"Failed to parse opportunities: {str(e)}", "raw": answer_json})
        }
