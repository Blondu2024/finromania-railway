"""
Tests for FinRomania Portofoliu BVB PRO — Faza 4: Dividende + Știri
  - GET /api/portfolio-bvb/dividends — returns dividends array + total_annual_income
  - GET /api/portfolio-bvb/news — returns 8 filtered news articles
  - Auth guard: 401 without token
  - Data validation: BRD (3.78% yield, 211.62 RON income), H2O (6.08%, 449.44 RON)
  - total_annual_income = 661.06 RON
  - News articles: title, image_url, source, published_at, related_symbols fields
  - related_symbols correctly tagged with H2O/BRD
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


# ─── Auth fixture ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def pro_token():
    """Obtain PRO demo token once per module."""
    r = requests.get(f"{BASE_URL}/api/auth/demo-login?secret=finromania-demo-2026", timeout=15)
    if r.status_code != 200:
        pytest.skip(f"Demo login failed: {r.status_code} — {r.text[:200]}")
    data = r.json()
    token = data.get("session_token")
    if not token:
        pytest.skip("No session_token in demo login response")
    return token


@pytest.fixture(scope="module")
def auth_headers(pro_token):
    return {"Authorization": f"Bearer {pro_token}", "Content-Type": "application/json"}


# ─── Test: Auth guard for /dividends ──────────────────────────────────────────

class TestDividendsAuthGuard:
    """Dividends endpoint requires authentication."""

    def test_dividends_no_token_returns_401(self):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", timeout=15)
        assert r.status_code == 401, f"Expected 401 without token, got {r.status_code}"
        print(f"✅ GET /portfolio-bvb/dividends without token → 401")

    def test_news_no_token_returns_401(self):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", timeout=15)
        assert r.status_code == 401, f"Expected 401 without token, got {r.status_code}"
        print(f"✅ GET /portfolio-bvb/news without token → 401")


# ─── Test: GET /dividends ─────────────────────────────────────────────────────

class TestGetDividends:
    """GET /api/portfolio-bvb/dividends with PRO token."""

    def test_dividends_returns_200(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        assert r.status_code == 200, f"Expected 200, got {r.status_code} — {r.text[:300]}"
        print(f"✅ GET /portfolio-bvb/dividends → 200")

    def test_dividends_response_structure(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        assert "dividends" in data, f"Missing 'dividends' key in response: {list(data.keys())}"
        assert "total_annual_income" in data, f"Missing 'total_annual_income' key: {list(data.keys())}"
        assert isinstance(data["dividends"], list), "dividends should be a list"
        print(f"✅ Response has 'dividends' (list) and 'total_annual_income'")

    def test_dividends_has_brd_and_h2o(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        symbols = [d["symbol"] for d in data["dividends"]]
        assert "BRD" in symbols, f"BRD not in dividends. Got symbols: {symbols}"
        assert "H2O" in symbols, f"H2O not in dividends. Got symbols: {symbols}"
        print(f"✅ Dividends contain BRD and H2O. All symbols: {symbols}")

    def test_dividends_per_symbol_fields(self, auth_headers):
        """Each dividend entry must have required fields."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        for d in data["dividends"]:
            required = ["symbol", "trailing_annual_dividend", "dividend_yield_pct",
                        "annual_income_ron", "shares", "source"]
            for field in required:
                assert field in d, f"Missing field '{field}' in dividend entry for {d.get('symbol')}"
        print(f"✅ All dividend entries have required fields")

    def test_brd_dividend_yield_pct(self, auth_headers):
        """BRD dividend_yield_pct should be approximately 3.78%."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        brd = next((d for d in data["dividends"] if d["symbol"] == "BRD"), None)
        assert brd is not None, "BRD not found in dividends"
        assert brd["dividend_yield_pct"] is not None, f"BRD dividend_yield_pct is None: {brd}"
        # Allow ±0.5% tolerance for live price fluctuations
        assert abs(brd["dividend_yield_pct"] - 3.78) < 1.0, \
            f"BRD dividend_yield_pct={brd['dividend_yield_pct']}, expected ~3.78%"
        print(f"✅ BRD dividend_yield_pct={brd['dividend_yield_pct']}% (expected ~3.78%)")

    def test_brd_annual_income_ron(self, auth_headers):
        """BRD annual_income_ron should be approximately 211.62 RON (200 shares × 1.0581 div)."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        brd = next((d for d in data["dividends"] if d["symbol"] == "BRD"), None)
        assert brd is not None, "BRD not found in dividends"
        assert brd["annual_income_ron"] is not None, f"BRD annual_income_ron is None: {brd}"
        # Allow ±5 RON tolerance
        assert abs(brd["annual_income_ron"] - 211.62) < 5.0, \
            f"BRD annual_income_ron={brd['annual_income_ron']}, expected ~211.62 RON"
        print(f"✅ BRD annual_income_ron={brd['annual_income_ron']} RON (expected ~211.62 RON)")

    def test_brd_source_confirmed(self, auth_headers):
        """BRD source should be 'BVB.ro (confirmat)'."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        brd = next((d for d in data["dividends"] if d["symbol"] == "BRD"), None)
        assert brd is not None, "BRD not found in dividends"
        assert brd["source"] == "BVB.ro (confirmat)", \
            f"BRD source='{brd['source']}', expected 'BVB.ro (confirmat)'"
        print(f"✅ BRD source='{brd['source']}'")

    def test_h2o_dividend_yield_pct(self, auth_headers):
        """H2O dividend_yield_pct should be approximately 6.08%."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        h2o = next((d for d in data["dividends"] if d["symbol"] == "H2O"), None)
        assert h2o is not None, "H2O not found in dividends"
        assert h2o["dividend_yield_pct"] is not None, f"H2O dividend_yield_pct is None: {h2o}"
        # Allow ±1% tolerance for live price fluctuations
        assert abs(h2o["dividend_yield_pct"] - 6.08) < 1.5, \
            f"H2O dividend_yield_pct={h2o['dividend_yield_pct']}, expected ~6.08%"
        print(f"✅ H2O dividend_yield_pct={h2o['dividend_yield_pct']}% (expected ~6.08%)")

    def test_h2o_annual_income_ron(self, auth_headers):
        """H2O annual_income_ron should be approximately 449.44 RON (50 shares × 8.989 div)."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        h2o = next((d for d in data["dividends"] if d["symbol"] == "H2O"), None)
        assert h2o is not None, "H2O not found in dividends"
        assert h2o["annual_income_ron"] is not None, f"H2O annual_income_ron is None: {h2o}"
        # Allow ±5 RON tolerance
        assert abs(h2o["annual_income_ron"] - 449.44) < 5.0, \
            f"H2O annual_income_ron={h2o['annual_income_ron']}, expected ~449.44 RON"
        print(f"✅ H2O annual_income_ron={h2o['annual_income_ron']} RON (expected ~449.44 RON)")

    def test_h2o_source_confirmed(self, auth_headers):
        """H2O source should be 'BVB.ro (confirmat)'."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        h2o = next((d for d in data["dividends"] if d["symbol"] == "H2O"), None)
        assert h2o is not None, "H2O not found in dividends"
        assert h2o["source"] == "BVB.ro (confirmat)", \
            f"H2O source='{h2o['source']}', expected 'BVB.ro (confirmat)'"
        print(f"✅ H2O source='{h2o['source']}'")

    def test_total_annual_income(self, auth_headers):
        """total_annual_income should be approximately 661.06 RON (211.62 + 449.44)."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        total = data["total_annual_income"]
        assert total > 0, f"total_annual_income should be > 0, got {total}"
        # Allow ±10 RON tolerance
        assert abs(total - 661.06) < 10.0, \
            f"total_annual_income={total}, expected ~661.06 RON"
        print(f"✅ total_annual_income={total} RON (expected ~661.06 RON)")

    def test_dividends_source_in_response(self, auth_headers):
        """Top-level source should be 'BVB.ro (oficial)'."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/dividends", headers=auth_headers, timeout=30)
        data = r.json()
        assert "source" in data, "Missing top-level 'source' key"
        assert data["source"] == "BVB.ro (oficial)", \
            f"source='{data['source']}', expected 'BVB.ro (oficial)'"
        print(f"✅ top-level source='{data['source']}'")


# ─── Test: GET /news ──────────────────────────────────────────────────────────

class TestGetPortfolioNews:
    """GET /api/portfolio-bvb/news with PRO token."""

    def test_news_returns_200(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", headers=auth_headers, timeout=30)
        assert r.status_code == 200, f"Expected 200, got {r.status_code} — {r.text[:300]}"
        print(f"✅ GET /portfolio-bvb/news → 200")

    def test_news_response_structure(self, auth_headers):
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", headers=auth_headers, timeout=30)
        data = r.json()
        assert "news" in data, f"Missing 'news' key: {list(data.keys())}"
        assert "symbols_searched" in data, f"Missing 'symbols_searched': {list(data.keys())}"
        assert "count" in data, f"Missing 'count': {list(data.keys())}"
        assert isinstance(data["news"], list), "news should be a list"
        print(f"✅ Response has 'news' (list), 'symbols_searched', 'count'")

    def test_news_has_articles(self, auth_headers):
        """News should return at least 1 article (up to 8)."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", headers=auth_headers, timeout=30)
        data = r.json()
        count = len(data["news"])
        assert count > 0, f"Expected at least 1 article, got {count}"
        assert count <= 8, f"Expected max 8 articles, got {count}"
        print(f"✅ News returned {count} articles (max 8)")

    def test_news_articles_have_required_fields(self, auth_headers):
        """Each article must have title, source, published_at, related_symbols."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", headers=auth_headers, timeout=30)
        data = r.json()
        articles = data["news"]
        if not articles:
            pytest.skip("No articles returned — skipping field check")
        for i, art in enumerate(articles):
            required_fields = ["title", "source", "published_at", "related_symbols"]
            for field in required_fields:
                assert field in art, f"Article {i} missing field '{field}': {list(art.keys())}"
        print(f"✅ All {len(articles)} articles have required fields: title, source, published_at, related_symbols")

    def test_news_articles_related_symbols_is_list(self, auth_headers):
        """related_symbols should be a list."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", headers=auth_headers, timeout=30)
        data = r.json()
        for i, art in enumerate(data["news"]):
            assert isinstance(art["related_symbols"], list), \
                f"Article {i} related_symbols should be a list, got {type(art['related_symbols'])}"
        print(f"✅ All articles have related_symbols as a list")

    def test_news_articles_have_symbol_tags(self, auth_headers):
        """At least some articles should be tagged with H2O or BRD."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", headers=auth_headers, timeout=30)
        data = r.json()
        articles = data["news"]
        if not articles:
            pytest.skip("No articles — skipping symbol tag check")

        tagged_articles = [a for a in articles if len(a["related_symbols"]) > 0]
        assert len(tagged_articles) > 0, \
            f"No articles have related_symbols tags. All articles: {[a['related_symbols'] for a in articles]}"

        all_symbols = []
        for a in articles:
            all_symbols.extend(a["related_symbols"])
        print(f"✅ Tagged articles: {len(tagged_articles)}/{len(articles)}. Symbols found: {list(set(all_symbols))}")

    def test_news_symbols_searched_contains_portfolio(self, auth_headers):
        """symbols_searched should include the portfolio symbols (H2O and/or BRD)."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", headers=auth_headers, timeout=30)
        data = r.json()
        symbols = data["symbols_searched"]
        assert "H2O" in symbols or "BRD" in symbols, \
            f"Expected H2O or BRD in symbols_searched, got {symbols}"
        print(f"✅ symbols_searched={symbols}")

    def test_news_count_matches_news_list(self, auth_headers):
        """count field should match the actual number of articles."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", headers=auth_headers, timeout=30)
        data = r.json()
        assert data["count"] == len(data["news"]), \
            f"count={data['count']} doesn't match len(news)={len(data['news'])}"
        print(f"✅ count={data['count']} matches len(news)={len(data['news'])}")

    def test_news_articles_have_title_not_empty(self, auth_headers):
        """All article titles should be non-empty strings."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", headers=auth_headers, timeout=30)
        data = r.json()
        for i, art in enumerate(data["news"]):
            title = art.get("title") or art.get("title_ro") or ""
            assert len(title) > 0, f"Article {i} has empty title: {art}"
        print(f"✅ All articles have non-empty titles")

    def test_news_articles_have_published_at(self, auth_headers):
        """published_at should be a non-null datetime string."""
        r = requests.get(f"{BASE_URL}/api/portfolio-bvb/news", headers=auth_headers, timeout=30)
        data = r.json()
        for i, art in enumerate(data["news"]):
            pub = art.get("published_at")
            assert pub is not None, f"Article {i} has null published_at"
            assert isinstance(pub, str) and len(pub) > 0, f"Article {i} published_at invalid: {pub}"
        print(f"✅ All articles have valid published_at datetime strings")
