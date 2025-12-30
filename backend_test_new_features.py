#!/usr/bin/env python3
"""
Backend API Testing for FinRomania New Features - Education, Risk Assessment, AI Advisor
Tests the new features added: Education Package, Risk Assessment, and AI Advisor
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class FinRomaniaNewFeaturesAPITester:
    def __init__(self, base_url="https://finmarket-4.preview.emergentagent.com"):
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
              is_admin: false,
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
            db.risk_assessments.deleteMany({{user_id: '{self.user_id}'}});
            db.advisor_questions.deleteMany({{user_id: '{self.user_id}'}});
            print('CLEANUP: Test data removed');
            """
            
            subprocess.run(['mongosh', '--eval', mongo_script], timeout=30)
        except Exception as e:
            print(f"Cleanup warning: {e}")

    def validate_education_package(self, data: Dict) -> tuple:
        """Validate education package response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['id', 'name', 'description', 'price', 'currency', 'lessons_count']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Check specific values
        if data.get('price') != 5.0:
            return False, f"Expected price 5.0, got {data.get('price')}"
        
        if data.get('currency') != 'ron':
            return False, f"Expected currency 'ron', got {data.get('currency')}"
            
        if data.get('lessons_count') != 6:
            return False, f"Expected 6 lessons, got {data.get('lessons_count')}"
                
        return True, f"Valid package: {data.get('name')} - {data.get('price')} {data.get('currency').upper()}"

    def validate_education_lessons(self, data: Dict) -> tuple:
        """Validate education lessons response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['lessons', 'has_access', 'total_lessons', 'free_lessons']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        lessons = data.get('lessons', [])
        if not isinstance(lessons, list):
            return False, "Lessons should be a list"
            
        if len(lessons) != 6:
            return False, f"Expected 6 lessons, got {len(lessons)}"
        
        # Check first lesson is free
        first_lesson = lessons[0] if lessons else None
        if not first_lesson or not first_lesson.get('is_free'):
            return False, "First lesson should be free"
            
        if first_lesson.get('id') != 'lesson_1':
            return False, f"First lesson should have id 'lesson_1', got {first_lesson.get('id')}"
                
        return True, f"Valid lessons: {len(lessons)} total, {data.get('free_lessons')} free"

    def validate_lesson_content(self, data: Dict) -> tuple:
        """Validate individual lesson content"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['id', 'order', 'title', 'description', 'duration', 'content', 'is_free']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Check it's lesson 1 and free
        if data.get('id') != 'lesson_1':
            return False, f"Expected lesson_1, got {data.get('id')}"
            
        if not data.get('is_free'):
            return False, "Lesson 1 should be free"
            
        content = data.get('content', '')
        if len(content) < 100:
            return False, f"Content too short: {len(content)} characters"
                
        return True, f"Valid lesson: {data.get('title')} ({len(content)} chars content)"

    def validate_risk_questions(self, data: Dict) -> tuple:
        """Validate risk assessment questions"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['questions', 'total_questions']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        questions = data.get('questions', [])
        if not isinstance(questions, list):
            return False, "Questions should be a list"
            
        if len(questions) != 7:
            return False, f"Expected 7 questions, got {len(questions)}"
        
        # Validate first question structure
        first_q = questions[0] if questions else None
        if not first_q:
            return False, "No questions found"
            
        q_required_fields = ['id', 'question', 'options']
        for field in q_required_fields:
            if field not in first_q:
                return False, f"Question missing field: {field}"
        
        options = first_q.get('options', [])
        if not isinstance(options, list) or len(options) < 2:
            return False, "Question should have at least 2 options"
                
        return True, f"Valid questions: {len(questions)} questions with options"

    def validate_tip_of_day(self, data: Dict) -> tuple:
        """Validate tip of the day response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
            
        required_fields = ['tip', 'category', 'date']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        tip = data.get('tip', '')
        if len(tip) < 20:
            return False, f"Tip too short: {len(tip)} characters"
            
        category = data.get('category', '')
        if not category:
            return False, "Category should not be empty"
                
        return True, f"Valid tip: {category} - {len(tip)} chars"

    def run_new_features_tests(self):
        """Run comprehensive test suite for new features"""
        print("🚀 Starting FinRomania New Features Testing...")
        print(f"📍 Testing against: {self.base_url}")
        print("🎯 Features: Education, Risk Assessment, AI Advisor")
        print("=" * 60)
        
        # Setup test user for auth-required endpoints
        success, details = self.setup_test_user()
        self.log_test("Setup Test User & Session", success, details)
        
        # Test 1: Education Package - Get package details
        success, details, data = self.test_api_endpoint(
            'GET', '/api/education/package',
            validate_response=self.validate_education_package
        )
        self.log_test("Education - Get Package Details", success, details, data)
        
        # Test 2: Education Lessons - Get all lessons (no auth)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/education/lessons',
            validate_response=self.validate_education_lessons
        )
        self.log_test("Education - Get All Lessons", success, details, data)
        
        # Test 3: Education Lessons - Get lesson 1 (free, no auth required)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/education/lessons/lesson_1',
            validate_response=self.validate_lesson_content
        )
        self.log_test("Education - Get Free Lesson Content", success, details, data)
        
        # Test 4: Education Lessons - Try to get lesson 2 (should fail without purchase)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/education/lessons/lesson_2',
            expected_status=403
        )
        self.log_test("Education - Access Paid Lesson (Expected 403)", success, details)
        
        # Test 5: Risk Assessment - Get questions
        success, details, data = self.test_api_endpoint(
            'GET', '/api/risk-assessment/questions',
            validate_response=self.validate_risk_questions
        )
        self.log_test("Risk Assessment - Get Questions", success, details, data)
        
        # Test 6: Risk Assessment - Get profiles (reference data)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/risk-assessment/profiles'
        )
        self.log_test("Risk Assessment - Get Risk Profiles", success, details, data)
        
        # Test 7: AI Advisor - Get tip of the day
        success, details, data = self.test_api_endpoint(
            'GET', '/api/advisor/tip-of-the-day',
            validate_response=self.validate_tip_of_day
        )
        self.log_test("AI Advisor - Get Tip of the Day", success, details, data)
        
        # Test 8: AI Advisor - Portfolio advice (requires auth)
        if self.session_token:
            success, details, data = self.test_api_endpoint(
                'GET', '/api/advisor/portfolio-advice',
                auth_required=True
            )
            self.log_test("AI Advisor - Get Portfolio Advice", success, details, data)
        
        # Test 9: AI Advisor - Ask question (requires auth)
        if self.session_token:
            success, details, data = self.test_api_endpoint(
                'POST', '/api/advisor/ask',
                data={'question': 'Ce este un ETF?'},
                auth_required=True
            )
            self.log_test("AI Advisor - Ask Question", success, details, data)
        
        # Test 10: Risk Assessment - Submit assessment (requires auth)
        if self.session_token:
            # Sample answers for all 7 questions
            sample_answers = [
                {'question_id': 'q1', 'answer_value': 'long'},
                {'question_id': 'q2', 'answer_value': 'buy'},
                {'question_id': 'q3', 'answer_value': 'growth'},
                {'question_id': 'q4', 'answer_value': 'basic'},
                {'question_id': 'q5', 'answer_value': 'medium'},
                {'question_id': 'q6', 'answer_value': 'yes'},
                {'question_id': 'q7', 'answer_value': 'risky'}
            ]
            
            success, details, data = self.test_api_endpoint(
                'POST', '/api/risk-assessment/submit',
                data={'answers': sample_answers},
                auth_required=True
            )
            self.log_test("Risk Assessment - Submit Assessment", success, details, data)
        
        # Test 11: Risk Assessment - Get my profile (after submission)
        if self.session_token:
            success, details, data = self.test_api_endpoint(
                'GET', '/api/risk-assessment/my-profile',
                auth_required=True
            )
            self.log_test("Risk Assessment - Get My Profile", success, details, data)
        
        # Test 12: Education - Check access (should be false without purchase)
        if self.session_token:
            success, details, data = self.test_api_endpoint(
                'GET', '/api/education/my-access',
                auth_required=True
            )
            self.log_test("Education - Check My Access", success, details, data)
        
        # Cleanup
        self.cleanup_test_user()
        
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All new features tests passed!")
            return True
        else:
            failed_tests = [t for t in self.test_results if not t['success']]
            print(f"❌ {len(failed_tests)} tests failed:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
            return False

def main():
    """Main test execution"""
    tester = FinRomaniaNewFeaturesAPITester()
    
    try:
        success = tester.run_new_features_tests()
        
        # Save detailed results
        with open('/app/backend_test_new_features_results.json', 'w') as f:
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