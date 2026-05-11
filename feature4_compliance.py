import json
import boto3
from datetime import datetime, timezone

# ── Compliance Rules ───────────────────────────────────────────────────────────
COMPLIANCE_RULES = [
    {
        "id": "RULE-001",
        "name": "Equity Concentration Risk",
        "description": "Equity allocation exceeds maximum for risk profile",
        "check": lambda client, portfolio: (
            portfolio["equity"]["allocation"] > 70
            and client["risk_profile"] == "Conservative"
        ),
        "severity": "HIGH",
        "action": "Immediate rebalancing required. Reduce equity to max 40% for Conservative profile."
    },
    {
        "id": "RULE-002",
        "name": "Aggressive Equity Overweight",
        "description": "Equity allocation exceeds 85% even for aggressive profiles",
        "check": lambda client, portfolio: (
            portfolio["equity"]["allocation"] > 85
        ),
        "severity": "MEDIUM",
        "action": "Review equity concentration. Even aggressive profiles should maintain some diversification."
    },
    {
        "id": "RULE-003",
        "name": "Cash Drag",
        "description": "Excessive cash allocation reducing returns",
        "check": lambda client, portfolio: (
            portfolio["cash"]["allocation"] > 20
        ),
        "severity": "LOW",
        "action": "Review idle cash. Consider deploying into suitable instruments per client risk profile."
    },
    {
        "id": "RULE-004",
        "name": "KYC Refresh Required",
        "description": "Client has pending KYC compliance flag",
        "check": lambda client, portfolio: (
            len(client.get("compliance_flags", [])) > 0
        ),
        "severity": "HIGH",
        "action": "Complete KYC refresh before processing any new transactions."
    },
    {
        "id": "RULE-005",
        "name": "Fixed Income Underweight",
        "description": "Conservative client has insufficient fixed income allocation",
        "check": lambda client, portfolio: (
            portfolio["fixed_income"]["allocation"] < 40
            and client["risk_profile"] == "Conservative"
        ),
        "severity": "MEDIUM",
        "action": "Increase fixed income allocation to minimum 40% for Conservative profile."
    },
    {
        "id": "RULE-006",
        "name": "Large Single Day Loss",
        "description": "Portfolio experiencing significant single day loss",
        "check": lambda client, portfolio: (
            portfolio["equity"]["day_change"] < -3.0
        ),
        "severity": "HIGH",
        "action": "Alert advisor immediately. Review stop-loss triggers and client communication."
    },
]

# ── Mock data (same as lambda_handler) ────────────────────────────────────────
PORTFOLIO_DATA = {
  "clients": [
    {
      "id": "C001", "name": "Priya Sharma", "risk_profile": "Moderate",
      "aum": 850000, "ytd_return": 12.4,
      "portfolio": {
        "equity": {"allocation": 55, "value": 467500, "day_change": 1.2},
        "fixed_income": {"allocation": 30, "value": 255000, "day_change": -0.3},
        "cash": {"allocation": 10, "value": 85000, "day_change": 0},
        "alternatives": {"allocation": 5, "value": 42500, "day_change": 0.8}
      },
      "compliance_flags": []
    },
    {
      "id": "C002", "name": "Rahul Mehta", "risk_profile": "Aggressive",
      "aum": 2100000, "ytd_return": 22.7,
      "portfolio": {
        "equity": {"allocation": 80, "value": 1680000, "day_change": 2.3},
        "fixed_income": {"allocation": 10, "value": 210000, "day_change": -0.1},
        "cash": {"allocation": 5, "value": 105000, "day_change": 0},
        "alternatives": {"allocation": 5, "value": 105000, "day_change": 1.5}
      },
      "compliance_flags": ["Large cash inflow - KYC refresh required"]
    },
    {
      "id": "C003", "name": "Anita Desai", "risk_profile": "Conservative",
      "aum": 450000, "ytd_return": 6.1,
      "portfolio": {
        "equity": {"allocation": 25, "value": 112500, "day_change": 0.4},
        "fixed_income": {"allocation": 60, "value": 270000, "day_change": -0.2},
        "cash": {"allocation": 12, "value": 54000, "day_change": 0},
        "alternatives": {"allocation": 3, "value": 13500, "day_change": 0.2}
      },
      "compliance_flags": []
    }
  ]
}

# ── CloudWatch logger ──────────────────────────────────────────────────────────
cloudwatch = boto3.client("logs", region_name="us-east-1")
LOG_GROUP = "/advisor-ai/compliance"
LOG_STREAM = "compliance-alerts"

def log_to_cloudwatch(client_name: str, violations: list):
    """Log compliance violations to CloudWatch for audit trail."""
    try:
        # Ensure log group exists
        try:
            cloudwatch.create_log_group(logGroupName=LOG_GROUP)
        except Exception:
            pass

        # Ensure log stream exists
        try:
            cloudwatch.create_log_stream(
                logGroupName=LOG_GROUP,
                logStreamName=LOG_STREAM
            )
        except Exception:
            pass

        # Log the event
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client": client_name,
            "violations_count": len(violations),
            "violations": [
                {
                    "rule_id": v["rule_id"],
                    "rule_name": v["rule_name"],
                    "severity": v["severity"]
                }
                for v in violations
            ]
        }

        cloudwatch.put_log_events(
            logGroupName=LOG_GROUP,
            logStreamName=LOG_STREAM,
            logEvents=[{
                "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                "message": json.dumps(log_entry)
            }]
        )
        return True
    except Exception as e:
        print(f"CloudWatch logging failed: {e}")
        return False


def run_compliance_check(client_name: str = None) -> dict:
    """
    Run compliance checks on all clients or a specific client.
    Returns violations found with severity levels.
    """
    results = []

    clients_to_check = PORTFOLIO_DATA["clients"]
    if client_name:
        clients_to_check = [
            c for c in PORTFOLIO_DATA["clients"]
            if client_name.lower() in c["name"].lower()
        ]

    for client in clients_to_check:
        portfolio = client["portfolio"]
        client_violations = []

        for rule in COMPLIANCE_RULES:
            try:
                if rule["check"](client, portfolio):
                    client_violations.append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "description": rule["description"],
                        "severity": rule["severity"],
                        "action": rule["action"]
                    })
            except Exception:
                pass

        # Log to CloudWatch if violations found
        if client_violations:
            log_to_cloudwatch(client["name"], client_violations)

        results.append({
            "client_id": client["id"],
            "client_name": client["name"],
            "risk_profile": client["risk_profile"],
            "aum": client["aum"],
            "violations": client_violations,
            "violation_count": len(client_violations),
            "status": "ALERT" if any(v["severity"] == "HIGH" for v in client_violations)
                      else "WARNING" if client_violations
                      else "CLEAN",
            "checked_at": datetime.now(timezone.utc).isoformat()
        })

    # Summary
    total_violations = sum(r["violation_count"] for r in results)
    high_severity = sum(
        1 for r in results
        for v in r["violations"]
        if v["severity"] == "HIGH"
    )

    return {
        "summary": {
            "total_clients_checked": len(results),
            "total_violations": total_violations,
            "high_severity_count": high_severity,
            "checked_at": datetime.now(timezone.utc).isoformat()
        },
        "results": results
    }


# ── Quick test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("COMPLIANCE CHECK — ALL CLIENTS")
    print("=" * 60)

    result = run_compliance_check()
    print(f"\nSummary:")
    print(f"  Total clients: {result['summary']['total_clients_checked']}")
    print(f"  Total violations: {result['summary']['total_violations']}")
    print(f"  High severity: {result['summary']['high_severity_count']}")

    for client_result in result["results"]:
        print(f"\n{'='*40}")
        print(f"Client: {client_result['client_name']} ({client_result['risk_profile']})")
        print(f"Status: {client_result['status']}")
        if client_result["violations"]:
            print("Violations:")
            for v in client_result["violations"]:
                print(f"  [{v['severity']}] {v['rule_name']}")
                print(f"    → {v['action']}")
        else:
            print("  No violations found ✓")
