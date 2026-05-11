import json
from bedrock_client import ask_llama

# Load client CRM data
with open("data/clients.json") as f:
    CLIENT_DATA = json.load(f)

SYSTEM_PROMPT = """You are an expert financial advisor assistant preparing meeting briefs.
Generate a comprehensive, professional meeting preparation brief.
Be specific, actionable, and concise. Use the exact data provided.
Format the brief clearly with sections. Focus on what the advisor needs to know."""

def get_client_by_name(name: str) -> dict:
    """Find client by name (case-insensitive partial match)."""
    name_lower = name.lower()
    for client in CLIENT_DATA["clients"]:
        if name_lower in client["name"].lower():
            return client
    return None

def generate_meeting_brief(client_name: str) -> dict:
    """Generate a full Client 360 meeting preparation brief."""

    client = get_client_by_name(client_name)
    if not client:
        return {"error": f"Client '{client_name}' not found."}

    # Build rich context from CRM data
    life_events = "\n".join([f"  - {e}" for e in client["life_events"]])
    goals = "\n".join([f"  - {g}" for g in client["goals"]])
    concerns = "\n".join([f"  - {c}" for c in client["concerns"]])
    opportunities = "\n".join([f"  - {o}" for o in client["cross_sell_opportunities"]])
    flags = "\n".join([f"  - {f}" for f in client["compliance_flags"]]) if client["compliance_flags"] else "  - None"

    context = f"""
CLIENT 360 DATA:

Basic Info:
- Name: {client['name']}
- Age: {client['age']}
- Occupation: {client['occupation']}
- Client Since: {client['since']}
- Risk Profile: {client['risk_profile']}
- AUM: ${client['aum']:,}

Meeting Details:
- Last Meeting: {client['last_meeting']}
- Next Meeting: {client['next_meeting']}

Last Interaction Notes:
{client['last_interaction_notes']}

Life Events:
{life_events}

Financial Goals:
{goals}

Current Concerns:
{concerns}

Cross-sell / Upsell Opportunities:
{opportunities}

Compliance Flags:
{flags}
"""

    user_message = f"""
{context}

Generate a professional meeting preparation brief for the advisor meeting with {client['name']}.

Include these sections:
1. CLIENT SNAPSHOT (key facts in 3-4 bullet points)
2. MEETING AGENDA (3 suggested talking points based on their concerns and life events)
3. PORTFOLIO ACTIONS (specific rebalancing or investment suggestions)
4. CROSS-SELL OPPORTUNITIES (ranked by priority with reasoning)
5. COMPLIANCE ALERTS (any flags to be aware of)
6. SUGGESTED OPENING LINE (a personalized conversation starter)
"""

    brief = ask_llama(SYSTEM_PROMPT, user_message)

    return {
        "client_name": client["name"],
        "meeting_time": client["next_meeting"],
        "aum": client["aum"],
        "risk_profile": client["risk_profile"],
        "compliance_flags": client["compliance_flags"],
        "brief": brief
    }


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TEST 1: Meeting prep for Priya Sharma")
    print("=" * 60)
    result = generate_meeting_brief("Priya")
    print(f"Client: {result['client_name']}")
    print(f"Meeting: {result['meeting_time']}")
    print(f"AUM: ${result['aum']:,}")
    print(f"Compliance Flags: {result['compliance_flags']}")
    print("\nBRIEF:")
    print(result["brief"])

    print("\n" + "=" * 60)
    print("TEST 2: Meeting prep for Rahul Mehta")
    print("=" * 60)
    result2 = generate_meeting_brief("Rahul")
    print(f"Client: {result2['client_name']}")
    print(f"Compliance Flags: {result2['compliance_flags']}")
    print("\nBRIEF:")
    print(result2["brief"])