"""
Test BVB.ro Dividend Scraping Feature - FinRomania 2.0
Tests all new BVB dividend endpoints and integration with existing features.
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://finromania-pro-2.preview.emergentagent.com')

class TestBVBDividendsAPI:
    """Tests for /api/bvb-dividends/* endpoints — BVB.ro scraped data"""
    
    def test_get_all_bvb_dividends(self):
        """GET /api/bvb-dividends/all — should return 99 dividend records from BVB.ro"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/all")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "dividends" in data, "Response should contain 'dividends' key"
        assert "count" in data, "Response should contain 'count' key"
        assert "source" in data, "Response should contain 'source' key"
        assert "last_scraped" in data, "Response should contain 'last_scraped' key"
        
        # Verify we have dividend records
        assert data["count"] >= 90, f"Expected at least 90 dividends, got {data['count']}"
        assert "BVB" in data["source"], f"Source should mention BVB, got {data['source']}"
        
        # Verify dividend record structure
        if data["dividends"]:
            div = data["dividends"][0]
            assert "symbol" in div, "Dividend should have 'symbol'"
            assert "company" in div, "Dividend should have 'company'"
            assert "dividend_per_share" in div, "Dividend should have 'dividend_per_share'"
            assert "ex_date" in div, "Dividend should have 'ex_date'"
            assert "source" in div, "Dividend should have 'source'"
            assert div["source"] == "BVB.ro", f"Source should be BVB.ro, got {div['source']}"
        
        print(f"✅ GET /api/bvb-dividends/all: {data['count']} dividends, source: {data['source']}")
    
    def test_get_latest_dividends(self):
        """GET /api/bvb-dividends/latest — should return latest dividend per symbol sorted by yield"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/latest")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "dividends" in data, "Response should contain 'dividends' key"
        assert "count" in data, "Response should contain 'count' key"
        
        # Verify sorted by yield (descending)
        dividends = data["dividends"]
        if len(dividends) >= 2:
            for i in range(len(dividends) - 1):
                yield_current = dividends[i].get("dividend_yield", 0)
                yield_next = dividends[i + 1].get("dividend_yield", 0)
                assert yield_current >= yield_next, f"Dividends should be sorted by yield descending"
        
        print(f"✅ GET /api/bvb-dividends/latest: {data['count']} unique symbols")
    
    def test_get_upcoming_dividends(self):
        """GET /api/bvb-dividends/upcoming — should return dividends with ex_date >= today"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/upcoming")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "dividends" in data, "Response should contain 'dividends' key"
        assert "count" in data, "Response should contain 'count' key"
        
        today = datetime.now().strftime("%Y-%m-%d")
        for div in data["dividends"]:
            ex_date = div.get("ex_date", "")
            assert ex_date >= today, f"Upcoming dividend ex_date {ex_date} should be >= {today}"
        
        print(f"✅ GET /api/bvb-dividends/upcoming: {data['count']} upcoming dividends")
    
    def test_get_scrape_status(self):
        """GET /api/bvb-dividends/status — should show last_scraped timestamp and record counts"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "dividends" in data, "Response should contain 'dividends' key"
        assert "calendar" in data, "Response should contain 'calendar' key"
        assert "source" in data, "Response should contain 'source' key"
        
        # Verify dividends meta
        div_meta = data["dividends"]
        assert "last_scraped" in div_meta or "status" in div_meta, "Dividends meta should have last_scraped or status"
        if "record_count" in div_meta:
            assert div_meta["record_count"] >= 90, f"Expected at least 90 dividend records"
        
        print(f"✅ GET /api/bvb-dividends/status: dividends={div_meta}, calendar={data['calendar']}")
    
    def test_get_trailing_dividend_tlv(self):
        """GET /api/bvb-dividends/trailing/TLV — should return trailing 12M dividend for TLV"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/trailing/TLV")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["symbol"] == "TLV", f"Symbol should be TLV, got {data.get('symbol')}"
        assert "trailing_annual_dividend" in data, "Response should contain 'trailing_annual_dividend'"
        assert "payments_count" in data, "Response should contain 'payments_count'"
        assert "payments" in data, "Response should contain 'payments' list"
        assert "source" in data, "Response should contain 'source'"
        
        assert data["trailing_annual_dividend"] > 0, "TLV should have positive trailing dividend"
        assert "BVB" in data["source"], f"Source should mention BVB, got {data['source']}"
        
        print(f"✅ GET /api/bvb-dividends/trailing/TLV: {data['trailing_annual_dividend']} RON ({data['payments_count']} payments)")
    
    def test_get_dividend_history_snp(self):
        """GET /api/bvb-dividends/history/SNP — should return dividend history for SNP"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/history/SNP")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["symbol"] == "SNP", f"Symbol should be SNP, got {data.get('symbol')}"
        assert "history" in data, "Response should contain 'history'"
        assert "count" in data, "Response should contain 'count'"
        assert "source" in data, "Response should contain 'source'"
        
        assert data["count"] > 0, "SNP should have dividend history"
        assert "BVB" in data["source"], f"Source should mention BVB, got {data['source']}"
        
        # Verify history is sorted by ex_date descending
        history = data["history"]
        if len(history) >= 2:
            for i in range(len(history) - 1):
                assert history[i].get("ex_date", "") >= history[i + 1].get("ex_date", ""), "History should be sorted descending"
        
        print(f"✅ GET /api/bvb-dividends/history/SNP: {data['count']} records, company: {data.get('company')}")


class TestDividendCalculatorWithBVB:
    """Tests for /api/dividend-calculator/* — should use BVB.ro data as primary source"""
    
    def test_get_dividend_stocks_bvb_source(self):
        """GET /api/dividend-calculator/stocks — should show BVB.ro as data_source for most stocks"""
        response = requests.get(f"{BASE_URL}/api/dividend-calculator/stocks")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "stocks" in data, "Response should contain 'stocks'"
        assert "count" in data, "Response should contain 'count'"
        assert "data_sources" in data, "Response should contain 'data_sources'"
        
        stocks = data["stocks"]
        assert len(stocks) > 0, "Should have dividend stocks"
        
        # Count BVB.ro sourced stocks
        bvb_count = sum(1 for s in stocks if s.get("data_source", "").startswith("BVB"))
        total = len(stocks)
        bvb_percentage = (bvb_count / total * 100) if total > 0 else 0
        
        print(f"✅ GET /api/dividend-calculator/stocks: {total} stocks, {bvb_count} from BVB.ro ({bvb_percentage:.1f}%)")
        
        # Verify stock structure
        if stocks:
            stock = stocks[0]
            assert "symbol" in stock, "Stock should have 'symbol'"
            assert "dividend_per_share" in stock, "Stock should have 'dividend_per_share'"
            assert "dividend_yield" in stock, "Stock should have 'dividend_yield'"
            assert "data_source" in stock, "Stock should have 'data_source'"
    
    def test_calculate_dividends_with_bvb_data(self):
        """POST /api/dividend-calculator/calculate — calculate with BVB.ro data (TLV 100, SNP 500)"""
        payload = {
            "holdings": [
                {"symbol": "TLV", "shares": 100},
                {"symbol": "SNP", "shares": 500}
            ],
            "reinvest_dividends": False,
            "years_projection": 5,
            "dividend_growth_rate": 3.0
        }
        
        response = requests.post(
            f"{BASE_URL}/api/dividend-calculator/calculate",
            json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "holdings" in data, "Response should contain 'holdings'"
        assert "summary" in data, "Response should contain 'summary'"
        assert "projections" in data, "Response should contain 'projections'"
        assert "data_source" in data, "Response should contain 'data_source'"
        
        # Verify holdings
        holdings = data["holdings"]
        assert len(holdings) >= 1, "Should have at least 1 holding calculated"
        
        # Verify summary
        summary = data["summary"]
        assert "total_investment" in summary, "Summary should have 'total_investment'"
        assert "total_annual_dividend_gross" in summary, "Summary should have 'total_annual_dividend_gross'"
        assert "total_annual_dividend_net" in summary, "Summary should have 'total_annual_dividend_net'"
        assert summary["total_annual_dividend_gross"] > 0, "Should have positive dividend"
        
        # Verify projections
        projections = data["projections"]
        assert len(projections) == 5, f"Should have 5 years projection, got {len(projections)}"
        
        # Check if BVB.ro is mentioned in data source
        assert "BVB" in data["data_source"], f"Data source should mention BVB, got {data['data_source']}"
        
        print(f"✅ POST /api/dividend-calculator/calculate: investment={summary['total_investment']}, gross={summary['total_annual_dividend_gross']}, net={summary['total_annual_dividend_net']}")


class TestDividendCalendarWithBVB:
    """Tests for /api/calendar/* — should use BVB.ro data"""
    
    def test_get_calendar_dividends_bvb_source(self):
        """GET /api/calendar/dividends — should show BVB.ro data_source, upcoming dividends"""
        response = requests.get(f"{BASE_URL}/api/calendar/dividends")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "dividends" in data, "Response should contain 'dividends'"
        assert "count" in data, "Response should contain 'count'"
        assert "data_source" in data, "Response should contain 'data_source'"
        
        # Verify BVB.ro source
        assert "BVB" in data["data_source"], f"Data source should mention BVB, got {data['data_source']}"
        
        # Verify dividend structure
        dividends = data["dividends"]
        if dividends:
            div = dividends[0]
            assert "symbol" in div, "Dividend should have 'symbol'"
            assert "ex_date" in div, "Dividend should have 'ex_date'"
            assert "data_source" in div, "Dividend should have 'data_source'"
        
        print(f"✅ GET /api/calendar/dividends: {data['count']} dividends, source: {data['data_source']}")
    
    def test_get_dividend_kings_bvb_source(self):
        """GET /api/calendar/dividend-kings — should show top yields from BVB.ro data"""
        response = requests.get(f"{BASE_URL}/api/calendar/dividend-kings")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "dividend_kings" in data, "Response should contain 'dividend_kings'"
        assert "count" in data, "Response should contain 'count'"
        assert "data_source" in data, "Response should contain 'data_source'"
        
        # Verify BVB.ro source
        assert "BVB" in data["data_source"], f"Data source should mention BVB, got {data['data_source']}"
        
        # Verify kings are sorted by yield
        kings = data["dividend_kings"]
        if len(kings) >= 2:
            for i in range(len(kings) - 1):
                yield_current = kings[i].get("dividend_yield", 0)
                yield_next = kings[i + 1].get("dividend_yield", 0)
                assert yield_current >= yield_next, "Kings should be sorted by yield descending"
        
        print(f"✅ GET /api/calendar/dividend-kings: {data['count']} kings, top: {kings[0]['symbol'] if kings else 'N/A'} ({kings[0]['dividend_yield'] if kings else 0}%)")


class TestBVBDividendsEdgeCases:
    """Edge case tests for BVB dividend endpoints"""
    
    def test_trailing_dividend_nonexistent_symbol(self):
        """GET /api/bvb-dividends/trailing/XXXXX — should return 404 for non-existent symbol"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/trailing/XXXXX")
        assert response.status_code == 404, f"Expected 404 for non-existent symbol, got {response.status_code}"
        print("✅ GET /api/bvb-dividends/trailing/XXXXX: correctly returns 404")
    
    def test_history_nonexistent_symbol(self):
        """GET /api/bvb-dividends/history/XXXXX — should return 404 for non-existent symbol"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/history/XXXXX")
        assert response.status_code == 404, f"Expected 404 for non-existent symbol, got {response.status_code}"
        print("✅ GET /api/bvb-dividends/history/XXXXX: correctly returns 404")
    
    def test_trailing_dividend_case_insensitive(self):
        """GET /api/bvb-dividends/trailing/tlv — should work with lowercase symbol"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/trailing/tlv")
        assert response.status_code == 200, f"Expected 200 for lowercase symbol, got {response.status_code}"
        data = response.json()
        assert data["symbol"] == "TLV", "Symbol should be normalized to uppercase"
        print("✅ GET /api/bvb-dividends/trailing/tlv: correctly handles lowercase")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
