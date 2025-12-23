#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for FinRomania Platform - Auth & New Features
Tests auth, watchlist, portfolio, newsletter, search, and admin endpoints
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class FinRomaniaAuthAPITester:
    def __init__(self, base_url="https://finromania.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.session_token = None
        self.user_id = None
        
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
                         auth_required: bool = False) -> tuple:
        """Generic API endpoint tester with auth support"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add auth header if required and available
        if auth_required and self.session_token:
            headers['Authorization'] = f'Bearer {self.session_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
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

    def setup_test_user(self):
        """Create test user and session using MongoDB directly"""
        try:
            import subprocess
            import uuid
            
            # Generate unique test data
            timestamp = int(datetime.now().timestamp())
            user_id = f"test-user-{timestamp}"
            session_token = f"test_session_{timestamp}"
            email = f"test.user.{timestamp}@example.com"
            
            # Create test user and session in MongoDB
            mongo_script = f"""
            use('stock_news_romania');
            var userId = '{user_id}';
            var sessionToken = '{session_token}';
            var email = '{email}';
            
            db.users.insertOne({{
              user_id: userId,
              email: email,
              name: 'Test User',
              picture: 'https://via.placeholder.com/150',
              is_admin: true,
              created_at: new Date().toISOString()
            }});
            
            db.user_sessions.insertOne({{
              user_id: userId,
              session_token: sessionToken,
              expires_at: new Date(Date.now() + 7*24*60*60*1000).toISOString(),
              created_at: new Date().toISOString()
            }});
            
            print('SUCCESS: User and session created');
            """
            
            result = subprocess.run(
                ['mongosh', '--eval', mongo_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and 'SUCCESS' in result.stdout:
                self.session_token = session_token
                self.user_id = user_id
                return True, f"Created test user: {user_id}"
            else:
                return False, f"MongoDB error: {result.stderr}"
                
        except Exception as e:
            return False, f"Setup error: {str(e)}"

    def cleanup_test_user(self):
        """Clean up test user data"""
        if not self.user_id:
            return
            
        try:
            import subprocess
            
            mongo_script = f"""
            use('stock_news_romania');
            db.users.deleteMany({{user_id: '{self.user_id}'}});
            db.user_sessions.deleteMany({{user_id: '{self.user_id}'}});
            db.watchlist.deleteMany({{user_id: '{self.user_id}'}});
            db.portfolio_holdings.deleteMany({{user_id: '{self.user_id}'}});
            db.portfolio_transactions.deleteMany({{user_id: '{self.user_id}'}});
            print('CLEANUP: Test data removed');
            """
            
            subprocess.run(['mongosh', '--eval', mongo_script], timeout=30)
        except Exception as e:
            print(f"Cleanup warning: {e}")

    def validate_auth_me(self, data: Dict) -> tuple:
        """Validate /api/auth/me response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['user_id', 'email', 'name']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        return True, "Valid user data"

    def validate_search_results(self, data: Dict) -> tuple:
        """Validate search results"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['query', 'stocks', 'news', 'total']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        return True, f"Valid search results: {data.get('total', 0)} total results"

    def validate_newsletter_response(self, data: Dict) -> tuple:
        """Validate newsletter subscription response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['message', 'status']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        return True, f"Newsletter response: {data.get('status')}"

    def validate_admin_stats(self, data: Dict) -> tuple:
        """Validate admin stats response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['totals', 'today', 'last_7_days']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
                
        return True, "Valid admin statistics"

    def run_auth_tests(self):
        """Run comprehensive auth and new features test suite"""
        print("🚀 Starting FinRomania Auth & New Features Testing...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Setup test user
        success, details = self.setup_test_user()
        self.log_test("Setup Test User & Session", success, details)
        
        if not success:
            print("❌ Cannot proceed without test user setup")
            return False
        
        # Test 1: Auth - Get current user (should work with session token)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/auth/me', 
            auth_required=True,
            validate_response=self.validate_auth_me
        )
        self.log_test("Auth - Get Current User", success, details, data)
        
        # Test 2: Auth - Get current user without token (should fail)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/auth/me', 
            expected_status=401
        )
        self.log_test("Auth - Unauthorized Access (Expected 401)", success, details)
        
        # Test 3: Search API
        success, details, data = self.test_api_endpoint(
            'GET', '/api/search?q=TLV',
            validate_response=self.validate_search_results
        )
        self.log_test("Search API - Stock Search", success, details, data)
        
        # Test 4: Newsletter subscription
        success, details, data = self.test_api_endpoint(
            'POST', '/api/newsletter/subscribe',
            data={'email': 'test@example.com', 'name': 'Test User'},
            validate_response=self.validate_newsletter_response
        )
        self.log_test("Newsletter - Subscribe", success, details, data)
        
        # Test 5: Watchlist - Get empty watchlist (auth required)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/watchlist',
            auth_required=True
        )
        self.log_test("Watchlist - Get Empty List", success, details, data)
        
        # Test 6: Watchlist - Add item
        success, details, data = self.test_api_endpoint(
            'POST', '/api/watchlist',
            data={
                'symbol': 'TLV',
                'type': 'bvb',
                'name': 'Banca Transilvania',
                'target_price': 25.0,
                'alert_enabled': True
            },
            auth_required=True
        )
        self.log_test("Watchlist - Add Item", success, details, data)
        
        # Store watchlist item ID for deletion test
        watchlist_item_id = None
        if success and isinstance(data, dict):
            watchlist_item_id = data.get('id')
        
        # Test 7: Watchlist - Get list with items
        success, details, data = self.test_api_endpoint(
            'GET', '/api/watchlist',
            auth_required=True
        )
        self.log_test("Watchlist - Get List with Items", success, details, data)
        
        # Test 8: Portfolio - Get empty holdings
        success, details, data = self.test_api_endpoint(
            'GET', '/api/portfolio/holdings',
            auth_required=True
        )
        self.log_test("Portfolio - Get Empty Holdings", success, details, data)
        
        # Test 9: Portfolio - Add transaction
        success, details, data = self.test_api_endpoint(
            'POST', '/api/portfolio/transaction',
            data={
                'symbol': 'TLV',
                'type': 'bvb',
                'name': 'Banca Transilvania',
                'action': 'buy',
                'quantity': 100,
                'price': 24.50
            },
            auth_required=True
        )
        self.log_test("Portfolio - Add Buy Transaction", success, details, data)
        
        # Test 10: Portfolio - Get holdings after transaction
        success, details, data = self.test_api_endpoint(
            'GET', '/api/portfolio/holdings',
            auth_required=True
        )
        self.log_test("Portfolio - Get Holdings After Transaction", success, details, data)
        
        # Test 11: Portfolio - Get summary
        success, details, data = self.test_api_endpoint(
            'GET', '/api/portfolio/summary',
            auth_required=True
        )
        self.log_test("Portfolio - Get Summary", success, details, data)
        
        # Test 12: Portfolio - Get transactions
        success, details, data = self.test_api_endpoint(
            'GET', '/api/portfolio/transactions',
            auth_required=True
        )
        self.log_test("Portfolio - Get Transaction History", success, details, data)
        
        # Test 13: Admin - Get stats (requires admin user)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/admin/stats',
            auth_required=True,
            validate_response=self.validate_admin_stats
        )
        self.log_test("Admin - Get Platform Statistics", success, details, data)
        
        # Test 14: Admin - Get users list
        success, details, data = self.test_api_endpoint(
            'GET', '/api/admin/users?limit=5',
            auth_required=True
        )
        self.log_test("Admin - Get Users List", success, details, data)
        
        # Test 15: Watchlist - Remove item (if we have an ID)
        if watchlist_item_id:
            success, details, data = self.test_api_endpoint(
                'DELETE', f'/api/watchlist/{watchlist_item_id}',
                auth_required=True
            )
            self.log_test("Watchlist - Remove Item", success, details, data)
        
        # Test 16: Auth - Logout
        success, details, data = self.test_api_endpoint(
            'POST', '/api/auth/logout',
            auth_required=True
        )
        self.log_test("Auth - Logout", success, details, data)
        
        # Cleanup
        self.cleanup_test_user()
        
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All auth & new features tests passed!")
            return True
        else:
            failed_tests = [t for t in self.test_results if not t['success']]
            print(f"❌ {len(failed_tests)} tests failed:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
            return False

def main():
    """Main test execution"""
    tester = FinRomaniaAuthAPITester()
    
    try:
        success = tester.run_auth_tests()
        
        # Save detailed results
        with open('/app/backend_test_auth_results.json', 'w') as f:
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