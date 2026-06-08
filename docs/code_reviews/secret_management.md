# Code Review: Secret Management Hardening

## Overview
Replaced all hardcoded secrets and default values with environment variables to satisfy production readiness.

## Changes Made
- Configured startup validations using `pydantic-settings`.
- Ensured default values of `change-me` or empty keys fail fast with `RuntimeError` at startup.
- Cleaned up config templates in `docker-compose.yml` and `alembic.ini`.
- Added fallback dynamic `DATABASE_URL` resolution inside `conftest.py` for CI compatibility.

## Reference
Closes #1
