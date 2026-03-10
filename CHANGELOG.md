# Changelog

All notable changes to SportsPulse are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] - 2026-03-13

### Added
- Full CRUD REST API for Teams, Players, Matches, and PlayerMatchStatistics
- Five analytics endpoints: leaderboard, team-performance, head-to-head, season-summary, player-profile
- Token-based authentication with register/login endpoints
- Rate limiting (anonymous: 100/hr, authenticated: 500/hr)
- Layered input validation with domain-specific rules
- 79 automated tests covering models, auth, CRUD, filtering, analytics, and status codes
- Swagger UI (`/api/docs/`) and ReDoc (`/api/redoc/`) interactive documentation via drf-spectacular
- Three HTML frontend pages: Dashboard, Fan Portal, Admin Portal
- PythonAnywhere deployment with static file serving and environment-based secrets
- GitHub Actions CI workflow for automated test runs on push/PR
- Comprehensive API documentation (PDF) with cURL examples

### Technical Decisions
- Django + DRF chosen over FastAPI for module alignment and ecosystem maturity
- SQLite retained for zero-config local/PythonAnywhere compatibility; PostgreSQL recommended for production
- Service layer (`api/services.py`) separates analytics business logic from views
- Token auth preferred over JWT for simplicity; aligns with REST stateless constraint

---

## [0.3.0] - 2026-03-08

### Added
- Admin Portal HTML template with full CRUD forms and token-based login
- Dashboard HTML with KPI cards, standings table, and head-to-head comparison widget
- Fan Portal HTML for read-only public browsing

---

## [0.2.0] - 2026-03-07

### Added
- Analytics endpoints: leaderboard, team-performance, head-to-head, season-summary, player-profile
- Rate limiting via DRF throttling classes
- Query parameter validation for analytics views
- Seed data management command (`python manage.py seed_data`)

### Fixed
- Team-performance endpoint N+1 query issue — refactored to use `aggregate()` and `F()` expressions

---

## [0.1.0] - 2026-03-06

### Added
- Initial Django project setup with DRF
- Models: Team, Player, Match, PlayerMatchStatistic with UniqueConstraints
- CRUD ViewSets for all four resources
- Token authentication (register/login endpoints)
- Serialisers with nested representations
- 79 tests with shared BaseTestCase fixture
- drf-spectacular integration for OpenAPI schema generation
- PythonAnywhere deployment configuration
