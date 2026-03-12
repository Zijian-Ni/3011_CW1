
## Security Checklist

Before going live, verify the following:

- [ ] `DEBUG = False` in production settings
- [ ] `SECRET_KEY` is set via environment variable, not hardcoded
- [ ] `ALLOWED_HOSTS` only contains your actual domain
- [ ] HTTPS is enforced (PythonAnywhere provides this by default)
- [ ] Admin panel URL changed from default `/admin/` if sensitive

---

## Performance & Production Tuning

### Database

- Use PostgreSQL in production for better concurrency and indexing support
- Enable connection pooling (e.g., `pgbouncer`) for high-traffic deployments
- Add `db_index=True` on frequently-filtered fields such as `Player.team`, `Match.date`

### Caching

- Django's `cache_page` decorator can be applied to read-heavy analytics endpoints
- Recommended: Redis as the cache backend for session and query caching
- Example: `@cache_page(60 * 15)` caches an endpoint for 15 minutes

### Rate Limiting

- Default limits are conservative (100/hr anonymous, 500/hr authenticated)
- Adjust in `settings.py` under `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES`
- Consider per-view overrides using DRF's `throttle_classes`

### Static Files

- Run `python manage.py collectstatic` before each deployment
- For PythonAnywhere: static files are served from `/static/` via the WSGI config
