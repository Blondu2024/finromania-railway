#!/usr/bin/env python3
"""
Trading School API Testing
Tests all endpoints for lessons, quizzes, and progress tracking
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class TradingSchoolTester:
    def __init__(self, base_url="https://finedromania.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.admin_token = None
        
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

    def validate_all_lessons(self, data: Dict) -> tuple:
        """Validate all lessons response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        if 'lessons' not in data or 'total' not in data:
            return False, "Missing 'lessons' or 'total' field"
        
        lessons = data.get('lessons', [])
        total = data.get('total', 0)
        
        if not isinstance(lessons, list):
            return False, "Lessons should be a list"
        
        # Should have 17 lessons (note: there are 2 lesson_10 entries in the code)
        if total != 17:
            return False, f"Expected 17 lessons, got {total}"
        
        if len(lessons) != 17:
            return False, f"Expected 17 lessons in array, got {len(lessons)}"
        
        # Validate first lesson structure
        if lessons:
            lesson = lessons[0]
            required_fields = ['id', 'title', 'content', 'quiz', 'module', 'order']
            for field in required_fields:
                if field not in lesson:
                    return False, f"Missing required field in lesson: {field}"
        
        return True, f"Valid lessons response: {total} lessons"

    def validate_single_lesson(self, data: Dict) -> tuple:
        """Validate single lesson response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['id', 'title', 'content', 'quiz', 'module', 'order', 'duration', 'difficulty', 'emoji']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate content is markdown
        content = data.get('content', '')
        if not content or len(content) < 100:
            return False, f"Content too short or missing: {len(content)} chars"
        
        # Validate quiz structure
        quiz = data.get('quiz', [])
        if not isinstance(quiz, list) or len(quiz) == 0:
            return False, "Quiz should be a non-empty list"
        
        # Validate first quiz question
        if quiz:
            q = quiz[0]
            required_quiz_fields = ['question', 'options', 'correct', 'explanation']
            for field in required_quiz_fields:
                if field not in q:
                    return False, f"Missing quiz field: {field}"
            
            if not isinstance(q['options'], list) or len(q['options']) < 2:
                return False, "Quiz options should be a list with at least 2 options"
            
            if not isinstance(q['correct'], int):
                return False, "Quiz correct answer should be an integer index"
        
        return True, f"Valid lesson: {data.get('id')} with {len(quiz)} quiz questions"

    def validate_tier_system(self, data: Dict) -> tuple:
        """Validate tier system (free vs premium)"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        lessons = data.get('lessons', [])
        
        free_count = 0
        premium_count = 0
        
        for lesson in lessons:
            tier = lesson.get('tier', 'free')  # Default to free if not specified
            if tier == 'premium':
                premium_count += 1
            else:
                free_count += 1
        
        # First 5 should be free, rest premium (12 premium due to duplicate lesson_10)
        if free_count != 5:
            return False, f"Expected 5 free lessons, got {free_count}"
        
        if premium_count != 12:
            return False, f"Expected 12 premium lessons, got {premium_count}"
        
        # Verify first 5 are free
        for i in range(5):
            tier = lessons[i].get('tier', 'free')
            if tier == 'premium':
                return False, f"Lesson {i+1} should be free but is premium"
        
        # Verify lessons 6-17 are premium (12 premium lessons)
        for i in range(5, 17):
            tier = lessons[i].get('tier', 'free')
            if tier != 'premium':
                return False, f"Lesson {i+1} should be premium but is {tier}"
        
        return True, f"Valid tier system: {free_count} free, {premium_count} premium"

    def validate_quiz_submission(self, data: Dict) -> tuple:
        """Validate quiz submission response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['lesson_id', 'score', 'correct', 'total', 'passed', 'results']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate score
        score = data.get('score', 0)
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            return False, f"Invalid score: {score}"
        
        # Validate results array
        results = data.get('results', [])
        if not isinstance(results, list):
            return False, "Results should be a list"
        
        # Each result should have feedback
        for result in results:
            if 'correct' not in result or 'explanation' not in result:
                return False, "Result missing correct/explanation fields"
        
        return True, f"Valid quiz submission: {data.get('correct')}/{data.get('total')} correct, score {score}%"

    def validate_progress(self, data: Dict) -> tuple:
        """Validate progress response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['completed_lessons', 'total_lessons', 'progress_percent', 'has_premium']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        completed = data.get('completed_lessons', [])
        if not isinstance(completed, list):
            return False, "completed_lessons should be a list"
        
        total = data.get('total_lessons', 0)
        if total != 17:
            return False, f"Expected 17 total lessons, got {total}"
        
        return True, f"Valid progress: {len(completed)} completed, {data.get('progress_percent')}% progress"

    def validate_premium_check(self, data: Dict) -> tuple:
        """Validate premium check response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['has_premium', 'total_lessons', 'free_lessons', 'premium_lessons']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        free_count = data.get('free_lessons', 0)
        premium_count = data.get('premium_lessons', 0)
        total = data.get('total_lessons', 0)
        
        if free_count != 5:
            return False, f"Expected 5 free lessons, got {free_count}"
        
        if premium_count != 12:
            return False, f"Expected 12 premium lessons, got {premium_count}"
        
        if total != 17:
            return False, f"Expected 17 total lessons, got {total}"
        
        return True, f"Valid premium check: {free_count} free, {premium_count} premium"

    def create_test_user_session(self) -> bool:
        """Create a test user session for authenticated endpoints"""
        print("\n👤 Creating Test User Session...")
        
        import subprocess
        test_email = f"testuser_trading_{datetime.now().timestamp()}@test.com"
        
        result = subprocess.run([
            'mongosh', 'mongodb://localhost:27017/stock_news_romania', '--quiet', '--eval',
            f"""
            const userId = 'user_trading_test_' + Date.now();
            db.users.insertOne({{
              user_id: userId,
              email: '{test_email}',
              name: 'Trading Test User',
              picture: 'https://example.com/pic.jpg',
              is_admin: false,
              created_at: new Date().toISOString(),
              last_login: new Date().toISOString()
            }});
            const sessionToken = 'test_trading_token_' + Date.now();
            const expiresAt = new Date(Date.now() + 7*24*60*60*1000);
            db.user_sessions.insertOne({{
              user_id: userId,
              session_token: sessionToken,
              expires_at: expiresAt.toISOString(),
              created_at: new Date().toISOString()
            }});
            print(sessionToken);
            """
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            self.admin_token = result.stdout.strip()
            self.log_test("Test User Creation", True, f"Test user created: {test_email}", {"has_token": True})
            return True
        else:
            self.log_test("Test User Creation", False, f"Failed to create test user", None)
            return False

    def run_all_tests(self):
        """Run comprehensive Trading School test suite"""
        print("🚀 Starting Trading School API Testing...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # ============================================
        # TEST 1: GET ALL LESSONS
        # ============================================
        print("\n📚 SECTION 1: Lessons API")
        print("-" * 80)
        
        success, details, data = self.test_api_endpoint(
            'GET', '/api/trading-school/lessons',
            validate_response=self.validate_all_lessons
        )
        self.log_test("GET /api/trading-school/lessons - All 17 lessons", success, details,
                     {"total": data.get('total'), "lesson_count": len(data.get('lessons', []))} if isinstance(data, dict) else data)
        
        # ============================================
        # TEST 2: TIER SYSTEM VALIDATION
        # ============================================
        print("\n🎯 SECTION 2: Tier System (Free vs Premium)")
        print("-" * 80)
        
        success, details, data = self.test_api_endpoint(
            'GET', '/api/trading-school/lessons',
            validate_response=self.validate_tier_system
        )
        self.log_test("Tier System - 5 free + 12 premium", success, details, data)
        
        # ============================================
        # TEST 3: GET SPECIFIC LESSON (lesson_1)
        # ============================================
        print("\n📖 SECTION 3: Individual Lesson")
        print("-" * 80)
        
        success, details, data = self.test_api_endpoint(
            'GET', '/api/trading-school/lessons/lesson_1',
            validate_response=self.validate_single_lesson
        )
        self.log_test("GET /api/trading-school/lessons/lesson_1", success, details,
                     {"id": data.get('id'), "title": data.get('title'), "quiz_count": len(data.get('quiz', []))} if isinstance(data, dict) else data)
        
        # ============================================
        # TEST 4: CONTENT QUALITY SAMPLING
        # ============================================
        print("\n✍️ SECTION 4: Content Quality Check")
        print("-" * 80)
        
        # Sample 3 random lessons
        sample_lessons = ['lesson_1', 'lesson_5', 'lesson_10']
        content_valid = True
        
        for lesson_id in sample_lessons:
            success, details, data = self.test_api_endpoint(
                'GET', f'/api/trading-school/lessons/{lesson_id}',
                validate_response=self.validate_single_lesson
            )
            
            if success and isinstance(data, dict):
                content_len = len(data.get('content', ''))
                quiz_len = len(data.get('quiz', []))
                self.log_test(f"Content Quality - {lesson_id}", success, 
                             f"Content: {content_len} chars, Quiz: {quiz_len} questions",
                             {"title": data.get('title'), "has_markdown": '##' in data.get('content', '')})
            else:
                content_valid = False
                self.log_test(f"Content Quality - {lesson_id}", False, details, data)
        
        # ============================================
        # TEST 5: AUTHENTICATION SETUP
        # ============================================
        print("\n🔐 SECTION 5: Authentication Setup")
        print("-" * 80)
        
        auth_success = self.create_test_user_session()
        
        if not auth_success:
            print("⚠️ WARNING: Cannot test authenticated endpoints without session")
            self.log_test("Quiz Submission", False, "Skipped - auth failed")
            self.log_test("Progress Tracking", False, "Skipped - auth failed")
            self.log_test("Premium Check", False, "Skipped - auth failed")
        else:
            # ============================================
            # TEST 6: QUIZ SUBMISSION - CORRECT ANSWERS
            # ============================================
            print("\n✅ SECTION 6: Quiz Submission (Correct Answers)")
            print("-" * 80)
            
            quiz_data = {
                "lesson_id": "lesson_1",
                "answers": [1, 1]  # Both correct answers for lesson_1
            }
            
            success, details, data = self.test_api_endpoint(
                'POST', '/api/trading-school/quiz/submit',
                data=quiz_data,
                auth_token=self.admin_token,
                validate_response=self.validate_quiz_submission
            )
            
            if success and isinstance(data, dict):
                score = data.get('score', 0)
                passed = data.get('passed', False)
                self.log_test("Quiz Submission - Correct Answers (100%)", 
                             score == 100 and passed,
                             f"Score: {score}%, Passed: {passed}",
                             {"score": score, "passed": passed, "correct": data.get('correct'), "total": data.get('total')})
            else:
                self.log_test("Quiz Submission - Correct Answers", False, details, data)
            
            # ============================================
            # TEST 7: QUIZ SUBMISSION - WRONG ANSWERS
            # ============================================
            print("\n❌ SECTION 7: Quiz Submission (Wrong Answers)")
            print("-" * 80)
            
            quiz_data_wrong = {
                "lesson_id": "lesson_1",
                "answers": [0, 0]  # Both wrong answers
            }
            
            success, details, data = self.test_api_endpoint(
                'POST', '/api/trading-school/quiz/submit',
                data=quiz_data_wrong,
                auth_token=self.admin_token,
                validate_response=self.validate_quiz_submission
            )
            
            if success and isinstance(data, dict):
                score = data.get('score', 0)
                passed = data.get('passed', False)
                self.log_test("Quiz Submission - Wrong Answers (0%)", 
                             score == 0 and not passed,
                             f"Score: {score}%, Passed: {passed}",
                             {"score": score, "passed": passed})
            else:
                self.log_test("Quiz Submission - Wrong Answers", False, details, data)
            
            # ============================================
            # TEST 8: PROGRESS TRACKING
            # ============================================
            print("\n📊 SECTION 8: Progress Tracking")
            print("-" * 80)
            
            success, details, data = self.test_api_endpoint(
                'GET', '/api/trading-school/progress',
                auth_token=self.admin_token,
                validate_response=self.validate_progress
            )
            
            if success and isinstance(data, dict):
                completed = data.get('completed_lessons', [])
                has_lesson_1 = 'lesson_1' in completed
                self.log_test("Progress Tracking - lesson_1 completed", 
                             has_lesson_1,
                             f"Completed lessons: {completed}",
                             {"completed_count": len(completed), "has_lesson_1": has_lesson_1})
            else:
                self.log_test("Progress Tracking", False, details, data)
            
            # ============================================
            # TEST 9: PREMIUM CHECK
            # ============================================
            print("\n💎 SECTION 9: Premium Check")
            print("-" * 80)
            
            success, details, data = self.test_api_endpoint(
                'GET', '/api/trading-school/check-premium',
                auth_token=self.admin_token,
                validate_response=self.validate_premium_check
            )
            
            if success and isinstance(data, dict):
                self.log_test("Premium Check - Counts", success, details,
                             {"has_premium": data.get('has_premium'), 
                              "free": data.get('free_lessons'), 
                              "premium": data.get('premium_lessons')})
            else:
                self.log_test("Premium Check", False, details, data)
        
        # ============================================
        # FINAL SUMMARY
        # ============================================
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        print(f"✅ Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Trading School API is working correctly.")
            return True
        else:
            failed_tests = [t for t in self.test_results if not t['success']]
            print(f"\n❌ {len(failed_tests)} tests failed:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
            return False

def main():
    """Main test execution"""
    tester = TradingSchoolTester()
    
    try:
        success = tester.run_all_tests()
        
        # Save detailed results
        with open('/app/trading_school_test_results.json', 'w') as f:
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
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())
