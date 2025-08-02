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
│   ├── i18n/          # Internationalization system
│   └── utils/         # JS utilities
```

## Technology Stack

- **Backend**: FastAPI + PostgreSQL + SQLAlchemy + Alembic + Poetry
- **Authentication**: FastAPI-Users with JWT tokens
- **AI**: Google Gemini Flash 2.0 with Context Caching and Structured Output
- **Frontend**: HTML5/CSS3/JavaScript ES6 (vanilla) with robust i18n system
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

## 🤖 Architecture & Coding Rules for Claude 4 Instances

### **MANDATORY: Before Writing Any Code**

1. 🔍 **ANALYZE FIRST** - Always read existing patterns before creating new code
2. 🏗️ **RESPECT HEXAGONAL ARCHITECTURE** - Never violate layer boundaries
3. 🔌 **USE DEPENDENCY INJECTION** - Services must accept ports in constructor
4. 📋 **FOLLOW INTERFACE CONTRACTS** - Check existing method signatures

### **🚨 Critical Patterns to Follow**

#### **1. Service Creation Pattern**
```python
# ✅ CORRECT - Always inject dependencies
class MyService:
    def __init__(self, ai_adapter: AIAdapterPort, repo: MyRepoPort):
        self.ai_adapter = ai_adapter
        self.repo = repo

# ❌ NEVER - Don't create dependencies inside
class MyService:
    def __init__(self):
        self.ai_adapter = AIAdapter()  # VIOLATION!
```

#### **2. AI Adapter Usage**
```python
# ✅ CORRECT - Current interface (returns STRING)
response = await self.ai_adapter.generate_content(
    prompt=prompt,
    temperature=0.7,
    session_id=session_id,
    learner_session_id=learner_session_id
)
# response is a STRING, not Dict!

# ❌ WRONG - Old interface
response = await self.ai_adapter.generate_content(prompt, model_name="...")
text = response.get('text')  # Will fail!
```

#### **3. Controller Pattern**
```python
# ✅ CORRECT - Dependency injection
@router.post("/endpoint")
async def endpoint(
    request: RequestSchema,
    service: MyService = Depends(get_my_service)
):
    try:
        result = await service.method(request)
        return ResponseSchema(**result)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Dependency function
async def get_my_service(session: AsyncSession = Depends(get_async_session)):
    ai_adapter = AIAdapter()
    repo = MyRepository(session)
    return MyService(ai_adapter, repo)
```

### **🏗️ Layer Rules - STRICT ENFORCEMENT**

#### **Domain Layer (`domain/`)**
```python
# ✅ ALLOWED imports
from app.domain.ports.* import *
from app.domain.entities.* import *
from typing import *
import logging, time, json  # Standard library OK

# ❌ FORBIDDEN imports
from app.adapters.*        # NO!
from app.infrastructure.*  # NO!
from sqlalchemy.*          # NO!
from fastapi.*            # NO!
```

#### **Adapters Layer (`adapters/`)**
```python
# ✅ Implement domain ports
class MyAdapter(MyAdapterPort):  # Must implement domain interface
    async def method(self, param: str) -> str:
        try:
            result = await self.infrastructure.call()
            return self._map_to_domain(result)
        except InfrastructureError as e:
            raise DomainError(str(e)) from e  # Convert exceptions
```

#### **Exception Handling**
```python
# ✅ DOMAIN services - Use domain exceptions
except Exception as e:
    raise DomainError(f"Business error: {e}")

# ✅ ADAPTERS - Convert infrastructure → domain
except VertexAIError as e:
    raise AIError(str(e)) from e

# ✅ CONTROLLERS - Convert domain → HTTP
except DomainError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### **🔧 Quick Verification Commands**
```bash
# Check existing patterns before coding
Grep pattern="class.*Service" path="app/domain/services"
Grep pattern="def __init__" path="app/domain/services" -A 3

# Verify architecture compliance
./.claude/hooks/test_hooks_quick.sh
```

### **📋 Pre-Commit Checklist**
- [ ] No infrastructure imports in `domain/`
- [ ] Services use dependency injection
- [ ] AI adapter returns string, not dict
- [ ] Exceptions converted at layer boundaries
- [ ] Followed existing naming patterns

## Context Caching Implementation Status & Improvements

### 🎯 **Context Caching Overview Analysis (August 2025)**

**Current Implementation Status: ✅ FUNCTIONAL with Improvement Opportunities**

#### **✅ Working Features**
- **Complete Context Cache Service** (`ContextCacheService`) with full CRUD operations
- **Document Processing Integration** - Auto-cache creation for training materials
- **Google Specs Compliance** - TTL 6-24h, 50MB limit, SHA256 cache keys
- **API Endpoints** - Full REST API (`/api/context-cache/*`) with authentication
- **Cost Optimization** - 75% token reduction on cache hits

#### **⚠️ Architecture Improvements Needed**
1. **Controller Not Exposed** - `context_cache_controller` missing from main.py
2. **Dependency Injection** - Service instantiates adapters directly (violates hexagonal)
3. **Auto-Integration** - No automatic cache usage in plan generation
4. **Cache Invalidation** - No strategy for file updates
5. **Monitoring** - Missing cache hit/miss metrics

#### **🔧 Recommended KISS Improvements (5-8h total)**

**Phase 1: Architecture Fixes (2h)**
- Expose context_cache_controller in main.py
- Fix dependency injection in ContextCacheService constructor
- Add proper adapter injection in controllers

**Phase 2: Auto-Integration (3h)**
- Auto-cache in PlanGenerationService when use_cache=True
- Cache invalidation on training file updates
- Background cleanup of expired caches

**Phase 3: Monitoring (2h)**
- Cache hit/miss rate tracking
- Storage cost monitoring
- Token savings analytics

**Benefits:** 75% cost reduction on repeated document analysis, improved response times, automatic cache management

## Current Implementation Status

### ✅ Complete: Full SPEC.md Compliance + Architecture Refactoring (August 2025)

**Phase 4 Complete: Security & Quality + Functional Trainer Dashboard + Progressive Learner Profiling**

**Architecture Refactoring Completed:**
1. **Hexagonal Architecture**: Pure domain entities separated from infrastructure models
2. **Dependency Injection**: All services use proper constructor injection with ports
3. **Interface Standardization**: AI adapter returns strings, consistent method signatures
4. **Exception Handling**: Proper layer-based exception conversion (Infrastructure → Domain → HTTP)
5. **Security Hardening**: Generic error messages, proper logging, no information disclosure
6. **Performance Optimization**: Database indexes, code cleanup, logging standards
7. **Language Standardization**: Full English consistency across codebase and frontend

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

**Recently Fixed Critical Issues (August 2025):**
1. **AI Adapter Interface**: Fixed model_name parameter issue - adapter now returns string, not dict
2. **Dependency Injection**: Fixed ChartGenerationService and other services to use proper constructor injection
3. **Exception Handling**: Removed infrastructure exceptions from domain layer (VertexAIError → generic Exception)
4. **Interface Consistency**: Standardized AI adapter method signatures across all services
5. **Architecture Compliance**: All services now follow hexagonal architecture principles
6. **Chart Generation**: Fixed string vs dict interface mismatch that was causing chart generation failures

**Previous Fixed Issues:**
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
- **TTS Audio System with Visual Feedback** (NEW)
- **Bulletproof i18n System with SafeT Helper** (NEW)
- Secure file upload and download system
- Real-time dashboard analytics
- Session management for learners
- Proper authentication and authorization
- Database performance optimization
- Security best practices compliance
- Full English language consistency
- Professional user experience with zero technical key display

**Testing Status:**
- ✅ Trainer registration and login
- ✅ Training creation with file upload
- ✅ File download functionality
- ✅ Dashboard statistics and activity
- ✅ Session creation (basic functionality)
- ✅ Profile management
- ✅ Error handling and validation
- ✅ Progressive profile enrichment logic
- ✅ Conversation service integration
- ✅ Slide personalization with enriched profile
- ✅ **Architecture refactoring and dependency injection** (NEW)
- ✅ **AI adapter interface standardization** (NEW)
- ✅ **Chart generation functionality** (NEW)
- ✅ **TTS spinner functionality and audio feedback** (NEW)
- ✅ **Robust i18n system with SafeT helper** (NEW)
- ✅ **Zero technical key display guarantee** (NEW)

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

## Frontend Features & User Experience

### 🎤 TTS Spinner System (August 2025)

**Implemented audio feedback system for Text-to-Speech functionality:**

**Features:**
- **Visual Feedback**: Green Bootstrap spinner during TTS generation
- **Button State Management**: Loading, playing, stopped states with appropriate icons
- **User Experience**: Prevents multiple clicks during audio generation
- **Bootstrap Integration**: Uses standard Bootstrap success color (`#198754`)

**Implementation Files:**
- `frontend/src/components/chat-interface.js` - TTS button state management
- `frontend/src/styles/main.css` - Loading state styling

**Button States:**
```javascript
// Loading state (during TTS generation)
button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
button.classList.add('loading');

// Playing state (audio is playing)
button.innerHTML = '<i class="bi bi-pause-fill"></i>';

// Stopped state (ready to play)
button.innerHTML = '<i class="bi bi-play-fill"></i>';
```

### 🌍 Robust i18n System with SafeT Helper (August 2025)

**Implemented bulletproof internationalization system preventing technical key display:**

**Core Architecture:**
- **SafeT Helper Function**: `window.safeT()` with intelligent fallbacks
- **Zero Technical Keys**: Never shows "status.validatingSession" to users
- **Graceful Degradation**: Works even when i18n isn't loaded
- **Smart Fallbacks**: Contextual defaults for loading/error states

**Implementation Files:**
- `frontend/src/i18n/i18n-helper.js` - Core safeT() helper with smart fallbacks
- `frontend/src/training-init.js` - Fixed i18n timing issues
- **8 Components Updated**: 28 total replacements across all UI components

**SafeT Helper Features:**
```javascript
// Intelligent fallback system
export function safeT(key, customFallback = null) {
    // Try official translation first
    if (window.i18n && window.i18n.translations) {
        const translation = window.i18n.t(key);
        if (translation && translation !== key) {
            return translation;
        }
    }
    
    // Smart contextual fallbacks
    return customFallback || smartFallbacks[key] || 'Loading...';
}
```

**Smart Fallbacks Implemented:**
- `status.loadingGeneric` → "Loading..."
- `status.loadingTrainings` → "Loading trainings..."
- `status.aiGenerating` → "AI Generating..."
- `error.generic` → "An error occurred"
- `error.loadingData` → "Error loading data"

**User Experience Benefits:**
- **Professional UX**: No technical jargon ever displayed
- **Consistent Messaging**: Uniform loading and error states
- **Language Independence**: Works in any target language
- **Future-Proof**: Easy to extend with new fallbacks

**Migration Completed:**
- ✅ All `window.t ? window.t()` patterns replaced with `window.safeT ? window.safeT()`
- ✅ 28 locations updated across 8 components
- ✅ Zero technical key display guaranteed
- ✅ Timing issues resolved (i18n loads before first UI messages)

### 📱 Responsive Design & Bootstrap Integration

**Consistent UI/UX Framework:**
- **Bootstrap 5** for all components and styling
- **Bootstrap Icons** for all iconography
- **Responsive Grid System** for mobile compatibility
- **Consistent Color Palette** using Bootstrap theme colors

## Development Phases

The project follows an 8-phase development strategy with manual interface testing at each phase. Each phase builds incrementally with testable interfaces before proceeding to the next phase.

## Testing Strategy

Testing is primarily manual through web interfaces:
- Phase-by-phase validation via UI
- Happy path and error scenarios
- Performance testing through actual usage
- Security testing via interface attempts
- Mobile responsiveness validation

## 🔧 Validation Hooks & Code Quality

### **Architecture Validation System**

The project includes comprehensive validation hooks to ensure code quality and architecture compliance:

```bash
# Quick validation (recommended before commits)
./.claude/hooks/test_hooks_quick.sh

# Complete validation (before releases)
./.claude/hooks/validate_best_practices.sh
```

### **Available Hooks**

1. **`architecture_validation.sh`** - Validates hexagonal architecture structure
2. **`naming_conventions.sh`** - Ensures English-first naming across codebase  
3. **`security_validation.sh`** - Checks security practices and data validation
4. **`performance_validation.sh`** - Validates performance optimizations
5. **`i18n_validation.sh`** - Ensures English-first development with i18n readiness

### **Common Issues Detected**

- Infrastructure imports in domain layer
- Missing dependency injection in services
- French terms in code (should be English-first)
- Missing rate limiting or context caching
- Hardcoded secrets or configuration

### **Hook Results Interpretation**

- ✅ **Green** - All validations passed, code ready for development
- ❌ **Red** - Critical issues found, must fix before proceeding
- ⚠️ **Yellow** - Warnings, review and improve if possible

## Important Notes

- Use only Bootstrap components, colors, effects, and animations
- No custom CSS frameworks beyond Bootstrap
- Environment variables for all configuration
- Poetry for all dependency management (from backend/ directory)
- FastAPI automatic API documentation
- Structured logging for all Gemini interactions
- Railway deployment exclusively
- **Run validation hooks before each commit to maintain code quality**