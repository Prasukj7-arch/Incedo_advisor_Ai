import json
from bedrock_client import ask_llama as ask_claude
# Load mock portfolio data
with open("data/portfolios.json") as f:
    PORTFOLIO_DATA = json.load(f)

SYSTEM_PROMPT = """You are an expert AI financial advisor assistant working for a broker-dealer firm.
You have access to real-time client portfolio data. When answering:
- Be concise, professional, and specific with numbers
- Always mention portfolio values, percentages, and day changes
- Flag any risks clearly
- Suggest actionable next steps when relevant
- Format responses clearly with sections when helpful"""

def get_client_by_name(name: str) -> dict:
    """Find a client by name (case-insensitive partial match)."""
    name_lower = name.lower()
    for client in PORTFOLIO_DATA["clients"]:
        if name_lower in client["name"].lower():
            return client
    return None

def get_all_clients_summary() -> str:
    """Get a summary string of all clients for the advisor's book."""
    lines = []
    total_aum = 0
    for c in PORTFOLIO_DATA["clients"]:
        total_aum += c["aum"]
        lines.append(
            f"- {c['name']} | AUM: ${c['aum']:,} | Risk: {c['risk_profile']} | "
            f"YTD Return: {c['ytd_return']}% | "
            f"Equity: {c['portfolio']['equity']['allocation']}% | "
            f"Fixed Income: {c['portfolio']['fixed_income']['allocation']}%"
        )
    lines.append(f"\nTotal Book AUM: ${total_aum:,}")
    return "\n".join(lines)

def portfolio_chat(user_question: str) -> str:
    """Main chat function - answers advisor questions about portfolios."""

    # Check if question is about a specific client
    specific_client = None
    for client in PORTFOLIO_DATA["clients"]:
        if client["name"].split()[0].lower() in user_question.lower() or \
           client["name"].lower() in user_question.lower():
            specific_client = client
            break

    if specific_client:
        # Build detailed context for specific client
        c = specific_client
        holdings_text = "\n".join([
            f"  - {h['ticker']}: ${h['value']:,} (Day change: {h['day_change']}%)"
            for h in c["top_holdings"]
        ])
        context = f"""
CLIENT PORTFOLIO DATA:
Name: {c['name']}
Risk Profile: {c['risk_profile']}
Total AUM: ${c['aum']:,}
YTD Return: {c['ytd_return']}%
Last Rebalanced: {c['last_rebalanced']}

ALLOCATION:
- Equity: {c['portfolio']['equity']['allocation']}% = ${c['portfolio']['equity']['value']:,} (Day: {c['portfolio']['equity']['day_change']}%)
- Fixed Income: {c['portfolio']['fixed_income']['allocation']}% = ${c['portfolio']['fixed_income']['value']:,} (Day: {c['portfolio']['fixed_income']['day_change']}%)
- Cash: {c['portfolio']['cash']['allocation']}% = ${c['portfolio']['cash']['value']:,}
- Alternatives: {c['portfolio']['alternatives']['allocation']}% = ${c['portfolio']['alternatives']['value']:,}

TOP HOLDINGS:
{holdings_text}
"""
    else:
        # General question about the whole book
        context = f"""
ADVISOR'S FULL BOOK SUMMARY:
{get_all_clients_summary()}
"""

    user_message = f"""
{context}

ADVISOR QUESTION: {user_question}
"""
    return ask_claude(SYSTEM_PROMPT, user_message)


# ── Quick test ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TEST 1: Full book summary")
    print("=" * 60)
    print(portfolio_chat("Summarize my entire book performance today"))

    print("\n" + "=" * 60)
    print("TEST 2: Specific client")
    print("=" * 60)
    print(portfolio_chat("What are the top risks in Rahul's portfolio?"))

    print("\n" + "=" * 60)
    print("TEST 3: Rebalancing suggestion")
    print("=" * 60)
    print(portfolio_chat("Does Priya's portfolio need rebalancing?"))