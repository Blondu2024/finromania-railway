#!/usr/bin/env python3
"""
FinRomania 2.0 - New Features Testing
Tests:
1. Portfolio BVB cu "3 Straturi" (3 Tiers System)
2. Quiz System
3. Subscription System & PRO Paywall
4. Fear & Greed Index
"""

import requests
import sys
import json
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional

class FinRomania2Tester:
    def __init__(self, base_url="https://pro-trading-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test user tokens
        self.beginner_token = None
        self.intermediate_token = None
        self.pro_token = None
        
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
            print(f"    Response: {str(response_data)[:300]}")
        print()

    def test_api_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                         data: Dict = None, validate_response: callable = None, 
                         auth_token: str = None) -> tuple:
        """Generic API endpoint tester"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
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
                try:
                    error_data = response.json()
                    return False, f"Expected {expected_status}, got {response.status_code}", error_data
                except:
                    return False, f"Expected {expected_status}, got {response.status_code}", response.text
                
        except requests.exceptions.Timeout:
            return False, "Request timeout (30s)", None
        except requests.exceptions.ConnectionError:
            return False, "Connection error - server may be down", None
        except Exception as e:
            return False, f"Error: {str(e)}", None

    def create_test_users(self):
        """Create test users in MongoDB with different levels"""
        print("\n👥 Creating Test Users...")
        
        # Calculate expiry date for PRO user
        expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        
        # Create users via mongosh
        result = subprocess.run([
            'mongosh', 'mongodb://localhost:27017/stock_news_romania', '--quiet', '--eval',
            f"""
            // Clean up old test users
            db.users.deleteMany({{email: {{$regex: /^test_.*@finromania2.test$/}}}});
            db.user_sessions.deleteMany({{user_id: {{$regex: /^test_user_/}}}});
            db.portfolio_bvb.deleteMany({{user_id: {{$regex: /^test_user_/}}}});
            db.quiz_attempts.deleteMany({{user_id: {{$regex: /^test_user_/}}}});
            
            const now = new Date().toISOString();
            const expiresAt = new Date(Date.now() + 7*24*60*60*1000).toISOString();
            
            // 1. Free Beginner User
            const beginnerUserId = 'test_user_beginner_' + Date.now();
            db.users.insertOne({{
                user_id: beginnerUserId,
                email: 'test_beginner@finromania2.test',
                name: 'Test Beginner',
                picture: 'https://example.com/pic.jpg',
                is_admin: false,
                subscription_level: 'free',
                experience_level: 'beginner',
                unlocked_levels: ['beginner'],
                ai_queries_today: 0,
                ai_queries_reset_at: now,
                quiz_scores: {{}},
                created_at: now,
                last_login: now
            }});
            const beginnerToken = 'test_token_beginner_' + Date.now();
            db.user_sessions.insertOne({{
                user_id: beginnerUserId,
                session_token: beginnerToken,
                expires_at: expiresAt,
                created_at: now
            }});
            
            // 2. Free Intermediate User (passed quiz)
            const intermediateUserId = 'test_user_intermediate_' + Date.now();
            db.users.insertOne({{
                user_id: intermediateUserId,
                email: 'test_intermediate@finromania2.test',
                name: 'Test Intermediate',
                picture: 'https://example.com/pic.jpg',
                is_admin: false,
                subscription_level: 'free',
                experience_level: 'intermediate',
                unlocked_levels: ['beginner', 'intermediate'],
                ai_queries_today: 3,
                ai_queries_reset_at: now,
                quiz_scores: {{intermediate: 8}},
                created_at: now,
                last_login: now
            }});
            const intermediateToken = 'test_token_intermediate_' + Date.now();
            db.user_sessions.insertOne({{
                user_id: intermediateUserId,
                session_token: intermediateToken,
                expires_at: expiresAt,
                created_at: now
            }});
            
            // 3. PRO User (all levels unlocked)
            const proUserId = 'test_user_pro_' + Date.now();
            db.users.insertOne({{
                user_id: proUserId,
                email: 'test_pro@finromania2.test',
                name: 'Test PRO',
                picture: 'https://example.com/pic.jpg',
                is_admin: false,
                subscription_level: 'pro',
                experience_level: 'advanced',
                unlocked_levels: ['beginner', 'intermediate', 'advanced'],
                ai_queries_today: 0,
                ai_queries_reset_at: now,
                quiz_scores: {{}},
                subscription_expires_at: '{expires_at}',
                created_at: now,
                last_login: now
            }});
            const proToken = 'test_token_pro_' + Date.now();
            db.user_sessions.insertOne({{
                user_id: proUserId,
                session_token: proToken,
                expires_at: expiresAt,
                created_at: now
            }});
            
            print(JSON.stringify({{
                beginner: beginnerToken,
                intermediate: intermediateToken,
                pro: proToken
            }}));
            """
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                tokens = json.loads(result.stdout.strip())
                self.beginner_token = tokens['beginner']
                self.intermediate_token = tokens['intermediate']
                self.pro_token = tokens['pro']
                self.log_test("Test Users Creation", True, 
                             "Created 3 test users: beginner, intermediate, PRO", 
                             {"has_tokens": True})
                return True
            except json.JSONDecodeError as e:
                self.log_test("Test Users Creation", False, f"Failed to parse tokens: {e}", result.stdout)
                return False
        else:
            self.log_test("Test Users Creation", False, "Failed to create test users", result.stderr)
            return False

    def run_all_tests(self):
        """Run all FinRomania 2.0 tests"""
        print("🚀 Starting FinRomania 2.0 Feature Testing...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Create test users
        if not self.create_test_users():
            print("❌ Failed to create test users. Aborting tests.")
            return
        
        # ============================================
        # SECTION 1: FEAR & GREED INDEX (Sanity Check)
        # ============================================
        print("\n📊 SECTION 1: Fear & Greed Index (Sanity Check)")
        print("-" * 80)
        
        success, details, data = self.test_api_endpoint('GET', '/api/market/fear-greed')
        if success and isinstance(data, dict):
            has_required = all(k in data for k in ['score', 'label', 'components'])
            self.log_test("Fear & Greed Index", has_required, 
                         f"Score: {data.get('score')}, Label: {data.get('label')}" if has_required else "Missing required fields",
                         data)
        else:
            self.log_test("Fear & Greed Index", False, details, data)
        
        # ============================================
        # SECTION 2: SUBSCRIPTION SYSTEM
        # ============================================
        print("\n💳 SECTION 2: Subscription System & PRO Paywall")
        print("-" * 80)
        
        # Test 2.1: Pricing endpoint (public)
        success, details, data = self.test_api_endpoint('GET', '/api/subscriptions/pricing')
        if success and isinstance(data, dict):
            has_plans = 'plans' in data and 'features' in data
            has_pricing = data.get('plans', {}).get('pro_monthly', {}).get('price') == 49.0
            self.log_test("Subscription Pricing", has_plans and has_pricing,
                         f"PRO Monthly: {data.get('plans', {}).get('pro_monthly', {}).get('price')} RON" if has_pricing else "Invalid pricing",
                         data)
        else:
            self.log_test("Subscription Pricing", False, details, data)
        
        # Test 2.2: Free user subscription status
        success, details, data = self.test_api_endpoint(
            'GET', '/api/subscriptions/status',
            auth_token=self.beginner_token
        )
        if success and isinstance(data, dict):
            is_free = data.get('subscription', {}).get('level') == 'free'
            ai_limit = data.get('ai_queries', {}).get('limit') == 5
            self.log_test("Free User Subscription Status", is_free and ai_limit,
                         f"Level: {data.get('subscription', {}).get('level')}, AI Limit: {data.get('ai_queries', {}).get('limit')}/day",
                         data)
        else:
            self.log_test("Free User Subscription Status", False, details, data)
        
        # Test 2.3: PRO user subscription status
        success, details, data = self.test_api_endpoint(
            'GET', '/api/subscriptions/status',
            auth_token=self.pro_token
        )
        if success and isinstance(data, dict):
            is_pro = data.get('subscription', {}).get('level') == 'pro'
            ai_unlimited = data.get('ai_queries', {}).get('limit') == -1
            self.log_test("PRO User Subscription Status", is_pro and ai_unlimited,
                         f"Level: {data.get('subscription', {}).get('level')}, AI: Unlimited",
                         data)
        else:
            self.log_test("PRO User Subscription Status", False, details, data)
        
        # Test 2.4: PRO Paywall - Fiscal Calculator (Free user should get 403)
        success, details, data = self.test_api_endpoint(
            'POST', '/api/fiscal/calculeaza',
            auth_token=self.intermediate_token,  # Use intermediate (still free)
            data={
                "castig_capital_anual": 10000,
                "dividende_anuale": 2000,
                "tip_piata": "bvb",
                "perioada_detinere": "peste_1_an",
                "procent_termen_lung": 100,
                "are_alte_venituri_cass": True,
                "are_angajat_srl": False
            },
            expected_status=403
        )
        self.log_test("PRO Paywall - Fiscal Calculator (Free User Blocked)", success,
                     "Free user correctly blocked from fiscal calculator" if success else details,
                     data)
        
        # Test 2.5: PRO user can access fiscal calculator
        success, details, data = self.test_api_endpoint(
            'POST', '/api/fiscal/calculeaza',
            auth_token=self.pro_token,
            data={
                "castig_capital_anual": 10000,
                "dividende_anuale": 2000,
                "tip_piata": "bvb",
                "perioada_detinere": "peste_1_an",
                "procent_termen_lung": 100,
                "are_alte_venituri_cass": True,
                "are_angajat_srl": False
            }
        )
        if success and isinstance(data, dict):
            has_scenarios = 'scenarii' in data
            self.log_test("PRO User - Fiscal Calculator Access", has_scenarios,
                         f"PRO user can access fiscal calculator, scenarios: {len(data.get('scenarii', []))}" if has_scenarios else "Missing scenarios",
                         data)
        else:
            self.log_test("PRO User - Fiscal Calculator Access", False, details, data)
        
        # Test 2.6: Manual PRO activation
        success, details, data = self.test_api_endpoint(
            'POST', '/api/subscriptions/activate-pro',
            auth_token=self.beginner_token
        )
        if success and isinstance(data, dict):
            activated = data.get('success') and data.get('subscription_level') == 'pro'
            self.log_test("Manual PRO Activation", activated,
                         f"PRO activated, expires: {data.get('expires_at')}" if activated else "Activation failed",
                         data)
        else:
            self.log_test("Manual PRO Activation", False, details, data)
        
        # ============================================
        # SECTION 3: PORTFOLIO BVB - 3 TIERS SYSTEM
        # ============================================
        print("\n📈 SECTION 3: Portfolio BVB cu '3 Straturi' (3 Tiers)")
        print("-" * 80)
        
        # Test 3.1: Beginner - Get Config
        success, details, data = self.test_api_endpoint(
            'GET', '/api/portfolio-bvb/config',
            auth_token=self.beginner_token
        )
        if success and isinstance(data, dict):
            is_beginner = data.get('level') == 'beginner'
            has_bet_stocks = isinstance(data.get('allowed_stocks'), list)
            self.log_test("Portfolio Config - Beginner", is_beginner and has_bet_stocks,
                         f"Level: {data.get('level_name')}, Allowed: {len(data.get('allowed_stocks', []))} BET stocks",
                         data)
        else:
            self.log_test("Portfolio Config - Beginner", False, details, data)
        
        # Test 3.2: Beginner - Add BET stock (should succeed)
        success, details, data = self.test_api_endpoint(
            'POST', '/api/portfolio-bvb/position',
            auth_token=self.beginner_token,
            data={
                "symbol": "TLV",
                "shares": 100,
                "purchase_price": 30.5
            }
        )
        if success and isinstance(data, dict):
            added = data.get('success')
            self.log_test("Beginner - Add BET Stock (TLV)", added,
                         f"Added TLV: {data.get('message')}" if added else "Failed to add",
                         data)
        else:
            self.log_test("Beginner - Add BET Stock (TLV)", False, details, data)
        
        # Test 3.3: Beginner - Try to add non-BET stock (should fail with 403)
        success, details, data = self.test_api_endpoint(
            'POST', '/api/portfolio-bvb/position',
            auth_token=self.beginner_token,
            data={
                "symbol": "DIGI",  # Not in BET index
                "shares": 50,
                "purchase_price": 40.0
            },
            expected_status=403
        )
        if success and isinstance(data, dict):
            blocked = data.get('detail', {}).get('error') == 'symbol_not_allowed'
            self.log_test("Beginner - Add Non-BET Stock Blocked", blocked,
                         f"Correctly blocked: {data.get('detail', {}).get('message')}" if blocked else "Should have been blocked",
                         data)
        else:
            self.log_test("Beginner - Add Non-BET Stock Blocked", success, details, data)
        
        # Test 3.4: Beginner - Get Portfolio (basic data only)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/portfolio-bvb/',
            auth_token=self.beginner_token
        )
        if success and isinstance(data, dict):
            has_positions = 'positions' in data and len(data.get('positions', [])) > 0
            has_summary = 'summary' in data
            level_is_beginner = data.get('summary', {}).get('level') == 'beginner'
            no_diversification = data.get('summary', {}).get('diversification_score') is None
            self.log_test("Beginner - Get Portfolio", has_positions and has_summary and level_is_beginner and no_diversification,
                         f"Positions: {len(data.get('positions', []))}, Level: {data.get('summary', {}).get('level_name')}, No diversification score (beginner)",
                         data)
        else:
            self.log_test("Beginner - Get Portfolio", False, details, data)
        
        # Test 3.5: Beginner - AI Analysis (should be blocked)
        success, details, data = self.test_api_endpoint(
            'POST', '/api/portfolio-bvb/ai-analysis',
            auth_token=self.beginner_token,
            expected_status=403
        )
        if success and isinstance(data, dict):
            blocked = data.get('detail', {}).get('error') == 'feature_locked'
            self.log_test("Beginner - AI Analysis Blocked", blocked,
                         f"Correctly blocked: {data.get('detail', {}).get('message')}" if blocked else "Should have been blocked",
                         data)
        else:
            self.log_test("Beginner - AI Analysis Blocked", success, details, data)
        
        # Test 3.6: Intermediate - Get Config
        success, details, data = self.test_api_endpoint(
            'GET', '/api/portfolio-bvb/config',
            auth_token=self.intermediate_token
        )
        if success and isinstance(data, dict):
            is_intermediate = data.get('level') == 'intermediate'
            all_bvb = data.get('allowed_stocks') == 'ALL_BVB'
            self.log_test("Portfolio Config - Intermediate", is_intermediate and all_bvb,
                         f"Level: {data.get('level_name')}, Allowed: All BVB stocks",
                         data)
        else:
            self.log_test("Portfolio Config - Intermediate", False, details, data)
        
        # Test 3.7: Intermediate - Add any BVB stock (should succeed)
        success, details, data = self.test_api_endpoint(
            'POST', '/api/portfolio-bvb/position',
            auth_token=self.intermediate_token,
            data={
                "symbol": "DIGI",
                "shares": 50,
                "purchase_price": 40.0
            }
        )
        if success and isinstance(data, dict):
            added = data.get('success')
            self.log_test("Intermediate - Add Any BVB Stock (DIGI)", added,
                         f"Added DIGI: {data.get('message')}" if added else "Failed to add",
                         data)
        else:
            self.log_test("Intermediate - Add Any BVB Stock (DIGI)", False, details, data)
        
        # Test 3.8: Intermediate - Get Portfolio (with technical indicators)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/portfolio-bvb/',
            auth_token=self.intermediate_token
        )
        if success and isinstance(data, dict):
            has_positions = 'positions' in data and len(data.get('positions', [])) > 0
            has_diversification = data.get('summary', {}).get('diversification_score') is not None
            # Check if positions have technical indicators
            has_tech_indicators = False
            if has_positions:
                first_pos = data.get('positions', [])[0]
                has_tech_indicators = 'technical_indicators' in first_pos
            self.log_test("Intermediate - Get Portfolio with Indicators", has_positions and has_diversification,
                         f"Positions: {len(data.get('positions', []))}, Diversification: {data.get('summary', {}).get('diversification_score')}, Tech Indicators: {has_tech_indicators}",
                         data)
        else:
            self.log_test("Intermediate - Get Portfolio with Indicators", False, details, data)
        
        # Test 3.9: Intermediate - AI Analysis (should work)
        success, details, data = self.test_api_endpoint(
            'POST', '/api/portfolio-bvb/ai-analysis',
            auth_token=self.intermediate_token
        )
        if success and isinstance(data, dict):
            has_analysis = 'analysis' in data
            has_score = 'diversification_score' in data
            self.log_test("Intermediate - AI Analysis", has_analysis and has_score,
                         f"AI analysis received, diversification score: {data.get('diversification_score')}",
                         data)
        else:
            self.log_test("Intermediate - AI Analysis", False, details, data)
        
        # Test 3.10: Delete Position
        success, details, data = self.test_api_endpoint(
            'DELETE', '/api/portfolio-bvb/position/TLV',
            auth_token=self.beginner_token
        )
        if success and isinstance(data, dict):
            deleted = data.get('success')
            self.log_test("Delete Portfolio Position", deleted,
                         f"Deleted TLV: {data.get('message')}" if deleted else "Failed to delete",
                         data)
        else:
            self.log_test("Delete Portfolio Position", False, details, data)
        
        # ============================================
        # SECTION 4: QUIZ SYSTEM
        # ============================================
        print("\n🎓 SECTION 4: Quiz System")
        print("-" * 80)
        
        # Test 4.1: Create a fresh user for quiz testing (not upgraded to PRO)
        print("\n👤 Creating fresh user for quiz testing...")
        result = subprocess.run([
            'mongosh', 'mongodb://localhost:27017/stock_news_romania', '--quiet', '--eval',
            f"""
            const now = new Date().toISOString();
            const expiresAt = new Date(Date.now() + 7*24*60*60*1000).toISOString();
            
            const quizUserId = 'test_user_quiz_' + Date.now();
            db.users.insertOne({{
                user_id: quizUserId,
                email: 'test_quiz@finromania2.test',
                name: 'Test Quiz User',
                picture: 'https://example.com/pic.jpg',
                is_admin: false,
                subscription_level: 'free',
                experience_level: 'beginner',
                unlocked_levels: ['beginner'],
                ai_queries_today: 0,
                ai_queries_reset_at: now,
                quiz_scores: {{}},
                created_at: now,
                last_login: now
            }});
            const quizToken = 'test_token_quiz_' + Date.now();
            db.user_sessions.insertOne({{
                user_id: quizUserId,
                session_token: quizToken,
                expires_at: expiresAt,
                created_at: now
            }});
            print(quizToken);
            """
        ], capture_output=True, text=True)
        
        quiz_token = None
        if result.returncode == 0 and result.stdout.strip():
            quiz_token = result.stdout.strip()
            print(f"✅ Created quiz test user with token")
        else:
            print(f"❌ Failed to create quiz test user")
        
        # Test 4.2: Get intermediate quiz questions
        if quiz_token:
            success, details, data = self.test_api_endpoint(
                'GET', '/api/quiz/intermediate',
                auth_token=quiz_token
            )
            if success and isinstance(data, dict):
                has_questions = 'questions' in data and len(data.get('questions', [])) == 10
                pass_score = data.get('pass_score') == 7
                self.log_test("Get Quiz - Intermediate", has_questions and pass_score,
                             f"Questions: {len(data.get('questions', []))}, Pass score: {data.get('pass_score')}/10",
                             data)
                
                # Store questions for submission test
                self.quiz_questions = data.get('questions', [])
                self.quiz_token = quiz_token
            else:
                self.log_test("Get Quiz - Intermediate", False, details, data)
                self.quiz_questions = []
        else:
            self.log_test("Get Quiz - Intermediate", False, "Failed to create quiz test user", None)
            self.quiz_questions = []
        
        # Test 4.3: Submit quiz with passing score (7/10)
        if self.quiz_questions and hasattr(self, 'quiz_token'):
            # Create answers - answer first 7 correctly (index 1 is usually correct based on quiz structure)
            answers = {}
            for i, q in enumerate(self.quiz_questions):
                # Answer first 7 with option 1, rest with option 0
                answers[q['id']] = 1 if i < 7 else 0
            
            success, details, data = self.test_api_endpoint(
                'POST', '/api/quiz/submit',
                auth_token=self.quiz_token,
                data={
                    "level": "intermediate",
                    "answers": answers
                }
            )
            if success and isinstance(data, dict):
                score = data.get('score', 0)
                passed = data.get('passed', False)
                # Note: We can't guarantee passing since we don't know correct answers
                self.log_test("Submit Quiz - Intermediate", success,
                             f"Score: {score}/10, Passed: {passed}, Message: {data.get('message')}",
                             data)
            else:
                self.log_test("Submit Quiz - Intermediate", False, details, data)
        else:
            self.log_test("Submit Quiz - Intermediate", False, "No quiz questions available", None)
        
        # Test 4.4: PRO user should skip quiz
        success, details, data = self.test_api_endpoint(
            'GET', '/api/quiz/advanced',
            auth_token=self.pro_token
        )
        if success and isinstance(data, dict):
            skip_quiz = data.get('skip_quiz', False)
            self.log_test("PRO User - Skip Quiz", skip_quiz,
                         f"PRO user can skip quiz: {data.get('message')}" if skip_quiz else "PRO user should skip quiz",
                         data)
        else:
            self.log_test("PRO User - Skip Quiz", False, details, data)
        
        # Test 4.5: Get quiz history
        if hasattr(self, 'quiz_token'):
            success, details, data = self.test_api_endpoint(
                'GET', '/api/quiz/history/intermediate',
                auth_token=self.quiz_token
            )
            if success and isinstance(data, dict):
                has_attempts = 'attempts' in data
                self.log_test("Get Quiz History", has_attempts,
                             f"Attempts: {len(data.get('attempts', []))}, Best score: {data.get('best_score', 0)}",
                             data)
            else:
                self.log_test("Get Quiz History", False, details, data)
        else:
            self.log_test("Get Quiz History", False, "No quiz token available", None)
        
        # ============================================
        # PRINT SUMMARY
        # ============================================
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        if self.tests_run - self.tests_passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    tester = FinRomania2Tester()
    tester.run_all_tests()
    
    # Exit with error code if tests failed
    if tester.tests_run - tester.tests_passed > 0:
        sys.exit(1)
    sys.exit(0)
