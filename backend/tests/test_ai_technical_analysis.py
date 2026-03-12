"""
AI Technical Analysis API Tests
Tests for POST /api/ai-analysis/analyze endpoint
Verifies PRO user authentication and comprehensive analysis response
"""
import pytest
import requests
import os
import time

# Get base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials provided
PRO_TOKEN = "test_token_223176562fd54dec"


class TestAITechnicalAnalysisEndpoint:
    """Tests for AI Technical Analysis PRO feature"""
    
    def test_analyze_endpoint_with_pro_token(self):
        """Test POST /api/ai-analysis/analyze with PRO user token"""
        response = requests.post(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRO_TOKEN}"
            },
            json={
                "symbol": "TLV",
                "period": "1m"
            }
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Response should have success=True"
        assert data.get("symbol") == "TLV", "Response should include symbol"
        assert "analysis" in data, "Response should include analysis object"
        assert "ai_interpretation" in data, "Response should include AI interpretation"
        
    def test_analysis_includes_volume_data(self):
        """Verify analysis response includes volume fields"""
        response = requests.post(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRO_TOKEN}"
            },
            json={"symbol": "TLV", "period": "1m"}
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis = data.get("analysis", {})
        
        # Volume fields
        print(f"Volume current: {analysis.get('volume_current')}")
        print(f"Volume avg: {analysis.get('volume_avg')}")
        print(f"Volume ratio: {analysis.get('volume_ratio')}")
        print(f"Volume status: {analysis.get('volume_status')}")
        print(f"Volume trend: {analysis.get('volume_trend')}")
        
        assert "volume_current" in analysis, "Missing volume_current field"
        assert "volume_avg" in analysis, "Missing volume_avg field"
        assert "volume_ratio" in analysis, "Missing volume_ratio field"
        assert "volume_status" in analysis, "Missing volume_status field"
        assert "volume_trend" in analysis, "Missing volume_trend field"
        
        # Verify volume_ratio is a number
        assert isinstance(analysis.get("volume_ratio"), (int, float)), "volume_ratio should be numeric"
        
        # Verify volume_status is one of expected values
        expected_statuses = ["FOARTE_MARE", "MARE", "PESTE_MEDIE", "NORMAL", "MIC", "FOARTE_MIC"]
        assert analysis.get("volume_status") in expected_statuses, f"Unexpected volume_status: {analysis.get('volume_status')}"
        
        # Verify volume_trend is one of expected values
        expected_trends = ["crescător", "descrescător", "stabil"]
        assert analysis.get("volume_trend") in expected_trends, f"Unexpected volume_trend: {analysis.get('volume_trend')}"
        
    def test_analysis_includes_market_context(self):
        """Verify analysis response includes market context (BET index, sentiment)"""
        response = requests.post(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRO_TOKEN}"
            },
            json={"symbol": "TLV", "period": "1m"}
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis = data.get("analysis", {})
        
        # Market context fields
        print(f"BET change: {analysis.get('bet_change')}")
        print(f"Market sentiment: {analysis.get('market_sentiment')}")
        print(f"Market description: {analysis.get('market_description')}")
        
        assert "bet_change" in analysis, "Missing bet_change field"
        assert "market_sentiment" in analysis, "Missing market_sentiment field"
        assert "market_description" in analysis, "Missing market_description field"
        
        # Verify market_sentiment is one of expected values
        expected_sentiments = ["FOARTE_BULLISH", "BULLISH", "NEUTRU", "BEARISH", "FOARTE_BEARISH"]
        assert analysis.get("market_sentiment") in expected_sentiments, f"Unexpected market_sentiment: {analysis.get('market_sentiment')}"
        
    def test_analysis_includes_liquidity_score(self):
        """Verify analysis response includes liquidity fields"""
        response = requests.post(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRO_TOKEN}"
            },
            json={"symbol": "TLV", "period": "1m"}
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis = data.get("analysis", {})
        
        # Liquidity fields
        print(f"Liquidity score: {analysis.get('liquidity_score')}")
        print(f"Liquidity tier: {analysis.get('liquidity_tier')}")
        print(f"Liquidity description: {analysis.get('liquidity_description')}")
        
        assert "liquidity_score" in analysis, "Missing liquidity_score field"
        assert "liquidity_tier" in analysis, "Missing liquidity_tier field"
        assert "liquidity_description" in analysis, "Missing liquidity_description field"
        
        # Verify liquidity_score is between 1-5
        score = analysis.get("liquidity_score")
        assert isinstance(score, int), "liquidity_score should be integer"
        assert 1 <= score <= 5, f"liquidity_score should be 1-5, got {score}"
        
        # Verify liquidity_tier is one of expected values
        expected_tiers = ["FOARTE_LICHIDĂ", "LICHIDĂ", "MEDIE", "SCĂZUTĂ", "FOARTE_SCĂZUTĂ"]
        assert analysis.get("liquidity_tier") in expected_tiers, f"Unexpected liquidity_tier: {analysis.get('liquidity_tier')}"
        
    def test_analysis_includes_technical_indicators(self):
        """Verify analysis includes RSI, MA, support/resistance"""
        response = requests.post(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRO_TOKEN}"
            },
            json={"symbol": "TLV", "period": "1m"}
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis = data.get("analysis", {})
        
        # Technical indicators
        print(f"RSI: {analysis.get('rsi')}")
        print(f"MA20: {analysis.get('ma20')}")
        print(f"Support: {analysis.get('support')}")
        print(f"Resistance: {analysis.get('resistance')}")
        print(f"Signal: {analysis.get('signal')}")
        print(f"Confidence: {analysis.get('confidence')}")
        
        assert "rsi" in analysis, "Missing rsi field"
        assert "support" in analysis, "Missing support field"
        assert "resistance" in analysis, "Missing resistance field"
        assert "signal" in analysis, "Missing signal field"
        assert "confidence" in analysis, "Missing confidence field"
        
        # Verify RSI is in valid range
        rsi = analysis.get("rsi")
        if rsi is not None:
            assert 0 <= rsi <= 100, f"RSI should be 0-100, got {rsi}"
            
        # Verify signal is one of expected values
        expected_signals = ["CUMPĂRĂ", "CUMPĂRĂ MODERAT", "PĂSTREAZĂ", "VINDE MODERAT", "VINDE"]
        assert analysis.get("signal") in expected_signals, f"Unexpected signal: {analysis.get('signal')}"
        
    def test_ai_interpretation_is_in_romanian(self):
        """Verify AI interpretation is comprehensive and in Romanian"""
        response = requests.post(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRO_TOKEN}"
            },
            json={"symbol": "TLV", "period": "1m"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        ai_interpretation = data.get("ai_interpretation", "")
        print(f"AI interpretation length: {len(ai_interpretation)} chars")
        print(f"AI interpretation preview: {ai_interpretation[:300]}...")
        
        # Should not be empty or error message
        assert len(ai_interpretation) > 50, "AI interpretation seems too short"
        assert "Nu am putut genera" not in ai_interpretation, "AI interpretation returned error"
        assert "Configurare AI lipsă" not in ai_interpretation, "AI configuration missing"
        
        # Check for Romanian words (common technical analysis terms in Romanian)
        romanian_indicators = ["preț", "trend", "suport", "rezistență", "volum", "piață", "risc", "investiții", "acțiune"]
        has_romanian = any(word in ai_interpretation.lower() for word in romanian_indicators)
        assert has_romanian, "AI interpretation should be in Romanian"
        
    def test_non_pro_user_gets_403(self):
        """Test that non-PRO user gets 403 Forbidden error"""
        # Using an invalid/basic user token
        response = requests.post(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer invalid_basic_token_12345"
            },
            json={"symbol": "TLV", "period": "1m"}
        )
        
        print(f"Status code for non-PRO user: {response.status_code}")
        
        # Should be either 401 (invalid token) or 403 (valid but not PRO)
        assert response.status_code in [401, 403], f"Expected 401 or 403, got {response.status_code}"
        
    def test_request_without_auth_returns_401(self):
        """Test that request without auth header returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={"Content-Type": "application/json"},
            json={"symbol": "TLV", "period": "1m"}
        )
        
        print(f"Status code without auth: {response.status_code}")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
    def test_different_periods(self):
        """Test analysis with different time periods"""
        periods = ["1w", "1m", "3m"]
        
        for period in periods:
            response = requests.post(
                f"{BASE_URL}/api/ai-analysis/analyze",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {PRO_TOKEN}"
                },
                json={"symbol": "TLV", "period": period}
            )
            
            print(f"Period {period}: Status {response.status_code}")
            assert response.status_code == 200, f"Failed for period {period}: {response.text}"
            
    def test_invalid_symbol_returns_404(self):
        """Test analysis with invalid symbol returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRO_TOKEN}"
            },
            json={"symbol": "INVALID_SYMBOL_XYZ", "period": "1m"}
        )
        
        print(f"Invalid symbol response: {response.status_code}")
        # Should return 404 or 500 with error message
        assert response.status_code in [404, 500], f"Expected 404/500 for invalid symbol, got {response.status_code}"
        
    def test_analysis_usage_endpoint(self):
        """Test GET /api/ai-analysis/usage endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/ai-analysis/usage",
            headers={
                "Authorization": f"Bearer {PRO_TOKEN}"
            }
        )
        
        print(f"Usage endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Usage data: {data}")
            assert "today" in data, "Missing 'today' in usage response"
            assert "total" in data, "Missing 'total' in usage response"
            assert "is_pro" in data, "Missing 'is_pro' in usage response"
        else:
            print(f"Usage endpoint returned: {response.text}")


class TestAIAnalysisComprehensiveResponse:
    """Test comprehensive analysis response structure"""
    
    def test_full_response_structure(self):
        """Verify complete response structure with all expected fields"""
        response = requests.post(
            f"{BASE_URL}/api/ai-analysis/analyze",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRO_TOKEN}"
            },
            json={"symbol": "TLV", "period": "1m"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Top-level fields
        assert "success" in data
        assert "symbol" in data
        assert "analysis" in data
        assert "ai_interpretation" in data
        assert "generated_at" in data
        
        analysis = data["analysis"]
        
        # All expected analysis fields
        expected_fields = [
            # Basic info
            "current_price",
            # Technical indicators
            "support", "resistance", "support_levels", "resistance_levels",
            "rsi", "ma20", "ma50",
            "trend_direction", "trend_strength",
            "short_change", "medium_change",
            # Volume analysis
            "volume_current", "volume_avg", "volume_ratio", 
            "volume_status", "volume_trend", "volume_alert", "volume_confirms",
            # Market context
            "bet_change", "market_sentiment", "market_description",
            # Price action
            "patterns", "near_high", "near_low",
            # Liquidity
            "liquidity_score", "liquidity_tier", "liquidity_description",
            # Signal
            "signal", "signal_color", "confidence", "reasons", "warnings"
        ]
        
        missing_fields = []
        for field in expected_fields:
            if field not in analysis:
                missing_fields.append(field)
                
        print(f"Total fields checked: {len(expected_fields)}")
        print(f"Missing fields: {missing_fields}")
        
        assert len(missing_fields) == 0, f"Missing fields in analysis: {missing_fields}"
        
        # Print full analysis for verification
        print("\n=== FULL ANALYSIS RESPONSE ===")
        for key, value in analysis.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
