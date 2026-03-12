# API Quick Reference

A condensed endpoint index for SportsPulse.

**Base URL:** `https://zijianni.pythonanywhere.com`

---

## Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | None | Create account, returns token |
| POST | `/api/auth/login/` | None | Login, returns token |

---

## Teams

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/teams/` | None | List all teams (`?country=`, `?search=`) |
| POST | `/api/teams/` | Token | Create team |
| GET | `/api/teams/{id}/` | None | Get team by ID |
| PUT | `/api/teams/{id}/` | Token | Full update |
| PATCH | `/api/teams/{id}/` | Token | Partial update |
| DELETE | `/api/teams/{id}/` | Token | Delete team |
| GET | `/api/teams/{id}/players/` | None | List team's players |

---

## Players

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/players/` | None | List players (`?team=`, `?position=`, `?search=`) |
| POST | `/api/players/` | Token | Create player |
| GET | `/api/players/{id}/` | None | Get player |
| PATCH | `/api/players/{id}/` | Token | Partial update |
| DELETE | `/api/players/{id}/` | Token | Delete player |

---

## Matches

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/matches/` | None | List matches (`?team=`, `?season=`, `?status=`) |
| POST | `/api/matches/` | Token | Create match |
| GET | `/api/matches/{id}/` | None | Get match |
| PATCH | `/api/matches/{id}/` | Token | Update score/status |
| DELETE | `/api/matches/{id}/` | Token | Delete match |

---

## Statistics

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/statistics/` | None | List stats (`?player=`, `?match=`) |
| POST | `/api/statistics/` | Token | Create stat record |
| GET | `/api/statistics/{id}/` | None | Get stat record |
| DELETE | `/api/statistics/{id}/` | Token | Delete stat record |

---

## Analytics (all read-only, no auth required)

| Method | Endpoint | Parameters | Description |
|--------|----------|-----------|-------------|
| GET | `/api/analytics/leaderboard/` | `metric`, `season`, `limit` | Goals/assists ranking |
| GET | `/api/analytics/team-performance/` | `season`, `team` | League standings |
| GET | `/api/analytics/head-to-head/` | `team1`*, `team2`*, `season` | H2H record |
| GET | `/api/analytics/season-summary/` | `season`* | Season aggregates |
| GET | `/api/analytics/player-profile/{id}/` | — | Career stats |

*Required parameter.

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | OK — successful GET / PUT / PATCH |
| 201 | Created — successful POST |
| 204 | No Content — successful DELETE |
| 400 | Bad Request — validation error |
| 401 | Unauthorized — missing/invalid token |
| 404 | Not Found |
| 429 | Too Many Requests — rate limit exceeded |

---

## Practical Usage Examples

### Workflow: Register, Login, and Fetch Data

```bash
# 1. Register a new user
curl -X POST https://zijianni.pythonanywhere.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "SecurePass123"}'

# 2. Login and capture the token
TOKEN=$(curl -s -X POST https://zijianni.pythonanywhere.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "SecurePass123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# 3. List all teams
curl -H "Authorization: Token $TOKEN" \
  https://zijianni.pythonanywhere.com/api/teams/

# 4. Get top scorer leaderboard
curl -H "Authorization: Token $TOKEN" \
  "https://zijianni.pythonanywhere.com/api/analytics/leaderboard/?season=2024/2025"

# 5. Get head-to-head comparison
curl -H "Authorization: Token $TOKEN" \
  "https://zijianni.pythonanywhere.com/api/analytics/head-to-head/?team1=1&team2=2"
```

### Filtering and Pagination

```bash
# Filter players by position
curl -H "Authorization: Token $TOKEN" \
  "https://zijianni.pythonanywhere.com/api/players/?position=FW"

# Filter matches by status
curl -H "Authorization: Token $TOKEN" \
  "https://zijianni.pythonanywhere.com/api/matches/?status=COMPLETED"

# Paginate results (page size default: 20)
curl -H "Authorization: Token $TOKEN" \
  "https://zijianni.pythonanywhere.com/api/teams/?page=2"
```
