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

### ✅ Complete: Full SPEC.md Compliance + Trainer Dashboard + Learner Profile Enrichment (January 2025)

**Phase 4 Complete: Security & Quality + Functional Trainer Dashboard + Progressive Learner Profiling**

**Architecture Refactoring Completed:**
1. **Hexagonal Architecture**: Pure domain entities separated from infrastructure models
2. **AI Services Separation**: Dedicated services for conversation vs engagement analysis
3. **Security Hardening**: Generic error messages, proper logging, no information disclosure
4. **Performance Optimization**: Database indexes, code cleanup, logging standards
5. **Language Standardization**: Full English consistency across codebase and frontend

**Core Services Implemented:**
1. **Plan Generation Service (Vertex)**: Gemini 2.0 Flash with personalized training plans
2. **Conversation Service**: Dedicated AI chat service for learner interactions with profile enrichment
3. **Learner Profile Enrichment Service**: Progressive profiling through conversation analysis
4. **Engagement Analysis Service**: AI-powered learner behavior and progress analysis
5. **Context Caching Service**: 75% cost optimization (6-24h TTL)
6. **Document Processing Service**: PDF/PowerPoint analysis with Gemini Document API
7. **File Storage Service**: Local file system with organized directory structure

**Trainer Dashboard Features (Fully Functional):**
- **Authentication System**: FastAPI-Users with JWT authentication working correctly
- **Training Management**: Create, upload, list, download, and delete training materials
- **File Upload**: PDF/PPT/PPTX support with validation (max 50MB)
- **Dashboard Analytics**: Real-time statistics (trainings count, sessions, learners, avg time)
- **Recent Activity**: Timeline of trainer activities
- **Session Management**: Create training sessions with unique learner links
- **File Download**: Direct download of uploaded training materials
- **Profile Management**: Update trainer profile information

**Learner Profile Enrichment Features (Newly Implemented):**
- **Progressive Profiling**: AI analyzes each conversation to enrich learner profile
- **Automatic Enrichment**: Every chat interaction updates the learner's enriched profile
- **Intelligent Fusion**: New insights merge with existing data without loss
- **Personalized Slides**: Slide generation uses enriched profile for maximum personalization
- **Profile Evolution**: Learner profile becomes more accurate with each interaction
- **Structured Storage**: Enriched data stored in `enriched_profile` JSONB column

**Fixed Critical Issues:**
1. **FastAPI-Users Authentication**: Fixed domain entity vs SQLAlchemy model conflict
2. **Dashboard Endpoints**: Created missing `/api/dashboard/stats` and `/api/dashboard/recent-activity`
3. **Database Schema**: Fixed column mismatches (expires_at vs updated_at)
4. **Training Creation**: Fixed FileType enum handling and domain entity mapping
5. **File Download**: Added file_path to API responses for download functionality
6. **Profile Enrichment Integration**: Fixed conversation service signatures for profile enrichment

**Key Architectural Features:**
- **Domain Purity**: Clean separation between business logic and infrastructure
- **Rate Limiting**: Comprehensive rate limiting across all AI services (60 req/min)
- **Structured Output**: JSON schema validation with Pydantic for all AI responses
- **Error Handling**: Secure error handling with fallback mechanisms
- **Database Optimization**: Performance indexes for frequent queries
- **File Management**: Secure file storage with trainer ownership validation
- **Progressive Profiling**: Automatic learner profile enrichment through conversation analysis
- **Adaptive Personalization**: Dynamic slide content based on enriched learner insights

**API Endpoints Available:**
- `POST /api/plan-generation/*` - Personalized training plan generation
- `POST /api/conversation/*` - AI conversation and chat services with profile enrichment
- `POST /api/engagement/*` - Learner engagement analysis
- `POST /api/context-cache/*` - Document caching and management
- `POST /api/document-processing/*` - Document analysis and parsing
- `GET /api/rate-limit/*` - Rate limiting status and testing
- `POST /api/trainings/` - Create training with file upload
- `GET /api/trainings/` - List trainer's trainings
- `GET /api/trainings/{id}/download` - Download training files
- `DELETE /api/trainings/{id}` - Delete training and associated file
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/recent-activity` - Recent activity timeline
- `POST /api/sessions/` - Create training sessions
- `POST /api/chat` - Learner chat with automatic profile enrichment
- `POST /auth/register` - Trainer registration
- `POST /auth/jwt/login` - JWT authentication

**Production Ready Features:**
- Complete hexagonal architecture implementation
- Fully functional trainer dashboard at `/frontend/public/trainer.html`
- **Progressive Learner Profile Enrichment System** (NEW)
- **AI-Powered Slide Personalization** (NEW)
- Secure file upload and download system
- Real-time dashboard analytics
- Session management for learners
- Proper authentication and authorization
- Database performance optimization
- Security best practices compliance
- Full English language consistency

**Testing Status:**
- ✅ Trainer registration and login
- ✅ Training creation with file upload
- ✅ File download functionality
- ✅ Dashboard statistics and activity
- ✅ Session creation (basic functionality)
- ✅ Profile management
- ✅ Error handling and validation
- ✅ **Progressive profile enrichment logic** (NEW)
- ✅ **Conversation service integration** (NEW)
- ✅ **Slide personalization with enriched profile** (NEW)

## Progressive Learner Profile Enrichment System

### 🧠 Architecture Overview

The learner profile enrichment system is designed using the **KISS principle** to progressively enhance learner profiles through conversation analysis, enabling increasingly personalized slide content.

### Database Schema Changes

**Migration Applied:** `007_rename_personalized_plan_to_enriched_profile`
- Renamed `learner_sessions.personalized_plan` → `learner_sessions.enriched_profile`
- Column stores JSONB data with structured learner insights

### Core Components

#### 1. LearnerProfileEnrichmentService (`app/domain/services/learner_profile_enrichment_service.py`)
- **Progressive Fusion**: Intelligently merges new insights with existing profile data
- **Data Preservation**: Arrays merge without duplicates, single values update with latest insights
- **Metadata Tracking**: Maintains enrichment history with timestamps and counters

#### 2. Enhanced Conversation Adapter (`app/adapters/outbound/conversation_adapter.py`)
- **Automatic Enrichment**: Every chat interaction generates learner profile insights
- **Structured Analysis**: AI analyzes conversation to extract learning patterns
- **JSON Schema**: Validates enriched profile data structure

#### 3. Slide Generation Integration (`app/services/slide_generation_service.py`)
- **Dynamic Personalization**: Uses enriched profile data in slide generation prompts
- **Adaptive Content**: Slide content becomes more personalized with each interaction

### Enriched Profile Structure

```json
{
  "learning_style_observed": "prefers concrete examples and visual aids",
  "comprehension_level": "good understanding but needs repetition on complex topics", 
  "interests": ["practical applications", "real-world case studies", "templates"],
  "blockers": ["abstract concepts", "too much theory at once", "complex planning"],
  "objectives": "apply knowledge to current job challenges",
  "engagement_patterns": "asks detailed questions, prefers step-by-step approach",
  "enrichment_history": {
    "first_enriched_at": "2025-01-28T14:00:00Z",
    "total_enrichments": 3,
    "last_updated_at": "2025-01-28T16:30:00Z"
  }
}
```

### Flow Architecture

```
💬 Learner Chat Message 
    ↓
🤖 AI Conversation Analysis (ConversationAdapter)
    ↓ 
📊 Profile Insights Extraction (JSON structured output)
    ↓
🔄 Intelligent Profile Fusion (LearnerProfileEnrichmentService)
    ↓
💾 Automatic Database Save (enriched_profile column)
    ↓
🎯 Enhanced Slide Personalization (SlideGenerationService)
```

### Key Features

- **Zero Configuration**: Works automatically with existing chat system
- **Intelligent Fusion**: New insights enhance rather than replace existing data
- **Performance Optimized**: Uses existing rate limiting and structured output
- **Error Resilient**: Profile enrichment failures don't break conversation flow
- **Hexagonal Compliance**: Clean separation between domain logic and infrastructure

### Implementation Files

**New Files Created:**
- `app/domain/services/learner_profile_enrichment_service.py` - Core enrichment service
- `alembic/versions/007_rename_personalized_plan_to_enriched_profile.py` - Database migration

**Modified Files:**
- `app/adapters/outbound/conversation_adapter.py` - Added profile enrichment to chat responses
- `app/services/slide_generation_service.py` - Integrated enriched profile in slide generation
- `app/domain/entities/learner_session.py` - Updated entity with enriched_profile field
- `app/domain/schemas/learner_session.py` - Updated Pydantic schema
- `app/adapters/repositories/learner_session_repository.py` - Updated repository mappings
- `app/domain/ports/outbound_ports.py` - Added learner_session_id parameter
- `app/domain/services/conversation_service.py` - Updated service call signatures

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