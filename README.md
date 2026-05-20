# User Profile Card Generator

A simple Flask application that accepts user data via a form and renders a formatted profile card on the frontend.

## Features

- GET and POST routing with Flask
- Form fields for name, bio, and image URL
- Conditional card rendering after submission
- Tailwind CSS layout for the profile card
- Secure login route with rate limiting
- Environment variable configuration and input validation

## Setup

1. Create a Python virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file from the example and set secret values:

```powershell
copy .env.example .env
```

4. Run the app:

```powershell
python app.py
```

5. Open `http://127.0.0.1:5000` in your browser.

## Security notes

- Login credentials are read from environment variables, not committed to source control.
- A `5 per 15 minutes` rate limit is applied to the `/login` endpoint.
- User inputs for the profile card are validated and sanitized.
- Static files, virtual environments, and secret files are excluded via `.gitignore`.

## Environment variables

- `FLASK_SECRET_KEY`: secret key for Flask sessions
- `FLASK_ENV`: set to `production` in production environments
- `LOGIN_USER`: allowed login username
- `LOGIN_PASSWORD`: allowed login password
- `FLASK_DEBUG`: set to `true` for local debug mode only
