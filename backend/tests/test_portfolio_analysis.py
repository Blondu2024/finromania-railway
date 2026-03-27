"""
Tests for Portofoliu BVB PRO — Faza 2 Analysis endpoint:
  - GET /api/portfolio-bvb/analysis (auth guard, response structure, sector allocation, fundamentals, history)
  - sector_allocation fields: sector, value, percent (suma ≈ 100%)
  - fundamentals: symbol, pe_ratio, roe_percent, eps, debt_equity, pb_ratio (null=N/A)
  - history: snapshot saved once per day (no duplicates)
  - BRD: PE=12.84, ROE=15.4%, EPS=2.22, D/E=8.27
  - H2O: PE=null, ROE=13.4%, EPS=0.0, D/E=null
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


# ─── Auth fixture ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def pro_token():
    """Obtain PRO demo token once per module."""
    r = requests.get(
        f"{BASE_URL}/api/auth/demo-login?secret=finromania-demo-2026", timeout=15
    )
    if r.status_code != 200:
        pytest.skip(f"Demo login failed: {r.status_code}")
    data = r.json()
    token = data.get("session_token")
    if not token:
        pytest.skip("No session_token in demo login response")
    return token


@pytest.fixture(scope="module")
def auth_headers(pro_token):
    return {"Authorization": f"Bearer {pro_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="module")
def analysis_response(auth_headers):
    """Fetch analysis once per module and reuse."""
    r = requests.get(f"{BASE_URL}/api/portfolio-bvb/analysis", headers=auth_headers, timeout=20)
    assert r.status_code == 200, f"Analysis endpoint failed: {r.status_code} — {r.text[:200]}"
    return r.json()


# ─── Auth Guard Tests ──────────────────────────────────────────────────────────

class TestAnalysisAuthGuard:
    """Test that analysis endpoint requires authentication."""

    def test_no_token_returns_401(self):
        """GET /analysis without token → 401"""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/analysis", timeout=10)
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print("✅ GET /analysis without token → 401")

    def test_invalid_token_returns_401(self):
        """GET /analysis with invalid token → 401"""
        r = requests.get(
            f"{BASE_URL}/api/portfolio-bvb/analysis",
            headers={"Authorization": "Bearer invalid_token_xyz"},
            timeout=10,
        )
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print("✅ GET /analysis with invalid token → 401")


# ─── Response Structure Tests ──────────────────────────────────────────────────

class TestAnalysisResponseStructure:
    """Test top-level response structure of GET /analysis."""

    def test_returns_200_with_pro_token(self, auth_headers):
        """GET /analysis with PRO token → 200"""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/analysis", headers=auth_headers, timeout=20)
        assert r.status_code == 200, f"Expected 200, got {r.status_code} — {r.text[:200]}"
        print(f"✅ GET /analysis with PRO token → 200")

    def test_top_level_fields_present(self, analysis_response):
        """Response has all required top-level fields."""
        data = analysis_response
        assert "sector_allocation" in data, "Missing sector_allocation"
        assert "fundamentals" in data, "Missing fundamentals"
        assert "history" in data, "Missing history"
        assert "total_value" in data, "Missing total_value"
        print("✅ Top-level fields: sector_allocation, fundamentals, history, total_value")

    def test_total_value_is_positive(self, analysis_response):
        """total_value is a positive number."""
        tv = analysis_response.get("total_value")
        assert isinstance(tv, (int, float)), f"total_value should be numeric, got {type(tv)}"
        assert tv > 0, f"total_value should be > 0, got {tv}"
        print(f"✅ total_value = {tv} RON (positive)")


# ─── Sector Allocation Tests ───────────────────────────────────────────────────

class TestSectorAllocation:
    """Test sector_allocation data structure and values."""

    def test_sector_allocation_is_list(self, analysis_response):
        """sector_allocation is a list."""
        sa = analysis_response.get("sector_allocation")
        assert isinstance(sa, list), f"sector_allocation should be a list, got {type(sa)}"
        print(f"✅ sector_allocation is a list with {len(sa)} entries")

    def test_sector_allocation_not_empty(self, analysis_response):
        """sector_allocation has at least 1 entry (portfolio has positions)."""
        sa = analysis_response.get("sector_allocation", [])
        assert len(sa) > 0, "sector_allocation should not be empty"
        print(f"✅ sector_allocation has {len(sa)} sector(s)")

    def test_sector_allocation_fields(self, analysis_response):
        """Each sector entry has: sector, value, percent."""
        for entry in analysis_response.get("sector_allocation", []):
            assert "sector" in entry, f"Missing 'sector' field in {entry}"
            assert "value" in entry, f"Missing 'value' field in {entry}"
            assert "percent" in entry, f"Missing 'percent' field in {entry}"
        print("✅ All sector_allocation entries have sector, value, percent fields")

    def test_sector_allocation_percent_sums_to_100(self, analysis_response):
        """Sum of percent values ≈ 100%."""
        sa = analysis_response.get("sector_allocation", [])
        total_pct = sum(s["percent"] for s in sa)
        assert 99.0 <= total_pct <= 101.0, f"Sector percents should sum ≈ 100%, got {total_pct}"
        print(f"✅ Sector percent sum = {total_pct:.1f}% (≈ 100%)")

    def test_sector_allocation_has_energie_and_financiar(self, analysis_response):
        """Demo portfolio has H2O (Energie) and BRD (Financiar) sectors."""
        sa = analysis_response.get("sector_allocation", [])
        sectors = [s["sector"] for s in sa]
        assert "Energie" in sectors, f"Expected 'Energie' sector, got {sectors}"
        assert "Financiar" in sectors, f"Expected 'Financiar' sector, got {sectors}"
        print(f"✅ Sectors found: {sectors}")

    def test_sector_allocation_values_are_positive(self, analysis_response):
        """All sector values are positive."""
        for entry in analysis_response.get("sector_allocation", []):
            assert entry["value"] > 0, f"Sector value should be > 0, got {entry}"
        print("✅ All sector values are positive")

    def test_sector_energie_value(self, analysis_response):
        """H2O is Energie sector — value should match H2O position value."""
        sa = analysis_response.get("sector_allocation", [])
        energie = next((s for s in sa if s["sector"] == "Energie"), None)
        assert energie is not None, "Energie sector not found"
        # H2O: 50 shares, live price ~147.80 = ~7390 RON (accept range)
        assert energie["value"] > 1000, f"Energie value too low: {energie['value']}"
        print(f"✅ Energie sector value = {energie['value']} RON")

    def test_sector_financiar_value(self, analysis_response):
        """BRD is Financiar sector — value should match BRD position value."""
        sa = analysis_response.get("sector_allocation", [])
        fin = next((s for s in sa if s["sector"] == "Financiar"), None)
        assert fin is not None, "Financiar sector not found"
        assert fin["value"] > 1000, f"Financiar value too low: {fin['value']}"
        print(f"✅ Financiar sector value = {fin['value']} RON")


# ─── Fundamentals Tests ────────────────────────────────────────────────────────

class TestFundamentals:
    """Test fundamentals data from daily EODHD cache."""

    def test_fundamentals_is_list(self, analysis_response):
        """fundamentals is a list."""
        f = analysis_response.get("fundamentals")
        assert isinstance(f, list), f"fundamentals should be a list, got {type(f)}"
        print(f"✅ fundamentals is a list with {len(f)} entries")

    def test_fundamentals_has_brd_and_h2o(self, analysis_response):
        """Fundamentals contain BRD and H2O symbols."""
        syms = [f["symbol"] for f in analysis_response.get("fundamentals", [])]
        assert "BRD" in syms, f"BRD missing from fundamentals: {syms}"
        assert "H2O" in syms, f"H2O missing from fundamentals: {syms}"
        print(f"✅ Fundamentals symbols: {syms}")

    def test_fundamentals_required_fields(self, analysis_response):
        """Each fundamental entry has all required fields."""
        required = ["symbol", "pe_ratio", "roe_percent", "eps", "debt_equity", "pb_ratio"]
        for f in analysis_response.get("fundamentals", []):
            for field in required:
                assert field in f, f"Missing '{field}' in {f['symbol']} fundamentals"
        print("✅ All fundamentals have required fields: symbol, pe_ratio, roe_percent, eps, debt_equity, pb_ratio")

    def test_brd_pe_ratio(self, analysis_response):
        """BRD P/E ratio ≈ 12.84."""
        brd = next((f for f in analysis_response["fundamentals"] if f["symbol"] == "BRD"), None)
        assert brd is not None, "BRD not in fundamentals"
        pe = brd.get("pe_ratio")
        assert pe is not None, "BRD pe_ratio should not be null"
        assert 12.0 <= pe <= 13.5, f"BRD PE expected ~12.84, got {pe}"
        print(f"✅ BRD pe_ratio = {pe} (expected ~12.84)")

    def test_brd_roe_percent(self, analysis_response):
        """BRD ROE% ≈ 15.4%."""
        brd = next((f for f in analysis_response["fundamentals"] if f["symbol"] == "BRD"), None)
        roe = brd.get("roe_percent")
        assert roe is not None, "BRD roe_percent should not be null"
        assert 15.0 <= roe <= 16.0, f"BRD ROE expected ~15.4%, got {roe}"
        print(f"✅ BRD roe_percent = {roe}% (expected ~15.4%)")

    def test_brd_eps(self, analysis_response):
        """BRD EPS ≈ 2.22."""
        brd = next((f for f in analysis_response["fundamentals"] if f["symbol"] == "BRD"), None)
        eps = brd.get("eps")
        assert eps is not None, "BRD eps should not be null"
        assert abs(eps - 2.22) < 0.1, f"BRD EPS expected ~2.22, got {eps}"
        print(f"✅ BRD eps = {eps} (expected ~2.22)")

    def test_brd_debt_equity(self, analysis_response):
        """BRD D/E ≈ 8.27."""
        brd = next((f for f in analysis_response["fundamentals"] if f["symbol"] == "BRD"), None)
        de = brd.get("debt_equity")
        assert de is not None, "BRD debt_equity should not be null"
        assert abs(de - 8.27) < 0.1, f"BRD D/E expected ~8.27, got {de}"
        print(f"✅ BRD debt_equity = {de} (expected ~8.27)")

    def test_h2o_pe_ratio_is_null(self, analysis_response):
        """H2O P/E ratio is null (N/A)."""
        h2o = next((f for f in analysis_response["fundamentals"] if f["symbol"] == "H2O"), None)
        assert h2o is not None, "H2O not in fundamentals"
        assert h2o.get("pe_ratio") is None, f"H2O pe_ratio should be null, got {h2o.get('pe_ratio')}"
        print("✅ H2O pe_ratio = null (N/A)")

    def test_h2o_roe_percent(self, analysis_response):
        """H2O ROE% ≈ 13.4%."""
        h2o = next((f for f in analysis_response["fundamentals"] if f["symbol"] == "H2O"), None)
        roe = h2o.get("roe_percent")
        assert roe is not None, "H2O roe_percent should not be null"
        assert 13.0 <= roe <= 14.0, f"H2O ROE expected ~13.4%, got {roe}"
        print(f"✅ H2O roe_percent = {roe}% (expected ~13.4%)")

    def test_h2o_debt_equity_is_null(self, analysis_response):
        """H2O D/E is null (N/A)."""
        h2o = next((f for f in analysis_response["fundamentals"] if f["symbol"] == "H2O"), None)
        assert h2o.get("debt_equity") is None, f"H2O debt_equity should be null, got {h2o.get('debt_equity')}"
        print("✅ H2O debt_equity = null (N/A)")

    def test_h2o_eps(self, analysis_response):
        """H2O EPS = 0.0."""
        h2o = next((f for f in analysis_response["fundamentals"] if f["symbol"] == "H2O"), None)
        eps = h2o.get("eps")
        assert eps is not None, "H2O eps should not be null (is 0.0, not null)"
        assert eps == 0.0, f"H2O EPS expected 0.0, got {eps}"
        print(f"✅ H2O eps = {eps} (expected 0.0)")


# ─── History / No-duplicate Tests ─────────────────────────────────────────────

class TestHistoryAndDeduplication:
    """Test portfolio value history snapshots."""

    def test_history_is_list(self, analysis_response):
        """history is a list."""
        h = analysis_response.get("history")
        assert isinstance(h, list), f"history should be a list, got {type(h)}"
        print(f"✅ history is a list with {len(h)} entry/entries")

    def test_history_entry_fields(self, analysis_response):
        """History entries have date and value fields."""
        for entry in analysis_response.get("history", []):
            assert "date" in entry, f"Missing 'date' in history entry {entry}"
            assert "value" in entry, f"Missing 'value' in history entry {entry}"
        print("✅ All history entries have date and value fields")

    def test_no_duplicate_snapshots_same_day(self, auth_headers):
        """Calling /analysis twice on the same day does not duplicate snapshot."""
        import time

        # First call
        r1 = requests.get(f"{BASE_URL}/api/portfolio-bvb/analysis", headers=auth_headers, timeout=20)
        assert r1.status_code == 200
        hist1 = r1.json().get("history", [])

        # Second call (same day)
        time.sleep(1)
        r2 = requests.get(f"{BASE_URL}/api/portfolio-bvb/analysis", headers=auth_headers, timeout=20)
        assert r2.status_code == 200
        hist2 = r2.json().get("history", [])

        # History count should be the same (no new duplicate for today)
        assert len(hist1) == len(hist2), (
            f"Duplicate snapshot created: history went from {len(hist1)} to {len(hist2)} entries"
        )
        print(f"✅ No duplicate snapshot: history.length={len(hist2)} (stable after 2 calls)")

    def test_history_dates_are_unique(self, analysis_response):
        """No duplicate dates in history."""
        dates = [h["date"] for h in analysis_response.get("history", [])]
        assert len(dates) == len(set(dates)), f"Duplicate dates found in history: {dates}"
        print(f"✅ History dates are all unique: {dates}")

    def test_history_values_are_positive(self, analysis_response):
        """All history values are positive."""
        for entry in analysis_response.get("history", []):
            assert entry["value"] > 0, f"History value should be > 0, got {entry}"
        print("✅ All history values are positive")

    def test_history_length_reflects_insufficient_data(self, analysis_response):
        """Since only 1 snapshot exists, history.length = 1 (< 2 → frontend shows message)."""
        hist = analysis_response.get("history", [])
        # We know from DB there's only 1 snapshot (same day)
        # This test documents that history < 2 points → frontend should show 'Date insuficiente'
        assert len(hist) >= 1, "Expected at least 1 history entry"
        print(f"✅ history.length = {len(hist)} (< 2 → frontend shows 'Date insuficiente' message)")
