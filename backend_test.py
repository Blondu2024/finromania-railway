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
    def __init__(self, base_url="https://finromania-3.preview.emergentagent.com"):
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
        
        # Check for bvb_source field (direct) or nested bvb.source
        bvb_source = data.get('bvb_source', '') or data.get('bvb', {}).get('source', '')
        
        if not bvb_source:
            return False, "No BVB source information found in response"
        
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

    def validate_financial_lessons(self, data: Dict) -> tuple:
        """Validate financial education lessons response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        if 'lessons' not in data or 'total' not in data:
            return False, "Missing 'lessons' or 'total' field"
        
        lessons = data.get('lessons', [])
        total = data.get('total', 0)
        
        if not isinstance(lessons, list):
            return False, "Lessons should be a list"
        
        # Should have 15 lessons
        if total != 15:
            return False, f"Expected 15 lessons, got {total}"
        
        if len(lessons) != 15:
            return False, f"Expected 15 lessons in array, got {len(lessons)}"
        
        # Validate lesson structure
        for lesson in lessons[:3]:  # Check first 3 lessons
            required_fields = ['id', 'title', 'subtitle', 'content', 'quiz', 'module', 'order', 'difficulty', 'emoji']
            for field in required_fields:
                if field not in lesson:
                    return False, f"Missing required field in lesson: {field}"
        
        # Check modules distribution
        module_1 = [l for l in lessons if l.get('module') == 1]
        module_2 = [l for l in lessons if l.get('module') == 2]
        module_3 = [l for l in lessons if l.get('module') == 3]
        
        if len(module_1) != 5:
            return False, f"Module 1 should have 5 lessons, got {len(module_1)}"
        if len(module_2) != 5:
            return False, f"Module 2 should have 5 lessons, got {len(module_2)}"
        if len(module_3) != 5:
            return False, f"Module 3 should have 5 lessons, got {len(module_3)}"
        
        return True, f"Valid financial lessons: {total} lessons across 3 modules"

    def validate_financial_lesson_detail(self, data: Dict) -> tuple:
        """Validate individual financial lesson response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['id', 'title', 'subtitle', 'content', 'quiz', 'module', 'order', 'difficulty', 'emoji']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate content is in Romanian and substantial
        content = data.get('content', '')
        if len(content) < 500:
            return False, f"Content too short: {len(content)} chars, expected 500+"
        
        # Check for Romanian content indicators
        romanian_indicators = ['RON', 'România', 'BNR', 'BVB', 'lei', 'lună']
        if not any(indicator in content for indicator in romanian_indicators):
            return False, "Content doesn't appear to be Romanian-focused"
        
        # Validate quiz structure
        quiz = data.get('quiz', [])
        if not isinstance(quiz, list) or len(quiz) == 0:
            return False, "Quiz should be a non-empty list"
        
        for q in quiz:
            quiz_fields = ['question', 'options', 'correct', 'explanation']
            for field in quiz_fields:
                if field not in q:
                    return False, f"Missing quiz field: {field}"
            
            if not isinstance(q['options'], list) or len(q['options']) < 2:
                return False, "Quiz options should be a list with at least 2 options"
            
            if not isinstance(q['correct'], int) or q['correct'] >= len(q['options']):
                return False, "Quiz correct answer index is invalid"
        
        return True, f"Valid lesson: {data['title']} with {len(quiz)} quiz questions"

    def validate_quiz_submission(self, data: Dict) -> tuple:
        """Validate quiz submission response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['lesson_id', 'score', 'correct', 'total', 'passed', 'results', 'message']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate score calculation
        score = data.get('score', 0)
        correct = data.get('correct', 0)
        total = data.get('total', 0)
        
        if total == 0:
            return False, "Total questions should be > 0"
        
        expected_score = (correct / total) * 100
        if abs(score - expected_score) > 0.1:
            return False, f"Score calculation error: expected {expected_score}, got {score}"
        
        # Validate pass threshold (80%)
        passed = data.get('passed', False)
        expected_passed = score >= 80
        if passed != expected_passed:
            return False, f"Pass status error: score {score}%, passed={passed}, expected={expected_passed}"
        
        # Validate results structure
        results = data.get('results', [])
        if len(results) != total:
            return False, f"Results count mismatch: expected {total}, got {len(results)}"
        
        return True, f"Valid quiz result: {score}% ({correct}/{total}), passed={passed}"

    def validate_financial_progress(self, data: Dict) -> tuple:
        """Validate financial education progress response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['completed_lessons', 'total_lessons', 'progress_percent']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        completed = data.get('completed_lessons', [])
        total = data.get('total_lessons', 0)
        progress = data.get('progress_percent', 0)
        
        if not isinstance(completed, list):
            return False, "completed_lessons should be a list"
        
        if total != 15:
            return False, f"Expected 15 total lessons, got {total}"
        
        # Validate progress calculation
        expected_progress = (len(completed) / total) * 100 if total > 0 else 0
        if abs(progress - expected_progress) > 0.1:
            return False, f"Progress calculation error: expected {expected_progress}, got {progress}"
        
        return True, f"Valid progress: {len(completed)}/{total} lessons ({progress}%)"

    def validate_global_overview(self, data: Dict) -> tuple:
        """Validate global markets overview response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['indices', 'commodities', 'crypto', 'forex', 'sentiment', 'market_status', 'updated_at']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate indices (should have 10)
        indices = data.get('indices', [])
        if not isinstance(indices, list):
            return False, "Indices should be a list"
        if len(indices) < 8:  # Allow some flexibility for market hours
            return False, f"Expected at least 8 indices, got {len(indices)}"
        
        # Validate commodities (should have 6)
        commodities = data.get('commodities', [])
        if not isinstance(commodities, list):
            return False, "Commodities should be a list"
        if len(commodities) < 5:  # Allow some flexibility
            return False, f"Expected at least 5 commodities, got {len(commodities)}"
        
        # Validate crypto (should have 5)
        crypto = data.get('crypto', [])
        if not isinstance(crypto, list):
            return False, "Crypto should be a list"
        if len(crypto) < 4:  # Allow some flexibility
            return False, f"Expected at least 4 crypto assets, got {len(crypto)}"
        
        # Validate forex (should have 4)
        forex = data.get('forex', [])
        if not isinstance(forex, list):
            return False, "Forex should be a list"
        if len(forex) < 3:  # Allow some flexibility
            return False, f"Expected at least 3 forex pairs, got {len(forex)}"
        
        # Validate sentiment data
        sentiment = data.get('sentiment', {})
        sentiment_fields = ['gainers', 'losers', 'avg_change', 'status']
        for field in sentiment_fields:
            if field not in sentiment:
                return False, f"Missing sentiment field: {field}"
        
        # Validate market status
        market_status = data.get('market_status', {})
        expected_markets = ['us', 'europe', 'asia', 'crypto']
        for market in expected_markets:
            if market not in market_status:
                return False, f"Missing market status for: {market}"
            market_data = market_status[market]
            if 'name' not in market_data or 'open' not in market_data:
                return False, f"Invalid market status structure for {market}"
        
        return True, f"Valid global overview: {len(indices)} indices, {len(commodities)} commodities, {len(crypto)} crypto, {len(forex)} forex"

    def validate_global_indices_only(self, data: Dict) -> tuple:
        """Validate global indices endpoint response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['indices', 'count', 'updated_at']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        indices = data.get('indices', [])
        if not isinstance(indices, list):
            return False, "Indices should be a list"
        
        if len(indices) < 8:  # Should have 10 but allow some flexibility
            return False, f"Expected at least 8 indices, got {len(indices)}"
        
        # Validate structure of first index
        if indices:
            index = indices[0]
            required_index_fields = ['symbol', 'name', 'price', 'change', 'change_percent', 'flag', 'country']
            for field in required_index_fields:
                if field not in index:
                    return False, f"Missing index field: {field}"
        
        return True, f"Valid global indices: {len(indices)} indices"

    def validate_commodities_only(self, data: Dict) -> tuple:
        """Validate commodities endpoint response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['commodities', 'count', 'updated_at']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        commodities = data.get('commodities', [])
        if not isinstance(commodities, list):
            return False, "Commodities should be a list"
        
        if len(commodities) < 5:  # Should have 6 but allow some flexibility
            return False, f"Expected at least 5 commodities, got {len(commodities)}"
        
        # Validate structure of first commodity
        if commodities:
            commodity = commodities[0]
            required_fields = ['symbol', 'name', 'price', 'change', 'change_percent', 'flag', 'unit']
            for field in required_fields:
                if field not in commodity:
                    return False, f"Missing commodity field: {field}"
        
        return True, f"Valid commodities: {len(commodities)} commodities"

    def validate_crypto_only(self, data: Dict) -> tuple:
        """Validate crypto endpoint response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['crypto', 'count', 'updated_at']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        crypto = data.get('crypto', [])
        if not isinstance(crypto, list):
            return False, "Crypto should be a list"
        
        if len(crypto) < 4:  # Should have 5 but allow some flexibility
            return False, f"Expected at least 4 crypto assets, got {len(crypto)}"
        
        # Validate structure of first crypto
        if crypto:
            crypto_asset = crypto[0]
            required_fields = ['symbol', 'name', 'price', 'change', 'change_percent', 'flag']
            for field in required_fields:
                if field not in crypto_asset:
                    return False, f"Missing crypto field: {field}"
        
        return True, f"Valid crypto: {len(crypto)} crypto assets"

    def validate_forex_only(self, data: Dict) -> tuple:
        """Validate forex endpoint response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['forex', 'count', 'updated_at']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        forex = data.get('forex', [])
        if not isinstance(forex, list):
            return False, "Forex should be a list"
        
        if len(forex) < 3:  # Should have 4 but allow some flexibility
            return False, f"Expected at least 3 forex pairs, got {len(forex)}"
        
        # Validate structure of first forex pair
        if forex:
            forex_pair = forex[0]
            required_fields = ['symbol', 'name', 'price', 'change', 'change_percent', 'flag']
            for field in required_fields:
                if field not in forex_pair:
                    return False, f"Missing forex field: {field}"
        
        return True, f"Valid forex: {len(forex)} forex pairs"

    def validate_chart_data(self, data: Dict) -> tuple:
        """Validate chart data response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['symbol', 'name', 'period', 'data', 'current_price']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        chart_data = data.get('data', [])
        if not isinstance(chart_data, list):
            return False, "Chart data should be a list"
        
        if len(chart_data) < 10:  # Should have around 30 days but allow flexibility
            return False, f"Expected at least 10 data points, got {len(chart_data)}"
        
        # Validate structure of first data point
        if chart_data:
            point = chart_data[0]
            required_point_fields = ['date', 'open', 'high', 'low', 'close', 'volume']
            for field in required_point_fields:
                if field not in point:
                    return False, f"Missing chart data field: {field}"
        
        return True, f"Valid chart data: {len(chart_data)} data points for {data.get('symbol')}"

    def validate_vapid_key(self, data: Dict) -> tuple:
        """Validate VAPID public key response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        if 'publicKey' not in data:
            return False, "Missing 'publicKey' field"
        
        public_key = data.get('publicKey', '')
        if not public_key or len(public_key) < 50:
            return False, f"Invalid public key length: {len(public_key)}"
        
        # Check if it's a valid base64url string (basic check)
        import re
        if not re.match(r'^[A-Za-z0-9_-]+$', public_key):
            return False, "Public key should be valid base64url string"
        
        return True, f"Valid VAPID public key: {public_key[:20]}..."

    def validate_push_status(self, data: Dict) -> tuple:
        """Validate push notification status response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['subscribed', 'subscription_count']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        subscribed = data.get('subscribed')
        if not isinstance(subscribed, bool):
            return False, "subscribed should be a boolean"
        
        count = data.get('subscription_count')
        if not isinstance(count, int) or count < 0:
            return False, "subscription_count should be a non-negative integer"
        
        return True, f"Valid push status: subscribed={subscribed}, count={count}"

    def validate_push_subscription_response(self, data: Dict) -> tuple:
        """Validate push subscription response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['success', 'message']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        success = data.get('success')
        if not isinstance(success, bool):
            return False, "success should be a boolean"
        
        message = data.get('message', '')
        if not isinstance(message, str) or len(message) == 0:
            return False, "message should be a non-empty string"
        
        return True, f"Valid subscription response: {message}"

    def validate_push_test_response(self, data: Dict) -> tuple:
        """Validate push test notification response"""
        if not isinstance(data, dict):
            return False, "Response should be a dictionary"
        
        required_fields = ['success', 'message']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        success = data.get('success')
        if not isinstance(success, bool):
            return False, "success should be a boolean"
        
        # For test endpoint, it might fail if no real subscriptions exist
        # This is expected behavior, so we'll accept both success and failure
        message = data.get('message', '')
        if not isinstance(message, str):
            return False, "message should be a string"
        
        return True, f"Valid test response: {message}"

    def test_admin_login(self) -> bool:
        """Test admin authentication - use pre-created session token"""
        print("\n🔐 Setting up Admin Authentication...")
        
        # For testing, we'll create a session token directly in the database
        # since there's no password-based login endpoint
        import subprocess
        result = subprocess.run([
            'mongosh', 'mongodb://localhost:27017/stock_news_romania', '--quiet', '--eval',
            """
            const adminUser = db.users.findOne({email: 'admin@finromania.ro'});
            if (adminUser) {
              const sessionToken = 'test_admin_token_' + Date.now();
              const expiresAt = new Date(Date.now() + 7*24*60*60*1000);
              db.user_sessions.insertOne({
                user_id: adminUser.user_id,
                session_token: sessionToken,
                expires_at: expiresAt.toISOString(),
                created_at: new Date().toISOString()
              });
              print(sessionToken);
            }
            """
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            self.admin_token = result.stdout.strip()
            self.log_test("Admin Authentication Setup", True, f"Admin session token created", {"has_token": True})
            return True
        else:
            self.log_test("Admin Authentication Setup", False, f"Failed to create admin session", None)
            return False

    def test_regular_user_creation(self) -> bool:
        """Create a regular test user session"""
        print("\n👤 Creating Regular Test User Session...")
        
        # Create a regular user directly in database for testing
        import subprocess
        test_email = f"testuser_{datetime.now().timestamp()}@test.com"
        
        result = subprocess.run([
            'mongosh', 'mongodb://localhost:27017/stock_news_romania', '--quiet', '--eval',
            f"""
            const userId = 'user_test_' + Date.now();
            db.users.insertOne({{
              user_id: userId,
              email: '{test_email}',
              name: 'Test User',
              picture: 'https://example.com/pic.jpg',
              is_admin: false,
              created_at: new Date().toISOString(),
              last_login: new Date().toISOString()
            }});
            const sessionToken = 'test_user_token_' + Date.now();
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
            self.regular_user_token = result.stdout.strip()
            self.log_test("Regular User Creation", True, f"Test user created: {test_email}", {"has_token": True})
            return True
        else:
            self.log_test("Regular User Creation", False, f"Failed to create test user", None)
            return False

    def test_auth_session_endpoint(self):
        """Test /api/auth/session endpoint - should return user data WITH session_token"""
        print("\n🔐 Testing Authentication Session Endpoint...")
        
        # Test with a mock session_id
        test_session_data = {"session_id": "test-session-id-123"}
        
        success, details, data = self.test_api_endpoint(
            'POST', '/api/auth/session',
            data=test_session_data,
            expected_status=401  # Expected to fail with mock data
        )
        
        # Since we're using mock data, we expect 401, but we want to verify the endpoint exists
        if success and details.startswith("Status: 401"):
            self.log_test("Auth Session Endpoint Structure", True, 
                         "Endpoint exists and properly rejects invalid session_id", 
                         {"endpoint": "/api/auth/session", "expected_behavior": "401 for invalid session"})
            return True
        else:
            self.log_test("Auth Session Endpoint Structure", False, 
                         f"Unexpected response: {details}", data)
            return False

    def test_auth_me_endpoint(self):
        """Test /api/auth/me endpoint with Bearer token"""
        print("\n👤 Testing Authentication Me Endpoint...")
        
        # First, create a test session in the database
        import subprocess
        test_email = f"auth_test_{datetime.now().timestamp()}@test.com"
        
        result = subprocess.run([
            'mongosh', 'mongodb://localhost:27017/stock_news_romania', '--quiet', '--eval',
            f"""
            const userId = 'auth_test_' + Date.now();
            db.users.insertOne({{
              user_id: userId,
              email: '{test_email}',
              name: 'Auth Test User',
              picture: 'https://example.com/pic.jpg',
              is_admin: false,
              created_at: new Date().toISOString(),
              last_login: new Date().toISOString()
            }});
            const sessionToken = 'auth_test_token_' + Date.now();
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
            test_token = result.stdout.strip()
            
            # Test /api/auth/me with Bearer token
            success, details, data = self.test_api_endpoint(
                'GET', '/api/auth/me',
                auth_token=test_token
            )
            
            if success and isinstance(data, dict) and 'user_id' in data and 'email' in data:
                self.log_test("Auth Me Endpoint with Bearer Token", True, 
                             f"Successfully authenticated and returned user data", 
                             {"user_id": data.get('user_id'), "email": data.get('email')})
                return True
            else:
                self.log_test("Auth Me Endpoint with Bearer Token", False, 
                             f"Failed to authenticate or return proper user data: {details}", data)
                return False
        else:
            self.log_test("Auth Me Endpoint with Bearer Token", False, 
                         "Failed to create test session in database", None)
            return False

    def test_auth_me_without_token(self):
        """Test /api/auth/me endpoint without token - should return 401"""
        print("\n🚫 Testing Authentication Me Endpoint without token...")
        
        success, details, data = self.test_api_endpoint(
            'GET', '/api/auth/me',
            expected_status=401
        )
        
        if success:
            self.log_test("Auth Me Endpoint - No Token (401)", True, 
                         "Correctly returns 401 when no authentication provided", data)
            return True
        else:
            self.log_test("Auth Me Endpoint - No Token (401)", False, 
                         f"Should return 401 but got: {details}", data)
            return False

    def run_all_tests(self):
        """Run comprehensive test suite focusing on authentication flow"""
        print("🚀 Starting FinRomania API Testing - Authentication Flow Focus...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # ============================================
        # AUTHENTICATION FLOW TESTING (PRIMARY FOCUS)
        # ============================================
        print("\n🔐 SECTION 1: Authentication Flow Testing")
        print("-" * 80)
        
        # Test 1: /api/auth/session endpoint
        self.test_auth_session_endpoint()
        
        # Test 2: /api/auth/me endpoint with Bearer token
        self.test_auth_me_endpoint()
        
        # Test 3: /api/auth/me endpoint without token
        self.test_auth_me_without_token()
        
        # ============================================
        # BASIC HEALTH CHECKS
        # ============================================
        print("\n📋 SECTION 2: Basic Health Checks")
        print("-" * 80)
        
        # ============================================
        # BASIC HEALTH CHECKS
        # ============================================
        print("\n📋 SECTION 2: Basic Health Checks")
        print("-" * 80)
        
        # Test 4: Health Check
        success, details, data = self.test_api_endpoint('GET', '/api/health')
        self.log_test("Health Check", success, details, data)
        
        # Test 5: API Root
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
        # SESSION 9: FINANCIAL EDUCATION MODULE
        # ============================================
        print("\n🎓 SECTION 8: Financial Education Module (NEW)")
        print("-" * 80)
        
        # Test 20: Financial Education Lessons - All 15 lessons
        success, details, data = self.test_api_endpoint(
            'GET', '/api/financial-education/lessons',
            validate_response=self.validate_financial_lessons
        )
        self.log_test("Financial Education - All Lessons (15 total)", success, details,
                     {"total": data.get('total'), "modules": len(data.get('modules', {})), 
                      "sample_lessons": [l.get('title') for l in data.get('lessons', [])][:3]} if isinstance(data, dict) else data)
        
        # Test 21: Individual Lesson - fin_lesson_1
        success, details, data = self.test_api_endpoint(
            'GET', '/api/financial-education/lessons/fin_lesson_1',
            validate_response=self.validate_financial_lesson_detail
        )
        self.log_test("Financial Education - Lesson 1 Detail", success, details,
                     {"title": data.get('title'), "module": data.get('module'), "quiz_count": len(data.get('quiz', [])),
                      "content_length": len(data.get('content', ''))} if isinstance(data, dict) else data)
        
        # Test 22: Quiz Submission (requires auth)
        if self.regular_user_token:
            # Test with correct answers for fin_lesson_1 (answers: [1, 2] based on quiz structure)
            success, details, data = self.test_api_endpoint(
                'POST', '/api/financial-education/quiz/submit',
                auth_token=self.regular_user_token,
                data={"lesson_id": "fin_lesson_1", "answers": [1, 2]},
                validate_response=self.validate_quiz_submission
            )
            self.log_test("Financial Education - Quiz Submit (Correct)", success, details,
                         {"score": data.get('score'), "passed": data.get('passed'), 
                          "correct": data.get('correct'), "total": data.get('total')} if isinstance(data, dict) else data)
            
            # Test 23: Progress Tracking
            success, details, data = self.test_api_endpoint(
                'GET', '/api/financial-education/progress',
                auth_token=self.regular_user_token,
                validate_response=self.validate_financial_progress
            )
            self.log_test("Financial Education - Progress Tracking", success, details,
                         {"completed": len(data.get('completed_lessons', [])), 
                          "total": data.get('total_lessons'), "progress": data.get('progress_percent')} if isinstance(data, dict) else data)
        else:
            self.log_test("Financial Education - Quiz Submit", False, "Skipped - no user token")
            self.log_test("Financial Education - Progress Tracking", False, "Skipped - no user token")
        
        # Test 24: Quiz with wrong answers
        if self.regular_user_token:
            success, details, data = self.test_api_endpoint(
                'POST', '/api/financial-education/quiz/submit',
                auth_token=self.regular_user_token,
                data={"lesson_id": "fin_lesson_1", "answers": [0, 0]},  # Wrong answers
                validate_response=self.validate_quiz_submission
            )
            self.log_test("Financial Education - Quiz Submit (Wrong)", success, details,
                         {"score": data.get('score'), "passed": data.get('passed')} if isinstance(data, dict) else data)
        else:
            self.log_test("Financial Education - Quiz Submit (Wrong)", False, "Skipped - no user token")

        # ============================================
        # GLOBAL MARKETS TESTING (NEW FEATURE)
        # ============================================
        print("\n🌍 SECTION 9: Global Markets Feature (NEW)")
        print("-" * 80)
        
        # Test 25: Global Markets Overview - Main endpoint
        success, details, data = self.test_api_endpoint(
            'GET', '/api/global/overview',
            validate_response=self.validate_global_overview
        )
        self.log_test("Global Markets - Overview (Main Endpoint)", success, details,
                     {"indices_count": len(data.get('indices', [])), 
                      "commodities_count": len(data.get('commodities', [])),
                      "crypto_count": len(data.get('crypto', [])),
                      "forex_count": len(data.get('forex', [])),
                      "sentiment": data.get('sentiment', {})} if isinstance(data, dict) else data)
        
        # Test 26: Global Indices
        success, details, data = self.test_api_endpoint(
            'GET', '/api/global/indices',
            validate_response=self.validate_global_indices_only
        )
        self.log_test("Global Markets - Indices", success, details,
                     {"count": data.get('count'), 
                      "sample_indices": [idx.get('name') for idx in data.get('indices', [])][:3]} if isinstance(data, dict) else data)
        
        # Test 27: Commodities
        success, details, data = self.test_api_endpoint(
            'GET', '/api/global/commodities',
            validate_response=self.validate_commodities_only
        )
        self.log_test("Global Markets - Commodities", success, details,
                     {"count": data.get('count'),
                      "sample_commodities": [c.get('name') for c in data.get('commodities', [])][:3]} if isinstance(data, dict) else data)
        
        # Test 28: Cryptocurrency
        success, details, data = self.test_api_endpoint(
            'GET', '/api/global/crypto',
            validate_response=self.validate_crypto_only
        )
        self.log_test("Global Markets - Cryptocurrency", success, details,
                     {"count": data.get('count'),
                      "sample_crypto": [c.get('name') for c in data.get('crypto', [])][:3]} if isinstance(data, dict) else data)
        
        # Test 29: Forex
        success, details, data = self.test_api_endpoint(
            'GET', '/api/global/forex',
            validate_response=self.validate_forex_only
        )
        self.log_test("Global Markets - Forex", success, details,
                     {"count": data.get('count'),
                      "sample_forex": [f.get('name') for f in data.get('forex', [])][:3]} if isinstance(data, dict) else data)
        
        # Test 30: Chart Data - S&P 500
        success, details, data = self.test_api_endpoint(
            'GET', '/api/global/chart/^GSPC',
            validate_response=self.validate_chart_data
        )
        self.log_test("Global Markets - Chart Data (S&P 500)", success, details,
                     {"symbol": data.get('symbol'), "data_points": len(data.get('data', [])),
                      "current_price": data.get('current_price')} if isinstance(data, dict) else data)
        
        # Test 31: Chart Data - Bitcoin
        success, details, data = self.test_api_endpoint(
            'GET', '/api/global/chart/BTC-USD',
            validate_response=self.validate_chart_data
        )
        self.log_test("Global Markets - Chart Data (Bitcoin)", success, details,
                     {"symbol": data.get('symbol'), "data_points": len(data.get('data', [])),
                      "current_price": data.get('current_price')} if isinstance(data, dict) else data)

        # ============================================
        # PUSH NOTIFICATIONS TESTING (NEW FEATURE)
        # ============================================
        print("\n🔔 SECTION 10: Push Notifications API (NEW)")
        print("-" * 80)
        
        # Test 32: VAPID Public Key (no auth required)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/push/vapid-key',
            validate_response=self.validate_vapid_key
        )
        self.log_test("Push Notifications - VAPID Public Key", success, details,
                     {"publicKey": data.get('publicKey', '')[:20] + "..." if isinstance(data, dict) else None})
        
        # Test 33: Push Status (requires auth)
        if self.regular_user_token:
            success, details, data = self.test_api_endpoint(
                'GET', '/api/push/status',
                auth_token=self.regular_user_token,
                validate_response=self.validate_push_status
            )
            self.log_test("Push Notifications - Status (Auth Required)", success, details,
                         {"subscribed": data.get('subscribed'), "count": data.get('subscription_count')} if isinstance(data, dict) else data)
        else:
            self.log_test("Push Notifications - Status", False, "Skipped - no user token")
        
        # Test 34: Push Subscribe (requires auth)
        if self.regular_user_token:
            test_subscription = {
                "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint-123",
                "keys": {
                    "p256dh": "test-p256dh-key",
                    "auth": "test-auth-key"
                }
            }
            success, details, data = self.test_api_endpoint(
                'POST', '/api/push/subscribe',
                auth_token=self.regular_user_token,
                data=test_subscription,
                validate_response=self.validate_push_subscription_response
            )
            self.log_test("Push Notifications - Subscribe (Auth Required)", success, details,
                         {"success": data.get('success'), "message": data.get('message')} if isinstance(data, dict) else data)
        else:
            self.log_test("Push Notifications - Subscribe", False, "Skipped - no user token")
        
        # Test 35: Push Unsubscribe (requires auth)
        if self.regular_user_token:
            test_unsubscription = {
                "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint-123",
                "keys": {}
            }
            success, details, data = self.test_api_endpoint(
                'DELETE', '/api/push/unsubscribe',
                auth_token=self.regular_user_token,
                data=test_unsubscription,
                validate_response=self.validate_push_subscription_response
            )
            self.log_test("Push Notifications - Unsubscribe (Auth Required)", success, details,
                         {"success": data.get('success'), "message": data.get('message')} if isinstance(data, dict) else data)
        else:
            self.log_test("Push Notifications - Unsubscribe", False, "Skipped - no user token")
        
        # Test 36: Push Test Notification (requires auth)
        if self.regular_user_token:
            success, details, data = self.test_api_endpoint(
                'POST', '/api/push/test',
                auth_token=self.regular_user_token,
                validate_response=self.validate_push_test_response
            )
            # Note: This test may fail if no real subscriptions exist, which is expected
            self.log_test("Push Notifications - Test Send (Auth Required)", success, details,
                         {"success": data.get('success'), "message": data.get('message')} if isinstance(data, dict) else data)
        else:
            self.log_test("Push Notifications - Test Send", False, "Skipped - no user token")
        
        # Test 37: Push endpoints without auth (should return 401)
        success, details, data = self.test_api_endpoint(
            'GET', '/api/push/status',
            expected_status=401
        )
        self.log_test("Push Notifications - Status Without Auth (401)", success, 
                     "Correctly returns 401 when no authentication provided" if success else details, data)
        
        success, details, data = self.test_api_endpoint(
            'POST', '/api/push/subscribe',
            data={"endpoint": "test", "keys": {}},
            expected_status=401
        )
        self.log_test("Push Notifications - Subscribe Without Auth (401)", success,
                     "Correctly returns 401 when no authentication provided" if success else details, data)

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