# Troubleshooting Guide

Common issues when running or deploying SportsPulse, with solutions.

---

## Local Development

### `ModuleNotFoundError: No module named 'rest_framework'`

The virtual environment is not activated, or dependencies were not installed.

```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

### `django.db.utils.OperationalError: no such table`

Migrations have not been applied.

```bash
python manage.py migrate
```

---

### `401 Unauthorized` on write endpoints

You must include a valid token in the `Authorization` header:

```bash
curl -X POST http://127.0.0.1:8000/api/teams/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name": "Arsenal", "short_name": "ARS", "country": "England"}'
```

Obtain a token via `POST /api/auth/login/` or `POST /api/auth/register/`.

---

### `400 Bad Request` on analytics endpoints

Check that query parameters are correctly formatted:

| Parameter | Valid format | Example |
|-----------|-------------|---------|
| `season` | `YYYY/YYYY` (sequential years) | `2024/2025` |
| `metric` | `goals` or `assists` only | `goals` |
| `limit` | Integer 1–50 | `10` |

---

### `429 Too Many Requests`

You have exceeded the rate limit. Wait and retry. The `Retry-After` header indicates how many seconds to wait.

Limits: anonymous 100/hr, authenticated 500/hr, register 5/hr, login 20/hr.

---

## PythonAnywhere Deployment

### `DisallowedHost at /`

Your `ALLOWED_HOSTS` setting does not include the deployment domain. Fix in `sportspulse/settings.py`:

```python
ALLOWED_HOSTS = ['.pythonanywhere.com', 'localhost', '127.0.0.1']
```

Then reload the web app.

---

### `ImproperlyConfigured: The SECRET_KEY setting must not be empty`

The environment variable is not being passed through the WSGI file. Add to your WSGI configuration:

```python
os.environ['SECRET_KEY'] = 'your-actual-secret-key'
```

---

### Static files returning 404

1. Run `python manage.py collectstatic --noinput`
2. Confirm the static file mapping in the PythonAnywhere Web tab points to `/home/yourusername/sportspulse/staticfiles/`
3. Reload the web app

---

### `ImproperlyConfigured` with mixed paths

Ensure there are no `./` or double slashes in your WSGI file path:

```python
# Correct
path = '/home/yourusername/sportspulse'

# Wrong — will cause errors
path = '/home/yourusername/sportspulse/./api'
```

---

### Changes not reflecting after git pull

You must reload the PythonAnywhere web app after every code change:

1. Go to the **Web** tab
2. Click the green **Reload** button

---

## Testing

### Tests fail with `django.test.utils.DatabaseBlockedByRouter`

Ensure you are using the standard test runner with no custom database routers enabled.

### Test fixture errors

The shared `BaseTestCase` in `api/tests.py` creates two teams, players, one completed match, and statistics. If you have modified models without updating the fixture, run:

```bash
python manage.py migrate
python manage.py test api --verbosity=2
```

---

## Still Stuck?

Open an issue on GitHub: https://github.com/Zijian-Ni/3011_CW1/issues
