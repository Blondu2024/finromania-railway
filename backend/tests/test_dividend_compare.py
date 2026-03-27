"""
Test suite for BVB Dividends Compare endpoint
Tests the new comparison feature: /api/bvb-dividends/compare
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDividendCompare:
    """Tests for /api/bvb-dividends/compare endpoint"""

    def test_compare_three_symbols_success(self):
        """Compare 3 stocks (TLV, BRD, SNP) - should return chart_data, stocks with scores"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/compare?symbols=TLV,BRD,SNP")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        
        # Verify structure
        assert "symbols" in data, "Response should have 'symbols' field"
        assert "stocks" in data, "Response should have 'stocks' field"
        assert "chart_data" in data, "Response should have 'chart_data' field"
        assert "years" in data, "Response should have 'years' field"
        assert "source" in data, "Response should have 'source' field"
        
        # Verify symbols list
        assert data["symbols"] == ["TLV", "BRD", "SNP"], f"Expected ['TLV', 'BRD', 'SNP'], got {data['symbols']}"
        
        # Verify stocks data
        assert len(data["stocks"]) == 3, f"Expected 3 stocks, got {len(data['stocks'])}"
        for sym in ["TLV", "BRD", "SNP"]:
            assert sym in data["stocks"], f"Stock {sym} should be in response"
            stock = data["stocks"][sym]
            assert "symbol" in stock
            assert "company" in stock
            assert "price" in stock
            assert "current_yield" in stock
            assert "cagr" in stock
            assert "consecutive_years" in stock
            assert "dividend_score" in stock
            assert "score" in stock["dividend_score"]
            assert "rating" in stock["dividend_score"]
            assert "breakdown" in stock["dividend_score"]
        
        # Verify chart_data structure
        assert len(data["chart_data"]) > 0, "chart_data should not be empty"
        for row in data["chart_data"]:
            assert "year" in row, "Each chart row should have 'year'"
            for sym in ["TLV", "BRD", "SNP"]:
                assert sym in row, f"Each chart row should have '{sym}' dividend value"
        
        print(f"✅ Compare 3 symbols: {len(data['chart_data'])} years of data, source: {data['source']}")

    def test_compare_two_symbols_success(self):
        """Compare 2 stocks (minimum allowed)"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/compare?symbols=TLV,BRD")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert len(data["symbols"]) == 2
        assert len(data["stocks"]) == 2
        print("✅ Compare 2 symbols works correctly")

    def test_compare_four_symbols_success(self):
        """Compare 4 stocks (maximum allowed)"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/compare?symbols=TLV,BRD,SNP,SNG")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert len(data["symbols"]) == 4
        assert len(data["stocks"]) == 4
        print("✅ Compare 4 symbols works correctly")

    def test_compare_one_symbol_returns_400(self):
        """Single symbol should return 400 (minimum 2 required)"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/compare?symbols=TLV")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data
        assert "Minim 2" in data["detail"] or "minim 2" in data["detail"].lower()
        print("✅ Single symbol correctly returns 400")

    def test_compare_five_symbols_returns_400(self):
        """5 symbols should return 400 (maximum 4 allowed)"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/compare?symbols=TLV,BRD,SNP,H2O,SNN")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        data = response.json()
        assert "detail" in data
        assert "Maxim 4" in data["detail"] or "maxim 4" in data["detail"].lower()
        print("✅ 5 symbols correctly returns 400")

    def test_compare_lowercase_symbols_converted(self):
        """Lowercase symbols should be converted to uppercase"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/compare?symbols=tlv,brd")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["symbols"] == ["TLV", "BRD"], "Symbols should be uppercase"
        print("✅ Lowercase symbols converted to uppercase")

    def test_compare_dividend_scores_present(self):
        """Verify dividend scores have correct structure"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/compare?symbols=TLV,SNP")
        assert response.status_code == 200
        
        data = response.json()
        for sym in ["TLV", "SNP"]:
            score = data["stocks"][sym]["dividend_score"]
            assert 0 <= score["score"] <= 100, f"Score should be 0-100, got {score['score']}"
            assert score["rating"] in ["Excelent", "Foarte Bun", "Bun", "Mediu", "Slab"]
            
            breakdown = score["breakdown"]
            assert "stability" in breakdown
            assert "growth" in breakdown
            assert "yield_score" in breakdown
            
            # Verify breakdown sums approximately to total (with rounding tolerance)
            total_breakdown = breakdown["stability"] + breakdown["growth"] + breakdown["yield_score"]
            assert abs(total_breakdown - score["score"]) <= 2, f"Breakdown sum {total_breakdown} should be close to score {score['score']}"
        
        print("✅ Dividend scores have correct structure and values")

    def test_compare_chart_data_years_sorted(self):
        """Chart data years should be sorted ascending"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/compare?symbols=TLV,BRD,SNP")
        assert response.status_code == 200
        
        data = response.json()
        years = [row["year"] for row in data["chart_data"]]
        assert years == sorted(years), "Years should be sorted ascending"
        assert data["years"] == sorted(data["years"]), "Years list should be sorted"
        print(f"✅ Chart data years sorted: {years[0]} to {years[-1]}")

    def test_compare_source_field(self):
        """Source should indicate BVB.ro + EODHD"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/compare?symbols=TLV,BRD")
        assert response.status_code == 200
        
        data = response.json()
        assert "BVB.ro" in data["source"] or "EODHD" in data["source"]
        print(f"✅ Source field: {data['source']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
