# SportsPulse (Final Coursework Version)

> 🏆 **COMP3011 Coursework 1 — SportsPulse**  
> Live demo: [zijianni.pythonanywhere.com](https://zijianni.pythonanywhere.com)  
> API docs: [Swagger UI](https://zijianni.pythonanywhere.com/api/docs/) | [ReDoc](https://zijianni.pythonanywhere.com/api/redoc/)  
> GitHub: [Zijian-Ni/3011_CW1](https://github.com/Zijian-Ni/3011_CW1)


Last updated: 2026-03-10

SportsPulse is a Django + Django REST Framework football statistics and analytics platform for COMP3011 coursework.
It includes full CRUD APIs, analytics endpoints, token auth, frontend pages for both normal users and admin operations, automated tests, and PythonAnywhere deployment support.

## 1. Final Submission Status

This repository currently provides:

- [x] 4 core REST resources (Teams, Players, Matches, PlayerMatchStatistic)
- [x] Full CRUD for all resources
- [x] Query filtering and validation
- [x] Authentication (register/login + token)
- [x] Permission control (read public, write authenticated)
- [x] Throttling for anon/user/register/login
- [x] Analytics endpoints (leaderboard, team performance, head-to-head, season summary, player profile)
- [x] OpenAPI schema + Swagger + ReDoc
- [x] Frontend pages for dashboard, fan view, and admin CRUD operations
- [x] Automated tests (79 tests passing)
- [x] PythonAnywhere deployment instructions (Python 3.10)

## 2. Technology Stack

- Python 3.10+
- Django 5.x
- Django REST Framework 3.16.x
- drf-spectacular (OpenAPI 3 docs)
- SQLite (default)
- Django templates + vanilla JS + CSS

Dependencies are in `requirements.txt`:

- `Django>=5.0,<6.0`
- `djangorestframework>=3.15,<4.0`
- `drf-spectacular>=0.27,<1.0`

## 3. Project Structure

```text
sportspulse/
|-- manage.py
|-- requirements.txt
|-- README.md

|-- sportspulse/
|   |-- settings.py
|   |-- urls.py
|   |-- views.py
|   |-- wsgi.py
|   `-- asgi.py
|-- api/
|   |-- __init__.py
|   |-- apps.py
|   |-- models.py
|   |-- serializers.py
|   |-- validators.py
|   |-- services.py
|   |-- views.py
|   |-- urls.py
|   |-- tests.py
|   |-- migrations/
|   `-- management/commands/seed_data.py
|-- templates/
|   |-- dashboard.html
|   |-- fan_portal.html
|   `-- admin_portal.html
`-- static/api/
    |-- dashboard.css
    |-- dashboard.js
    |-- fan.css
    |-- fan.js
    |-- admin.css
    `-- admin.js
```

## 4. Local Setup

### 4.1 Create environment and install

```bash
git clone https://github.com/Zijian-Ni/3011_CW1
cd sportspulse

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
```

### 4.2 Database and seed data

```bash
python manage.py migrate
python manage.py seed_data
```

### 4.3 Run server

```bash
python manage.py runserver
```

## 5. Main URLs

Local URLs (default `127.0.0.1:8000`):

- Dashboard: `http://127.0.0.1:8000/`
- Fan view: `http://127.0.0.1:8000/fan/`
- Admin portal (custom frontend): `http://127.0.0.1:8000/admin-portal/`
- Django admin site: `http://127.0.0.1:8000/admin/`
- API root: `http://127.0.0.1:8000/api/`
- OpenAPI schema JSON: `http://127.0.0.1:8000/api/schema/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`

## 6. Auth, Permissions, Pagination, Throttling

Configured in `sportspulse/settings.py`:

- Authentication:
  - `TokenAuthentication`
  - `SessionAuthentication`
- Default permission:
  - `IsAuthenticatedOrReadOnly`
  - GET endpoints are public
  - POST/PUT/PATCH/DELETE require auth token
- Pagination:
  - `PageNumberPagination`
  - `PAGE_SIZE = 20`
- Throttling:
  - `anon = 100/hour`
  - `user = 500/hour`
  - `register = 5/hour`
  - `login = 20/hour`

## 7. API Endpoints

### 7.1 CRUD resources

| Resource | List/Create | Detail |
|---|---|---|
| Teams | `/api/teams/` | `/api/teams/{id}/` |
| Players | `/api/players/` | `/api/players/{id}/` |
| Matches | `/api/matches/` | `/api/matches/{id}/` |
| Statistics | `/api/statistics/` | `/api/statistics/{id}/` |

Extra endpoint:

- `GET /api/teams/{id}/players/`

### 7.2 Auth endpoints

- `POST /api/auth/register/`
- `POST /api/auth/login/`

### 7.3 Analytics endpoints

- `GET /api/analytics/leaderboard/`
- `GET /api/analytics/team-performance/`
- `GET /api/analytics/head-to-head/`
- `GET /api/analytics/season-summary/`
- `GET /api/analytics/player-profile/{id}/`

### 7.4 Common filters

```text
GET /api/teams/?country=England&search=ars
GET /api/players/?team=1&position=FW&search=saka
GET /api/matches/?team=1&season=2024/2025&status=COMPLETED
GET /api/statistics/?player=1&match=5
GET /api/analytics/leaderboard/?metric=goals&season=2024/2025&limit=10
GET /api/analytics/head-to-head/?team1=1&team2=2&season=2024/2025
```

Validation rules include:

- Season format must be `YYYY/YYYY` and second year must be exactly +1
- ID query params must be positive integers
- Position/status filter values must be valid enum values

## 8. Frontend Pages and Interaction

### 8.1 Normal user pages

- Dashboard (`/`)
  - KPI cards
  - leaderboard table
  - team performance table
  - season summary
  - head-to-head panel
- Fan view (`/fan/`)
  - read-only browsing
  - team and match exploration
  - leaderboard and player profile view

### 8.2 Admin operations page

- Admin portal (`/admin-portal/`)
  - register/login token workflow
  - manual token input
  - CRUD actions for all 4 resources:
    - add
    - edit
    - delete
    - refresh/list
  - feedback to user via UI status/toast messages

## 9. Seed Data

Run:

```bash
python manage.py seed_data
```

Current seed behavior:

- clears existing Team/Player/Match/PlayerMatchStatistic data
- creates 6 teams
- creates 36 players (6 per team)
- creates 30 completed matches (season `2024/2025`)
- creates per-match player stats for all lineups
- creates demo user if missing:
  - username: `demo`
  - password: `demopass123`

## 10. Testing

Run:

```bash
python manage.py test api
```

Latest verified result (2026-03-07):

- Found 79 tests
- Ran 79 tests
- Status: OK

Coverage includes:

- model constraints and behavior
- register/login success and failure
- CRUD + auth boundaries
- query filtering and validation errors
- analytics payload correctness
- expected HTTP status codes

## 11. PythonAnywhere Deployment (Python 3.10)

### 11.1 Create project and virtualenv

```bash
cd ~
git clone https://github.com/Zijian-Ni/3011_CW1 3011_CW1
cd 3011_CW1

mkvirtualenv sportspulse-venv --python=/usr/bin/python3.10
workon sportspulse-venv

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### 11.2 Web tab settings

- Source code: `/home/<username>/3011_CW1`
- Working directory: `/home/<username>/3011_CW1`
- Virtualenv: `/home/<username>/.virtualenvs/sportspulse-venv`

### 11.3 WSGI file

Edit `/var/www/<username>_pythonanywhere_com_wsgi.py`:

```python
import os
import sys

project_home = "/home/<username>/3011_CW1"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sportspulse.settings")
os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_SECRET_KEY"] = "<replace-with-your-own-strong-random-key>"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Then click `Reload` in the PythonAnywhere Web tab.

## 12. PythonAnywhere Error Fix Guide

### 12.1 `ImproperlyConfigured: api has multiple filesystem locations`

Cause:

- mixed paths like `/home/<user>/3011_CW1/./api` and `/home/<user>/3011_CW1/api`
- app loaded as namespace package without explicit path

Fix:

- use clean absolute path (no `/./`) in WSGI and Web tab config
- keep `INSTALLED_APPS` as `api.apps.ApiConfig` (already done)
- keep `api/apps.py` with:
  - `name = "api"`
  - `path = str(Path(__file__).resolve().parent)`
- ensure `api/__init__.py` exists

### 12.2 `DisallowedHost: Invalid HTTP_HOST`

Fix:

- add your domain to `ALLOWED_HOSTS` in `sportspulse/settings.py`, for example:
  - `zijianni.pythonanywhere.com`

### 12.3 `OSError: write error` and `SIGPIPE Broken pipe`

Meaning:

- client disconnected before response finished
- usually not a code bug and can be ignored if app otherwise works

### 12.4 Flask SQLAlchemy SAWarning in old logs

Meaning:

- these warnings are from a different Flask app / old Python 3.6 virtualenv
- not from this Django SportsPulse project

## 13. Coursework Requirement Mapping

| Coursework requirement area | Evidence in this project |
|---|---|
| REST resource design | `/api/teams/`, `/api/players/`, `/api/matches/`, `/api/statistics/` with correct methods |
| Model relationships | Team-Player, Team-Match (home/away), Player+Match-Statistic |
| Validation and error handling | shared validators in `api/validators.py`, serializer validation, DRF errors |
| Auth and authorization | register/login endpoints + token auth + `IsAuthenticatedOrReadOnly` |
| Advanced functionality | analytics service layer (`api/services.py`) |
| API documentation | OpenAPI schema + Swagger + ReDoc |
| Frontend interaction | dashboard, fan portal, admin portal with CRUD flows |
| Test quality | `api/tests.py`, 79 tests passing |
| Deployment readiness | PythonAnywhere 3.10 workflow + troubleshooting section |

## 14. Marker Quick Verification

```bash
python manage.py migrate
python manage.py seed_data
python manage.py test api
python manage.py runserver
```

Then open:

- `/api/docs/` for endpoint docs
- `/` and `/fan/` for user-facing frontend
- `/admin-portal/` for token-based admin CRUD frontend

## 15. Notes

- This is a coursework submission project.
- For public deployment, always set a private `DJANGO_SECRET_KEY` and set `DJANGO_DEBUG=False`.

---

## 16. Submitted Deliverables

| Deliverable | Location |
|---|---|
| Source code | This repository |
| API documentation (Swagger) | [`/api/docs/`](https://zijianni.pythonanywhere.com/api/docs/) (live) |
| API documentation (ReDoc) | [`/api/redoc/`](https://zijianni.pythonanywhere.com/api/redoc/) (live) |
| API documentation (PDF) | [`docs/api_documentation.pdf`](docs/api_documentation.pdf) |
| Technical report | [`docs/technical_report.md`](docs/technical_report.md) |
| GenAI declaration | [`docs/genai_declaration.md`](docs/genai_declaration.md) |

## 17. Live Deployment

| URL | Description |
|---|---|
| https://zijianni.pythonanywhere.com | Dashboard (home page) |
| https://zijianni.pythonanywhere.com/fan/ | Fan portal (read-only) |
| https://zijianni.pythonanywhere.com/admin-portal/ | Admin CRUD portal |
| https://zijianni.pythonanywhere.com/api/ | API root |
| https://zijianni.pythonanywhere.com/api/docs/ | Swagger UI |
| https://zijianni.pythonanywhere.com/api/redoc/ | ReDoc |
| https://zijianni.pythonanywhere.com/api/schema/ | OpenAPI JSON schema |

## 18. Test Results

```
$ python manage.py test api
Found 79 tests
Ran 79 tests in X.XXXs
OK
```

Last verified: 2026-03-07
