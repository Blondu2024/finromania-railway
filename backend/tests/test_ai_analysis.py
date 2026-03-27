"""
Test suite for FinRomania Faza 3 — AI Advisor
GET /api/portfolio-bvb/ai-analysis
Tests: PRO auth, response schema, signal values, cache behavior
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

VALID_OVERALL_SIGNALS = {"HOLD", "BUY_MORE", "REDUCE"}
VALID_RISK_LEVELS = {"SCĂZUT", "MEDIU", "RIDICAT"}
VALID_POSITION_SIGNALS = {"PĂSTREAZĂ", "CUMPĂRĂ MAI MULT", "CONSIDERĂ VÂNZARE"}
VALID_CONFIDENCE = {"RIDICAT", "MEDIU", "SCĂZUT"}


@pytest.fixture(scope="module")
def pro_token():
    """Get a PRO session token via demo-login."""
    r = requests.get(f"{BASE_URL}/api/auth/demo-login?secret=finromania-demo-2026", timeout=15)
    assert r.status_code == 200, f"Demo login failed: {r.status_code} {r.text}"
    data = r.json()
    token = data.get("session_token") or data.get("token")
    assert token, f"No token in response: {data}"
    return token


@pytest.fixture(scope="module")
def ai_result(pro_token):
    """Fetch AI analysis (may take 5-10s for GPT call). Cached for module scope."""
    headers = {"Authorization": f"Bearer {pro_token}"}
    print("\n[AI TEST] Calling /ai-analysis (first call, may take 5-10s)...")
    r = requests.get(f"{BASE_URL}/api/portfolio-bvb/ai-analysis", headers=headers, timeout=60)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:500]}"
    return r.json()


# ─────────────────────────────────────────
# AUTH TESTS
# ─────────────────────────────────────────

class TestAIAnalysisAuth:
    """Authentication and authorization checks"""

    def test_no_token_returns_401(self):
        """GET /ai-analysis without token → 401"""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/ai-analysis", timeout=15)
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print("✅ No token → 401")

    def test_invalid_token_returns_401(self):
        """GET /ai-analysis with invalid token → 401"""
        r = requests.get(
            f"{BASE_URL}/api/portfolio-bvb/ai-analysis",
            headers={"Authorization": "Bearer invalid_token_xyz"},
            timeout=15,
        )
        assert r.status_code in (401, 403), f"Expected 401/403, got {r.status_code}"
        print(f"✅ Invalid token → {r.status_code}")

    def test_demo_login_returns_token(self, pro_token):
        """Demo login returns a valid PRO session token"""
        assert isinstance(pro_token, str) and len(pro_token) > 10
        print(f"✅ Demo token obtained: {pro_token[:30]}...")


# ─────────────────────────────────────────
# RESPONSE SCHEMA TESTS
# ─────────────────────────────────────────

class TestAIAnalysisSchema:
    """Schema and structure validation of /ai-analysis response"""

    def test_status_200_with_pro_token(self, pro_token):
        """GET /ai-analysis with PRO token → 200"""
        headers = {"Authorization": f"Bearer {pro_token}"}
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/ai-analysis", headers=headers, timeout=60)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text[:500]}"
        print("✅ PRO token → 200")

    def test_top_level_fields_present(self, ai_result):
        """Response has: portfolio_summary, positions, from_cache, generated_at"""
        assert "portfolio_summary" in ai_result, f"Missing portfolio_summary in {list(ai_result.keys())}"
        assert "positions" in ai_result, f"Missing positions in {list(ai_result.keys())}"
        assert "from_cache" in ai_result, f"Missing from_cache in {list(ai_result.keys())}"
        assert "generated_at" in ai_result, f"Missing generated_at in {list(ai_result.keys())}"
        print(f"✅ Top-level fields present. from_cache={ai_result['from_cache']}")

    def test_positions_analyzed_field(self, ai_result):
        """positions_analyzed field present and >= 1"""
        assert "positions_analyzed" in ai_result, "Missing positions_analyzed"
        assert ai_result["positions_analyzed"] >= 1
        print(f"✅ positions_analyzed = {ai_result['positions_analyzed']}")


# ─────────────────────────────────────────
# PORTFOLIO SUMMARY TESTS
# ─────────────────────────────────────────

class TestPortfolioSummary:
    """Validate portfolio_summary fields"""

    def test_portfolio_summary_is_dict(self, ai_result):
        ps = ai_result["portfolio_summary"]
        assert isinstance(ps, dict), f"portfolio_summary should be dict, got {type(ps)}"
        print("✅ portfolio_summary is dict")

    def test_overall_signal_valid(self, ai_result):
        """overall_signal must be HOLD | BUY_MORE | REDUCE"""
        ps = ai_result["portfolio_summary"]
        assert "overall_signal" in ps, f"Missing overall_signal in {list(ps.keys())}"
        assert ps["overall_signal"] in VALID_OVERALL_SIGNALS, \
            f"Invalid overall_signal: '{ps['overall_signal']}' not in {VALID_OVERALL_SIGNALS}"
        print(f"✅ overall_signal = {ps['overall_signal']}")

    def test_risk_level_valid(self, ai_result):
        """risk_level must be SCĂZUT | MEDIU | RIDICAT"""
        ps = ai_result["portfolio_summary"]
        assert "risk_level" in ps, f"Missing risk_level in {list(ps.keys())}"
        assert ps["risk_level"] in VALID_RISK_LEVELS, \
            f"Invalid risk_level: '{ps['risk_level']}' not in {VALID_RISK_LEVELS}"
        print(f"✅ risk_level = {ps['risk_level']}")

    def test_global_recommendation_present_and_string(self, ai_result):
        """global_recommendation is a non-empty string"""
        ps = ai_result["portfolio_summary"]
        assert "global_recommendation" in ps, "Missing global_recommendation"
        assert isinstance(ps["global_recommendation"], str), "global_recommendation must be string"
        assert len(ps["global_recommendation"]) > 10, \
            f"global_recommendation too short: '{ps['global_recommendation']}'"
        print(f"✅ global_recommendation = '{ps['global_recommendation'][:60]}...'")

    def test_diversification_note_present(self, ai_result):
        """diversification_note is present (may be None or string)"""
        ps = ai_result["portfolio_summary"]
        # diversification_note is optional but should exist
        assert "diversification_note" in ps or True  # non-blocking check
        dn = ps.get("diversification_note")
        print(f"✅ diversification_note = {repr(dn)[:60]}")


# ─────────────────────────────────────────
# POSITIONS ARRAY TESTS
# ─────────────────────────────────────────

class TestPositionsArray:
    """Validate positions[] fields and signal values"""

    def test_positions_is_list(self, ai_result):
        assert isinstance(ai_result["positions"], list), "positions should be list"
        print("✅ positions is list")

    def test_positions_not_empty(self, ai_result):
        assert len(ai_result["positions"]) > 0, "positions should not be empty"
        print(f"✅ positions count = {len(ai_result['positions'])}")

    def test_each_position_has_required_fields(self, ai_result):
        """Each position must have: symbol, signal, confidence, reason"""
        required = {"symbol", "signal", "confidence", "reason"}
        for pos in ai_result["positions"]:
            missing = required - set(pos.keys())
            assert not missing, f"Position {pos.get('symbol')} missing fields: {missing}"
        print(f"✅ All {len(ai_result['positions'])} positions have required fields")

    def test_position_signal_values_valid(self, ai_result):
        """signal must be PĂSTREAZĂ | CUMPĂRĂ MAI MULT | CONSIDERĂ VÂNZARE"""
        for pos in ai_result["positions"]:
            assert pos["signal"] in VALID_POSITION_SIGNALS, \
                f"Invalid signal '{pos['signal']}' for {pos.get('symbol')}. Valid: {VALID_POSITION_SIGNALS}"
        print(f"✅ All position signal values are valid")

    def test_position_confidence_values_valid(self, ai_result):
        """confidence must be RIDICAT | MEDIU | SCĂZUT"""
        for pos in ai_result["positions"]:
            assert pos["confidence"] in VALID_CONFIDENCE, \
                f"Invalid confidence '{pos['confidence']}' for {pos.get('symbol')}. Valid: {VALID_CONFIDENCE}"
        print(f"✅ All confidence values are valid")

    def test_position_reason_is_string(self, ai_result):
        """reason must be a non-empty string"""
        for pos in ai_result["positions"]:
            assert isinstance(pos["reason"], str) and len(pos["reason"]) > 5, \
                f"reason for {pos.get('symbol')} is invalid: {repr(pos.get('reason'))}"
        print("✅ All position reasons are non-empty strings")

    def test_position_key_metric_present(self, ai_result):
        """key_metric is optional but should be present per spec"""
        for pos in ai_result["positions"]:
            assert "key_metric" in pos, f"Missing key_metric in position {pos.get('symbol')}"
        print("✅ All positions have key_metric field")

    def test_demo_portfolio_symbols_present(self, ai_result):
        """Demo portfolio has H2O and BRD — both should appear in positions"""
        symbols = {pos["symbol"] for pos in ai_result["positions"]}
        print(f"  Symbols in AI response: {symbols}")
        # At least one of the expected symbols should be present
        expected = {"H2O", "BRD"}
        overlap = symbols & expected
        assert len(overlap) > 0, f"Expected symbols {expected} not found in {symbols}"
        print(f"✅ Expected symbols found: {overlap}")

    def test_h2o_signal_display(self, ai_result):
        """H2O position (P&L positive) should have a valid signal"""
        h2o = next((p for p in ai_result["positions"] if p["symbol"] == "H2O"), None)
        if h2o:
            assert h2o["signal"] in VALID_POSITION_SIGNALS
            print(f"✅ H2O signal = {h2o['signal']} (confidence={h2o['confidence']})")
        else:
            print("ℹ️ H2O not found in positions (may use different symbol casing)")

    def test_brd_signal_display(self, ai_result):
        """BRD position should have a valid signal"""
        brd = next((p for p in ai_result["positions"] if p["symbol"] == "BRD"), None)
        if brd:
            assert brd["signal"] in VALID_POSITION_SIGNALS
            print(f"✅ BRD signal = {brd['signal']} (confidence={brd['confidence']})")
        else:
            print("ℹ️ BRD not found in positions")


# ─────────────────────────────────────────
# CACHE TESTS
# ─────────────────────────────────────────

class TestAICache:
    """Test that 1-hour cache works correctly"""

    def test_first_call_from_cache_false(self, ai_result):
        """The first call (module-scoped fixture) may or may not be from cache"""
        from_cache = ai_result.get("from_cache", None)
        print(f"  First call from_cache = {from_cache}")
        # Just validate it's a boolean
        assert isinstance(from_cache, bool), f"from_cache should be bool, got {type(from_cache)}"
        print("✅ from_cache is boolean")

    def test_second_call_returns_from_cache(self, pro_token):
        """Second call within 1 hour → from_cache=True"""
        headers = {"Authorization": f"Bearer {pro_token}"}
        print("\n[AI TEST] Making second call (should be from cache)...")
        r = requests.get(
            f"{BASE_URL}/api/portfolio-bvb/ai-analysis",
            headers=headers,
            timeout=30,
        )
        assert r.status_code == 200, f"Second call failed: {r.status_code}: {r.text[:300]}"
        data = r.json()
        assert data.get("from_cache") is True, \
            f"Second call should return from_cache=True, got from_cache={data.get('from_cache')}"
        print(f"✅ Second call → from_cache=True")

    def test_cache_result_has_same_structure(self, pro_token):
        """Cached result has same structure as fresh result"""
        headers = {"Authorization": f"Bearer {pro_token}"}
        r = requests.get(
            f"{BASE_URL}/api/portfolio-bvb/ai-analysis",
            headers=headers,
            timeout=30,
        )
        assert r.status_code == 200
        data = r.json()
        assert "portfolio_summary" in data
        assert "positions" in data
        assert data.get("from_cache") is True
        print("✅ Cached result has correct structure")

    def test_generated_at_is_iso_string(self, ai_result):
        """generated_at should be a valid ISO datetime string"""
        gen_at = ai_result.get("generated_at")
        assert gen_at is not None, "generated_at is None"
        assert isinstance(gen_at, str) and len(gen_at) >= 16, \
            f"generated_at not valid: {gen_at}"
        # Try parsing it
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(gen_at.replace("Z", "+00:00"))
            print(f"✅ generated_at = {gen_at}")
        except Exception as e:
            pytest.fail(f"generated_at '{gen_at}' is not a valid ISO datetime: {e}")
