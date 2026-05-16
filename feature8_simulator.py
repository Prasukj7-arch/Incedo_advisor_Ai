import json
import boto3
import time
from datetime import datetime

# Import data and shared functions from main handler
# (Note: In a real app we'd move data to a shared constants.py, 
# but for Lambda zipping we'll pass them in or import carefully)

def handle_scenario_simulation(body, portfolio_data, call_llama_fn, save_metrics_fn, cors_headers):
    """Refactored logic for Feature 8: Portfolio Scenario Simulator."""
    client_name = body.get("client_name", "").strip()
    scenario = body.get("scenario", "").strip()

    if not client_name or not scenario:
        return {"statusCode": 400, "headers": cors_headers, 
                "body": json.dumps({"error": "client_name and scenario are required"})}

    client = next((c for c in portfolio_data["clients"] if client_name.lower() in c["name"].lower()), None)
    if not client:
        return {"statusCode": 404, "headers": cors_headers,
                "body": json.dumps({"error": f"Client '{client_name}' not found"})}

    current_allocation = client["portfolio"]
    current_return = client["ytd_return"]
    current_risk = client["risk_profile"]

    prompt = f"""You are a portfolio simulation engine. 
Analyze this client portfolio and the proposed 'What-If' scenario.

CLIENT: {client['name']}
CURRENT ALLOCATION:
- Equity: {current_allocation['equity']['allocation']}%
- Fixed Income: {current_allocation['fixed_income']['allocation']}%
- Cash: {current_allocation['cash']['allocation']}%
- Alternatives: {current_allocation['alternatives']['allocation']}%

SCENARIO: {scenario}

TASK:
1. Estimate the new allocation percentages after this scenario.
2. Estimate the new annual return percentage (current is {current_return}%).
3. Determine the new risk level (High, Medium, or Low).
4. Provide a 2-3 sentence impact analysis.
5. Check compliance (PASS/FAIL/WARNING) - e.g. Conservative profile should not be >70% Equity.

Return ONLY a JSON object:
{{
  "simulated_allocation": {{
    "equity": 0, "fixed_income": 0, "cash": 0, "alternatives": 0
  }},
  "simulated_return": 0.0,
  "simulated_risk": "Level",
  "impact_analysis": "Text",
  "compliance_status": "PASS/FAIL/WARNING"
}}
JSON only."""

    answer_json, metrics = call_llama_fn("You are a portfolio simulation engine.", [{"role": "user", "content": prompt}])
    save_metrics_fn("portfolio_simulation", metrics)

    try:
        clean_json = answer_json.replace('```json', '').replace('```', '').strip()
        sim_results = json.loads(clean_json)
        return {
            "statusCode": 200, "headers": cors_headers,
            "body": json.dumps({
                "current": {
                    "equity": current_allocation["equity"]["allocation"],
                    "fixed_income": current_allocation["fixed_income"]["allocation"],
                    "cash": current_allocation["cash"]["allocation"],
                    "alternatives": current_allocation["alternatives"]["allocation"],
                    "return": current_return,
                    "risk": current_risk
                },
                "simulated": {
                    "equity": sim_results["simulated_allocation"]["equity"],
                    "fixed_income": sim_results["simulated_allocation"]["fixed_income"],
                    "cash": sim_results["simulated_allocation"]["cash"],
                    "alternatives": sim_results["simulated_allocation"]["alternatives"],
                    "return": sim_results["simulated_return"],
                    "risk": sim_results["simulated_risk"]
                },
                "analysis": sim_results["impact_analysis"],
                "compliance_status": sim_results["compliance_status"]
            })
        }
    except Exception as e:
        return {
            "statusCode": 500, "headers": cors_headers,
            "body": json.dumps({"error": f"Failed to parse simulation: {str(e)}", "raw": answer_json})
        }
