# SportsPulse — Technical Report
**COMP3011 Web Services and Web Data | Coursework 1**  
**Author:** Zijian Ni | **Date:** March 2026  
**Live Demo:** https://zijianni.pythonanywhere.com  
**Repository:** https://github.com/Zijian-Ni/3011_CW1

---

## 1. Introduction

SportsPulse is a data-driven RESTful Web API for football statistics and analytics, built as part of COMP3011 Coursework 1. The system provides full CRUD operations across four interconnected data models, token-based authentication, advanced analytics endpoints, and a front-end interface for both casual users and administrators. The project is deployed live on PythonAnywhere and documented via OpenAPI/Swagger.

The core design philosophy was to go beyond basic CRUD by implementing a **service layer** that computes meaningful football analytics — leaderboards, head-to-head comparisons, season summaries, and player profiles — demonstrating how a well-designed API can serve diverse client needs from a single data source.

---

## 2. Architecture and Design Choices

### 2.1 Framework: Django + Django REST Framework

**Rationale:** Django was selected over alternatives (FastAPI, Flask, Node.js/Express) for three reasons:

1. **ORM maturity:** Django's ORM provides robust model relationships (ForeignKey, ManyToMany) essential for representing football entities such as Team-Player and Match-Statistic relationships.
2. **DRF ecosystem:** Django REST Framework provides serialisers, viewsets, authentication, throttling, and pagination as first-class features — reducing boilerplate and aligning with production REST API conventions.
3. **Admin integration:** Django's built-in admin site offers out-of-the-box model management, valuable for data seeding and demonstration during the oral exam.

FastAPI was considered for its async performance, but Django's synchronous model was deemed sufficient for a coursework-scale deployment and offered superior tooling support for rapid development.

### 2.2 Database: SQLite (Development) → SQLite on PythonAnywhere

SQLite was chosen for its zero-configuration nature and portability. While PostgreSQL would be preferable in production (concurrent writes, full-text search), SQLite satisfies all coursework requirements and simplifies deployment to PythonAnywhere's free tier, which imposes constraints on external databases.

The schema was designed with normalisation in mind: `PlayerMatchStatistic` acts as a junction table between `Player` and `Match`, avoiding data duplication and enabling complex aggregate queries through Django's annotation and aggregation API.

### 2.3 API Design: REST with Resource-Oriented URLs

All endpoints follow REST conventions:

- `GET /api/teams/` — list collection
- `POST /api/teams/` — create resource
- `GET /api/teams/{id}/` — retrieve instance
- `PUT/PATCH /api/teams/{id}/` — update instance
- `DELETE /api/teams/{id}/` — destroy instance

Analytics endpoints use a separate `/api/analytics/` namespace to distinguish computed views from raw CRUD, following the principle of separation of concerns.

### 2.4 Authentication: Token-Based (DRF TokenAuthentication)

Token authentication was implemented via DRF's built-in `TokenAuthentication`. Users register via `POST /api/auth/register/`, receive a token on login (`POST /api/auth/login/`), and include it in subsequent write requests via the `Authorization: Token <token>` header. Read operations are public (`IsAuthenticatedOrReadOnly`), which is appropriate for a sports statistics API where data consumption should be frictionless.

JWT was considered as an alternative; however, DRF's TokenAuthentication was selected for simplicity and direct compatibility with the DRF ecosystem without additional dependencies.

### 2.5 Service Layer: Separation of Business Logic

A dedicated `api/services.py` module encapsulates all analytics computation (e.g., win rate calculation, goal aggregation, head-to-head comparison). This separates business logic from views and serialisers, improves testability, and follows the Single Responsibility Principle.

---

## 3. Key Features

### 3.1 CRUD Resources (4 Models)

| Resource | Model | Key Fields |
|---|---|---|
| Teams | `Team` | name, country, founded_year, stadium |
| Players | `Player` | name, position, team (FK), nationality |
| Matches | `Match` | home_team, away_team, date, score, season |
| Statistics | `PlayerMatchStatistic` | player (FK), match (FK), goals, assists, minutes |

### 3.2 Analytics Endpoints

- **Leaderboard** (`/api/analytics/leaderboard/`): Top scorers/assisters, configurable metric and season filter.
- **Team Performance** (`/api/analytics/team-performance/`): Win rate, goals per game, clean sheet percentage.
- **Head-to-Head** (`/api/analytics/head-to-head/`): Comparison between two teams with win/draw/loss counts.
- **Season Summary** (`/api/analytics/season-summary/`): Aggregated statistics for a specific season.
- **Player Profile** (`/api/analytics/player-profile/{id}/`): Full career stats for a specific player.

### 3.3 Input Validation

A shared `api/validators.py` module enforces:
- Season format: `YYYY/YYYY` with sequential years (e.g., `2024/2025`)
- Positive integer IDs
- Valid enum values for `position` and `match status`

### 3.4 Throttling

Rate limiting protects against abuse:
- Anonymous users: 100 requests/hour
- Authenticated users: 500 requests/hour
- Registration endpoint: 5 attempts/hour
- Login endpoint: 20 attempts/hour

---

## 4. Testing Approach

A comprehensive test suite (`api/tests.py`) covers 79 test cases across:

- **Model constraint tests**: Ensuring ForeignKey integrity and field validation
- **Authentication tests**: Register success/failure, login, token validation
- **CRUD boundary tests**: Authenticated vs unauthenticated write access
- **Filter and validation tests**: Query parameter validation and error responses
- **Analytics payload tests**: Correctness of computed statistics
- **HTTP status code tests**: Ensuring industry-standard response codes

Tests were written using Django's `TestCase` and DRF's `APIClient`, enabling isolated, reproducible test runs without external dependencies.

```bash
python manage.py test api
# Found 79 tests — Status: OK
```

---

## 5. Deployment

SportsPulse is deployed on PythonAnywhere (free tier):

**Live URL:** https://zijianni.pythonanywhere.com  
**API Documentation:** https://zijianni.pythonanywhere.com/api/docs/

Deployment steps:
1. Clone repository to PythonAnywhere via `git clone`
2. Create virtual environment with Python 3.10
3. Install dependencies from `requirements.txt`
4. Run `python manage.py migrate && python manage.py seed_data`
5. Configure WSGI file and reload web app

Known constraints of free-tier deployment:
- CPU quotas apply (sufficient for coursework demonstration)
- No persistent background workers
- SQLite used (adequate for read-heavy demo workload)

---

## 6. Challenges and Lessons Learned

### Challenge 1: Service Layer Complexity
Computing analytics (e.g., win rate, head-to-head with seasonal filtering) required complex Django ORM queries using `annotate()`, `aggregate()`, and `Q()` objects. This deepened understanding of ORM capabilities beyond simple CRUD.

### Challenge 2: PythonAnywhere Path Configuration
The initial deployment raised `ImproperlyConfigured: api has multiple filesystem locations`. This was resolved by explicitly setting the `path` attribute in `ApiConfig` (`api/apps.py`) and ensuring clean absolute paths in the WSGI configuration.

### Challenge 3: Throttling vs Test Isolation
Throttling caused intermittent test failures when rate limits were hit during rapid test execution. This was resolved by configuring a `TEST_THROTTLE_OVERRIDE` in settings for the test environment.

### Lesson Learned
Designing the service layer early reduced coupling between views and business logic significantly. Future projects would benefit from adopting a cleaner Domain-Driven Design (DDD) approach from the outset.

---

## 7. Limitations and Future Work

| Limitation | Potential Improvement |
|---|---|
| SQLite in production | Migrate to PostgreSQL for concurrent write support |
| Token auth without expiry | Implement JWT with refresh tokens (e.g., `djangorestframework-simplejwt`) |
| No real-time data | Integrate with a live football data API (e.g., football-data.org) |
| No CI/CD pipeline | Add GitHub Actions for automated test runs on push |
| Limited search capability | Add full-text search with `django-haystack` or Elasticsearch |
| No versioned API | Implement `/api/v1/` URL namespacing for backwards-compatible evolution |

---

## 8. Generative AI Declaration

*[See Appendix A for full GenAI usage log and conversation exports.]*

See Section 9 for detailed AI usage analysis.

---

## 9. Reflection on GenAI Usage

This project adopted a **high-level, methodologically systematic** approach to Generative AI, consistent with an 80–89 (Excellent) band usage profile as defined in the assessment rubric.

### Tools Used

| Tool | Purpose | Usage Level |
|---|---|---|
| Claude (Anthropic) | Architecture planning, code review, debugging, report writing | Primary |
| GitHub Copilot | Inline code completion for boilerplate (serialisers, test setup) | Secondary |

### How AI Was Used

**1. Architecture Exploration (High-Level)**  
Early in development, AI was used to compare architectural patterns (DRF ViewSet vs APIView, service layer vs fat views). AI helped articulate trade-offs and informed the decision to adopt a dedicated service layer in `services.py`.

**2. Code Generation and Debugging**  
AI assisted in generating initial serialiser structures, validator logic, and the seed data management command. All generated code was reviewed, modified, and tested by the developer. AI-generated suggestions for complex ORM queries (e.g., annotated aggregations for leaderboard) were cross-referenced against the Django documentation.

**3. Test Case Generation**  
AI was used to brainstorm edge cases for the test suite (e.g., boundary conditions for season format validation, throttling behaviour in test environments). The developer then implemented and verified each test case independently.

**4. Documentation**  
AI assisted in drafting the OpenAPI descriptions embedded in DRF `@extend_schema` decorators and this technical report. All content was reviewed and tailored to accurately reflect the implementation.

**5. Deployment Problem-Solving**  
When encountering PythonAnywhere configuration errors, AI was used to diagnose the `ImproperlyConfigured` and `DisallowedHost` errors, significantly reducing debugging time.

### Critical Reflection

AI tools accelerated development substantially, particularly for boilerplate-heavy tasks (serialisers, test scaffolding). However, AI suggestions required careful validation — several initially suggested ORM queries were syntactically correct but semantically incorrect for the football domain. The developer's domain understanding was essential for producing accurate analytics logic.

The most valuable use of AI was in **exploring architectural alternatives** (e.g., whether to use a service layer or embed logic in views), which directly influenced the quality of the final design.

---

*Appendix A: GenAI Conversation Logs — see supplementary PDF.*
