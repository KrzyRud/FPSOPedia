# FPSOpedia

FPSO (Floating Production Storage and Offloading) vessel encyclopedia for the maritime/oil & gas industry. Users can browse, search, and manage detailed technical profiles for FPSO units — including cargo specs, positioning systems, communication channels, and operational data.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | Flask 2.1.2 |
| ORM / DB | SQLAlchemy 1.4.39 + SQLite (`app.db`) |
| Migrations | Flask-Migrate 3.1.0 (Alembic) |
| Authentication | Flask-Login 0.6.1 + PyJWT 2.4.0 |
| Forms | Flask-WTF 1.0.1 + WTForms 3.0.1 |
| Email | Flask-Mail-SendGrid 0.3 |
| Frontend | Bootstrap 5.3.8 (CDN) + Jinja2 |
| WSGI (prod) | Gunicorn 20.1.0 |

## Key Directories

```
App/
├── __init__.py      # App factory — extensions init, module imports
├── models.py        # User, Fpso, Remark, Post models + DB relationships
├── routes.py        # All 28+ route handlers (single file, no blueprints)
├── forms.py         # WTForms definitions (login, register, FPSO detail, etc.)
├── email.py         # Async SendGrid email helpers
├── errors.py        # Custom 404/500 handlers
├── static/          # CSS, images, downloadable files
└── templates/       # Jinja2 HTML templates (base.html + ~25 pages)
migrations/          # Alembic version files (8 migrations to date)
config.py            # Flask config class — reads from env vars
fpsopedia.py         # Entry point: imports and exposes `app`
passenger_wsgi.py    # Passenger WSGI adapter (hosting)
```

## Build & Run

**Development:**
```bash
flask run                    # uses .flaskenv (FLASK_APP=App, FLASK_DEBUG=1)
```

**Database migrations:**
```bash
flask db migrate -m "description"   # generate migration from model changes
flask db upgrade                    # apply pending migrations
```

**Production:**
```bash
gunicorn fpsopedia:app              # Procfile target
```

**Dependencies:**
```bash
pip install -r requirements.txt
```

## Key Conventions

- **Entry point:** `fpsopedia.py:1` — imports `app` from `App`
- **Config:** `config.py:1` — `SECRET_KEY` and DB URL must come from env in production; fallback values are dev-only
- **Admin check:** `App/routes.py:93` — hardcoded `username == "Admin"` string, not a role system
- **No tests** — no `tests/` directory exists; manual verification only
- **No blueprints** — all routes live in `App/routes.py`

## Additional Documentation

| File | When to consult |
|------|----------------|
| [.claude/docs/architectural_patterns.md](.claude/docs/architectural_patterns.md) | App factory setup, auth flow, form validation, DB session handling, template inheritance, flash messaging |
