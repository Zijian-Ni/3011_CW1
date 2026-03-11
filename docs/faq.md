# Frequently Asked Questions

## General

**Q: What is SportsPulse?**
A: SportsPulse is a RESTful web service for sports fixture tracking and match predictions, built with Django REST Framework.

**Q: Where is the live demo?**
A: https://zijianni.pythonanywhere.com — Swagger UI available at `/api/docs/`

## Development

**Q: How do I run the project locally?**
A: Clone the repo, install dependencies with `pip install -r requirements.txt`, run `python manage.py migrate`, then `python manage.py runserver`.

**Q: Why is my login returning 401?**
A: Make sure you're passing the token as `Authorization: Token <your_token>` in the header.

**Q: How do I reset the database?**
A: Delete `db.sqlite3` and run `python manage.py migrate` again. Use `createsuperuser` to recreate the admin account.

## Deployment

**Q: How do I deploy to PythonAnywhere?**
A: See `docs/deployment.md` for the full step-by-step guide.

**Q: Why are static files not loading in production?**
A: Run `python manage.py collectstatic` and ensure `STATIC_ROOT` is configured in your WSGI settings.
