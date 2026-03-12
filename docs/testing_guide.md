# Testing Guide

SportsPulse includes a comprehensive test suite with 79 tests across 6 categories.

---

## Running Tests

```bash
# Run all tests
python manage.py test api

# Verbose output (recommended)
python manage.py test api --verbosity=2

# Run a specific test class
python manage.py test api.tests.TeamAPITests
python manage.py test api.tests.AnalyticsTests
python manage.py test api.tests.AuthTests

# Run a specific test method
python manage.py test api.tests.TeamAPITests.test_create_team_authenticated
```

All tests should complete in under 30 seconds.

---

## Test Structure

Tests are in `api/tests.py` and organised around a shared `BaseTestCase` that creates a consistent fixture:

| Fixture Object | Details |
|---------------|---------|
| 2 Teams | Arsenal (ARS), Chelsea (CHE) |
| 4 Players | 2 per team, with jersey numbers and positions |
| 1 Match | Arsenal 2 - 1 Chelsea, COMPLETED, 2024/2025 |
| 4 PlayerMatchStatistics | One per player for the test match |
| 1 Auth User | Created for write-operation tests |

---

## Test Categories

### Model Tests (8)
- String representation (`__str__`) of all four models
- UniqueConstraint violation raises `IntegrityError`
- Computed field behaviour (e.g. `result_summary`)

### Authentication Tests (6)
- Successful registration returns token
- Duplicate username returns 400
- Successful login returns token
- Invalid credentials return 401
- Protected endpoint without token returns 401
- Protected endpoint with valid token returns 200/201/204

### CRUD Tests (28)
All four resources (Team, Player, Match, Statistic) × operations:
- List (GET /resource/)
- Create (POST /resource/) — authenticated
- Retrieve (GET /resource/{id}/)
- Full update (PUT /resource/{id}/) — authenticated
- Partial update (PATCH /resource/{id}/) — authenticated
- Delete (DELETE /resource/{id}/) — authenticated
- Unauthenticated write → 401

### Query Filtering Tests (10)
- `/api/players/?position=GK` returns only goalkeepers
- `/api/players/?team=1` returns only team 1 players
- `/api/matches/?season=2024/2025` filters by season
- `/api/matches/?status=COMPLETED` filters by status
- `/api/analytics/leaderboard/?metric=invalid` returns 400
- `/api/analytics/season-summary/?season=bad-format` returns 400

### Analytics Tests (15)
- Leaderboard returns ranked list ordered by `total` descending
- Leaderboard `metric=assists` returns assist data
- Team performance returns correct points calculation (W=3, D=1, L=0)
- Head-to-head requires both `team1` and `team2` parameters
- Season summary requires `season` parameter
- Player profile returns career totals and per-season breakdown
- All analytics endpoints return 200 without authentication

### Status Code Tests (6)
Explicit verification of correct HTTP codes:
- `200 OK` on list/retrieve/update
- `201 Created` on create
- `204 No Content` on delete
- `400 Bad Request` on invalid input
- `401 Unauthorized` on unauthenticated writes
- `404 Not Found` for non-existent resource IDs

---

## Adding New Tests

Follow the existing pattern in `api/tests.py`:

```python
class NewFeatureTests(BaseTestCase):
    def test_new_endpoint_returns_200(self):
        response = self.client.get('/api/new-endpoint/')
        self.assertEqual(response.status_code, 200)

    def test_new_endpoint_authenticated(self):
        response = self.auth_client.post('/api/new-endpoint/', {...})
        self.assertEqual(response.status_code, 201)
```

The `self.auth_client` is pre-configured with a valid token. Use `self.client` for unauthenticated requests.

---

## Continuous Integration

Tests run automatically on every push to `main` and every pull request via GitHub Actions. See `.github/workflows/django.yml`.

Current status: all 79 tests pass on Python 3.10 and 3.12.
