# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FIA v3.0 is an AI-powered e-learning platform that enables trainers to create personalized training sessions for learners. The application uses Google Gemini Flash 2.0 to generate dynamic, personalized learning content based on uploaded PDF/PowerPoint materials and learner profiles.

## Architecture

This project follows **hexagonal architecture** with clear separation of concerns:

### Backend Structure (FastAPI + PostgreSQL)
```
backend/
├── app/
│   ├── main.py
│   ├── domain/            # Business logic
│   │   ├── entities/      # Business entities
│   │   ├── ports/         # Interfaces (repositories, services)
│   │   └── services/      # Business services
│   ├── adapters/          # Adaptation layer
│   │   ├── inbound/       # API controllers
│   │   ├── outbound/      # Database, Gemini, external APIs
│   │   └── repositories/  # Repository implementations
│   ├── infrastructure/    # Configuration, database, security
│   └── utils/             # Utilities
├── alembic/               # Database migrations
└── pyproject.toml         # Poetry configuration
```

### Frontend Structure (Vanilla HTML/CSS/JS)
```
frontend/
├── public/            # HTML pages
├── src/
│   ├── components/    # Reusable JS components
│   ├── styles/        # Modular CSS
│   └── utils/         # JS utilities
```

## Technology Stack

- **Backend**: FastAPI + PostgreSQL + SQLAlchemy + Alembic + Poetry
- **Authentication**: FastAPI-Users with JWT tokens
- **AI**: Google Gemini Flash 2.0 with Context Caching and Structured Output
- **Frontend**: HTML5/CSS3/JavaScript ES6 (vanilla)
- **UI**: Bootstrap + Bootstrap Icons only
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Deployment**: Railway
- **Version Control**: GitHub

## Development Commands

Since this is a new project without existing configuration files, common commands will be:

### Backend (from backend/ directory)
```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload

# Database migrations
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "description"

# Run tests (when implemented)
poetry run pytest
```

## Core Business Logic

### User Flows

1. **Trainer Flow**:
   - Register/login via `/register.html` and `/login.html`
   - Access dashboard at `trainer.html`
   - Create training sessions with PDF/PowerPoint uploads
   - Generate session links for learners
   - View analytics and learner progress

2. **Learner Flow**:
   - Access session via unique link
   - Complete profile questionnaire (email, level, learning style, job, sector, country, language)
   - Receive AI-generated personalized training plan
   - Navigate through dynamically generated slides (75% width)
   - Interact with AI trainer via chat (25% width)
   - Progress tracked: slides viewed, time spent, chat messages

3. **Administrator Flow**:
   - Monitor Gemini API calls and responses via structured logs

### AI Integration Strategy

- **Context Caching**: Use Gemini's Context Caching with 6-24 hour TTL for training materials (75% cost reduction)
- **Structured Output**: All AI responses use JSON structured format with Pydantic validation
- **Personalized Plan Generation**: Smart prompts combining learner profile + training content
- **Rate Limiting**: Implement rate limiting for Gemini API calls
- **Separate API Calls**: Distinct calls for content generation vs. engagement analysis

## Key Technical Requirements

### Internationalization (English First)
- All code, variables, routes, database tables/columns in English
- UI labels and system messages in English
- Exception: AI prompts can be in target languages (French for testing)
- Architecture prepared for future translation support

### Database Conventions
- Tables: `snake_case` English (e.g., `training_sessions`, `chat_messages`)
- Columns: `snake_case` English (e.g., `email_captured_at`, `engagement_level`)
- Classes: `PascalCase` English (e.g., `TrainingSession`, `LearnerSession`)

### Security & Validation
- All passwords hashed, never stored in plain text
- All environment variables externally configured
- Pydantic validation for all POST/PUT/PATCH endpoints
- JWT-based authentication for sessions
- Input sanitization and validation on backend

### Performance Optimizations
- Database indexing for frequent queries
- SQL query optimization, avoid N+1 queries
- Pagination with `limit()` and `offset()` for all lists
- Gemini Context Caching for training materials
- Rate limiting on AI API calls

## Current Implementation Status

### ✅ Phase 2 Complete: Personalized Training Plan Generation

**Implemented Services:**
1. **Document Processing Service**: PDF/PowerPoint parsing with Gemini Document Understanding API
2. **Context Caching Service**: 75% cost optimization through intelligent caching (6-24h TTL)
3. **Plan Generation Service**: Smart personalized plan creation with optimized prompts
4. **Plan Parser Service**: JSON → Database entities conversion and persistence

**Key Features:**
- **Smart Personalization Engine**: Combines learner profile (experience, learning style, job, sector) with training content
- **5-Stage Training Structure**: Découverte → Apprentissage → Application → Approfondissement → Maîtrise
- **Structured Output**: JSON schema validation with Pydantic for reliable plan generation
- **Database Persistence**: Complete plan storage with modules, submodules, and slide titles
- **Cost Optimization**: Context Caching reduces API costs by 75% on repeated content usage

**API Endpoints Available:**
- `POST /api/context-cache/*` - Document caching and management (9 endpoints)
- `POST /api/plan-generation/*` - Plan generation and management (6 endpoints)
- `POST /api/document-processing/*` - Document analysis and parsing

**Ready for Testing:**
Upload PDF → Create Learner Profile → Generate Personalized Plan → Save to Database

## Development Phases

The project follows an 8-phase development strategy with manual interface testing at each phase. Each phase builds incrementally with testable interfaces before proceeding to the next phase.

## Testing Strategy

Testing is primarily manual through web interfaces:
- Phase-by-phase validation via UI
- Happy path and error scenarios
- Performance testing through actual usage
- Security testing via interface attempts
- Mobile responsiveness validation

## Important Notes

- Use only Bootstrap components, colors, effects, and animations
- No custom CSS frameworks beyond Bootstrap
- Environment variables for all configuration
- Poetry for all dependency management (from backend/ directory)
- FastAPI automatic API documentation
- Structured logging for all Gemini interactions
- Railway deployment exclusively