# Contributing to SportsPulse

Thank you for your interest in SportsPulse! This document describes how to set up a development environment, run tests, and submit changes.

> **Note:** This is a university coursework project. External contributions are welcome for learning purposes but are not merged into the main submission branch.

---

## Prerequisites

- Python 3.10 or higher
- `pip` and `venv`
- Git

---

## Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/Zijian-Ni/3011_CW1.git
cd 3011_CW1

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Seed sample data (optional but recommended)
python manage.py seed_data

# 6. Run the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/` and Swagger UI at `http://127.0.0.1:8000/api/docs/`.

---

## Running Tests

```bash
# Run the full test suite
python manage.py test api

# Run with verbosity for detailed output
python manage.py test api --verbosity=2

# Run a specific test class
python manage.py test api.tests.TeamAPITests
```

All 79 tests should pass before submitting a pull request.

---

## Code Style

- Follow PEP 8 conventions.
- Use descriptive variable and function names.
- Add docstrings to all view classes and service functions.
- Keep views thin — complex logic belongs in `api/services.py`.

---

## Commit Message Convention

Use the imperative mood and a concise summary line:

```
Add player career statistics endpoint

- Implement PlayerProfileService in api/services.py
- Add /api/analytics/player-profile/{id}/ view
- Add 5 test cases covering career totals and by-season breakdown
```

Avoid commit messages like `fix stuff`, `update`, or `WIP`.

---

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable, submission-ready code |
| `feature/<name>` | New feature development |
| `fix/<name>` | Bug fixes |
| `docs/<name>` | Documentation-only changes |

---

## Reporting Issues

Use the GitHub Issue templates provided in `.github/ISSUE_TEMPLATE/`. Include:
- Steps to reproduce
- Expected vs actual behaviour
- Python and Django version

---

## Questions

Open a Discussion on GitHub or contact via the repository's issue tracker.
