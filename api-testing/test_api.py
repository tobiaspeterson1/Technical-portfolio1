"""
API-testning – Strukturerad testning av REST API
=================================================
Teknisk testning av JSONPlaceholder API med:
  - Statuskodvalidering
  - Schemavalidering (fälttyper och obligatoriska fält)
  - Negativa testfall (felaktig input)
  - Parametriserade tester

Kör med: pytest test_api.py -v
"""

import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

# ── Hjälpfunktioner ──────────────────────────────────────────────────────────

def assert_schema(data: dict, required_fields: dict):
    """
    Validerar att ett JSON-objekt innehåller rätt fält med rätt typ.
    required_fields = {"fältnamn": förväntad_typ}
    """
    for field, expected_type in required_fields.items():
        assert field in data, f"Saknat fält: '{field}'"
        assert isinstance(data[field], expected_type), (
            f"Fält '{field}': förväntade {expected_type.__name__}, "
            f"fick {type(data[field]).__name__}"
        )


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def session():
    """Återanvänd HTTP-session för bättre prestanda."""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    yield s
    s.close()


# ── GET-tester ────────────────────────────────────────────────────────────────

class TestGetRequests:

    def test_get_all_posts_returns_200(self, session):
        """Hämta alla inlägg – förväntar 200 OK."""
        response = session.get(f"{BASE_URL}/posts")
        assert response.status_code == 200

    def test_get_all_posts_returns_list(self, session):
        """Svaret ska vara en lista med 100 inlägg."""
        response = session.get(f"{BASE_URL}/posts")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 100

    def test_post_schema_validation(self, session):
        """Varje inlägg ska ha rätt fälttyper."""
        response = session.get(f"{BASE_URL}/posts/1")
        assert response.status_code == 200
        post = response.json()
        assert_schema(post, {
            "id":     int,
            "userId": int,
            "title":  str,
            "body":   str,
        })

    def test_get_single_user(self, session):
        """Hämta en specifik användare och validera schemat."""
        response = session.get(f"{BASE_URL}/users/1")
        assert response.status_code == 200
        user = response.json()
        assert_schema(user, {
            "id":       int,
            "name":     str,
            "email":    str,
            "username": str,
        })
        # Extra kontroll: e-post ska innehålla @
        assert "@" in user["email"], "E-postadressen verkar ogiltig"

    def test_response_time_under_2_seconds(self, session):
        """Svarstiden ska vara under 2 sekunder."""
        response = session.get(f"{BASE_URL}/posts")
        assert response.elapsed.total_seconds() < 2.0, (
            f"API svarade för långsamt: {response.elapsed.total_seconds():.2f}s"
        )

    def test_content_type_is_json(self, session):
        """Content-Type ska vara application/json."""
        response = session.get(f"{BASE_URL}/posts/1")
        assert "application/json" in response.headers.get("Content-Type", "")


# ── Negativa testfall ─────────────────────────────────────────────────────────

class TestNegativeCases:

    def test_nonexistent_resource_returns_404(self, session):
        """Begäran om icke-existerande resurs ska ge 404."""
        response = session.get(f"{BASE_URL}/posts/99999")
        assert response.status_code == 404

    def test_invalid_endpoint_returns_404(self, session):
        """Okänd endpoint ska ge 404."""
        response = session.get(f"{BASE_URL}/nonexistent-endpoint")
        assert response.status_code == 404


# ── POST-tester ───────────────────────────────────────────────────────────────

class TestPostRequests:

    def test_create_post_returns_201(self, session):
        """Skapa ett nytt inlägg – förväntar 201 Created."""
        payload = {
            "title":  "Testinlägg från portfolio",
            "body":   "Detta är ett automatiserat testinlägg.",
            "userId": 1,
        }
        response = session.post(f"{BASE_URL}/posts", json=payload)
        assert response.status_code == 201

    def test_create_post_returns_created_data(self, session):
        """Svaret ska spegla den skickade datan + ett genererat id."""
        payload = {"title": "Test", "body": "Kropp", "userId": 1}
        response = session.post(f"{BASE_URL}/posts", json=payload)
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["body"] == payload["body"]
        assert "id" in data  # servern ska tilldela ett id

    def test_update_post_returns_200(self, session):
        """PUT-uppdatering av ett inlägg ska ge 200 OK."""
        payload = {"id": 1, "title": "Uppdaterad titel", "body": "Ny text", "userId": 1}
        response = session.put(f"{BASE_URL}/posts/1", json=payload)
        assert response.status_code == 200

    def test_delete_post_returns_200(self, session):
        """DELETE ska ge 200 OK."""
        response = session.delete(f"{BASE_URL}/posts/1")
        assert response.status_code == 200


# ── Parametriserade tester ────────────────────────────────────────────────────

@pytest.mark.parametrize("post_id", [1, 5, 10, 50, 100])
def test_multiple_posts_have_valid_schema(session, post_id):
    """Kontrollerar att ett urval av inlägg alla följer rätt schema."""
    response = session.get(f"{BASE_URL}/posts/{post_id}")
    assert response.status_code == 200
    assert_schema(response.json(), {
        "id": int, "userId": int, "title": str, "body": str
    })
