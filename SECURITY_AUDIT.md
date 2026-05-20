# Security Audit Summary

## Findings

- Bandit scan executed against `app.py` found no security issues.
- A repository-wide secret pattern scan found no hardcoded API keys, tokens, or real passwords in source files.
- Temporary and sensitive files are excluded from source control by `.gitignore`.

## Improvements applied

- Added environment variable support for `FLASK_SECRET_KEY`, `LOGIN_USER`, and `LOGIN_PASSWORD`.
- Removed insecure default login credentials and require configured login variables to enable `/login`.
- Added a rate limit of `5 per 15 minutes` to the `/login` endpoint.
- Added validation and sanitization of all profile form inputs.
- Added strict content security and HTTP security headers.
- Added `.env.example` and `.gitignore` to keep secrets and local environment files out of the repository.

## Recommendations

- Do not commit the actual `.env` file or production secrets.
- Set strong, unique login credentials in environment variables.
- Run periodic security scans whenever new dependencies are added.
