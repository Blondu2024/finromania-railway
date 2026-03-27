"""
Tests for Portofoliu BVB PRO endpoints:
  - GET /api/portfolio-bvb/  (returns positions + summary with live EODHD data)
  - POST /api/portfolio-bvb/position  (add new position)
  - PUT /api/portfolio-bvb/position/{symbol}  (update position)
  - DELETE /api/portfolio-bvb/position/{symbol}  (delete position)
  - GET /api/portfolio-bvb/export  (CSV export)
  - Auth guard: 401 without token
  - Invalid symbol: 404 for non-BVB symbol
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
DEMO_TOKEN = None

# ─── Auth fixture ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def pro_token():
    """Obtain PRO demo token once per module."""
    global DEMO_TOKEN
    r = requests.get(f"{BASE_URL}/api/auth/demo-login?secret=finromania-demo-2026", timeout=15)
    if r.status_code != 200:
        pytest.skip(f"Demo login failed: {r.status_code} — {r.text[:200]}")
    data = r.json()
    token = data.get("session_token")
    if not token:
        pytest.skip("No session_token in demo login response")
    DEMO_TOKEN = token
    return token


@pytest.fixture(scope="module")
def auth_headers(pro_token):
    return {"Authorization": f"Bearer {pro_token}", "Content-Type": "application/json"}


# ─── Cleanup fixture ──────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def cleanup_test_positions(auth_headers):
    """Delete TEST positions before and after the test module."""
    test_symbols = ["TLV", "SNP"]

    def _delete(sym):
        requests.delete(f"{BASE_URL}/api/portfolio-bvb/position/{sym}", headers=auth_headers, timeout=15)

    # Before
    for s in test_symbols:
        _delete(s)

    yield

    # After
    for s in test_symbols:
        _delete(s)


# ─── Test: Auth guard ─────────────────────────────────────────────────────────

class TestAuthGuard:
    """Endpoints should return 401 without a token."""

    def test_get_portfolio_no_token(self):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/", timeout=15)
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print(f"✅ GET /portfolio-bvb/ without token → {r.status_code}")

    def test_post_position_no_token(self):
        r = requests.post(
            f"{BASE_URL}/api/portfolio-bvb/position",
            json={"symbol": "TLV", "shares": 100, "purchase_price": 22.50},
            timeout=15,
        )
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print(f"✅ POST /portfolio-bvb/position without token → {r.status_code}")

    def test_delete_position_no_token(self):
        r = requests.delete(f"{BASE_URL}/api/portfolio-bvb/position/TLV", timeout=15)
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print(f"✅ DELETE /portfolio-bvb/position/TLV without token → {r.status_code}")

    def test_export_no_token(self):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/export", timeout=15)
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print(f"✅ GET /portfolio-bvb/export without token → {r.status_code}")


# ─── Test: GET portfolio ──────────────────────────────────────────────────────

class TestGetPortfolio:
    """GET /api/portfolio-bvb/ with PRO token."""

    def test_get_portfolio_returns_200(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/", headers=auth_headers, timeout=30)
        assert r.status_code == 200, f"Expected 200, got {r.status_code} — {r.text[:300]}"
        print(f"✅ GET /portfolio-bvb/ → 200")

    def test_get_portfolio_response_structure(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/", headers=auth_headers, timeout=30)
        data = r.json()
        assert "positions" in data, "Missing 'positions' key"
        assert "summary" in data, "Missing 'summary' key"
        print(f"✅ Response has 'positions' and 'summary'")

    def test_get_portfolio_summary_fields(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/", headers=auth_headers, timeout=30)
        summary = r.json()["summary"]
        required_fields = ["total_value", "total_invested", "pl_ron", "pl_percent", "today_pl", "positions_count"]
        for field in required_fields:
            assert field in summary, f"Missing summary field: {field}"
        print(f"✅ Summary has all required fields: {required_fields}")

    def test_get_portfolio_positions_fields(self, auth_headers):
        """If there are positions, verify each has live data fields."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/", headers=auth_headers, timeout=30)
        positions = r.json()["positions"]
        if not positions:
            print("⚠️ Portfolio is empty — skipping position field check")
            return
        pos = positions[0]
        required = ["symbol", "shares", "purchase_price", "current_price", "pl_ron", "pl_percent", "rsi", "rsi_signal"]
        for field in required:
            assert field in pos, f"Missing position field: {field}"
        print(f"✅ Position has all required fields: {required}")


# ─── Test: POST position ──────────────────────────────────────────────────────

class TestAddPosition:
    """POST /api/portfolio-bvb/position"""

    def test_add_tlv_position(self, auth_headers):
        payload = {"symbol": "TLV", "shares": 100, "purchase_price": 22.50}
        r = requests.post(f"{BASE_URL}/api/portfolio-bvb/position", json=payload, headers=auth_headers, timeout=15)
        print(f"POST /portfolio-bvb/position TLV → {r.status_code}: {r.text[:200]}")
        assert r.status_code in [200, 201], f"Expected 200/201, got {r.status_code} — {r.text[:300]}"
        data = r.json()
        assert data.get("status") == "ok" or "symbol" in data, f"Unexpected response: {data}"
        print(f"✅ Added TLV position")

    def test_add_duplicate_position_returns_409(self, auth_headers):
        """Adding the same symbol again should return 409."""
        payload = {"symbol": "TLV", "shares": 50, "purchase_price": 20.00}
        r = requests.post(f"{BASE_URL}/api/portfolio-bvb/position", json=payload, headers=auth_headers, timeout=15)
        assert r.status_code == 409, f"Expected 409 for duplicate, got {r.status_code} — {r.text[:200]}"
        print(f"✅ Duplicate TLV → 409 Conflict")

    def test_add_invalid_symbol_returns_404(self, auth_headers):
        """Symbol ZZZ should not exist on BVB → 404."""
        payload = {"symbol": "ZZZ", "shares": 10, "purchase_price": 5.00}
        r = requests.post(f"{BASE_URL}/api/portfolio-bvb/position", json=payload, headers=auth_headers, timeout=15)
        assert r.status_code == 404, f"Expected 404 for invalid symbol, got {r.status_code} — {r.text[:200]}"
        print(f"✅ Invalid symbol ZZZ → 404")

    def test_verify_tlv_in_portfolio(self, auth_headers):
        """After adding TLV, it should appear in portfolio."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/", headers=auth_headers, timeout=30)
        assert r.status_code == 200
        positions = r.json()["positions"]
        symbols = [p["symbol"] for p in positions]
        assert "TLV" in symbols, f"TLV not found in portfolio after add. Got: {symbols}"
        print(f"✅ TLV persisted in portfolio")


# ─── Test: PUT position ───────────────────────────────────────────────────────

class TestUpdatePosition:
    """PUT /api/portfolio-bvb/position/{symbol}"""

    def test_update_tlv_position(self, auth_headers):
        payload = {"shares": 200, "purchase_price": 23.00}
        r = requests.put(
            f"{BASE_URL}/api/portfolio-bvb/position/TLV",
            json=payload,
            headers=auth_headers,
            timeout=15,
        )
        assert r.status_code == 200, f"Expected 200, got {r.status_code} — {r.text[:200]}"
        data = r.json()
        assert data.get("status") == "ok"
        print(f"✅ TLV updated → 200")

    def test_verify_update_persisted(self, auth_headers):
        """After update, GET should show new shares and price."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/", headers=auth_headers, timeout=30)
        assert r.status_code == 200
        positions = r.json()["positions"]
        tlv = next((p for p in positions if p["symbol"] == "TLV"), None)
        assert tlv is not None, "TLV not found after update"
        assert tlv["shares"] == 200, f"Expected 200 shares, got {tlv['shares']}"
        assert tlv["purchase_price"] == 23.00, f"Expected 23.00, got {tlv['purchase_price']}"
        print(f"✅ TLV update persisted: shares={tlv['shares']}, price={tlv['purchase_price']}")

    def test_update_nonexistent_position_returns_404(self, auth_headers):
        payload = {"shares": 10, "purchase_price": 5.00}
        r = requests.put(
            f"{BASE_URL}/api/portfolio-bvb/position/ZZZ",
            json=payload,
            headers=auth_headers,
            timeout=15,
        )
        assert r.status_code == 404, f"Expected 404 for ZZZ, got {r.status_code}"
        print(f"✅ Update non-existent ZZZ → 404")


# ─── Test: DELETE position ────────────────────────────────────────────────────

class TestDeletePosition:
    """DELETE /api/portfolio-bvb/position/{symbol}"""

    def test_add_snp_for_delete(self, auth_headers):
        """Add SNP so we can delete it."""
        # Clean first
        requests.delete(f"{BASE_URL}/api/portfolio-bvb/position/SNP", headers=auth_headers, timeout=15)
        payload = {"symbol": "SNP", "shares": 50, "purchase_price": 0.55}
        r = requests.post(f"{BASE_URL}/api/portfolio-bvb/position", json=payload, headers=auth_headers, timeout=15)
        print(f"Add SNP for delete test → {r.status_code}: {r.text[:150]}")
        assert r.status_code in [200, 201], f"Setup failed: {r.text[:200]}"
        print(f"✅ SNP added for delete test")

    def test_delete_snp_position(self, auth_headers):
        r = requests.delete(f"{BASE_URL}/api/portfolio-bvb/position/SNP", headers=auth_headers, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code} — {r.text[:200]}"
        data = r.json()
        assert data.get("status") == "ok"
        print(f"✅ SNP deleted → 200")

    def test_verify_snp_removed(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/", headers=auth_headers, timeout=30)
        positions = r.json()["positions"]
        symbols = [p["symbol"] for p in positions]
        assert "SNP" not in symbols, f"SNP should be removed but found in: {symbols}"
        print(f"✅ SNP removed from portfolio")

    def test_delete_nonexistent_returns_404(self, auth_headers):
        r = requests.delete(f"{BASE_URL}/api/portfolio-bvb/position/ZZZ", headers=auth_headers, timeout=15)
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        print(f"✅ Delete non-existent ZZZ → 404")

    def test_delete_tlv_cleanup(self, auth_headers):
        """Clean up TLV at the end."""
        r = requests.delete(f"{BASE_URL}/api/portfolio-bvb/position/TLV", headers=auth_headers, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        print(f"✅ TLV cleaned up")


# ─── Test: CSV Export ─────────────────────────────────────────────────────────

class TestExportCSV:
    """GET /api/portfolio-bvb/export"""

    def test_export_returns_200(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/export", headers=auth_headers, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code} — {r.text[:200]}"
        print(f"✅ GET /portfolio-bvb/export → 200")

    def test_export_content_type_csv(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/export", headers=auth_headers, timeout=15)
        content_type = r.headers.get("content-type", "")
        assert "text/csv" in content_type, f"Expected text/csv, got: {content_type}"
        print(f"✅ Content-Type is text/csv: {content_type}")

    def test_export_has_csv_header_row(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/export", headers=auth_headers, timeout=15)
        content = r.content.decode("utf-8-sig")  # handle BOM
        first_line = content.split("\n")[0]
        assert "Simbol" in first_line, f"CSV header missing 'Simbol': {first_line}"
        assert "Cantitate" in first_line or "Preț" in first_line, f"CSV header incomplete: {first_line}"
        print(f"✅ CSV header row present: {first_line}")

    def test_export_content_disposition(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/export", headers=auth_headers, timeout=15)
        cd = r.headers.get("content-disposition", "")
        assert "attachment" in cd, f"Missing 'attachment' in Content-Disposition: {cd}"
        assert ".csv" in cd, f"Missing .csv in Content-Disposition: {cd}"
        print(f"✅ Content-Disposition: {cd}")
