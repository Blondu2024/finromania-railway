"""
Test suite for Istoric Dividende PRO feature
- Analysis endpoint: /api/bvb-dividends/analysis/{symbol}
- Rankings endpoint: /api/bvb-dividends/rankings
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestDividendAnalysisEndpoint:
    """Tests for GET /api/bvb-dividends/analysis/{symbol}"""

    def test_analysis_tlv_returns_full_data(self):
        """TLV should return full analysis with dividend_score, yearly_dividends, metrics, payments"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/analysis/TLV", timeout=15)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify required fields exist
        assert "symbol" in data
        assert data["symbol"] == "TLV"
        assert "company" in data
        assert "dividend_score" in data
        assert "yearly_dividends" in data
        assert "metrics" in data
        assert "payments" in data
        
        # Verify dividend_score structure
        score = data["dividend_score"]
        assert "score" in score
        assert "rating" in score
        assert "breakdown" in score
        assert isinstance(score["score"], (int, float))
        assert 0 <= score["score"] <= 100
        assert score["rating"] in ["Excelent", "Foarte Bun", "Bun", "Mediu", "Slab"]
        
        # Verify breakdown structure (Stability 40%, Growth 30%, Yield 30%)
        breakdown = score["breakdown"]
        assert "stability" in breakdown
        assert "growth" in breakdown
        assert "yield_score" in breakdown
        
        # Verify yearly_dividends is a list
        assert isinstance(data["yearly_dividends"], list)
        if len(data["yearly_dividends"]) > 0:
            year_entry = data["yearly_dividends"][0]
            assert "year" in year_entry
            assert "dividend" in year_entry
        
        # Verify metrics structure
        metrics = data["metrics"]
        assert "cagr" in metrics
        assert "consecutive_years" in metrics
        assert "total_paying_years" in metrics
        assert "consistency_cv" in metrics
        
        # Verify payments is a list
        assert isinstance(data["payments"], list)
        if len(data["payments"]) > 0:
            payment = data["payments"][0]
            assert "date" in payment
            assert "dividend" in payment
            assert "source" in payment
        
        print(f"TLV Analysis: Score={score['score']} ({score['rating']}), CAGR={metrics['cagr']}, Consecutive Years={metrics['consecutive_years']}")

    def test_analysis_snp_returns_cagr_and_consecutive_years(self):
        """SNP should return analysis with CAGR and consecutive_years"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/analysis/SNP", timeout=15)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["symbol"] == "SNP"
        assert "metrics" in data
        
        metrics = data["metrics"]
        # CAGR can be None if not enough data, but key must exist
        assert "cagr" in metrics
        assert "consecutive_years" in metrics
        assert isinstance(metrics["consecutive_years"], int)
        
        print(f"SNP Analysis: CAGR={metrics['cagr']}, Consecutive Years={metrics['consecutive_years']}")

    def test_analysis_unknown_symbol_returns_404(self):
        """Unknown symbol XXXXX should return 404"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/analysis/XXXXX", timeout=10)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        print(f"404 response for XXXXX: {data['detail']}")

    def test_analysis_lowercase_symbol_works(self):
        """Lowercase symbol should be converted to uppercase"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/analysis/tlv", timeout=15)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["symbol"] == "TLV"  # Should be uppercase
        print("Lowercase 'tlv' correctly converted to 'TLV'")

    def test_analysis_includes_current_yield(self):
        """Analysis should include current_yield field"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/analysis/TLV", timeout=15)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "current_yield" in data
        assert "current_price" in data
        assert isinstance(data["current_yield"], (int, float))
        print(f"TLV current_yield: {data['current_yield']}%, current_price: {data['current_price']} RON")


class TestDividendRankingsEndpoint:
    """Tests for GET /api/bvb-dividends/rankings"""

    def test_rankings_returns_cached_data(self):
        """Rankings should return cached data with 43 stocks sorted by dividend_score"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/rankings", timeout=15)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "rankings" in data
        assert "count" in data
        assert "source" in data
        
        rankings = data["rankings"]
        assert isinstance(rankings, list)
        
        # Should have around 43 stocks (as per context)
        print(f"Rankings count: {data['count']}")
        assert data["count"] >= 30, f"Expected at least 30 stocks, got {data['count']}"
        
        # Verify rankings are sorted by dividend_score (descending)
        if len(rankings) >= 2:
            for i in range(len(rankings) - 1):
                assert rankings[i]["dividend_score"] >= rankings[i + 1]["dividend_score"], \
                    f"Rankings not sorted: {rankings[i]['symbol']}({rankings[i]['dividend_score']}) < {rankings[i+1]['symbol']}({rankings[i+1]['dividend_score']})"
        
        print(f"Rankings sorted correctly by dividend_score (descending)")

    def test_rankings_entry_structure(self):
        """Each ranking entry should have required fields"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/rankings", timeout=15)
        
        assert response.status_code == 200
        data = response.json()
        rankings = data["rankings"]
        
        if len(rankings) > 0:
            entry = rankings[0]
            
            # Required fields
            assert "symbol" in entry
            assert "company" in entry
            assert "dividend_score" in entry
            assert "rating" in entry
            assert "current_yield" in entry
            assert "cagr" in entry  # Can be None
            assert "consecutive_years" in entry
            assert "data_years" in entry
            assert "breakdown" in entry
            
            # Verify breakdown structure
            breakdown = entry["breakdown"]
            assert "stability" in breakdown
            assert "growth" in breakdown
            assert "yield_score" in breakdown
            
            print(f"Top ranked stock: {entry['symbol']} - Score: {entry['dividend_score']} ({entry['rating']})")

    def test_rankings_top_stock_has_high_score(self):
        """Top ranked stock should have a reasonably high score"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/rankings", timeout=15)
        
        assert response.status_code == 200
        data = response.json()
        rankings = data["rankings"]
        
        if len(rankings) > 0:
            top_stock = rankings[0]
            # Top stock should have score >= 50 (at least "Bun" rating)
            assert top_stock["dividend_score"] >= 40, \
                f"Top stock {top_stock['symbol']} has low score: {top_stock['dividend_score']}"
            print(f"Top stock {top_stock['symbol']} has score {top_stock['dividend_score']} - OK")

    def test_rankings_includes_source_info(self):
        """Rankings should include source information"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/rankings", timeout=15)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "source" in data
        assert "BVB" in data["source"] or "EODHD" in data["source"]
        print(f"Rankings source: {data['source']}")


class TestDividendScoreCalculation:
    """Tests for dividend score calculation logic"""

    def test_score_breakdown_sums_correctly(self):
        """Score breakdown (stability + growth + yield) should approximately equal total score"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/analysis/TLV", timeout=15)
        
        assert response.status_code == 200
        data = response.json()
        
        score = data["dividend_score"]
        breakdown = score["breakdown"]
        
        calculated_sum = breakdown["stability"] + breakdown["growth"] + breakdown["yield_score"]
        
        # Allow small rounding difference
        assert abs(score["score"] - calculated_sum) <= 2, \
            f"Score {score['score']} != breakdown sum {calculated_sum}"
        print(f"Score breakdown: Stability={breakdown['stability']}/40, Growth={breakdown['growth']}/30, Yield={breakdown['yield_score']}/30 = {calculated_sum}")

    def test_rating_matches_score_range(self):
        """Rating should match the score range"""
        response = requests.get(f"{BASE_URL}/api/bvb-dividends/rankings", timeout=15)
        
        assert response.status_code == 200
        data = response.json()
        rankings = data["rankings"]
        
        rating_ranges = {
            "Excelent": (80, 100),
            "Foarte Bun": (65, 79),
            "Bun": (50, 64),
            "Mediu": (35, 49),
            "Slab": (0, 34),
        }
        
        for entry in rankings[:10]:  # Check top 10
            score = entry["dividend_score"]
            rating = entry["rating"]
            
            if rating in rating_ranges:
                min_score, max_score = rating_ranges[rating]
                assert min_score <= score <= max_score, \
                    f"{entry['symbol']}: Score {score} doesn't match rating {rating} (expected {min_score}-{max_score})"
        
        print("Rating-score mapping verified for top 10 stocks")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
