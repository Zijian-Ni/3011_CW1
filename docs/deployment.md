
## Security Checklist

Before going live, verify the following:

- [ ] `DEBUG = False` in production settings
- [ ] `SECRET_KEY` is set via environment variable, not hardcoded
- [ ] `ALLOWED_HOSTS` only contains your actual domain
- [ ] HTTPS is enforced (PythonAnywhere provides this by default)
- [ ] Admin panel URL changed from default `/admin/` if sensitive
