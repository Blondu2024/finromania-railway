"""
Tests for new features:
- CFD vs Acțiuni Reale page (backend health check)
- Daily Summary subscription endpoints: GET /my-subscription, POST /toggle-subscription
- Notification settings integration
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


@pytest.fixture(scope="module")
def demo_token():
    """Get demo PRO session token for authenticated tests."""
    resp = requests.get(f"{BASE_URL}/api/auth/demo-login?secret=finromania-demo-2026")
    if resp.status_code != 200:
        pytest.skip(f"Demo login failed with status {resp.status_code}")
    data = resp.json()
    token = data.get("session_token") or data.get("token") or data.get("access_token")
    if not token:
        pytest.skip(f"No token in demo login response: {data}")
    return token


@pytest.fixture(scope="module")
def auth_headers(demo_token):
    """Headers with Bearer token for authenticated requests."""
    return {"Authorization": f"Bearer {demo_token}"}


# =============================================
# Health check
# =============================================
class TestHealthCheck:
    """Basic health check endpoints"""

    def test_api_health(self):
        """Backend is reachable"""
        resp = requests.get(f"{BASE_URL}/api/")
        assert resp.status_code in [200, 404], f"Unexpected status: {resp.status_code}"
        print(f"✅ Backend reachable, status={resp.status_code}")

    def test_demo_login(self):
        """Demo login returns a valid token"""
        resp = requests.get(f"{BASE_URL}/api/auth/demo-login?secret=finromania-demo-2026")
        assert resp.status_code == 200, f"Demo login failed: {resp.status_code} — {resp.text}"
        data = resp.json()
        token = data.get("session_token") or data.get("token") or data.get("access_token")
        assert token, f"No token in response: {data}"
        print(f"✅ Demo login OK, token starts with: {token[:20]}...")


# =============================================
# Daily Summary Subscription Endpoints
# =============================================
class TestDailySummarySubscription:
    """Tests for GET /my-subscription and POST /toggle-subscription"""

    def test_my_subscription_requires_auth(self):
        """GET /my-subscription returns 401 without token"""
        resp = requests.get(f"{BASE_URL}/api/daily-summary/my-subscription")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        print("✅ /my-subscription requires auth (401 without token)")

    def test_toggle_subscription_requires_auth(self):
        """POST /toggle-subscription returns 401 without token"""
        resp = requests.post(f"{BASE_URL}/api/daily-summary/toggle-subscription")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        print("✅ /toggle-subscription requires auth (401 without token)")

    def test_my_subscription_authenticated(self, auth_headers):
        """GET /my-subscription returns subscribed status for logged-in user"""
        resp = requests.get(
            f"{BASE_URL}/api/daily-summary/my-subscription",
            headers=auth_headers
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code} — {resp.text}"
        data = resp.json()
        assert "subscribed" in data, f"Missing 'subscribed' field in: {data}"
        assert isinstance(data["subscribed"], bool), f"'subscribed' should be bool: {data}"
        assert "email" in data, f"Missing 'email' field in: {data}"
        print(f"✅ GET /my-subscription OK: subscribed={data['subscribed']}, email={data['email']}")

    def test_toggle_subscription_changes_state(self, auth_headers):
        """POST /toggle-subscription toggles the subscription state"""
        # Get initial state
        before = requests.get(
            f"{BASE_URL}/api/daily-summary/my-subscription",
            headers=auth_headers
        )
        assert before.status_code == 200
        initial = before.json()["subscribed"]

        # Toggle
        toggle = requests.post(
            f"{BASE_URL}/api/daily-summary/toggle-subscription",
            headers=auth_headers
        )
        assert toggle.status_code == 200, f"Toggle failed: {toggle.status_code} — {toggle.text}"
        toggle_data = toggle.json()
        assert "success" in toggle_data, f"Missing 'success' in: {toggle_data}"
        assert toggle_data.get("success") is True
        assert "subscribed" in toggle_data
        assert toggle_data["subscribed"] == (not initial), \
            f"Expected toggled={not initial}, got {toggle_data['subscribed']}"
        print(f"✅ POST /toggle-subscription: {initial} → {toggle_data['subscribed']}")

    def test_toggle_subscription_response_structure(self, auth_headers):
        """POST /toggle-subscription returns proper response with message"""
        resp = requests.post(
            f"{BASE_URL}/api/daily-summary/toggle-subscription",
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "success" in data
        assert "subscribed" in data
        assert "message" in data
        assert isinstance(data["subscribed"], bool)
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0
        print(f"✅ Toggle response structure OK: {data}")

    def test_toggle_persists_state(self, auth_headers):
        """After toggling, GET /my-subscription should reflect new state"""
        # Get current state
        before_resp = requests.get(
            f"{BASE_URL}/api/daily-summary/my-subscription",
            headers=auth_headers
        )
        assert before_resp.status_code == 200
        before_state = before_resp.json()["subscribed"]

        # Toggle once
        toggle_resp = requests.post(
            f"{BASE_URL}/api/daily-summary/toggle-subscription",
            headers=auth_headers
        )
        assert toggle_resp.status_code == 200
        toggled_state = toggle_resp.json()["subscribed"]

        # Verify via GET
        after_resp = requests.get(
            f"{BASE_URL}/api/daily-summary/my-subscription",
            headers=auth_headers
        )
        assert after_resp.status_code == 200
        after_state = after_resp.json()["subscribed"]
        assert after_state == toggled_state, \
            f"State not persisted: toggle returned {toggled_state}, GET returned {after_state}"
        print(f"✅ Toggle persisted: {before_state} → {after_state}")

        # Restore original state
        requests.post(
            f"{BASE_URL}/api/daily-summary/toggle-subscription",
            headers=auth_headers
        )
        print("✅ State restored to original")


# =============================================
# Daily Summary Preview Endpoint
# =============================================
class TestDailySummaryPreview:
    """Test existing daily summary endpoints still work"""

    def test_daily_summary_preview(self):
        """GET /preview returns 200 or 404 (no summary yet)"""
        resp = requests.get(f"{BASE_URL}/api/daily-summary/preview")
        assert resp.status_code in [200, 404], \
            f"Unexpected status: {resp.status_code} — {resp.text}"
        print(f"✅ /preview returned {resp.status_code}")

    def test_subscribers_count(self):
        """GET /subscribers/count returns totals"""
        resp = requests.get(f"{BASE_URL}/api/daily-summary/subscribers/count")
        assert resp.status_code == 200, f"Failed: {resp.status_code}"
        data = resp.json()
        assert "total" in data
        assert "registered_users" in data
        assert "anonymous" in data
        print(f"✅ Subscribers count: {data}")
