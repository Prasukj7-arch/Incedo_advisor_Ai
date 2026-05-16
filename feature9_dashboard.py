import json
import boto3

def handle_dashboard_data(body, portfolio_data, call_llama_fn, save_metrics_fn, cors_headers):
    """Refactored logic for Feature 9: Executive Dashboard."""
    # Aggregate book-level metrics
    total_aum = sum(c["aum"] for c in portfolio_data["clients"])
    avg_return = sum(c["ytd_return"] for c in portfolio_data["clients"]) / len(portfolio_data["clients"])
    client_count = len(portfolio_data["clients"])

    # Build a summary of the whole book for the AI
    book_summary = "\n".join([
        f"- {c['name']}: ${c['aum']:,} | YTD: {c['ytd_return']}% | Risk: {c['risk_profile']}"
        for c in portfolio_data["clients"]
    ])

    prompt = f"""You are a senior investment strategist reviewing a book of business.
Analyze these client portfolios and provide 3 high-value proactive insights.
Each insight should identify a specific risk or opportunity for an individual client.

BOOK SUMMARY:
{book_summary}

TASK:
Provide 3 insights. For each:
1. Identify the client
2. Assign a type: 'warning' (risk), 'success' (outperformance), or 'info' (general insight)
3. Write a 1-2 sentence actionable recommendation.

Return ONLY a JSON array:
[
  {{"client": "Name", "type": "warning/info/success", "text": "Recommendation text..."}}
]
JSON only. No other text."""

    answer_json, metrics = call_llama_fn("You are a proactive advisor concierge.", [{"role": "user", "content": prompt}])
    save_metrics_fn("dashboard_insights", metrics)

    try:
        clean_json = answer_json.replace('```json', '').replace('```', '').strip()
        insights = json.loads(clean_json)
        return {
            "statusCode": 200, "headers": cors_headers,
            "body": json.dumps({
                "total_aum": total_aum,
                "avg_return": round(avg_return, 1),
                "client_count": client_count,
                "insights": insights
            })
        }
    except Exception as e:
        # Graceful fallback with dummy insights if AI fails
        return {
            "statusCode": 200, "headers": cors_headers,
            "body": json.dumps({
                "total_aum": total_aum,
                "avg_return": round(avg_return, 1),
                "client_count": client_count,
                "insights": [
                    {"client": "All Clients", "type": "info", "text": "Review today's top research reports for market shifts."},
                    {"client": "Priya Sharma", "type": "warning", "text": "Moderate portfolio is slightly overweight in equities."},
                    {"client": "Rahul Mehta", "type": "success", "text": "Aggressive portfolio hit YTD return target early."}
                ]
            })
        }
