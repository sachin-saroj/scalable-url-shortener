# Contributing to Scalable URL Shortener

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## Table of Contents

- [Development Setup](#development-setup)
- [Architecture Overview](#architecture-overview)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Commit Messages](#commit-messages)

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 20+
- Docker & Docker Compose
- Redis 7+
- PostgreSQL 16+

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/sachin-saroj/scalable-url-shortener.git
cd scalable-url-shortener

# 2. Copy environment config
cp .env.example .env
# Edit .env with your local values (especially secrets)

# 3. Start with Docker Compose
docker-compose up -d

# 4. Backend runs at http://localhost:8000
# 5. Frontend runs at http://localhost:5173
```

### Local Development (without Docker)

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Architecture Overview

```
├── backend/           # FastAPI + SQLAlchemy + Celery
│   ├── app/
│   │   ├── api/v1/    # Route handlers (thin controllers)
│   │   ├── models/    # SQLAlchemy ORM models
│   │   ├── schemas/   # Pydantic request/response schemas
│   │   ├── services/  # Business logic layer
│   │   ├── utils/     # Utilities (auth, rate limiting, validation)
│   │   └── workers/   # Celery background tasks
│   └── tests/         # pytest test suite
├── frontend/          # React + Vite + Tailwind
│   └── src/
│       ├── components/
│       ├── pages/
│       └── context/
└── monitoring/        # Prometheus + Grafana configs
```

**Key principle**: Route handlers are thin controllers. All business logic lives in the `services/` layer.

## Coding Standards

### Backend (Python)

- **Formatter**: Ruff (`ruff format`)
- **Linter**: Ruff (`ruff check`)
- **Type checker**: MyPy (`mypy app/`)
- **Line length**: 100 characters
- **Imports**: Sorted by isort (via Ruff)
- **Async**: Use `async/await` for all I/O operations
- **ORM**: SQLAlchemy 2.0 style (no legacy Query API)

### Frontend (JavaScript/React)

- **Framework**: React with Vite
- **Styling**: Tailwind CSS
- **Components**: Functional components with hooks

### Security Requirements

Every PR touching auth, payments, or PII must include:
- Input validation on all request bodies/params
- Parameterized queries (no string-concatenated SQL)
- Rate limiting on write endpoints
- No hardcoded secrets

## Pull Request Process

1. **Create an issue** first describing the change
2. **Branch** from `main`: `feat/description`, `fix/description`, `docs/description`
3. **Implement** with tests for new/changed logic
4. **Run checks** locally:
   ```bash
   cd backend
   ruff format --check .
   ruff check .
   pytest tests/ -v --tb=short
   ```
5. **Submit PR** referencing the issue (`Closes #N`)
6. **Address feedback** from code review
7. **Squash merge** after approval

### PR Checklist

- [ ] Tests added/updated for new functionality
- [ ] Code passes `ruff format --check` and `ruff check`
- [ ] No new hardcoded secrets or config values
- [ ] `.env.example` updated if new env vars added
- [ ] Documentation updated if API changes

## Testing

```bash
# Run all tests
cd backend
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_url_service.py -v
```

### Test Requirements

- **New endpoints**: At minimum one happy-path test and one auth-failure test
- **Bug fixes**: A regression test that fails before the fix and passes after
- **Coverage**: Minimum 75% (enforced by CI)

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore`

**Examples**:
```
feat(api): add bulk URL shortening endpoint
fix(cache): handle Redis connection timeout gracefully
test(auth): add regression test for token refresh race condition
docs(readme): update deployment instructions
```

## Questions?

Open a [GitHub Discussion](https://github.com/sachin-saroj/scalable-url-shortener/discussions) or file an issue.
