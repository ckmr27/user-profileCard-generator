import html
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask, abort, render_template, request

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV', '').lower() == 'production'

MAX_NAME_LENGTH = 100
MAX_BIO_LENGTH = 500
MAX_URL_LENGTH = 2048


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


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
