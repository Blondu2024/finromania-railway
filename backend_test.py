#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for FinRomania Platform
Tests all endpoints for BVB stocks, global indices, news, currencies, and market overview
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class FinRomaniaAPITester:
    def __init__(self, base_url="https://stockdata-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_sample": response_data if isinstance(response_data, (dict, list)) else str(response_data)[:200] if response_data else None
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {str(response_data)[:200]}")
        print()

    def test_api_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                         data: Dict = None, validate_response: callable = None) -> tuple:
        """Generic API endpoint tester"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}", None
                
            success = response.status_code == expected_status
            
            if success and response.headers.get('content-type', '').startswith('application/json'):
                try:
                    json_data = response.json()
                    if validate_response:
                        validation_result = validate_response(json_data)
                        if not validation_result[0]:
                            return False, f"Validation failed: {validation_result[1]}", json_data
                    return True, f"Status: {response.status_code}", json_data
                except json.JSONDecodeError:
                    return False, f"Invalid JSON response. Status: {response.status_code}", response.text
            elif success:
                return True, f"Status: {response.status_code}", response.text
            else:
                return False, f"Expected {expected_status}, got {response.status_code}", response.text
                
        except requests.exceptions.Timeout:
            return False, "Request timeout (30s)", None
        except requests.exceptions.ConnectionError:
            return False, "Connection error - server may be down", None
        except Exception as e:
            return False, f"Error: {str(e)}", None

    def validate_bvb_stocks(self, data: List[Dict]) -> tuple:
        """Validate BVB stocks response"""
        if not isinstance(data, list):
            return False, "Response should be a list"
        
        if len(data) == 0:
            return False, "No BVB stocks returned"
            
        # Check if we have expected number of stocks (should be around 10)
        if len(data) < 5:
            return False, f"Too few stocks returned: {len(data)}"
            
        # Validate first stock structure
        stock = data[0]
        required_fields = ['symbol', 'name', 'price', 'change', 'change_percent']
        for field in required_fields:
            if field not in stock:
                return False, f"Missing required field: {field}"
                
        # Check if it's marked as mock data
        if not stock.get('is_mock', False):
            return False, "BVB data should be marked as mock for MVP"
            
        return True, f"Valid BVB stocks: {len(data)} stocks"

    def validate_global_indices(self, data: List[Dict]) -> tuple:
        """Validate global indices response"""
        if not isinstance(data, list):
            return False, "Response should be a list"
            
        if len(data) == 0:
            return False, "No global indices returned"
            
        # Should have 6 major indices
        expected_symbols = ['^GSPC', '^IXIC', '^DJI', '^GDAXI', '^FTSE', '^N225']
        returned_symbols = [idx.get('symbol') for idx in data]
        
        missing_symbols = [s for s in expected_symbols if s not in returned_symbols]
        if missing_symbols:
            return False, f"Missing indices: {missing_symbols}"
            
        # Validate structure
        index = data[0]
        required_fields = ['symbol', 'name', 'price', 'change', 'change_percent']
        for field in required_fields:
            if field not in index:
                return False, f"Missing required field: {field}"
                
        return True, f"Valid global indices: {len(data)} indices"

    def validate_news(self, data: List[Dict]) -> tuple:
        """Validate news response"""
        if not isinstance(data, list):
            return False, "Response should be a list"
            
        if len(data) == 0:
            return False, "No news articles returned"
            
        # Validate first article structure
        article = data[0]
        required_fields = ['title', 'url', 'source', 'published_at']
        for field in required_fields:
            if field not in article:
                return False, f"Missing required field: {field}"
                
        # Check source structure
        if not isinstance(article.get('source'), dict):
            return False, "Source should be a dictionary"
            
        return True, f"Valid news articles: {len(data)} articles"

    def validate_currencies(self, data: Dict) -> tuple:
        """Validate currencies response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['date', 'rates', 'source']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        rates = data.get('rates', {})
        if not isinstance(rates, dict):
            return False, "Rates should be a dictionary"
            
        # Check for main currencies
        main_currencies = ['EUR', 'USD', 'GBP', 'CHF']
        missing_currencies = [c for c in main_currencies if c not in rates]
        if missing_currencies:
            return False, f"Missing main currencies: {missing_currencies}"
            
        # Should have around 38 currencies as mentioned in requirements
        if len(rates) < 30:
            return False, f"Too few currencies: {len(rates)}, expected around 38"
            
        return True, f"Valid currencies: {len(rates)} rates from BNR"

    def validate_market_overview(self, data: Dict) -> tuple:
        """Validate market overview response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['bvb_stocks', 'global_indices', 'last_updated']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        # Validate sub-components
        bvb_result = self.validate_bvb_stocks(data['bvb_stocks'])
        if not bvb_result[0]:
            return False, f"BVB stocks validation failed: {bvb_result[1]}"
            
        global_result = self.validate_global_indices(data['global_indices'])
        if not global_result[0]:
            return False, f"Global indices validation failed: {global_result[1]}"
            
        return True, "Valid market overview with all components"

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting FinRomania API Testing...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test 1: Health Check
        success, details, data = self.test_api_endpoint('GET', '/api/health')
        self.log_test("Health Check", success, details, data)
        
        # Test 2: API Root
        success, details, data = self.test_api_endpoint('GET', '/api/')
        self.log_test("API Root Endpoint", success, details, data)
        
        # Test 3: BVB Stocks
        success, details, data = self.test_api_endpoint(
            'GET', '/api/stocks/bvb', 
            validate_response=self.validate_bvb_stocks
        )
        self.log_test("BVB Stocks (MOCK)", success, details, data[:2] if isinstance(data, list) else data)
        
        # Test 4: Global Indices
        success, details, data = self.test_api_endpoint(
            'GET', '/api/stocks/global',
            validate_response=self.validate_global_indices
        )
        self.log_test("Global Indices (Yahoo Finance)", success, details, data[:2] if isinstance(data, list) else data)
        
        # Test 5: News
        success, details, data = self.test_api_endpoint(
            'GET', '/api/news?limit=10',
            validate_response=self.validate_news
        )
        self.log_test("Financial News (NewsAPI)", success, details, data[:1] if isinstance(data, list) else data)
        
        # Test 6: Currencies
        success, details, data = self.test_api_endpoint(
            'GET', '/api/currencies',
            validate_response=self.validate_currencies
        )
        self.log_test("Currency Rates (BNR)", success, details, 
                     {"sample_rates": list(data.get('rates', {}).keys())[:5]} if isinstance(data, dict) else data)
        
        # Test 7: Market Overview
        success, details, data = self.test_api_endpoint(
            'GET', '/api/market/overview',
            validate_response=self.validate_market_overview
        )
        self.log_test("Market Overview (Combined)", success, details, 
                     {"bvb_count": len(data.get('bvb_stocks', [])), 
                      "global_count": len(data.get('global_indices', []))} if isinstance(data, dict) else data)
        
        # Test 8: Manual Refresh BVB
        success, details, data = self.test_api_endpoint('POST', '/api/refresh/bvb')
        self.log_test("Manual Refresh BVB", success, details, data)
        
        # Test 9: Manual Refresh Currencies
        success, details, data = self.test_api_endpoint('POST', '/api/refresh/currencies')
        self.log_test("Manual Refresh Currencies", success, details, data)
        
        # Test 10: Manual Refresh News
        success, details, data = self.test_api_endpoint('POST', '/api/refresh/news')
        self.log_test("Manual Refresh News", success, details, data)
        
        # Test 11: Manual Refresh Global
        success, details, data = self.test_api_endpoint('POST', '/api/refresh/global')
        self.log_test("Manual Refresh Global Indices", success, details, data)
        
        # Test 12: Individual BVB Stock (if we have data)
        if self.test_results[2]['success']:  # BVB stocks test passed
            success, details, data = self.test_api_endpoint('GET', '/api/stocks/bvb/H2O')
            self.log_test("Individual BVB Stock (H2O)", success, details, data)
        
        # Test 13: BVB Stock Details with History (V2 Feature)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/stocks/bvb/H2O/details',
            validate_response=self.validate_stock_details
        )
        self.log_test("BVB Stock Details with 30-day History", success, details, 
                     {"history_count": len(data.get('history', [])), "has_chart_data": bool(data.get('history'))} if isinstance(data, dict) else data)
        
        # Test 14: Global Index Details with History (V2 Feature)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/stocks/global/%5EGSPC/details',  # S&P 500 encoded
            validate_response=self.validate_stock_details
        )
        self.log_test("Global Index Details with 30-day History", success, details,
                     {"history_count": len(data.get('history', [])), "has_chart_data": bool(data.get('history'))} if isinstance(data, dict) else data)
        
        # Test 15: Article Translation (V2 Feature) - Get first article and test translation
        if self.test_results[4]['success']:  # News test passed
            # First get news to get an article ID
            success, details, news_data = self.test_api_endpoint('GET', '/api/news?limit=1')
            if success and isinstance(news_data, list) and len(news_data) > 0:
                article_id = news_data[0].get('id')
                if article_id:
                    success, details, data = self.test_api_endpoint(
                        'GET', f'/api/news/{article_id}',
                        validate_response=self.validate_article_translation
                    )
                    self.log_test("Article Translation to Romanian", success, details,
                                 {"has_translation": data.get('is_translated'), "has_romanian_content": bool(data.get('title_ro'))} if isinstance(data, dict) else data)
                else:
                    self.log_test("Article Translation to Romanian", False, "No article ID found in news response")
        
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            failed_tests = [t for t in self.test_results if not t['success']]
            print(f"❌ {len(failed_tests)} tests failed:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
            return False

def main():
    """Main test execution"""
    tester = FinRomaniaAPITester()
    
    try:
        success = tester.run_all_tests()
        
        # Save detailed results
        with open('/app/backend_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': tester.tests_run,
                    'passed_tests': tester.tests_passed,
                    'success_rate': f"{(tester.tests_passed/tester.tests_run*100):.1f}%",
                    'timestamp': datetime.now().isoformat()
                },
                'detailed_results': tester.test_results
            }, f, indent=2)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"💥 Critical error during testing: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())