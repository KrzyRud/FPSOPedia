# Architectural Patterns

## Application Factory (flat, no `create_app`)

`App/__init__.py:1-32` — The app is created at module level (not wrapped in a factory function). Extensions are initialized directly on the `app` object. Modules are imported at the **end** of `__init__.py` (after `app` and extensions exist) to avoid circular imports:

```
app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
...
from App import routes, models, forms, errors   # bottom of file
```

**Impact:** There is no `create_app()` function. Tests or CLI tools that need a custom config must patch `config.py` before importing `App`.

---

## Model-View-Template Layout

No blueprints. All three concerns are flat files under `App/`:

- **Models** — `App/models.py` (User, Fpso, Remark, Post, `favorite` association table)
- **Views** — `App/routes.py` (single file, 28+ endpoints)
- **Templates** — `App/templates/` (~25 HTML files + partials)

---

## Template Inheritance

Every page template starts with:
```jinja2
{% extends "base.html" %}
{% set active_page = '<name>' %}
```

`App/templates/base.html` includes two partials:
- `_navbar.html` — uses `active_page` variable to set Bootstrap `active` class
- `_footer.html`

Partial templates (`_navbar.html`, `_footer.html`, `_fpso.html`) are prefixed with `_`.

---

## Flash Messaging

Routes use `flash("message")` (`App/routes.py` throughout) and all pages inherit the flash block from `base.html`. The pattern appears in `index.html:5-27`:

```jinja2
{% with messages = get_flashed_messages() %}
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-success alert-dismissible ...">
```

Flash messages are the only mechanism for user feedback after form submissions and redirects.

---

## Form Validation (WTForms)

`App/forms.py` — All forms extend `FlaskForm`. Pattern:

1. Field-level validators declared inline (`DataRequired()`, `Email()`, `EqualTo()`, `Length()`).
2. Custom cross-field validation uses `validate_<fieldname>(self, field)` methods — see `RegisterForm:30-38` for duplicate username/email checks against the DB.
3. CSRF protection is automatic from `FlaskForm`.

Route handler pattern (`App/routes.py`):
```python
form = SomeForm()
if form.validate_on_submit():
    # process
    return redirect(...)
return render_template('page.html', form=form)
```

---

## Authentication & Authorization

**Session management** — Flask-Login via `@login_required` decorator and `current_user` proxy.

**User loader** — `App/models.py:12-14`:
```python
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
```

**Password hashing** — `App/models.py:52-56`: `set_password()` / `check_password()` via Werkzeug.

**Password reset** — Stateless JWT tokens (`App/models.py:64-80`). Token expires after 600 s. Generated with `PyJWT`, verified in `verify_reset_password_token()`.

**Admin check** — `App/routes.py:93`: string equality `admin = "Admin"`. Not a role system; based purely on `current_user.username`.

**Login redirect** — Standard `next` query-param pattern (`App/routes.py:397`).

---

## Database Session Management

Flask-SQLAlchemy provides a request-scoped session. The consistent pattern throughout `App/routes.py`:

```python
db.session.add(obj)
db.session.commit()
```

On 500 errors, `App/errors.py:12` issues `db.session.rollback()` before rendering the error page to prevent a broken transaction from leaking into the next request.

No explicit `db.session.remove()` calls — Flask-SQLAlchemy tears down the session automatically at request end.

---

## Data Models & Relationships

`App/models.py` — Four models:

| Model | Key unique constraints | Relationships |
|-------|----------------------|---------------|
| `User` | `username`, `user_email` | M:M Fpso (favorites), 1:M Post |
| `Fpso` | `fpso_name` | 1:M Remark |
| `Remark` | — | M:1 Fpso |
| `Post` | — | M:1 User |

Many-to-many join table `favorite` (`App/models.py:17-20`): columns `user_id`, `fpso_id`.

---

## Email (Async SendGrid)

`App/email.py` — Email is sent in a background thread to avoid blocking the request:

```python
Thread(target=send_async_email, args=(app, msg)).start()
```

`send_async_email` pushes an app context manually because the thread does not inherit Flask's request context. Configuration is in `config.py:14-26` (SendGrid SMTP, SSL port 465).

---

## File Downloads

`App/routes.py:533-538` — Files are served from `App/static/downloads/` using Flask's `send_from_directory`. The download root path is set in `config.py:29` (`DOWNLOAD_FOLDER`).

---

## Search

`App/routes.py:30` — Case-insensitive LIKE query on `Fpso.fpso_name`:
```python
Fpso.query.filter(Fpso.fpso_name.like(f"%{fpso}%"))
```

No full-text search engine; limited to name substring matching.
