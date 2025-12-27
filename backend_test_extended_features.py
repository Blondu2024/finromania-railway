#!/usr/bin/env python3
"""
FinRomania Extended Features Testing
Testing: Extended Education (Starter 5 RON + Premium 20 RON), Currency Converter (30+ currencies), AI Advisor
"""

import requests
import sys
import json
from datetime import datetime

class FinRomaniaExtendedTester:
    def __init__(self, base_url="https://finedromania.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.results.append({
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def test_education_packages(self):
        """Test education packages API - should return Starter (5 RON) and Premium (20 RON)"""
        try:
            response = requests.get(f"{self.base_url}/api/education/packages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get("packages", [])
                
                # Check if we have both packages
                starter_found = False
                premium_found = False
                
                for pkg in packages:
                    if pkg.get("id") == "edu_starter_pack":
                        starter_found = True
                        if pkg.get("price") == 5.0 and pkg.get("currency") == "ron":
                            self.log_test("Education Starter Package (5 RON)", True)
                        else:
                            self.log_test("Education Starter Package (5 RON)", False, f"Price: {pkg.get('price')} {pkg.get('currency')}")
                    
                    elif pkg.get("id") == "edu_premium_pack":
                        premium_found = True
                        if pkg.get("price") == 20.0 and pkg.get("currency") == "ron":
                            self.log_test("Education Premium Package (20 RON)", True)
                        else:
                            self.log_test("Education Premium Package (20 RON)", False, f"Price: {pkg.get('price')} {pkg.get('currency')}")
                
                if not starter_found:
                    self.log_test("Education Starter Package Found", False, "Starter package not found")
                if not premium_found:
                    self.log_test("Education Premium Package Found", False, "Premium package not found")
                    
                self.log_test("GET /api/education/packages", True, f"Found {len(packages)} packages")
            else:
                self.log_test("GET /api/education/packages", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/education/packages", False, str(e))

    def test_education_lessons(self):
        """Test education lessons API - should return 12 lessons with tier info"""
        try:
            response = requests.get(f"{self.base_url}/api/education/lessons", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                lessons = data.get("lessons", [])
                
                if len(lessons) >= 12:
                    self.log_test("Education Lessons Count (12+)", True, f"Found {len(lessons)} lessons")
                else:
                    self.log_test("Education Lessons Count (12+)", False, f"Only {len(lessons)} lessons found")
                
                # Check tier information
                has_free = any(l.get("tier") == "free" for l in lessons)
                has_starter = any(l.get("tier") == "starter" for l in lessons)
                has_premium = any(l.get("tier") == "premium" for l in lessons)
                
                self.log_test("Lessons have tier info (free/starter/premium)", 
                            has_free and has_starter and has_premium,
                            f"Free: {has_free}, Starter: {has_starter}, Premium: {has_premium}")
                
                self.log_test("GET /api/education/lessons", True)
            else:
                self.log_test("GET /api/education/lessons", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/education/lessons", False, str(e))

    def test_education_glossary(self):
        """Test education glossary API - should return 50+ terms"""
        try:
            response = requests.get(f"{self.base_url}/api/education/glossary", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                terms = data.get("terms", {})
                total = data.get("total", 0)
                
                if total >= 50:
                    self.log_test("Education Glossary (50+ terms)", True, f"Found {total} terms")
                else:
                    self.log_test("Education Glossary (50+ terms)", False, f"Only {total} terms found")
                
                self.log_test("GET /api/education/glossary", True)
            else:
                self.log_test("GET /api/education/glossary", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/education/glossary", False, str(e))

    def test_currency_converter_currencies(self):
        """Test currency converter - should return 30+ currencies"""
        try:
            response = requests.get(f"{self.base_url}/api/currency/currencies", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                currencies = data.get("currencies", [])
                total = data.get("total", 0)
                
                if total >= 30:
                    self.log_test("Currency Converter (30+ currencies)", True, f"Found {total} currencies")
                else:
                    self.log_test("Currency Converter (30+ currencies)", False, f"Only {total} currencies found")
                
                # Check for key currencies
                currency_codes = [c.get("code") for c in currencies]
                required_currencies = ["RON", "EUR", "USD", "GBP"]
                missing = [c for c in required_currencies if c not in currency_codes]
                
                if not missing:
                    self.log_test("Key currencies present (RON, EUR, USD, GBP)", True)
                else:
                    self.log_test("Key currencies present", False, f"Missing: {missing}")
                
                self.log_test("GET /api/currency/currencies", True)
            else:
                self.log_test("GET /api/currency/currencies", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/currency/currencies", False, str(e))

    def test_currency_conversion(self):
        """Test currency conversion - 100 EUR to RON"""
        try:
            payload = {
                "amount": 100,
                "from_currency": "EUR",
                "to_currency": "RON"
            }
            
            response = requests.post(
                f"{self.base_url}/api/currency/convert",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")
                rate = data.get("rate")
                
                if result and rate and result > 0:
                    self.log_test("Currency Conversion (100 EUR to RON)", True, f"Result: {result} RON, Rate: {rate}")
                else:
                    self.log_test("Currency Conversion (100 EUR to RON)", False, f"Invalid result: {result}")
                
                self.log_test("POST /api/currency/convert", True)
            else:
                self.log_test("POST /api/currency/convert", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("POST /api/currency/convert", False, str(e))

    def test_currency_popular_pairs(self):
        """Test popular currency pairs - should return RON pairs"""
        try:
            response = requests.get(f"{self.base_url}/api/currency/popular-pairs", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])
                
                # Check for RON pairs
                ron_pairs = [p for p in pairs if p.get("to") == "RON" or p.get("from") == "RON"]
                
                if len(ron_pairs) >= 3:
                    self.log_test("Popular RON Currency Pairs", True, f"Found {len(ron_pairs)} RON pairs")
                else:
                    self.log_test("Popular RON Currency Pairs", False, f"Only {len(ron_pairs)} RON pairs found")
                
                self.log_test("GET /api/currency/popular-pairs", True, f"Found {len(pairs)} pairs")
            else:
                self.log_test("GET /api/currency/popular-pairs", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/currency/popular-pairs", False, str(e))

    def test_ai_advisor_tip_of_day(self):
        """Test AI Advisor tip of the day"""
        try:
            response = requests.get(f"{self.base_url}/api/advisor/tip-of-the-day", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tip = data.get("tip")
                category = data.get("category")
                
                if tip and category:
                    self.log_test("AI Advisor Tip of Day", True, f"Category: {category}")
                else:
                    self.log_test("AI Advisor Tip of Day", False, "Missing tip or category")
                
                self.log_test("GET /api/advisor/tip-of-the-day", True)
            else:
                self.log_test("GET /api/advisor/tip-of-the-day", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("GET /api/advisor/tip-of-the-day", False, str(e))

    def test_homepage_health(self):
        """Test if homepage loads correctly"""
        try:
            # Test main API health
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Homepage API Health", True)
            else:
                self.log_test("Homepage API Health", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Homepage API Health", False, str(e))

    def run_all_tests(self):
        """Run all extended feature tests"""
        print("🚀 Starting FinRomania Extended Features Testing...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Education Package Tests
        print("\n📚 Testing Education Packages...")
        self.test_education_packages()
        self.test_education_lessons()
        self.test_education_glossary()
        
        # Currency Converter Tests
        print("\n💱 Testing Currency Converter...")
        self.test_currency_converter_currencies()
        self.test_currency_conversion()
        self.test_currency_popular_pairs()
        
        # AI Advisor Tests
        print("\n🤖 Testing AI Advisor...")
        self.test_ai_advisor_tip_of_day()
        
        # General Health
        print("\n🏠 Testing Homepage...")
        self.test_homepage_health()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Save results
        results_file = "/app/backend_test_extended_features_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": self.tests_run,
                    "passed_tests": self.tests_passed,
                    "success_rate": f"{success_rate:.1f}%",
                    "timestamp": datetime.now().isoformat()
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"💾 Results saved to: {results_file}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = FinRomaniaExtendedTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())