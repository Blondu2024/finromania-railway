"""
Test Suite for Feedback Management API
Tests:
- POST /api/feedback - Public endpoint for submitting feedback
- GET /api/admin/feedback - Admin-protected endpoint (expects 401 without auth)
- PUT /api/admin/feedback/{id} - Admin-protected endpoint (expects 401 without auth)
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

# Base URL from environment variable
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Known feedback IDs from the database (provided in context)
KNOWN_FEEDBACK_IDS = [
    "69aa96dd2a47638fbf66d9f1",
    "69aa96e42a47638fbf66d9f2", 
    "69aa96e42a47638fbf66d9f3"
]

class TestPublicFeedbackSubmission:
    """Test the public feedback submission endpoint POST /api/feedback"""
    
    def test_submit_bug_feedback_success(self):
        """Test submitting a bug report feedback"""
        unique_email = f"test_bug_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "type": "bug",
            "message": "TEST_This is a test bug report for backend testing",
            "email": unique_email,
            "page": "/test-page",
            "timestamp": datetime.utcnow().isoformat(),
            "userAgent": "TestAgent/1.0"
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        assert "message" in data, "Response should contain a message"
        print(f"✅ Bug feedback submitted successfully: {data['message']}")
    
    def test_submit_idea_feedback_success(self):
        """Test submitting an idea/feature request feedback"""
        unique_email = f"test_idea_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "type": "idea",
            "message": "TEST_This is a test idea/feature suggestion",
            "email": unique_email,
            "page": "/dashboard"
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"✅ Idea feedback submitted successfully: {data['message']}")
    
    def test_submit_question_feedback_success(self):
        """Test submitting a question feedback"""
        unique_email = f"test_question_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "type": "question",
            "message": "TEST_This is a test question from automated testing",
            "email": unique_email,
            "page": "/help"
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"✅ Question feedback submitted successfully: {data['message']}")
    
    def test_submit_anonymous_feedback(self):
        """Test submitting anonymous feedback (no email provided)"""
        payload = {
            "type": "bug",
            "message": "TEST_Anonymous feedback submission test"
            # No email field - should default to 'anonim'
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"✅ Anonymous feedback submitted successfully")
    
    def test_submit_feedback_minimal_payload(self):
        """Test submitting feedback with minimal required fields"""
        payload = {
            "type": "idea",
            "message": "TEST_Minimal payload test"
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"✅ Minimal payload feedback submitted successfully")
    
    def test_submit_feedback_missing_type_fails(self):
        """Test that feedback without type field fails validation"""
        payload = {
            "message": "TEST_Missing type field"
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        
        # Should fail validation (422 Unprocessable Entity)
        assert response.status_code == 422, f"Expected 422 for missing required field, got {response.status_code}"
        print(f"✅ Correctly rejected feedback without type field (422)")
    
    def test_submit_feedback_missing_message_fails(self):
        """Test that feedback without message field fails validation"""
        payload = {
            "type": "bug"
        }
        
        response = requests.post(f"{BASE_URL}/api/feedback", json=payload)
        
        # Should fail validation (422 Unprocessable Entity)
        assert response.status_code == 422, f"Expected 422 for missing required field, got {response.status_code}"
        print(f"✅ Correctly rejected feedback without message field (422)")


class TestAdminFeedbackEndpointsProtection:
    """Test that admin feedback endpoints are protected and return 401 without auth"""
    
    def test_get_feedback_without_auth_returns_401(self):
        """GET /api/admin/feedback should return 401 without authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/feedback")
        
        # Should return 401 Unauthorized
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}: {response.text}"
        print(f"✅ GET /api/admin/feedback correctly returns 401 without auth")
    
    def test_get_feedback_with_status_filter_without_auth(self):
        """GET /api/admin/feedback?status=new should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/feedback?status=new")
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✅ GET /api/admin/feedback?status=new correctly returns 401")
    
    def test_get_feedback_with_type_filter_without_auth(self):
        """GET /api/admin/feedback?feedback_type=bug should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/feedback?feedback_type=bug")
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✅ GET /api/admin/feedback?feedback_type=bug correctly returns 401")
    
    def test_update_feedback_status_without_auth_returns_401(self):
        """PUT /api/admin/feedback/{id} should return 401 without authentication"""
        feedback_id = KNOWN_FEEDBACK_IDS[0]
        payload = {"status": "in_progress"}
        
        response = requests.put(
            f"{BASE_URL}/api/admin/feedback/{feedback_id}",
            json=payload
        )
        
        # Should return 401 Unauthorized
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}: {response.text}"
        print(f"✅ PUT /api/admin/feedback/{feedback_id} correctly returns 401 without auth")
    
    def test_update_feedback_to_resolved_without_auth(self):
        """Updating feedback to resolved status should return 401 without auth"""
        feedback_id = KNOWN_FEEDBACK_IDS[1]
        payload = {"status": "resolved"}
        
        response = requests.put(
            f"{BASE_URL}/api/admin/feedback/{feedback_id}",
            json=payload
        )
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✅ Status update to 'resolved' correctly blocked without auth")
    
    def test_update_feedback_with_invalid_token(self):
        """PUT with invalid Bearer token should return 401"""
        feedback_id = KNOWN_FEEDBACK_IDS[0]
        payload = {"status": "in_progress"}
        
        response = requests.put(
            f"{BASE_URL}/api/admin/feedback/{feedback_id}",
            json=payload,
            headers={"Authorization": "Bearer invalid_fake_token_12345"}
        )
        
        # Should return 401 Unauthorized with invalid token
        assert response.status_code == 401, f"Expected 401 with invalid token, got {response.status_code}"
        print(f"✅ Invalid Bearer token correctly rejected with 401")


class TestOtherAdminEndpointsProtection:
    """Test that other admin endpoints are also protected"""
    
    def test_get_admin_users_without_auth(self):
        """GET /api/admin/users should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/users")
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✅ GET /api/admin/users correctly returns 401 without auth")
    
    def test_get_admin_stats_without_auth(self):
        """GET /api/admin/stats should return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✅ GET /api/admin/stats correctly returns 401 without auth")
    
    def test_set_subscription_without_auth(self):
        """POST /api/admin/set-subscription should return 401 without auth"""
        payload = {
            "email": "test@test.com",
            "subscription_level": "pro",
            "duration_days": 30
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/set-subscription",
            json=payload
        )
        
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✅ POST /api/admin/set-subscription correctly returns 401 without auth")


class TestHealthEndpoint:
    """Basic health check to verify API is accessible"""
    
    def test_health_endpoint(self):
        """Test that the health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✅ Health endpoint returns healthy status")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
