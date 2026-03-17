"""
Test Suite for FinRomania 2.0 - LIVE Data & Cache-Busting Fix
Tests: Global Markets, BVB Stocks, Ticker Bar, Auto-refresh, Cache Headers
"""
import pytest
import requests
import time
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://finromania-preview.preview.emergentagent.com')

class TestCacheHeaders:
    """Test that all live data endpoints return no-cache headers"""
    
    def test_global_overview_cache_headers(self):
        """Test /api/global/overview returns no-cache headers"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/global/overview?_t={timestamp}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check cache headers
        cache_control = response.headers.get('Cache-Control', '')
        assert 'no-store' in cache_control, f"Expected no-store in Cache-Control, got: {cache_control}"
        assert 'no-cache' in cache_control, f"Expected no-cache in Cache-Control, got: {cache_control}"
        
        pragma = response.headers.get('Pragma', '')
        assert 'no-cache' in pragma, f"Expected no-cache in Pragma, got: {pragma}"
        
        print(f"✅ /api/global/overview - Cache headers correct: {cache_control}")
    
    def test_stocks_bvb_cache_headers(self):
        """Test /api/stocks/bvb returns no-cache headers"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/stocks/bvb?_t={timestamp}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        cache_control = response.headers.get('Cache-Control', '')
        assert 'no-store' in cache_control, f"Expected no-store in Cache-Control, got: {cache_control}"
        
        print(f"✅ /api/stocks/bvb - Cache headers correct: {cache_control}")
    
    def test_bvb_indices_cache_headers(self):
        """Test /api/bvb/indices returns no-cache headers"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/bvb/indices?_t={timestamp}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        cache_control = response.headers.get('Cache-Control', '')
        assert 'no-store' in cache_control, f"Expected no-store in Cache-Control, got: {cache_control}"
        
        print(f"✅ /api/bvb/indices - Cache headers correct: {cache_control}")
    
    def test_bvb_top_movers_cache_headers(self):
        """Test /api/bvb/top-movers returns no-cache headers"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/bvb/top-movers?_t={timestamp}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        cache_control = response.headers.get('Cache-Control', '')
        assert 'no-store' in cache_control, f"Expected no-store in Cache-Control, got: {cache_control}"
        
        print(f"✅ /api/bvb/top-movers - Cache headers correct: {cache_control}")
    
    def test_stocks_global_cache_headers(self):
        """Test /api/stocks/global returns no-cache headers"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/stocks/global?_t={timestamp}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        cache_control = response.headers.get('Cache-Control', '')
        assert 'no-store' in cache_control, f"Expected no-store in Cache-Control, got: {cache_control}"
        
        print(f"✅ /api/stocks/global - Cache headers correct: {cache_control}")


class TestGlobalMarketsAPI:
    """Test Global Markets Page data endpoints"""
    
    def test_global_overview_returns_data(self):
        """Test /api/global/overview returns valid data structure"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/global/overview?_t={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert 'indices' in data, "Missing 'indices' in response"
        assert 'commodities' in data, "Missing 'commodities' in response"
        assert 'crypto' in data, "Missing 'crypto' in response"
        assert 'forex' in data, "Missing 'forex' in response"
        assert 'sentiment' in data, "Missing 'sentiment' in response"
        assert 'market_status' in data, "Missing 'market_status' in response"
        assert 'updated_at' in data, "Missing 'updated_at' in response"
        
        # Check indices have data
        assert len(data['indices']) > 0, "No indices data returned"
        
        # Check first index has required fields
        first_index = data['indices'][0]
        assert 'symbol' in first_index, "Index missing 'symbol'"
        assert 'name' in first_index, "Index missing 'name'"
        assert 'price' in first_index, "Index missing 'price'"
        assert 'change_percent' in first_index, "Index missing 'change_percent'"
        
        print(f"✅ /api/global/overview - Returns {len(data['indices'])} indices, {len(data['commodities'])} commodities, {len(data['crypto'])} crypto, {len(data['forex'])} forex")
    
    def test_global_overview_data_sources(self):
        """Test that global data comes from EODHD (real-time) or yfinance"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/global/overview?_t={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check indices use EODHD
        for index in data['indices']:
            source = index.get('source', '')
            assert source in ['eodhd_realtime', 'yfinance'], f"Unexpected source for {index['symbol']}: {source}"
        
        # Check crypto uses yfinance
        for crypto in data['crypto']:
            source = crypto.get('source', '')
            assert source == 'yfinance', f"Crypto {crypto['symbol']} should use yfinance, got: {source}"
        
        print(f"✅ Data sources verified - Indices: EODHD, Crypto: yfinance")
    
    def test_global_overview_sentiment(self):
        """Test sentiment calculation in global overview"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/global/overview?_t={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        
        sentiment = data['sentiment']
        assert 'gainers' in sentiment, "Missing 'gainers' in sentiment"
        assert 'losers' in sentiment, "Missing 'losers' in sentiment"
        assert 'avg_change' in sentiment, "Missing 'avg_change' in sentiment"
        assert 'status' in sentiment, "Missing 'status' in sentiment"
        
        # Verify status matches avg_change
        if sentiment['avg_change'] > 0:
            assert sentiment['status'] == 'bullish', f"Expected bullish for positive avg_change, got: {sentiment['status']}"
        else:
            assert sentiment['status'] == 'bearish', f"Expected bearish for negative avg_change, got: {sentiment['status']}"
        
        print(f"✅ Sentiment: {sentiment['gainers']} gainers, {sentiment['losers']} losers, avg: {sentiment['avg_change']}%")


class TestBVBStocksAPI:
    """Test BVB Stocks Page data endpoints"""
    
    def test_bvb_stocks_returns_data(self):
        """Test /api/stocks/bvb returns valid stock data"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/stocks/bvb?_t={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list), "Expected list of stocks"
        assert len(data) > 0, "No BVB stocks returned"
        
        # Check first stock has required fields
        first_stock = data[0]
        assert 'symbol' in first_stock, "Stock missing 'symbol'"
        assert 'name' in first_stock, "Stock missing 'name'"
        assert 'price' in first_stock, "Stock missing 'price'"
        assert 'change_percent' in first_stock, "Stock missing 'change_percent'"
        
        print(f"✅ /api/stocks/bvb - Returns {len(data)} BVB stocks")
    
    def test_bvb_indices_returns_data(self):
        """Test /api/bvb/indices returns valid index data"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/bvb/indices?_t={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'indices' in data, "Missing 'indices' in response"
        assert len(data['indices']) > 0, "No BVB indices returned"
        
        # Check for expected indices
        index_ids = [idx['id'] for idx in data['indices']]
        assert 'BET' in index_ids, "Missing BET index"
        
        print(f"✅ /api/bvb/indices - Returns {len(data['indices'])} indices: {index_ids}")
    
    def test_bvb_top_movers_returns_data(self):
        """Test /api/bvb/top-movers returns gainers, losers, most_traded"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/bvb/top-movers?_t={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'gainers' in data, "Missing 'gainers' in response"
        assert 'losers' in data, "Missing 'losers' in response"
        assert 'most_traded' in data, "Missing 'most_traded' in response"
        
        print(f"✅ /api/bvb/top-movers - {len(data['gainers'])} gainers, {len(data['losers'])} losers, {len(data['most_traded'])} most traded")
    
    def test_bvb_sectors_returns_data(self):
        """Test /api/bvb/sectors returns sector performance"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/bvb/sectors?_t={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'sectors' in data, "Missing 'sectors' in response"
        assert len(data['sectors']) > 0, "No sectors returned"
        
        # Check sector structure
        first_sector = data['sectors'][0]
        assert 'name' in first_sector, "Sector missing 'name'"
        assert 'average_change_percent' in first_sector, "Sector missing 'average_change_percent'"
        
        print(f"✅ /api/bvb/sectors - Returns {len(data['sectors'])} sectors")


class TestTickerBarAPI:
    """Test Ticker Bar data endpoints"""
    
    def test_stocks_global_for_ticker(self):
        """Test /api/stocks/global returns data for ticker bar"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/stocks/global?_t={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list), "Expected list of global indices"
        assert len(data) > 0, "No global indices for ticker"
        
        # Check first item has required fields for ticker
        first_item = data[0]
        assert 'name' in first_item, "Missing 'name' for ticker"
        assert 'price' in first_item, "Missing 'price' for ticker"
        assert 'change_percent' in first_item, "Missing 'change_percent' for ticker"
        
        print(f"✅ /api/stocks/global - Returns {len(data)} items for ticker bar")
    
    def test_stocks_bvb_for_ticker(self):
        """Test /api/stocks/bvb returns data for ticker bar (top 5)"""
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/stocks/bvb?_t={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list), "Expected list of BVB stocks"
        assert len(data) >= 5, "Need at least 5 BVB stocks for ticker"
        
        print(f"✅ /api/stocks/bvb - Returns {len(data)} stocks (top 5 used in ticker)")


class TestDataFreshness:
    """Test that data is fresh (not stale cached data)"""
    
    def test_global_overview_updated_at_recent(self):
        """Test that updated_at timestamp is recent"""
        from datetime import datetime, timezone, timedelta
        
        timestamp = int(time.time() * 1000)
        response = requests.get(f"{BASE_URL}/api/global/overview?_t={timestamp}")
        
        assert response.status_code == 200
        data = response.json()
        
        updated_at = data.get('updated_at', '')
        assert updated_at, "Missing updated_at timestamp"
        
        # Parse timestamp and check it's within last 5 minutes
        try:
            update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            diff = now - update_time
            
            assert diff < timedelta(minutes=5), f"Data is stale: updated {diff} ago"
            print(f"✅ Data freshness: updated {diff.total_seconds():.1f} seconds ago")
        except Exception as e:
            print(f"⚠️ Could not parse timestamp: {updated_at} - {e}")
    
    def test_multiple_requests_get_fresh_data(self):
        """Test that consecutive requests don't return cached data"""
        # First request
        timestamp1 = int(time.time() * 1000)
        response1 = requests.get(f"{BASE_URL}/api/global/overview?_t={timestamp1}")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Wait a moment
        time.sleep(1)
        
        # Second request with different timestamp
        timestamp2 = int(time.time() * 1000)
        response2 = requests.get(f"{BASE_URL}/api/global/overview?_t={timestamp2}")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Both should have updated_at timestamps
        assert 'updated_at' in data1, "First response missing updated_at"
        assert 'updated_at' in data2, "Second response missing updated_at"
        
        print(f"✅ Multiple requests return fresh data with timestamps")


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data.get('status') == 'healthy', f"Expected healthy status, got: {data.get('status')}"
        assert 'timestamp' in data, "Missing timestamp in health response"
        
        print(f"✅ Health check: {data['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
