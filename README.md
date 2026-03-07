# SportsPulse API

A football match statistics and analytics REST API built with Django and Django REST Framework.

SportsPulse allows users to manage and query football data — teams, players, matches, and per-match player statistics — and provides analytical endpoints for leaderboards, league standings, head-to-head records, season summaries, and player career profiles.

## Table of Contents

- [Project Overview](#project-overview)
- [Technology Stack](#technology-stack)
- [Setup Instructions](#setup-instructions)
- [Running the Server](#running-the-server)
- [Frontend Pages](#frontend-pages)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [Deployment on PythonAnywhere](#deployment-on-pythonanywhere)
- [Project Structure](#project-structure)

---

## Project Overview

SportsPulse is a data-driven web API for the **COMP3011 Web Services and Web Data** module. It follows RESTful architectural principles (Lecture 3) and uses HTTP methods and status codes according to industry conventions (Lecture 2).

The API implements **full CRUD** (Create, Read, Update, Delete) on four data models connected to an SQL database, plus five analytical endpoints that aggregate statistics for meaningful insights.

---

## Technology Stack

| Component        | Choice                       | Rationale                                                                 |
|------------------|------------------------------|---------------------------------------------------------------------------|
| Language         | Python 3.12                  | Taught in module; large ecosystem for web development                     |
| Framework        | Django 5.x                   | Covered in lectures 6-7; robust ORM, admin, and security                  |
| API layer        | Django REST Framework 3.15   | Adds serialisation, authentication, and browsable API on top of Django    |
| Database         | SQLite                       | Ships with Python; sufficient for project scope; SQL-compliant            |
| Authentication   | Token-based (DRF)            | Stateless, aligns with REST constraint #2 (Lecture 3)                     |
| Documentation    | drf-spectacular (OpenAPI 3)  | Auto-generates interactive Swagger UI from code                           |
| Testing          | Django TestCase + DRF client | Built-in; no extra dependencies needed                                    |

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/sportspulse-api.git
cd sportspulse-api

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # On macOS/Linux
# venv\Scripts\activate       # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create an admin superuser (for Django admin panel)
python manage.py createsuperuser

# 6. Seed the database with sample data (optional but recommended)
python manage.py seed_data

# 7. Run the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

---

## Running the Server

```bash
python manage.py runserver
```

Key URLs:
- **API Root**: http://127.0.0.1:8000/api/
- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **ReDoc**: http://127.0.0.1:8000/api/redoc/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Insights Dashboard**: http://127.0.0.1:8000/
- **Fan View (read-only)**: http://127.0.0.1:8000/fan/
- **Admin Portal (CRUD UI)**: http://127.0.0.1:8000/admin-portal/

---

## Frontend Pages

The project now includes three browser UIs in addition to Swagger/ReDoc:

- **Insights Dashboard** (`/`): analytics-focused page with leaderboard, team performance, season summary, and head-to-head comparison.
- **Fan View** (`/fan/`): read-only experience for regular users (team explorer, match feed, player explorer, profile analytics).
- **Admin Portal** (`/admin-portal/`): token-authenticated management UI for create/update/delete operations on teams, players, matches, and statistics.

### Admin Portal auth flow

1. Register or login in the portal (uses `/api/auth/register/` and `/api/auth/login/`).
2. The returned token is stored in browser local storage.
3. Write actions (POST/PATCH/DELETE) are sent with `Authorization: Token ...`.
4. Read actions remain public as per API permission settings.

---

## API Documentation

Interactive API documentation is auto-generated and available at:

- **Swagger UI**: `/api/docs/` — interactive endpoint explorer
- **ReDoc**: `/api/redoc/` — readable reference documentation
- **OpenAPI Schema**: `/api/schema/` — raw JSON schema

A PDF version of the API documentation is included in the repository as `API_Documentation.pdf`.

---

## Authentication

The API uses **Token Authentication**. Read (GET) requests are publicly accessible. Create, update, and delete operations require a valid token.

### Register a new account

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "email": "me@example.com", "password": "mypassword1"}'
```

Response:
```json
{
  "message": "Account created successfully.",
  "user": {"id": 1, "username": "myuser", "email": "me@example.com"},
  "token": "abc123def456..."
}
```

### Log in

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "mypassword1"}'
```

### Use the token

Include the token in the `Authorization` header for authenticated requests:

```bash
curl -H "Authorization: Token abc123def456..." \
  http://127.0.0.1:8000/api/teams/
```

---

## API Endpoints

### CRUD Endpoints

| Method | Endpoint                     | Description                |
|--------|------------------------------|----------------------------|
| GET    | `/api/teams/`                | List all teams             |
| POST   | `/api/teams/`                | Create a team              |
| GET    | `/api/teams/{id}/`           | Retrieve a team            |
| PUT    | `/api/teams/{id}/`           | Update a team (full)       |
| PATCH  | `/api/teams/{id}/`           | Update a team (partial)    |
| DELETE | `/api/teams/{id}/`           | Delete a team              |
| GET    | `/api/teams/{id}/players/`   | List players of a team     |
| GET    | `/api/players/`              | List all players           |
| POST   | `/api/players/`              | Create a player            |
| GET    | `/api/players/{id}/`         | Retrieve a player          |
| PUT    | `/api/players/{id}/`         | Update a player (full)     |
| PATCH  | `/api/players/{id}/`         | Update a player (partial)  |
| DELETE | `/api/players/{id}/`         | Delete a player            |
| GET    | `/api/matches/`              | List all matches           |
| POST   | `/api/matches/`              | Create a match             |
| GET    | `/api/matches/{id}/`         | Retrieve a match           |
| PUT    | `/api/matches/{id}/`         | Update a match (full)      |
| PATCH  | `/api/matches/{id}/`         | Update a match (partial)   |
| DELETE | `/api/matches/{id}/`         | Delete a match             |
| GET    | `/api/statistics/`           | List all statistics        |
| POST   | `/api/statistics/`           | Create a statistic         |
| GET    | `/api/statistics/{id}/`      | Retrieve a statistic       |
| PUT    | `/api/statistics/{id}/`      | Update a statistic (full)  |
| PATCH  | `/api/statistics/{id}/`      | Update a statistic (partial)|
| DELETE | `/api/statistics/{id}/`      | Delete a statistic         |

### Analytics Endpoints

| Method | Endpoint                              | Description                         |
|--------|---------------------------------------|-------------------------------------|
| GET    | `/api/analytics/leaderboard/`         | Top scorers / assisters             |
| GET    | `/api/analytics/team-performance/`    | League standings with points        |
| GET    | `/api/analytics/head-to-head/`        | Head-to-head record between teams   |
| GET    | `/api/analytics/season-summary/`      | Season-wide aggregated stats        |
| GET    | `/api/analytics/player-profile/{id}/` | Full career profile for a player    |

### Query Parameters

Most list endpoints support filtering:

```
GET /api/teams/?country=England&search=arsenal
GET /api/players/?team=1&position=FW&search=saka
GET /api/matches/?team=1&season=2024/2025&status=COMPLETED
GET /api/statistics/?player=1&match=5
GET /api/analytics/leaderboard/?metric=assists&season=2024/2025&limit=5
GET /api/analytics/head-to-head/?team1=1&team2=2
```

---

## Running Tests

```bash
python manage.py test api
```

The test suite includes 50+ tests covering:
- Model creation and constraints
- Authentication (register, login, invalid credentials)
- Full CRUD on all four resources
- Query parameter filtering
- All five analytics endpoints
- HTTP status code correctness (200, 201, 204, 400, 401, 404)

---

## Deployment on PythonAnywhere

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com/)
2. Open a Bash console and clone your repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/sportspulse-api.git
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   cd sportspulse-api
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run migrations and seed data:
   ```bash
   python manage.py migrate
   python manage.py seed_data
   python manage.py createsuperuser
   ```
5. Go to **Web** tab → **Add a new web app** → **Manual configuration** → **Python 3.12**
6. Set the **Source code** path to `/home/YOUR_USERNAME/sportspulse-api`
7. Set the **Virtualenv** path to `/home/YOUR_USERNAME/sportspulse-api/venv`
8. Edit the **WSGI configuration file** and replace its contents with:
   ```python
   import os
   import sys
   path = '/home/YOUR_USERNAME/sportspulse-api'
   if path not in sys.path:
       sys.path.insert(0, path)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'sportspulse.settings'
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
9. Add your PythonAnywhere domain to `ALLOWED_HOSTS` in `settings.py` (already included as `'.pythonanywhere.com'`)
10. Click **Reload** on the Web tab
11. Collect static files:
    ```bash
    python manage.py collectstatic
    ```
12. Set the static files mapping on the Web tab:
    - URL: `/static/` → Directory: `/home/YOUR_USERNAME/sportspulse-api/staticfiles`

---

## Project Structure

```
sportspulse-api/
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                 # Git ignore rules
├── db.sqlite3                 # SQLite database (generated)
├── sportspulse/               # Django project configuration
│   ├── settings.py            # Settings (DRF, auth, DB config)
│   ├── urls.py                # Root URL routing
│   ├── wsgi.py                # WSGI entry point
│   └── asgi.py                # ASGI entry point
└── api/                       # Main application
    ├── models.py              # Data models (Team, Player, Match, Stat)
    ├── serializers.py         # DRF serializers for JSON conversion
    ├── views.py               # ViewSets (CRUD) + APIViews (analytics)
    ├── urls.py                # API URL routing
    ├── admin.py               # Admin site registration
    ├── tests.py               # Test suite (50+ tests)
    └── management/
        └── commands/
            └── seed_data.py   # Database seeding command
```

---

## Licence

This project is submitted as coursework for COMP3011 at the University of Leeds.
