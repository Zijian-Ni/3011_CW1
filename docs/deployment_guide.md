# Deployment Guide

This guide walks through deploying SportsPulse to PythonAnywhere (free tier).

---

## Prerequisites

- A free PythonAnywhere account at [pythonanywhere.com](https://www.pythonanywhere.com)
- Your GitHub repository (public)

---

## Step 1: Clone the Repository

Open a PythonAnywhere Bash console and run:

```bash
git clone https://github.com/Zijian-Ni/3011_CW1.git sportspulse
cd sportspulse
```

---

## Step 2: Create a Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 3: Configure Environment Variables

Create a `.env` file (never commit this):

```bash
echo "SECRET_KEY=your-long-random-secret-key-here" > .env
echo "DEBUG=False" >> .env
echo "ALLOWED_HOSTS=yourusername.pythonanywhere.com" >> .env
```

Or set them directly in the WSGI file (see Step 5).

---

## Step 4: Set Up the Database

```bash
python manage.py migrate
python manage.py seed_data      # optional: loads sample data
python manage.py collectstatic --noinput
```

---

## Step 5: Configure the WSGI File

In the PythonAnywhere Web tab, set the WSGI file path to:

```
/home/yourusername/sportspulse/sportspulse/wsgi.py
```

Edit the WSGI file and replace its contents with:

```python
import os
import sys

path = '/home/yourusername/sportspulse'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'sportspulse.settings'
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['DEBUG'] = 'False'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

> **Important:** Use the absolute path without trailing slashes or `.` segments.

---

## Step 6: Configure Static Files

In the PythonAnywhere Web tab, add a static file mapping:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/sportspulse/staticfiles/` |

---

## Step 7: Update ALLOWED_HOSTS

In `sportspulse/settings.py`, confirm:

```python
ALLOWED_HOSTS = ['.pythonanywhere.com', 'localhost', '127.0.0.1']
```

---

## Step 8: Reload the Web App

Click **Reload** in the PythonAnywhere Web tab. Your API should now be live at:

```
https://yourusername.pythonanywhere.com/api/
```

---

## Updating the Deployment

To pull the latest changes:

```bash
cd ~/sportspulse
source venv/bin/activate
git pull origin main
python manage.py migrate --noinput
python manage.py collectstatic --noinput
# Then reload in the Web tab
```

---

## Troubleshooting

See [docs/troubleshooting.md](troubleshooting.md) for common deployment issues.
