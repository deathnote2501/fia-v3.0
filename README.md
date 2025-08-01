# FIA v3.0 - AI-powered e-learning platform

FIA v3.0 is an AI-powered e-learning platform that enables trainers to create personalized training sessions for learners using Google Gemini Flash 2.0.

## Architecture

This project follows hexagonal architecture with clear separation of concerns:
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy + Alembic + Poetry
- **Frontend**: HTML5/CSS3/JavaScript ES6 (vanilla)
- **AI**: Google Gemini Flash 2.0 via Vertex AI
- **Deployment**: Railway

## Deployment

The application is configured for Railway deployment with automatic builds using Nixpacks and Poetry.