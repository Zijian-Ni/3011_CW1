# SportsPulse API Documentation
**COMP3011 Coursework 1 | Zijian Ni | March 2026**

---

## Overview

| | |
|---|---|
| **Base URL** | `https://zijianni.pythonanywhere.com` |
| **API Root** | `https://zijianni.pythonanywhere.com/api/` |
| **Swagger UI** | `https://zijianni.pythonanywhere.com/api/docs/` |
| **ReDoc** | `https://zijianni.pythonanywhere.com/api/redoc/` |
| **OpenAPI Schema** | `https://zijianni.pythonanywhere.com/api/schema/` |
| **Version** | 1.0.0 |
| **Format** | JSON |

SportsPulse is a RESTful API for football statistics and analytics. It provides CRUD operations for Teams, Players, Matches, and Match Statistics, as well as advanced analytics endpoints.

---

## Authentication

SportsPulse uses **Token Authentication** (DRF `TokenAuthentication`).

### Obtain a Token

1. Register: `POST /api/auth/register/`
2. Login: `POST /api/auth/login/` → receive `token`
3. Include in requests: `Authorization: Token <your_token>`

**Read endpoints (GET)** are publicly accessible without authentication.  
**Write endpoints (POST, PUT, PATCH, DELETE)** require a valid token.

---

## Rate Limiting

| Client Type | Limit |
|---|---|
| Anonymous | 100 requests/hour |
| Authenticated | 500 requests/hour |
| Registration endpoint | 5 requests/hour |
| Login endpoint | 20 requests/hour |

---

## Pagination

All list endpoints return paginated responses:

```json
{
  "count": 100,
  "next": "http://api/teams/?page=2",
  "previous": null,
  "results": [...]
}
```

Default page size: **20 items**.

---

## Standard HTTP Status Codes

| Code | Meaning |
|---|---|
| `200 OK` | Successful GET, PUT, PATCH |
| `201 Created` | Successful POST |
| `204 No Content` | Successful DELETE |
| `400 Bad Request` | Validation error |
| `401 Unauthorized` | Missing or invalid token |
| `403 Forbidden` | Authenticated but not permitted |
| `404 Not Found` | Resource not found |
| `429 Too Many Requests` | Rate limit exceeded |

---

## Endpoints

### `/api/analytics/head-to-head/`

#### `GET /api/analytics/head-to-head/`
GET /api/analytics/head-to-head/?team1=1&team2=2

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `season` | string | ❌ | Optional season filter |
| `team1` | integer | ✅ | First team ID |
| `team2` | integer | ✅ | Second team ID |

**Responses:**

- `200` 

---

### `/api/analytics/leaderboard/`

#### `GET /api/analytics/leaderboard/`
GET /api/analytics/leaderboard/

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | ❌ | Number of results (default 10, max 50) |
| `metric` | string | ❌ | Ranking metric: goals or assists |
| `season` | string | ❌ | Filter by season |

**Responses:**

- `200` 

---

### `/api/analytics/player-profile/{id}/`

#### `GET /api/analytics/player-profile/{id}/`
GET /api/analytics/player-profile/{id}/

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Responses:**

- `200` 

---

### `/api/analytics/season-summary/`

#### `GET /api/analytics/season-summary/`
GET /api/analytics/season-summary/?season=2024/2025

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `season` | string | ✅ | Season, e.g. 2024/2025 |

**Responses:**

- `200` 

---

### `/api/analytics/team-performance/`

#### `GET /api/analytics/team-performance/`
GET /api/analytics/team-performance/

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `season` | string | ❌ | Filter by season |
| `team` | integer | ❌ | Single team ID |

**Responses:**

- `200` 

---

### `/api/auth/login/`

#### `POST /api/auth/login/`
POST /api/auth/login/
Authenticate with username/password and return a token.

- **Auth required:** ✅ Yes (Token)

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `username` | string | ✅ |  |
| `password` | string | ✅ |  |

**Responses:**

- `200` 

---

### `/api/auth/register/`

#### `POST /api/auth/register/`
POST /api/auth/register/
Create a new user account and return a token immediately.

- **Auth required:** ✅ Yes (Token)

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ✅ |  |
| `username` | string | ✅ | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. |
| `email` | string | ❌ |  |
| `password` | string | ✅ |  |

**Responses:**

- `201` 

---

### `/api/matches/`

#### `GET /api/matches/`
CRUD for matches with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `page` | integer | ❌ | A page number within the paginated result set. |
| `season` | string | ❌ | Filter by season, e.g. 2024/2025 |
| `status` | string | ❌ | Filter by status (SCHEDULED/LIVE/COMPLETED/POSTPONED) |
| `team` | integer | ❌ | Filter by team ID (home or away) |

**Responses:**

- `200` 

---

#### `POST /api/matches/`
CRUD for matches with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ✅ |  |
| `home_team` | integer | ✅ |  |
| `home_team_detail` | object | ✅ |  |
| `away_team` | integer | ✅ |  |
| `away_team_detail` | object | ✅ |  |
| `date` | string | ✅ |  |
| `venue` | string | ❌ |  |
| `season` | string | ✅ | Format: 2024/2025 |
| `home_score` | integer | ❌ |  |
| `away_score` | integer | ❌ |  |
| `status` | StatusEnum | ❌ |  |
| `result_summary` | string | ✅ |  |
| `created_at` | string | ✅ |  |
| `updated_at` | string | ✅ |  |

**Responses:**

- `201` 

---

### `/api/matches/{id}/`

#### `GET /api/matches/{id}/`
CRUD for matches with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Responses:**

- `200` 

---

#### `PUT /api/matches/{id}/`
CRUD for matches with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ✅ |  |
| `home_team` | integer | ✅ |  |
| `home_team_detail` | object | ✅ |  |
| `away_team` | integer | ✅ |  |
| `away_team_detail` | object | ✅ |  |
| `date` | string | ✅ |  |
| `venue` | string | ❌ |  |
| `season` | string | ✅ | Format: 2024/2025 |
| `home_score` | integer | ❌ |  |
| `away_score` | integer | ❌ |  |
| `status` | StatusEnum | ❌ |  |
| `result_summary` | string | ✅ |  |
| `created_at` | string | ✅ |  |
| `updated_at` | string | ✅ |  |

**Responses:**

- `200` 

---

#### `PATCH /api/matches/{id}/`
CRUD for matches with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ❌ |  |
| `home_team` | integer | ❌ |  |
| `home_team_detail` | object | ❌ |  |
| `away_team` | integer | ❌ |  |
| `away_team_detail` | object | ❌ |  |
| `date` | string | ❌ |  |
| `venue` | string | ❌ |  |
| `season` | string | ❌ | Format: 2024/2025 |
| `home_score` | integer | ❌ |  |
| `away_score` | integer | ❌ |  |
| `status` | StatusEnum | ❌ |  |
| `result_summary` | string | ❌ |  |
| `created_at` | string | ❌ |  |
| `updated_at` | string | ❌ |  |

**Responses:**

- `200` 

---

#### `DELETE /api/matches/{id}/`
CRUD for matches with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Responses:**

- `204` No response body

---

### `/api/players/`

#### `GET /api/players/`
CRUD for players with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `page` | integer | ❌ | A page number within the paginated result set. |
| `position` | string | ❌ | Filter by position code (GK/DF/MF/FW) |
| `search` | string | ❌ | Search by player name |
| `team` | integer | ❌ | Filter by team ID |

**Responses:**

- `200` 

---

#### `POST /api/players/`
CRUD for players with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ✅ |  |
| `name` | string | ✅ |  |
| `team` | integer | ✅ |  |
| `team_detail` | object | ✅ |  |
| `position` | PositionEnum | ✅ |  |
| `position_display` | string | ✅ |  |
| `nationality` | string | ❌ |  |
| `date_of_birth` | string | ❌ |  |
| `jersey_number` | integer | ❌ |  |
| `created_at` | string | ✅ |  |
| `updated_at` | string | ✅ |  |

**Responses:**

- `201` 

---

### `/api/players/{id}/`

#### `GET /api/players/{id}/`
CRUD for players with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Responses:**

- `200` 

---

#### `PUT /api/players/{id}/`
CRUD for players with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ✅ |  |
| `name` | string | ✅ |  |
| `team` | integer | ✅ |  |
| `team_detail` | object | ✅ |  |
| `position` | PositionEnum | ✅ |  |
| `position_display` | string | ✅ |  |
| `nationality` | string | ❌ |  |
| `date_of_birth` | string | ❌ |  |
| `jersey_number` | integer | ❌ |  |
| `created_at` | string | ✅ |  |
| `updated_at` | string | ✅ |  |

**Responses:**

- `200` 

---

#### `PATCH /api/players/{id}/`
CRUD for players with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ❌ |  |
| `name` | string | ❌ |  |
| `team` | integer | ❌ |  |
| `team_detail` | object | ❌ |  |
| `position` | PositionEnum | ❌ |  |
| `position_display` | string | ❌ |  |
| `nationality` | string | ❌ |  |
| `date_of_birth` | string | ❌ |  |
| `jersey_number` | integer | ❌ |  |
| `created_at` | string | ❌ |  |
| `updated_at` | string | ❌ |  |

**Responses:**

- `200` 

---

#### `DELETE /api/players/{id}/`
CRUD for players with optional filtering.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Responses:**

- `204` No response body

---

### `/api/statistics/`

#### `GET /api/statistics/`
CRUD for per-match player statistics.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `match` | integer | ❌ | Filter by match ID |
| `page` | integer | ❌ | A page number within the paginated result set. |
| `player` | integer | ❌ | Filter by player ID |

**Responses:**

- `200` 

---

#### `POST /api/statistics/`
CRUD for per-match player statistics.

- **Auth required:** ✅ Yes (Token)

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ✅ |  |
| `player` | integer | ✅ |  |
| `player_detail` | object | ✅ |  |
| `match` | integer | ✅ |  |
| `match_detail` | object | ✅ |  |
| `goals` | integer | ❌ |  |
| `assists` | integer | ❌ |  |
| `minutes_played` | integer | ❌ |  |
| `yellow_cards` | integer | ❌ |  |
| `red_cards` | integer | ❌ |  |
| `shots_on_target` | integer | ❌ |  |
| `passes_completed` | integer | ❌ |  |
| `tackles` | integer | ❌ |  |
| `saves` | integer | ❌ |  |
| `created_at` | string | ✅ |  |

**Responses:**

- `201` 

---

### `/api/statistics/{id}/`

#### `GET /api/statistics/{id}/`
CRUD for per-match player statistics.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Responses:**

- `200` 

---

#### `PUT /api/statistics/{id}/`
CRUD for per-match player statistics.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ✅ |  |
| `player` | integer | ✅ |  |
| `player_detail` | object | ✅ |  |
| `match` | integer | ✅ |  |
| `match_detail` | object | ✅ |  |
| `goals` | integer | ❌ |  |
| `assists` | integer | ❌ |  |
| `minutes_played` | integer | ❌ |  |
| `yellow_cards` | integer | ❌ |  |
| `red_cards` | integer | ❌ |  |
| `shots_on_target` | integer | ❌ |  |
| `passes_completed` | integer | ❌ |  |
| `tackles` | integer | ❌ |  |
| `saves` | integer | ❌ |  |
| `created_at` | string | ✅ |  |

**Responses:**

- `200` 

---

#### `PATCH /api/statistics/{id}/`
CRUD for per-match player statistics.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ❌ |  |
| `player` | integer | ❌ |  |
| `player_detail` | object | ❌ |  |
| `match` | integer | ❌ |  |
| `match_detail` | object | ❌ |  |
| `goals` | integer | ❌ |  |
| `assists` | integer | ❌ |  |
| `minutes_played` | integer | ❌ |  |
| `yellow_cards` | integer | ❌ |  |
| `red_cards` | integer | ❌ |  |
| `shots_on_target` | integer | ❌ |  |
| `passes_completed` | integer | ❌ |  |
| `tackles` | integer | ❌ |  |
| `saves` | integer | ❌ |  |
| `created_at` | string | ❌ |  |

**Responses:**

- `200` 

---

#### `DELETE /api/statistics/{id}/`
CRUD for per-match player statistics.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Responses:**

- `204` No response body

---

### `/api/teams/`

#### `GET /api/teams/`
CRUD for football teams.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `country` | string | ❌ | Filter by country |
| `page` | integer | ❌ | A page number within the paginated result set. |
| `search` | string | ❌ | Search by team name |

**Responses:**

- `200` 

---

#### `POST /api/teams/`
CRUD for football teams.

- **Auth required:** ✅ Yes (Token)

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ✅ |  |
| `name` | string | ✅ |  |
| `short_name` | string | ✅ | Abbreviation, e.g. ARS for Arsenal |
| `country` | string | ❌ |  |
| `founded_year` | integer | ❌ |  |
| `stadium` | string | ❌ |  |
| `crest_url` | string | ❌ |  |
| `player_count` | integer | ✅ |  |
| `created_at` | string | ✅ |  |
| `updated_at` | string | ✅ |  |

**Responses:**

- `201` 

---

### `/api/teams/{id}/`

#### `GET /api/teams/{id}/`
CRUD for football teams.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Responses:**

- `200` 

---

#### `PUT /api/teams/{id}/`
CRUD for football teams.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ✅ |  |
| `name` | string | ✅ |  |
| `short_name` | string | ✅ | Abbreviation, e.g. ARS for Arsenal |
| `country` | string | ❌ |  |
| `founded_year` | integer | ❌ |  |
| `stadium` | string | ❌ |  |
| `crest_url` | string | ❌ |  |
| `player_count` | integer | ✅ |  |
| `created_at` | string | ✅ |  |
| `updated_at` | string | ✅ |  |

**Responses:**

- `200` 

---

#### `PATCH /api/teams/{id}/`
CRUD for football teams.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Request Body (JSON):**

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | ❌ |  |
| `name` | string | ❌ |  |
| `short_name` | string | ❌ | Abbreviation, e.g. ARS for Arsenal |
| `country` | string | ❌ |  |
| `founded_year` | integer | ❌ |  |
| `stadium` | string | ❌ |  |
| `crest_url` | string | ❌ |  |
| `player_count` | integer | ❌ |  |
| `created_at` | string | ❌ |  |
| `updated_at` | string | ❌ |  |

**Responses:**

- `200` 

---

#### `DELETE /api/teams/{id}/`
CRUD for football teams.

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Responses:**

- `204` No response body

---

### `/api/teams/{id}/players/`

#### `GET /api/teams/{id}/players/`
GET /api/teams/{id}/players/

- **Auth required:** ✅ Yes (Token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|

**Responses:**

- `200` 

---

## Example Usage

### 1. Register and Obtain Token

```bash
# Register
curl -X POST https://zijianni.pythonanywhere.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "pass1234", "email": "test@example.com"}'

# Login
curl -X POST https://zijianni.pythonanywhere.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "pass1234"}'
# Response: {"token": "abc123..."}
```

### 2. List All Teams (Public)

```bash
curl https://zijianni.pythonanywhere.com/api/teams/
```

### 3. Create a Team (Auth Required)

```bash
curl -X POST https://zijianni.pythonanywhere.com/api/teams/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{"name": "Arsenal", "country": "England", "founded_year": 1886, "stadium": "Emirates Stadium"}'
```

### 4. Get Leaderboard

```bash
curl "https://zijianni.pythonanywhere.com/api/analytics/leaderboard/?metric=goals&season=2024/2025&limit=10"
```

### 5. Head-to-Head Comparison

```bash
curl "https://zijianni.pythonanywhere.com/api/analytics/head-to-head/?team1=1&team2=2&season=2024/2025"
```

---

*Generated from OpenAPI schema — March 2026*
