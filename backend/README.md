# FIA v3.0 Backend

AI-powered e-learning platform backend built with FastAPI.

## Architecture

This backend follows hexagonal architecture with:
- **Domain**: Business logic and entities
- **Adapters**: API controllers and external integrations
- **Infrastructure**: Database, configuration, and external services

## Technology Stack

- **FastAPI**: Modern web framework
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **PostgreSQL**: Primary database
- **Pydantic**: Data validation
- **FastAPI-Users**: Authentication
- **Google Gemini**: AI integration

## Development

```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload

# Database migrations
poetry run alembic upgrade head
```

## Environment Variables

Required environment variables (see `.env.example`):
- `DATABASE_URL`
- `GEMINI_API_KEY`
- `SECRET_KEY`