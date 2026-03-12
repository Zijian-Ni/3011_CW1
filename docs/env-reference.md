# Environment Variables Reference

SportsPulse uses environment variables to keep sensitive configuration out of source control.
All variables below should be set in your deployment environment (e.g., `.env` file, PythonAnywhere config, or CI secrets).

---

## Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key for cryptographic signing | `django-insecure-...` |
| `DEBUG` | Enable debug mode (`True` / `False`) | `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | `yourusername.pythonanywhere.com` |
| `DATABASE_URL` | Database connection string (optional; defaults to SQLite) | `postgres://user:pass@host/db` |

## Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ALLOWED_ORIGINS` | Origins permitted for cross-origin requests | Not set |
| `STATIC_ROOT` | Absolute path to collected static files | `staticfiles/` |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |
| `TOKEN_EXPIRY_HOURS` | Hours before auth tokens expire | `24` |

---

## Loading Variables Locally

Use a `.env` file with [python-dotenv](https://pypi.org/project/python-dotenv/) or export directly in your shell:

```bash
export SECRET_KEY="your-secret-key-here"
export DEBUG="False"
export ALLOWED_HOSTS="localhost,127.0.0.1"
```

> **Never commit `.env` to version control.** It is listed in `.gitignore`.
