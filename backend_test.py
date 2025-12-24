#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for FinRomania Platform - Session 6
Tests all endpoints including:
- BVB stocks with REAL EODHD data
- Admin Dashboard
- Glossary
- Data sources verification
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class FinRomaniaAPITester:
    def __init__(self, base_url="https://finromania-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.admin_token = None
        self.regular_user_token = None
        
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
                         data: Dict = None, validate_response: callable = None, 
                         auth_token: str = None) -> tuple:
        """Generic API endpoint tester"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add authorization header if token provided
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
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
        """Validate BVB stocks response - should be REAL data now"""
        if not isinstance(data, list):
            return False, "Response should be a list"
        
        if len(data) == 0:
            return False, "No BVB stocks returned"
            
        # Check if we have expected number of stocks
        if len(data) < 5:
            return False, f"Too few stocks returned: {len(data)}"
            
        # Validate first stock structure
        stock = data[0]
        required_fields = ['symbol', 'name', 'price', 'change', 'change_percent']
        for field in required_fields:
            if field not in stock:
                return False, f"Missing required field: {field}"
                
        # Check if it's REAL data (not mock) - Session 6 requirement
        if stock.get('is_mock', True):
            return False, "BVB data should be REAL (is_mock: false), not mock"
            
        return True, f"Valid BVB stocks: {len(data)} stocks with REAL data"

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

    def validate_stock_details(self, data: Dict) -> tuple:
        """Validate stock/index details with history response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['symbol', 'name', 'history', 'period']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        history = data.get('history', [])
        if not isinstance(history, list):
            return False, "History should be a list"
            
        if len(history) == 0:
            return False, "No history data returned"
            
        # Should have around 30 days of data
        if len(history) < 20:
            return False, f"Too few history entries: {len(history)}, expected around 30"
            
        # Validate first history entry structure
        if history:
            entry = history[0]
            required_history_fields = ['date', 'open', 'high', 'low', 'close', 'volume']
            for field in required_history_fields:
                if field not in entry:
                    return False, f"Missing history field: {field}"
                    
        return True, f"Valid stock details with {len(history)} days of history"

    def validate_article_translation(self, data: Dict) -> tuple:
        """Validate article translation response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['id', 'title', 'url', 'source']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        # Check if translation was attempted (should have Romanian fields or is_translated flag)
        has_translation = data.get('is_translated', False)
        has_romanian_title = bool(data.get('title_ro'))
        has_romanian_content = bool(data.get('content_ro'))
        
        if not has_translation and not has_romanian_title:
            return False, "Article should be translated or have translation attempted"
            
        return True, f"Valid article with translation status: {has_translation}"

    def validate_bvb_stock_details(self, data: Dict) -> tuple:
        """Validate BVB stock details with REAL EODHD data"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['symbol', 'name', 'history']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Check is_mock should be false for REAL data
        if data.get('is_mock', True):
            return False, "BVB stock details should have is_mock: false for REAL data"
        
        history = data.get('history', [])
        if not isinstance(history, list):
            return False, "History should be a list"
            
        if len(history) == 0:
            return False, "No history data returned"
            
        # Should have around 30 days of data
        if len(history) < 20:
            return False, f"Too few history entries: {len(history)}, expected around 30"
            
        return True, f"Valid BVB stock details with {len(history)} days of REAL history"

    def validate_data_sources(self, data: Dict) -> tuple:
        """Validate data sources - BVB should be EODHD (REAL)"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        bvb_source = data.get('bvb', {}).get('source', '')
        if 'EODHD' not in bvb_source or 'REAL' not in bvb_source:
            return False, f"BVB source should be 'EODHD (REAL)', got: {bvb_source}"
        
        return True, f"Valid data sources: BVB = {bvb_source}"

    def validate_admin_stats(self, data: Dict) -> tuple:
        """Validate admin stats response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_sections = ['totals', 'today', 'last_7_days']
        for section in required_sections:
            if section not in data:
                return False, f"Missing section: {section}"
        
        # Check totals section
        totals = data.get('totals', {})
        required_totals = ['users', 'articles', 'watchlist_items', 'portfolio_transactions', 'newsletter_subscribers']
        for field in required_totals:
            if field not in totals:
                return False, f"Missing totals field: {field}"
        
        return True, f"Valid admin stats with {totals.get('users', 0)} users"

    def validate_admin_users(self, data: Dict) -> tuple:
        """Validate admin users list response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        if 'users' not in data or 'total' not in data:
            return False, "Missing 'users' or 'total' field"
        
        users = data.get('users', [])
        if not isinstance(users, list):
            return False, "Users should be a list"
        
        return True, f"Valid users list: {len(users)} users returned, {data.get('total', 0)} total"

    def validate_admin_analytics(self, data: List[Dict]) -> tuple:
        """Validate admin analytics response"""
        if not isinstance(data, list):
            return False, "Response should be a list"
        
        if len(data) == 0:
            return False, "No analytics data returned"
        
        # Check first entry structure
        entry = data[0]
        required_fields = ['date', 'visits', 'logins']
        for field in required_fields:
            if field not in entry:
                return False, f"Missing field: {field}"
        
        return True, f"Valid analytics: {len(data)} days of data"

    def validate_glossary(self, data: Dict) -> tuple:
        """Validate glossary response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        if 'terms' not in data or 'total' not in data:
            return False, "Missing 'terms' or 'total' field"
        
        terms = data.get('terms', {})
        total = data.get('total', 0)
        
        if not isinstance(terms, dict):
            return False, "Terms should be a dictionary"
        
        # Should have around 99 terms
        if total < 90:
            return False, f"Too few terms: {total}, expected around 99"
        
        return True, f"Valid glossary: {total} financial terms"

    def test_admin_login(self) -> bool:
        """Test admin login and store token"""
        print("\n🔐 Testing Admin Authentication...")
        
        success, details, data = self.test_api_endpoint(
            'POST', '/api/auth/login',
            data={
                "email": "admin@finromania.ro",
                "password": "admin123"
            }
        )
        
        if success and isinstance(data, dict) and 'token' in data:
            self.admin_token = data['token']
            self.log_test("Admin Login", True, f"Admin authenticated successfully. Token obtained.", {"has_token": True})
            return True
        else:
            self.log_test("Admin Login", False, f"Failed to authenticate admin: {details}", data)
            return False

    def test_regular_user_creation(self) -> bool:
        """Create a regular test user"""
        print("\n👤 Creating Regular Test User...")
        
        test_email = f"testuser_{datetime.now().timestamp()}@test.com"
        
        success, details, data = self.test_api_endpoint(
            'POST', '/api/auth/session',
            data={
                "email": test_email,
                "name": "Test User",
                "picture": "https://example.com/pic.jpg"
            }
        )
        
        if success and isinstance(data, dict) and 'token' in data:
            self.regular_user_token = data['token']
            self.log_test("Regular User Creation", True, f"Test user created: {test_email}", {"has_token": True})
            return True
        else:
            self.log_test("Regular User Creation", False, f"Failed to create test user: {details}", data)
            return False

    def run_all_tests(self):
        """Run comprehensive test suite including Session 6 features"""
        print("🚀 Starting FinRomania API Testing - Session 6...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # ============================================
        # BASIC HEALTH CHECKS
        # ============================================
        print("\n📋 SECTION 1: Basic Health Checks")
        print("-" * 80)
        
        # Test 1: Health Check
        success, details, data = self.test_api_endpoint('GET', '/api/health')
        self.log_test("Health Check", success, details, data)
        
        # Test 2: API Root
        success, details, data = self.test_api_endpoint('GET', '/api/')
        self.log_test("API Root Endpoint", success, details, data)
        
        # ============================================
        # SESSION 6 PRIORITY 1: BVB STOCK DETAILS (CRITICAL - FRESHLY FIXED)
        # ============================================
        print("\n🔥 SECTION 2: BVB Stock Details - CRITICAL (Freshly Fixed)")
        print("-" * 80)
        
        # Test 3: BVB Stock Details for TLV
        success, details, data = self.test_api_endpoint(
            'GET', '/api/stocks/bvb/TLV/details',
            validate_response=self.validate_bvb_stock_details
        )
        self.log_test("BVB Stock Details - TLV (REAL EODHD)", success, details, 
                     {"symbol": data.get('symbol'), "history_count": len(data.get('history', [])), 
                      "is_mock": data.get('is_mock')} if isinstance(data, dict) else data)
        
        # Test 4: BVB Stock Details for H2O
        success, details, data = self.test_api_endpoint(
            'GET', '/api/stocks/bvb/H2O/details',
            validate_response=self.validate_bvb_stock_details
        )
        self.log_test("BVB Stock Details - H2O (REAL EODHD)", success, details,
                     {"symbol": data.get('symbol'), "history_count": len(data.get('history', [])),
                      "is_mock": data.get('is_mock')} if isinstance(data, dict) else data)
        
        # ============================================
        # SESSION 6 PRIORITY 2: DATA SOURCES VERIFICATION
        # ============================================
        print("\n📊 SECTION 3: Data Sources Verification")
        print("-" * 80)
        
        # Test 5: Data Sources
        success, details, data = self.test_api_endpoint(
            'GET', '/api/data-sources',
            validate_response=self.validate_data_sources
        )
        self.log_test("Data Sources - BVB should be EODHD (REAL)", success, details, data)
        
        # Test 6: BVB Stocks List (verify is_mock: false)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/stocks/bvb',
            validate_response=self.validate_bvb_stocks
        )
        self.log_test("BVB Stocks List (REAL data verification)", success, details, 
                     data[:2] if isinstance(data, list) else data)
        
        # ============================================
        # SESSION 6 PRIORITY 3: ADMIN DASHBOARD
        # ============================================
        print("\n👑 SECTION 4: Admin Dashboard (NEW)")
        print("-" * 80)
        
        # Test 7: Admin Login
        admin_login_success = self.test_admin_login()
        
        if admin_login_success and self.admin_token:
            # Test 8: Admin Stats
            success, details, data = self.test_api_endpoint(
                'GET', '/api/admin/stats',
                auth_token=self.admin_token,
                validate_response=self.validate_admin_stats
            )
            self.log_test("Admin Stats Endpoint", success, details, data)
            
            # Test 9: Admin Users List
            success, details, data = self.test_api_endpoint(
                'GET', '/api/admin/users?limit=5',
                auth_token=self.admin_token,
                validate_response=self.validate_admin_users
            )
            self.log_test("Admin Users List (limit=5)", success, details,
                         {"users_count": len(data.get('users', [])), "total": data.get('total')} if isinstance(data, dict) else data)
            
            # Test 10: Admin Analytics
            success, details, data = self.test_api_endpoint(
                'GET', '/api/admin/analytics/visits?days=7',
                auth_token=self.admin_token,
                validate_response=self.validate_admin_analytics
            )
            self.log_test("Admin Analytics (7 days)", success, details,
                         {"days_count": len(data)} if isinstance(data, list) else data)
        else:
            self.log_test("Admin Stats Endpoint", False, "Skipped - admin login failed")
            self.log_test("Admin Users List", False, "Skipped - admin login failed")
            self.log_test("Admin Analytics", False, "Skipped - admin login failed")
        
        # Test 11: Admin endpoint with non-admin user (should fail with 403)
        print("\n🔒 Testing Admin Access Control...")
        regular_user_created = self.test_regular_user_creation()
        
        if regular_user_created and self.regular_user_token:
            success, details, data = self.test_api_endpoint(
                'GET', '/api/admin/stats',
                auth_token=self.regular_user_token,
                expected_status=403
            )
            self.log_test("Admin Access Control (403 for non-admin)", success, 
                         "Correctly denied access to non-admin user" if success else "Failed to deny access", data)
        else:
            self.log_test("Admin Access Control", False, "Skipped - regular user creation failed")
        
        # ============================================
        # SESSION 6 PRIORITY 4: GLOSSARY
        # ============================================
        print("\n📚 SECTION 5: Glossary (NEW)")
        print("-" * 80)
        
        # Test 12: Glossary - All Terms
        success, details, data = self.test_api_endpoint(
            'GET', '/api/education/glossary',
            validate_response=self.validate_glossary
        )
        self.log_test("Glossary - All Terms (~99 terms)", success, details,
                     {"total": data.get('total'), "sample_terms": list(data.get('terms', {}).keys())[:3]} if isinstance(data, dict) else data)
        
        # Test 13: Glossary - Search
        success, details, data = self.test_api_endpoint(
            'GET', '/api/education/glossary?search=dividend'
        )
        search_success = success and isinstance(data, dict) and 'terms' in data and len(data.get('terms', {})) > 0
        self.log_test("Glossary - Search (dividend)", search_success,
                     f"Found {data.get('total', 0)} matching terms" if isinstance(data, dict) else details,
                     {"total": data.get('total'), "terms": list(data.get('terms', {}).keys())} if isinstance(data, dict) else data)
        
        # ============================================
        # EXISTING TESTS: Core Functionality
        # ============================================
        print("\n🌐 SECTION 6: Core Functionality (Existing)")
        print("-" * 80)
        
        # Test 14: Global Indices
        success, details, data = self.test_api_endpoint(
            'GET', '/api/stocks/global',
            validate_response=self.validate_global_indices
        )
        self.log_test("Global Indices (Yahoo Finance)", success, details, data[:2] if isinstance(data, list) else data)
        
        # Test 15: News
        success, details, data = self.test_api_endpoint(
            'GET', '/api/news?limit=10',
            validate_response=self.validate_news
        )
        self.log_test("Financial News", success, details, data[:1] if isinstance(data, list) else data)
        
        # Test 16: Currencies
        success, details, data = self.test_api_endpoint(
            'GET', '/api/currencies',
            validate_response=self.validate_currencies
        )
        self.log_test("Currency Rates (BNR)", success, details, 
                     {"sample_rates": list(data.get('rates', {}).keys())[:5]} if isinstance(data, dict) else data)
        
        # Test 17: Market Overview
        success, details, data = self.test_api_endpoint(
            'GET', '/api/market/overview',
            validate_response=self.validate_market_overview
        )
        self.log_test("Market Overview (Combined)", success, details, 
                     {"bvb_count": len(data.get('bvb_stocks', [])), 
                      "global_count": len(data.get('global_indices', []))} if isinstance(data, dict) else data)
        
        # ============================================
        # EDUCATION & PAYMENTS
        # ============================================
        print("\n🎓 SECTION 7: Education & Payments")
        print("-" * 80)
        
        # Test 18: Education Packages
        success, details, data = self.test_api_endpoint('GET', '/api/education/packages')
        packages_valid = success and isinstance(data, dict) and 'packages' in data
        self.log_test("Education Packages", packages_valid, 
                     f"Found {len(data.get('packages', []))} packages" if packages_valid else details, data)
        
        # Test 19: Tip of the Day
        success, details, data = self.test_api_endpoint('GET', '/api/advisor/tip-of-the-day')
        self.log_test("AI Advisor - Tip of the Day", success, details, data)
        
        # ============================================
        # FINAL SUMMARY
        # ============================================
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        print(f"✅ Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            failed_tests = [t for t in self.test_results if not t['success']]
            print(f"\n❌ {len(failed_tests)} tests failed:")
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