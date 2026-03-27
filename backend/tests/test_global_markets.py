"""
Backend tests for Global Markets page (FinRomania 2.0)
Tests: commodities with real prices, NASDAQ 100 in ticker, heatmap indices, chart endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Demo token obtained from /api/auth/demo-login?secret=finromania-demo-2026
DEMO_SECRET = "finromania-demo-2026"


@pytest.fixture(scope="module")
def demo_token():
    """Get demo session token for authenticated tests"""
    resp = requests.get(f"{BASE_URL}/api/auth/demo-login", params={"secret": DEMO_SECRET})
    assert resp.status_code == 200, f"Demo login failed: {resp.text}"
    return resp.json().get("session_token", "")


@pytest.fixture(scope="module")
def auth_headers(demo_token):
    return {"Authorization": f"Bearer {demo_token}"}


class TestGlobalOverview:
    """Test /api/global/overview - main endpoint for global markets page"""

    def test_overview_returns_200(self):
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text[:200]}"

    def test_overview_has_required_sections(self):
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        data = resp.json()
        for section in ["indices", "commodities", "crypto", "forex", "sentiment", "market_status"]:
            assert section in data, f"Missing section: {section}"

    def test_commodities_count_is_four(self):
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        commodities = resp.json().get("commodities", [])
        assert len(commodities) == 4, f"Expected 4 commodities, got {len(commodities)}: {[c['name'] for c in commodities]}"

    def test_gold_price_is_real_not_etf(self):
        """Gold price should be ~$4421/oz (real spot), NOT ~$407 (GLD ETF)"""
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        commodities = resp.json().get("commodities", [])
        gold = next((c for c in commodities if c["name"] == "Aur"), None)
        assert gold is not None, "Gold (Aur) commodity not found"
        # Real gold is in $3000-$5000 range; GLD ETF is ~$200-$450
        assert gold["price"] > 1000, f"Gold price {gold['price']} looks too low - might be GLD ETF price"
        assert gold["symbol"] == "XAUUSD.FOREX", f"Expected XAUUSD.FOREX, got {gold['symbol']}"

    def test_gold_source_is_eodhd_eod_spot(self):
        """Gold should use eodhd_eod_spot or eodhd_intraday_live, NOT GLD.US"""
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        commodities = resp.json().get("commodities", [])
        gold = next((c for c in commodities if c["name"] == "Aur"), None)
        assert gold is not None, "Gold not found"
        assert gold.get("source") in ("eodhd_eod_spot", "eodhd_intraday_live", "eodhd_realtime"), \
            f"Unexpected gold source: {gold.get('source')} - should not use GLD ETF"

    def test_silver_present_with_real_price(self):
        """Silver (Argint) should be present with real spot price ~$68/oz"""
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        commodities = resp.json().get("commodities", [])
        silver = next((c for c in commodities if c["name"] == "Argint"), None)
        assert silver is not None, "Silver (Argint) not found in commodities"
        assert silver["price"] > 10, f"Silver price {silver['price']} looks too low"
        assert silver["symbol"] == "XAGUSD.FOREX", f"Expected XAGUSD.FOREX, got {silver['symbol']}"

    def test_oil_labeled_as_etf(self):
        """Oil should be labeled as 'Petrol (ETF USO)' not 'Petrol WTI'"""
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        commodities = resp.json().get("commodities", [])
        oil = next((c for c in commodities if "Petrol" in c["name"]), None)
        assert oil is not None, "Oil/Petrol commodity not found"
        assert "ETF" in oil["name"] or "USO" in oil["name"], \
            f"Oil should be labeled as ETF, got: {oil['name']}"

    def test_nasdaq_100_in_indices(self):
        """NASDAQ 100 (NDX) should be present, not NASDAQ Composite"""
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        indices = resp.json().get("indices", [])
        nasdaq = next((i for i in indices if "NASDAQ" in i["name"]), None)
        assert nasdaq is not None, "NASDAQ index not found"
        assert "100" in nasdaq["name"], f"Should be NASDAQ 100, got: {nasdaq['name']}"
        # NASDAQ 100 is ~22000-24000 range; Composite was ~21145
        assert nasdaq["price"] > 20000, f"NASDAQ price {nasdaq['price']} seems too low for NASDAQ 100"

    def test_sp500_price_range(self):
        """S&P 500 should be in ~6000-7000 range"""
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        indices = resp.json().get("indices", [])
        sp500 = next((i for i in indices if "S&P" in i["name"] or "GSPC" in i["symbol"]), None)
        assert sp500 is not None, "S&P 500 not found"
        assert 5000 < sp500["price"] < 9000, f"S&P 500 price {sp500['price']} out of expected range"

    def test_overview_source_is_eodhd(self):
        """Source should be EODHD, not yfinance"""
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        data = resp.json()
        source = data.get("source", "")
        assert "EODHD" in source or "eodhd" in source.lower(), \
            f"Expected EODHD source, got: {source}"

    def test_sentiment_structure(self):
        resp = requests.get(f"{BASE_URL}/api/global/overview")
        sentiment = resp.json().get("sentiment", {})
        assert "gainers" in sentiment
        assert "losers" in sentiment
        assert "avg_change" in sentiment
        assert "status" in sentiment


class TestTickerBarEndpoint:
    """Test /api/stocks/global - used by TickerBar component"""

    def test_stocks_global_returns_list(self):
        resp = requests.get(f"{BASE_URL}/api/stocks/global")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"

    def test_ticker_has_nasdaq(self):
        resp = requests.get(f"{BASE_URL}/api/stocks/global")
        data = resp.json()
        nasdaq_items = [i for i in data if "NASDAQ" in i.get("name", "")]
        assert len(nasdaq_items) > 0, "NASDAQ not found in ticker bar data"

    def test_ticker_nasdaq_price_matches_eodhd(self):
        """NASDAQ in ticker should show EODHD price ~23300, not yfinance NASDAQ Composite ~21145"""
        resp = requests.get(f"{BASE_URL}/api/stocks/global")
        data = resp.json()
        nasdaq = next((i for i in data if "NASDAQ" in i.get("name", "")), None)
        if nasdaq:
            # NASDAQ Composite (old yfinance) was ~21145
            # NASDAQ 100 (EODHD) is ~23300
            # Either is acceptable if > 20000
            assert nasdaq["price"] > 20000, f"NASDAQ price {nasdaq['price']} seems low - check if using old yfinance data"
            print(f"NASDAQ ticker: {nasdaq['name']} - {nasdaq['price']} - source: {nasdaq.get('source','?')}")


class TestCommoditiesEndpoint:
    """Test /api/global/commodities endpoint"""

    def test_commodities_returns_200(self):
        resp = requests.get(f"{BASE_URL}/api/global/commodities")
        assert resp.status_code == 200

    def test_commodities_has_gold_and_silver(self):
        resp = requests.get(f"{BASE_URL}/api/global/commodities")
        commodities = resp.json().get("commodities", [])
        names = [c["name"] for c in commodities]
        assert "Aur" in names, f"Gold (Aur) missing. Found: {names}"
        assert "Argint" in names, f"Silver (Argint) missing. Found: {names}"

    def test_gold_real_price_via_commodities(self):
        resp = requests.get(f"{BASE_URL}/api/global/commodities")
        commodities = resp.json().get("commodities", [])
        gold = next((c for c in commodities if c["name"] == "Aur"), None)
        assert gold is not None
        assert gold["price"] > 1000, f"Gold price {gold['price']} too low - likely ETF price (GLD ~$407)"
        assert gold["unit"] == "USD/oz", f"Gold unit should be USD/oz, got: {gold.get('unit')}"


class TestChartEndpoint:
    """Test /api/global/chart/{symbol} endpoint"""

    def test_gold_chart_returns_data(self):
        resp = requests.get(f"{BASE_URL}/api/global/chart/XAUUSD.FOREX", params={"period": "1mo", "interval": "1d"})
        assert resp.status_code == 200, f"Chart failed: {resp.text[:200]}"
        data = resp.json()
        assert data.get("data_points", 0) > 0, "No chart data points returned"

    def test_gold_chart_prices_are_real(self):
        """Chart prices for gold should be in real range, not ETF range"""
        resp = requests.get(f"{BASE_URL}/api/global/chart/XAUUSD.FOREX", params={"period": "1mo", "interval": "1d"})
        data = resp.json()
        current = data.get("current_price", 0)
        assert current > 1000, f"Gold chart current price {current} too low - likely GLD ETF"

    def test_sp500_chart_works(self):
        resp = requests.get(f"{BASE_URL}/api/global/chart/GSPC.INDX", params={"period": "1mo", "interval": "1d"})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("data_points", 0) > 0

    def test_bitcoin_chart_works(self):
        resp = requests.get(f"{BASE_URL}/api/global/chart/BTC-USD.CC", params={"period": "1mo", "interval": "1d"})
        # BTC chart might return 404 if no data, that's acceptable
        assert resp.status_code in (200, 404), f"Unexpected status: {resp.status_code}"


class TestIndicesEndpoint:
    """Test /api/global/indices endpoint"""

    def test_indices_returns_200(self):
        resp = requests.get(f"{BASE_URL}/api/global/indices")
        assert resp.status_code == 200

    def test_indices_has_major_markets(self):
        resp = requests.get(f"{BASE_URL}/api/global/indices")
        data = resp.json()
        indices = data.get("indices", [])
        names = [i["name"] for i in indices]
        for expected in ["S&P 500", "NASDAQ 100", "Dow Jones"]:
            assert expected in names, f"{expected} not found in indices. Got: {names}"

    def test_indices_source_is_eodhd(self):
        resp = requests.get(f"{BASE_URL}/api/global/indices")
        indices = resp.json().get("indices", [])
        for idx in indices:
            src = idx.get("source", "")
            assert "eodhd" in src or "db_cache" in src, \
                f"Index {idx['name']} has unexpected source: {src} - should not use yfinance"
