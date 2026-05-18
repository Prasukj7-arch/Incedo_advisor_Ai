"""
Advisor AI — Automated Test Suite
Run with: pytest tests/test_advisor_ai.py -v
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal


# ── Compliance Engine Tests ────────────────────────────────────────────────────

from feature4_compliance import run_compliance_check, check_compliance, COMPLIANCE_RULES


class TestComplianceRules:
    """Unit tests for each individual compliance rule."""

    CONSERVATIVE_CLIENT = {
        "id": "T001", "name": "Test Conservative", "risk_profile": "Conservative",
        "compliance_flags": [],
        "portfolio": {
            "equity":       {"allocation": 75, "value": 75000, "day_change": -1.0},
            "fixed_income": {"allocation": 20, "value": 20000, "day_change": 0.0},
            "cash":         {"allocation": 5,  "value": 5000,  "day_change": 0.0},
            "alternatives": {"allocation": 0,  "value": 0,     "day_change": 0.0},
        }
    }

    AGGRESSIVE_CLIENT = {
        "id": "T002", "name": "Test Aggressive", "risk_profile": "Aggressive",
        "compliance_flags": [],
        "portfolio": {
            "equity":       {"allocation": 90, "value": 900000, "day_change": 2.0},
            "fixed_income": {"allocation": 5,  "value": 50000,  "day_change": 0.0},
            "cash":         {"allocation": 5,  "value": 50000,  "day_change": 0.0},
            "alternatives": {"allocation": 0,  "value": 0,      "day_change": 0.0},
        }
    }

    KYC_CLIENT = {
        "id": "T003", "name": "Test KYC", "risk_profile": "Moderate",
        "compliance_flags": ["Large cash inflow - KYC refresh required"],
        "portfolio": {
            "equity":       {"allocation": 50, "value": 500000, "day_change": 0.0},
            "fixed_income": {"allocation": 30, "value": 300000, "day_change": 0.0},
            "cash":         {"allocation": 20, "value": 200000, "day_change": 0.0},
            "alternatives": {"allocation": 0,  "value": 0,      "day_change": 0.0},
        }
    }

    def test_rule001_equity_concentration_conservative_triggers(self):
        """RULE-001: Conservative client with >70% equity should trigger."""
        client = self.CONSERVATIVE_CLIENT
        rule = next(r for r in COMPLIANCE_RULES if r["id"] == "RULE-001")
        assert rule["check"](client, client["portfolio"]) is True

    def test_rule001_equity_concentration_moderate_does_not_trigger(self):
        """RULE-001: Moderate client with 55% equity should NOT trigger."""
        client = {**self.CONSERVATIVE_CLIENT, "risk_profile": "Moderate"}
        rule = next(r for r in COMPLIANCE_RULES if r["id"] == "RULE-001")
        assert rule["check"](client, client["portfolio"]) is False

    def test_rule002_aggressive_overweight_triggers(self):
        """RULE-002: Any client with >85% equity should trigger."""
        client = self.AGGRESSIVE_CLIENT
        rule = next(r for r in COMPLIANCE_RULES if r["id"] == "RULE-002")
        assert rule["check"](client, client["portfolio"]) is True

    def test_rule002_aggressive_overweight_does_not_trigger_at_80pct(self):
        """RULE-002: 80% equity should NOT trigger the overweight rule."""
        portfolio = {**self.AGGRESSIVE_CLIENT["portfolio"],
                     "equity": {"allocation": 80, "value": 800000, "day_change": 0.0}}
        rule = next(r for r in COMPLIANCE_RULES if r["id"] == "RULE-002")
        assert rule["check"](self.AGGRESSIVE_CLIENT, portfolio) is False

    def test_rule003_cash_drag_triggers(self):
        """RULE-003: Cash > 20% should trigger."""
        portfolio = {**self.KYC_CLIENT["portfolio"],
                     "cash": {"allocation": 25, "value": 250000, "day_change": 0.0}}
        rule = next(r for r in COMPLIANCE_RULES if r["id"] == "RULE-003")
        assert rule["check"](self.KYC_CLIENT, portfolio) is True

    def test_rule003_cash_drag_does_not_trigger_at_15pct(self):
        """RULE-003: Cash at 15% should NOT trigger."""
        portfolio = {**self.KYC_CLIENT["portfolio"],
                     "cash": {"allocation": 15, "value": 150000, "day_change": 0.0}}
        rule = next(r for r in COMPLIANCE_RULES if r["id"] == "RULE-003")
        assert rule["check"](self.KYC_CLIENT, portfolio) is False

    def test_rule004_kyc_refresh_triggers_when_flags_present(self):
        """RULE-004: Client with compliance_flags should trigger KYC rule."""
        rule = next(r for r in COMPLIANCE_RULES if r["id"] == "RULE-004")
        assert rule["check"](self.KYC_CLIENT, self.KYC_CLIENT["portfolio"]) is True

    def test_rule004_kyc_refresh_does_not_trigger_when_clean(self):
        """RULE-004: Client with no flags should NOT trigger KYC rule."""
        rule = next(r for r in COMPLIANCE_RULES if r["id"] == "RULE-004")
        assert rule["check"](self.AGGRESSIVE_CLIENT, self.AGGRESSIVE_CLIENT["portfolio"]) is False

    def test_rule005_fixed_income_underweight_triggers(self):
        """RULE-005: Conservative client with <40% fixed income should trigger."""
        rule = next(r for r in COMPLIANCE_RULES if r["id"] == "RULE-005")
        assert rule["check"](self.CONSERVATIVE_CLIENT, self.CONSERVATIVE_CLIENT["portfolio"]) is True

    def test_rule006_large_single_day_loss_triggers(self):
        """RULE-006: Equity day_change < -3% should trigger."""
        portfolio = {**self.CONSERVATIVE_CLIENT["portfolio"],
                     "equity": {"allocation": 25, "value": 25000, "day_change": -4.5}}
        rule = next(r for r in COMPLIANCE_RULES if r["id"] == "RULE-006")
        assert rule["check"](self.CONSERVATIVE_CLIENT, portfolio) is True


class TestRunComplianceCheck:
    """Integration tests for the run_compliance_check function."""

    def test_returns_all_3_clients_when_no_filter(self):
        result = run_compliance_check()
        assert result["summary"]["total_clients_checked"] == 3

    def test_summary_keys_present(self):
        result = run_compliance_check()
        assert "total_clients_checked" in result["summary"]
        assert "total_violations" in result["summary"]
        assert "high_severity_count" in result["summary"]
        assert "checked_at" in result["summary"]

    def test_rahul_mehta_has_kyc_violation(self):
        """Rahul Mehta has a KYC flag, so he must have at least 1 violation."""
        result = run_compliance_check("Rahul")
        assert result["summary"]["total_clients_checked"] == 1
        assert result["results"][0]["violation_count"] >= 1

    def test_priya_sharma_is_clean(self):
        """Priya Sharma (Moderate, balanced portfolio, no flags) should be CLEAN."""
        result = run_compliance_check("Priya")
        assert result["summary"]["total_clients_checked"] == 1
        assert result["results"][0]["status"] == "CLEAN"

    def test_each_result_has_required_fields(self):
        result = run_compliance_check()
        for r in result["results"]:
            assert "client_id" in r
            assert "client_name" in r
            assert "status" in r
            assert r["status"] in ("CLEAN", "WARNING", "ALERT")
            assert "violations" in r
            assert isinstance(r["violations"], list)

    def test_filter_returns_single_client(self):
        result = run_compliance_check("Anita")
        assert result["summary"]["total_clients_checked"] == 1
        assert result["results"][0]["client_name"] == "Anita Desai"

    def test_unknown_client_returns_empty(self):
        result = run_compliance_check("NoSuchClient99")
        assert result["summary"]["total_clients_checked"] == 0
        assert result["results"] == []


class TestCheckCompliance:
    """Unit tests for check_compliance (AI response gating)."""

    def test_clean_client_returns_no_violations(self):
        clean_client = {
            "id": "CX", "name": "Clean Client", "risk_profile": "Moderate",
            "compliance_flags": [],
            "portfolio": {
                "equity":       {"allocation": 50, "value": 500, "day_change": 0.0},
                "fixed_income": {"allocation": 40, "value": 400, "day_change": 0.0},
                "cash":         {"allocation": 10, "value": 100, "day_change": 0.0},
                "alternatives": {"allocation": 0,  "value": 0,   "day_change": 0.0},
            }
        }
        violations = check_compliance(clean_client, "Some AI recommendation")
        assert violations == []

    def test_flagged_client_returns_violations(self):
        flagged_client = {
            "id": "CY", "name": "Flagged Client", "risk_profile": "Moderate",
            "compliance_flags": ["KYC required"],
            "portfolio": {
                "equity":       {"allocation": 50, "value": 500, "day_change": 0.0},
                "fixed_income": {"allocation": 40, "value": 400, "day_change": 0.0},
                "cash":         {"allocation": 10, "value": 100, "day_change": 0.0},
                "alternatives": {"allocation": 0,  "value": 0,   "day_change": 0.0},
            }
        }
        violations = check_compliance(flagged_client, "Some AI recommendation")
        assert len(violations) >= 1


# ── Lambda Handler Routing Tests ───────────────────────────────────────────────

class TestLambdaHandlerRouting:
    """Test that the Lambda dispatcher routes paths correctly."""

    def _make_event(self, path, body=None, method="POST"):
        return {
            "httpMethod": method,
            "path": path,
            "body": json.dumps(body or {})
        }

    def test_options_preflight_returns_200(self):
        import lambda_handler
        event = {"httpMethod": "OPTIONS", "path": "/chat", "body": ""}
        result = lambda_handler.lambda_handler(event, None)
        assert result["statusCode"] == 200

    def test_health_check_returns_active(self):
        import lambda_handler
        event = self._make_event("/health", method="GET")
        event["httpMethod"] = "GET"
        result = lambda_handler.lambda_handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["status"] == "active"

    def test_null_body_does_not_crash(self):
        """Lambda must handle null body gracefully (API Gateway quirk)."""
        import lambda_handler
        event = {"httpMethod": "POST", "path": "/chat", "body": None}
        # Should not raise — must return a valid dict response
        result = lambda_handler.lambda_handler(event, None)
        assert "statusCode" in result

    def test_empty_string_body_does_not_crash(self):
        """Empty string body should also be handled gracefully."""
        import lambda_handler
        event = {"httpMethod": "POST", "path": "/chat", "body": ""}
        result = lambda_handler.lambda_handler(event, None)
        assert "statusCode" in result


# ── Dashboard Data Tests ───────────────────────────────────────────────────────

class TestDashboardData:
    """Test feature9_dashboard calculations."""

    MOCK_PORTFOLIO = {
        "clients": [
            {"name": "Client A", "aum": 1000000, "ytd_return": 10.0, "risk_profile": "Moderate"},
            {"name": "Client B", "aum": 2000000, "ytd_return": 20.0, "risk_profile": "Aggressive"},
        ]
    }
    CORS = {"Content-Type": "application/json"}

    def test_avg_return_calculation(self):
        """Average return must be the arithmetic mean of all clients."""
        from feature9_dashboard import handle_dashboard_data

        def mock_llama(system, messages):
            return '[{"client":"Client A","type":"info","text":"Test insight."}]', {
                "input_tokens": 10, "output_tokens": 5,
                "total_tokens": 15, "latency_ms": 100,
                "cost_usd": 0.000003, "model_id": "test",
                "timestamp": "2026-01-01T00:00:00"
            }

        result = handle_dashboard_data({}, self.MOCK_PORTFOLIO, mock_llama, lambda f, m: None, self.CORS)
        body = json.loads(result["body"])
        assert body["avg_return"] == 15.0

    def test_total_aum_calculation(self):
        """Total AUM must be sum of all client AUMs."""
        from feature9_dashboard import handle_dashboard_data

        def mock_llama(system, messages):
            return '[{"client":"A","type":"info","text":"X"}]', {
                "input_tokens": 10, "output_tokens": 5,
                "total_tokens": 15, "latency_ms": 100,
                "cost_usd": 0.000003, "model_id": "test",
                "timestamp": "2026-01-01T00:00:00"
            }

        result = handle_dashboard_data({}, self.MOCK_PORTFOLIO, mock_llama, lambda f, m: None, self.CORS)
        body = json.loads(result["body"])
        assert body["total_aum"] == 3000000

    def test_dashboard_fallback_on_bad_json(self):
        """If Llama returns non-JSON, dashboard must use fallback insights."""
        from feature9_dashboard import handle_dashboard_data

        def bad_llama(system, messages):
            return "This is not JSON at all", {
                "input_tokens": 1, "output_tokens": 1,
                "total_tokens": 2, "latency_ms": 50,
                "cost_usd": 0.0, "model_id": "test",
                "timestamp": "2026-01-01T00:00:00"
            }

        result = handle_dashboard_data({}, self.MOCK_PORTFOLIO, bad_llama, lambda f, m: None, self.CORS)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert len(body["insights"]) == 3  # fallback always returns 3


# ── Revenue Feature Tests ──────────────────────────────────────────────────────

class TestRevenueFeature:
    """Test feature10_revenue input validation."""

    PORTFOLIO = {"clients": [
        {"name": "Priya Sharma", "aum": 850000, "ytd_return": 12.4, "risk_profile": "Moderate",
         "portfolio": {"equity": {"allocation": 55}, "fixed_income": {"allocation": 30},
                       "cash": {"allocation": 10}, "alternatives": {"allocation": 5}}}
    ]}
    CRM = {"clients": [
        {"name": "Priya Sharma", "age": 42, "occupation": "Engineer", "risk_profile": "Moderate",
         "aum": 850000, "since": "2019-01-01",
         "life_events": ["Daughter going to college"], "goals": ["Retirement"],
         "concerns": ["Volatility"], "cross_sell_opportunities": ["NPS"]}
    ]}
    CORS = {"Content-Type": "application/json"}

    def test_missing_client_name_returns_400(self):
        from feature10_revenue import handle_revenue_opportunities
        result = handle_revenue_opportunities({}, self.PORTFOLIO, self.CRM, None, None, self.CORS)
        assert result["statusCode"] == 400

    def test_unknown_client_returns_404(self):
        from feature10_revenue import handle_revenue_opportunities
        result = handle_revenue_opportunities(
            {"client_name": "NonExistent"}, self.PORTFOLIO, self.CRM, None, None, self.CORS
        )
        assert result["statusCode"] == 404

    def test_valid_client_calls_llama(self):
        from feature10_revenue import handle_revenue_opportunities

        mock_calls = []
        def mock_llama(system, messages):
            mock_calls.append(True)
            return '[{"product":"NPS","priority":"HIGH","revenue_impact":"₹10k","rationale":"Test","compliance":"SUITABLE"}]', {
                "input_tokens": 10, "output_tokens": 10,
                "total_tokens": 20, "latency_ms": 100,
                "cost_usd": 0.0, "model_id": "test",
                "timestamp": "2026-01-01T00:00:00"
            }

        result = handle_revenue_opportunities(
            {"client_name": "Priya"}, self.PORTFOLIO, self.CRM, mock_llama, lambda f, m: None, self.CORS
        )
        assert result["statusCode"] == 200
        assert len(mock_calls) == 1


# ── Simulator Tests ────────────────────────────────────────────────────────────

class TestSimulator:
    """Test feature8_simulator input validation."""

    PORTFOLIO = {"clients": [
        {"name": "Rahul Mehta", "ytd_return": 22.7, "risk_profile": "Aggressive",
         "portfolio": {"equity": {"allocation": 80}, "fixed_income": {"allocation": 10},
                       "cash": {"allocation": 5}, "alternatives": {"allocation": 5}}}
    ]}
    CORS = {"Content-Type": "application/json"}

    def test_missing_params_returns_400(self):
        from feature8_simulator import handle_scenario_simulation
        result = handle_scenario_simulation({}, self.PORTFOLIO, None, None, self.CORS)
        assert result["statusCode"] == 400

    def test_unknown_client_returns_404(self):
        from feature8_simulator import handle_scenario_simulation
        result = handle_scenario_simulation(
            {"client_name": "Ghost", "scenario": "Move 10% to bonds"},
            self.PORTFOLIO, None, None, self.CORS
        )
        assert result["statusCode"] == 404
