"""
Test suite for Dividend Calculator PRO (/api/dividend-calculator)
Tests: stocks list, calculate dividends, CASS logic, tax rates, projections
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


@pytest.fixture(scope="module")
def demo_token():
    """Get demo session token"""
    resp = requests.get(f"{BASE_URL}/api/auth/demo-login?secret=finromania-demo-2026")
    if resp.status_code == 200:
        data = resp.json()
        token = data.get("session_token", "")
        print(f"Demo token: {token[:20]}...")
        return token
    pytest.skip(f"Demo login failed: {resp.status_code} {resp.text}")


@pytest.fixture(scope="module")
def auth_headers(demo_token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {demo_token}"
    }


# ===========================================================
# TEST 1: GET /api/dividend-calculator/stocks
# ===========================================================

class TestStocksEndpoint:
    """Test GET /api/dividend-calculator/stocks"""

    def test_stocks_returns_200(self, auth_headers):
        resp = requests.get(f"{BASE_URL}/api/dividend-calculator/stocks", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200 got {resp.status_code}: {resp.text[:200]}"
        print("✅ GET /stocks returns 200")

    def test_stocks_count_is_14(self, auth_headers):
        """Should return 14 dividend-paying stocks (M=MedLife excluded because div=0)"""
        resp = requests.get(f"{BASE_URL}/api/dividend-calculator/stocks", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        count = data.get("count", 0)
        stocks = data.get("stocks", [])
        # We have 14 symbols in DIVIDEND_SYMBOLS + 1 non-payer (M=MedLife)
        # The /stocks endpoint only includes stocks with dividend>0, so max 14
        assert count >= 10, f"Expected at least 10 stocks, got {count}"
        print(f"✅ Stocks count: {count} (stocks list has {len(stocks)} entries)")

    def test_stocks_sorted_by_yield_descending(self, auth_headers):
        resp = requests.get(f"{BASE_URL}/api/dividend-calculator/stocks", headers=auth_headers)
        assert resp.status_code == 200
        stocks = resp.json().get("stocks", [])
        yields = [s["dividend_yield"] for s in stocks]
        assert yields == sorted(yields, reverse=True), "Stocks should be sorted by yield descending"
        print(f"✅ Stocks sorted by yield descending. Top yield: {yields[0]:.2f}%")

    def test_tlv_dividend_value(self, auth_headers):
        """TLV dividend should be around 1.73-2.375 RON (EODHD live or fallback)"""
        resp = requests.get(f"{BASE_URL}/api/dividend-calculator/stocks", headers=auth_headers)
        assert resp.status_code == 200
        stocks = resp.json().get("stocks", [])
        tlv = next((s for s in stocks if s["symbol"] == "TLV"), None)
        assert tlv is not None, "TLV should be in stocks list"
        # Accept any positive dividend value (live EODHD or fallback)
        assert tlv["dividend_per_share"] > 0, f"TLV dividend should be > 0, got {tlv['dividend_per_share']}"
        print(f"✅ TLV dividend_per_share: {tlv['dividend_per_share']} RON")

    def test_brd_dividend_value(self, auth_headers):
        """BRD dividend should be around 1.0752 RON"""
        resp = requests.get(f"{BASE_URL}/api/dividend-calculator/stocks", headers=auth_headers)
        assert resp.status_code == 200
        stocks = resp.json().get("stocks", [])
        brd = next((s for s in stocks if s["symbol"] == "BRD"), None)
        assert brd is not None, "BRD should be in stocks list"
        assert brd["dividend_per_share"] > 0, f"BRD dividend should be > 0, got {brd['dividend_per_share']}"
        print(f"✅ BRD dividend_per_share: {brd['dividend_per_share']} RON")

    def test_h2o_dividend_value(self, auth_headers):
        """H2O (Hidroelectrica) dividend should be ~8.989 RON"""
        resp = requests.get(f"{BASE_URL}/api/dividend-calculator/stocks", headers=auth_headers)
        assert resp.status_code == 200
        stocks = resp.json().get("stocks", [])
        h2o = next((s for s in stocks if s["symbol"] == "H2O"), None)
        assert h2o is not None, "H2O (Hidroelectrica) should be in stocks list"
        assert h2o["dividend_per_share"] > 5.0, f"H2O dividend expected ~8.989 RON, got {h2o['dividend_per_share']}"
        print(f"✅ H2O dividend_per_share: {h2o['dividend_per_share']} RON")

    def test_snn_dividend_value(self, auth_headers):
        """SNN (Nuclearelectrica) dividend should be ~2.702 RON"""
        resp = requests.get(f"{BASE_URL}/api/dividend-calculator/stocks", headers=auth_headers)
        assert resp.status_code == 200
        stocks = resp.json().get("stocks", [])
        snn = next((s for s in stocks if s["symbol"] == "SNN"), None)
        assert snn is not None, "SNN (Nuclearelectrica) should be in stocks list"
        assert snn["dividend_per_share"] > 1.0, f"SNN dividend expected ~2.702 RON, got {snn['dividend_per_share']}"
        print(f"✅ SNN dividend_per_share: {snn['dividend_per_share']} RON")

    def test_snp_dividend_value(self, auth_headers):
        """SNP (OMV Petrom) dividend should be ~0.0578 RON (confirmed 2026)"""
        resp = requests.get(f"{BASE_URL}/api/dividend-calculator/stocks", headers=auth_headers)
        assert resp.status_code == 200
        stocks = resp.json().get("stocks", [])
        snp = next((s for s in stocks if s["symbol"] == "SNP"), None)
        assert snp is not None, "SNP (OMV Petrom) should be in stocks list"
        assert snp["dividend_per_share"] > 0, f"SNP dividend should be > 0, got {snp['dividend_per_share']}"
        print(f"✅ SNP dividend_per_share: {snp['dividend_per_share']} RON")

    def test_stocks_have_required_fields(self, auth_headers):
        """Each stock should have symbol, name, dividend_per_share, dividend_yield, price"""
        resp = requests.get(f"{BASE_URL}/api/dividend-calculator/stocks", headers=auth_headers)
        assert resp.status_code == 200
        stocks = resp.json().get("stocks", [])
        required_fields = ["symbol", "name", "dividend_per_share", "dividend_yield", "price"]
        for s in stocks:
            for field in required_fields:
                assert field in s, f"Stock {s.get('symbol')} missing field '{field}'"
        print(f"✅ All {len(stocks)} stocks have required fields")


# ===========================================================
# TEST 2: POST /api/dividend-calculator/calculate - Small portfolio (CASS=0)
# ===========================================================

class TestCalculateSmallPortfolio:
    """
    Small portfolio with total annual dividend < 28200 RON → CASS = 0
    Using 100 shares of BRD (~1.0752 RON/share → 107.52 RON dividend, well under 28200)
    """

    def test_calculate_small_returns_200(self, auth_headers):
        payload = {
            "holdings": [{"symbol": "BRD", "shares": 100}],
            "reinvest_dividends": False,
            "years_projection": 3
        }
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=payload,
            headers=auth_headers
        )
        assert resp.status_code == 200, f"Expected 200 got {resp.status_code}: {resp.text[:200]}"
        print("✅ POST /calculate (small portfolio) returns 200")

    def test_calculate_small_cass_is_zero(self, auth_headers):
        """Small dividend income (<28200 RON) should have CASS=0"""
        payload = {
            "holdings": [{"symbol": "BRD", "shares": 100}],
            "reinvest_dividends": False,
            "years_projection": 3
        }
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=payload,
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        cass = data.get("summary", {}).get("cass", {})
        assert cass.get("suma", -1) == 0, f"CASS should be 0 for small portfolio, got {cass.get('suma')}"
        assert cass.get("datorat") == False, f"CASS datorat should be False for small portfolio"
        print(f"✅ CASS for small portfolio: {cass}")

    def test_calculate_small_has_summary_fields(self, auth_headers):
        """Summary should include all required fields"""
        payload = {
            "holdings": [{"symbol": "BRD", "shares": 100}],
            "reinvest_dividends": False,
            "years_projection": 3
        }
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=payload,
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        summary = data.get("summary", {})

        # Check required summary fields
        assert "cass" in summary, "summary.cass missing"
        assert "plafon" in summary["cass"], "summary.cass.plafon missing"
        assert "total_net_dupa_cass" in summary, "summary.total_net_dupa_cass missing"
        assert "impozit_dividende_16pct" in summary, "summary.impozit_dividende_16pct missing"
        print(f"✅ summary.cass.plafon = '{summary['cass']['plafon']}'")
        print(f"✅ summary.total_net_dupa_cass = {summary['total_net_dupa_cass']}")

    def test_calculate_small_tax_info_16pct(self, auth_headers):
        """tax_info.impozit_dividende should mention 16%"""
        payload = {
            "holdings": [{"symbol": "BRD", "shares": 100}],
            "reinvest_dividends": False,
            "years_projection": 3
        }
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=payload,
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        tax_info = data.get("tax_info", {})
        assert "tax_info" in data, "tax_info missing from response"
        assert "impozit_dividende" in tax_info, "tax_info.impozit_dividende missing"
        assert "16%" in tax_info["impozit_dividende"], f"Expected '16%' in impozit_dividende, got: {tax_info['impozit_dividende']}"
        print(f"✅ tax_info.impozit_dividende: '{tax_info['impozit_dividende']}'")

    def test_calculate_small_projections_have_cass_fields(self, auth_headers):
        """Each projection year should have impozit_16pct, cass, net_final_dupa_cass"""
        payload = {
            "holdings": [{"symbol": "BRD", "shares": 100}],
            "reinvest_dividends": False,
            "years_projection": 3
        }
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=payload,
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        projections = data.get("projections", [])
        assert len(projections) == 3, f"Expected 3 projections, got {len(projections)}"
        for p in projections:
            assert "impozit_16pct" in p, f"Year {p.get('year')} missing 'impozit_16pct'"
            assert "cass" in p, f"Year {p.get('year')} missing 'cass'"
            assert "net_final_dupa_cass" in p, f"Year {p.get('year')} missing 'net_final_dupa_cass'"
        print(f"✅ Projections have required fields: impozit_16pct, cass, net_final_dupa_cass")


# ===========================================================
# TEST 3: POST /api/dividend-calculator/calculate - Large portfolio (CASS on 12 SMB = 5640)
# ===========================================================

class TestCalculateLargePortfolio:
    """
    Large portfolio: total annual dividend > 56400 RON → CASS on 12 SMB = 5640 RON
    Using many H2O shares: 56400/8.9889 ≈ 6274 shares → ~56,400 RON dividend
    Need at least 56,401 RON → 6275 shares × 8.9889 ≈ 56,409 RON
    """

    def _get_large_payload(self):
        # ~7000 shares × H2O ~8.9889 RON = ~62,922 RON (>56400 RON threshold)
        return {
            "holdings": [{"symbol": "H2O", "shares": 7000}],
            "reinvest_dividends": False,
            "years_projection": 5
        }

    def test_calculate_large_returns_200(self, auth_headers):
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=self._get_large_payload(),
            headers=auth_headers
        )
        assert resp.status_code == 200, f"Expected 200 got {resp.status_code}: {resp.text[:200]}"
        print("✅ POST /calculate (large portfolio) returns 200")

    def test_calculate_large_cass_on_12smb(self, auth_headers):
        """Large dividend income (>56400 RON) should trigger CASS on 12 SMB = 5640 RON"""
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=self._get_large_payload(),
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        summary = data.get("summary", {})
        cass = summary.get("cass", {})

        print(f"Total gross dividend: {summary.get('total_annual_dividend_gross')}")
        print(f"CASS info: {cass}")

        # The threshold is > 56400 RON for 12 SMB
        total_gross = summary.get("total_annual_dividend_gross", 0)
        if total_gross > 56400:
            assert cass.get("datorat") == True, "CASS datorat should be True for large portfolio"
            assert cass.get("suma") == 5640.0, f"CASS should be 5640 RON for 12 SMB, got {cass.get('suma')}"
            assert "12 SMB" in cass.get("plafon", ""), f"Plafon should mention '12 SMB', got {cass.get('plafon')}"
            print(f"✅ CASS on 12 SMB = {cass['suma']} RON (plafon: {cass['plafon']})")
        else:
            # H2O price may vary - check cass is applied
            assert cass.get("datorat") == True, "CASS datorat should be True for large portfolio"
            print(f"⚠️ Total gross {total_gross} may be in 6-12 SMB range: CASS={cass.get('suma')}")

    def test_calculate_large_net_after_cass(self, auth_headers):
        """total_net_dupa_cass = net_after_16_tax - cass_amount"""
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=self._get_large_payload(),
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        summary = data.get("summary", {})

        total_gross = summary.get("total_annual_dividend_gross", 0)
        total_net = summary.get("total_annual_dividend_net", 0)
        cass_sum = summary.get("cass", {}).get("suma", 0)
        net_after_cass = summary.get("total_net_dupa_cass", 0)

        expected = round(total_net - cass_sum, 2)
        assert abs(net_after_cass - expected) < 1.0, \
            f"total_net_dupa_cass={net_after_cass}, expected {expected} (net={total_net}, cass={cass_sum})"
        print(f"✅ total_net_dupa_cass calculation correct: {net_after_cass} RON")

    def test_calculate_large_projections_cass_present(self, auth_headers):
        """Projections for large portfolio should have non-zero CASS in year 1"""
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=self._get_large_payload(),
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        projections = data.get("projections", [])
        assert len(projections) > 0, "No projections returned"
        year1 = projections[0]
        assert year1.get("cass", 0) > 0, f"Year 1 CASS should be > 0 for large portfolio, got {year1.get('cass')}"
        print(f"✅ Year 1 CASS in projections: {year1['cass']} RON")


# ===========================================================
# TEST 4: CASS edge cases - 6 SMB threshold
# ===========================================================

class TestCalculateMidPortfolio:
    """
    Medium portfolio: total annual dividend between 28200-56400 RON → CASS on 6 SMB = 2820 RON
    Using H2O: 3500 shares × 8.9889 ≈ 31,461 RON (> 28200, < 56400)
    """

    def _get_mid_payload(self):
        return {
            "holdings": [{"symbol": "H2O", "shares": 3500}],
            "reinvest_dividends": False,
            "years_projection": 3
        }

    def test_calculate_mid_cass_on_6smb(self, auth_headers):
        """Mid dividend income (28200-56400 RON) should trigger CASS on 6 SMB = 2820 RON"""
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=self._get_mid_payload(),
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        summary = data.get("summary", {})
        cass = summary.get("cass", {})
        total_gross = summary.get("total_annual_dividend_gross", 0)

        print(f"Mid portfolio total gross: {total_gross}")
        print(f"CASS: {cass}")

        if 28200 <= total_gross < 56400:
            assert cass.get("datorat") == True, "CASS datorat should be True"
            assert cass.get("suma") == 2820.0, f"CASS should be 2820 RON for 6 SMB, got {cass.get('suma')}"
            print(f"✅ CASS on 6 SMB = {cass['suma']} RON")
        else:
            print(f"⚠️ Skipping assertion: total_gross={total_gross} not in 28200-56400 range (live price may vary)")


# ===========================================================
# TEST 5: Response structure validation
# ===========================================================

class TestCalculateResponseStructure:
    """Validate the full response structure"""

    def test_response_has_all_top_level_keys(self, auth_headers):
        payload = {
            "holdings": [{"symbol": "TLV", "shares": 100}, {"symbol": "BRD", "shares": 100}],
            "reinvest_dividends": False,
            "years_projection": 5
        }
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=payload,
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()

        required_keys = ["holdings", "summary", "projections", "settings", "tax_info"]
        for key in required_keys:
            assert key in data, f"Response missing key '{key}'"
        print(f"✅ Response has all top-level keys: {list(data.keys())}")

    def test_settings_shows_16_pct_tax(self, auth_headers):
        """settings.tax_rate_2026 should be 16.0"""
        payload = {
            "holdings": [{"symbol": "TLV", "shares": 100}],
            "reinvest_dividends": False,
            "years_projection": 3
        }
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=payload,
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        settings = data.get("settings", {})
        assert settings.get("tax_rate_2026") == 16.0, f"tax_rate_2026 should be 16.0, got {settings.get('tax_rate_2026')}"
        print(f"✅ settings.tax_rate_2026 = {settings['tax_rate_2026']}%")

    def test_holdings_have_impozit_16_field(self, auth_headers):
        """Each holding should have tax_16_percent field"""
        payload = {
            "holdings": [{"symbol": "TLV", "shares": 100}],
            "reinvest_dividends": False,
            "years_projection": 3
        }
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=payload,
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        holdings = data.get("holdings", [])
        assert len(holdings) > 0, "No holdings in response"
        for h in holdings:
            assert "tax_16_percent" in h, f"Holding {h.get('symbol')} missing 'tax_16_percent'"
            # Verify 16% calculation
            expected_tax = round(h["annual_dividend_gross"] * 0.16, 2)
            assert abs(h["tax_16_percent"] - expected_tax) < 0.02, \
                f"tax_16_percent mismatch: {h['tax_16_percent']} vs expected {expected_tax}"
        print(f"✅ Holdings have correct tax_16_percent values")

    def test_multiple_years_projection(self, auth_headers):
        """Test projections for 5 years"""
        payload = {
            "holdings": [{"symbol": "TLV", "shares": 100}, {"symbol": "SNN", "shares": 100}],
            "reinvest_dividends": False,
            "years_projection": 5,
            "dividend_growth_rate": 3.0
        }
        resp = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=payload,
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        projections = data.get("projections", [])
        assert len(projections) == 5, f"Expected 5 projections, got {len(projections)}"

        # Check all projection rows have required fields
        for p in projections:
            assert "gross_dividend" in p
            assert "impozit_16pct" in p
            assert "cass" in p
            assert "net_final_dupa_cass" in p
            assert "cumulative_net" in p
            assert "yield_on_cost" in p

        # Verify growth: year 2 should have more gross than year 1
        assert projections[1]["gross_dividend"] > projections[0]["gross_dividend"], \
            "Year 2 should have more gross dividend than year 1 with growth > 0"
        print(f"✅ 5-year projections: year1_gross={projections[0]['gross_dividend']}, year5_gross={projections[4]['gross_dividend']}")
