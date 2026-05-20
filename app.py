import html
import os
import secrets
import string
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask, abort, render_template, request

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV', '').lower() == 'production'

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['200 per day', '50 per hour'],
    storage_uri='memory://',
)

LOGIN_USER = os.getenv('LOGIN_USER')
LOGIN_PASSWORD = os.getenv('LOGIN_PASSWORD')
LOGIN_ENABLED = bool(LOGIN_USER and LOGIN_PASSWORD)
MAX_NAME_LENGTH = 100
MAX_BIO_LENGTH = 500
MAX_URL_LENGTH = 2048
MAX_LOGIN_LENGTH = 50


def is_safe_text(value: str, max_length: int) -> bool:
    if not value or len(value) > max_length:
        return False
    if any(ch in value for ch in '<>'):
        return False
    return True


def is_valid_url(value: str) -> bool:
    if not value or len(value) > MAX_URL_LENGTH:
        return False

    parsed = urlparse(value)
    if parsed.scheme not in ('https', 'http') or not parsed.netloc:
        return False

    if any(ch in value for ch in '<>"\''):
        return False

    return True


def sanitize_text(value: str) -> str:
    return html.escape(value.strip())


def validate_profile_input(name: str, bio: str, image_url: str) -> dict:
    if not is_safe_text(name, MAX_NAME_LENGTH):
        abort(400, 'Invalid name provided')
    if not is_safe_text(bio, MAX_BIO_LENGTH):
        abort(400, 'Invalid bio provided')
    if image_url and not is_valid_url(image_url):
        abort(400, 'Invalid image URL provided')

    return {
        'name': sanitize_text(name),
        'bio': sanitize_text(bio),
        'image_url': image_url.strip(),
    }


@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Permissions-Policy'] = 'interest-cohort=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; img-src 'self' https: data:; "
        "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "script-src 'self' https://cdn.tailwindcss.com;"
    )
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    profile = None

    if request.method == 'POST':
        profile = validate_profile_input(
            request.form.get('name', ''),
            request.form.get('bio', ''),
            request.form.get('image_url', ''),
        )

    return render_template('index.html', profile=profile)


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per 15 minutes')
def login():
    error = None
    success = False

    if request.method == 'POST':
        if not LOGIN_ENABLED:
            abort(503, 'Login is not configured. Set LOGIN_USER and LOGIN_PASSWORD in environment variables.')

        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if not is_safe_text(username, MAX_LOGIN_LENGTH) or not is_safe_text(password, MAX_LOGIN_LENGTH):
            abort(400, 'Malformed login input')

        if secrets.compare_digest(username, LOGIN_USER) and secrets.compare_digest(password, LOGIN_PASSWORD):
            success = True
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error, success=success)


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
