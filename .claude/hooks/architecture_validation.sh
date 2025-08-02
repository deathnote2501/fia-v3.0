#!/bin/bash

# Architecture Validation Hook
# Validates hexagonal architecture compliance and project structure

echo "🏗️ Validating Architecture..."

ERRORS=0

# Check hexagonal architecture structure
echo "Checking hexagonal architecture structure..."

if [ -d "backend/app/domain" ] && [ -d "backend/app/adapters" ] && [ -d "backend/app/infrastructure" ]; then
    echo "✅ Hexagonal architecture directories present"
else
    echo "❌ Missing hexagonal architecture directories (domain/, adapters/, infrastructure/)"
    ERRORS=$((ERRORS + 1))
fi

# Check required subdirectories
REQUIRED_DIRS=(
    "backend/app/domain/entities"
    "backend/app/domain/ports"
    "backend/app/domain/services"
    "backend/app/adapters/inbound"
    "backend/app/adapters/outbound"
    "backend/app/adapters/repositories"
    "backend/app/infrastructure"
    "backend/app/utils"
    "backend/alembic"
    "frontend/public"
    "frontend/src/components"
    "frontend/src/styles"
    "frontend/src/utils"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "⚠️  $dir missing (will be created when needed)"
    fi
done

# Check for forbidden patterns
echo "Checking for architectural violations..."

# Check for business logic in adapters
if find backend/app/adapters -name "*.py" -exec grep -l "class.*Service\|def.*business_logic" {} \; 2>/dev/null | grep -q .; then
    echo "❌ Business logic found in adapters layer"
    ERRORS=$((ERRORS + 1))
fi

# Check for infrastructure imports in domain (CRITICAL VIOLATION)
echo "Checking domain layer purity..."
DOMAIN_VIOLATIONS=0

# Check for database imports in domain
if find backend/app/domain -name "*.py" -exec grep -l "from sqlalchemy\|import sqlalchemy\|from database" {} \; 2>/dev/null | grep -q .; then
    echo "❌ Database imports found in domain layer:"
    find backend/app/domain -name "*.py" -exec grep -H "from sqlalchemy\|import sqlalchemy\|from database" {} \; 2>/dev/null | head -3
    DOMAIN_VIOLATIONS=$((DOMAIN_VIOLATIONS + 1))
fi

# Check for FastAPI dependencies in domain
if find backend/app/domain -name "*.py" -exec grep -l "from fastapi\|import fastapi\|fastapi_users" {} \; 2>/dev/null | grep -q .; then
    echo "❌ FastAPI imports found in domain layer:"
    find backend/app/domain -name "*.py" -exec grep -H "from fastapi\|import fastapi\|fastapi_users" {} \; 2>/dev/null | head -3
    DOMAIN_VIOLATIONS=$((DOMAIN_VIOLATIONS + 1))
fi

# Check for infrastructure imports in domain (NEW - CRITICAL)
if find backend/app/domain -name "*.py" -exec grep -l "from app\.infrastructure\|import.*infrastructure" {} \; 2>/dev/null | grep -q .; then
    echo "❌ Infrastructure imports found in domain layer:"
    find backend/app/domain -name "*.py" -exec grep -H "from app\.infrastructure\|import.*infrastructure" {} \; 2>/dev/null | head -5
    DOMAIN_VIOLATIONS=$((DOMAIN_VIOLATIONS + 1))
fi

# Check for adapter imports in domain (NEW)
if find backend/app/domain -name "*.py" -exec grep -l "from app\.adapters\|import.*adapters" {} \; 2>/dev/null | grep -q .; then
    echo "❌ Adapter imports found in domain layer:"
    find backend/app/domain -name "*.py" -exec grep -H "from app\.adapters\|import.*adapters" {} \; 2>/dev/null | head -3
    DOMAIN_VIOLATIONS=$((DOMAIN_VIOLATIONS + 1))
fi

# Check for dependency injection violations (NEW)
if find backend/app/domain/services -name "*.py" -exec grep -l "AsyncSession\|SessionLocal\|get_db" {} \; 2>/dev/null | grep -q .; then
    echo "❌ Direct database session usage in domain services:"
    find backend/app/domain/services -name "*.py" -exec grep -H "AsyncSession\|SessionLocal\|get_db" {} \; 2>/dev/null | head -3
    DOMAIN_VIOLATIONS=$((DOMAIN_VIOLATIONS + 1))
fi

if [ $DOMAIN_VIOLATIONS -gt 0 ]; then
    echo "💡 DOMAIN PURITY VIOLATION - Current: $((100 - DOMAIN_VIOLATIONS * 20))%"
    echo "   Target: 90%+ domain purity for hexagonal architecture"
    ERRORS=$((ERRORS + DOMAIN_VIOLATIONS))
fi

# Check pyproject.toml location
if [ -f "backend/pyproject.toml" ]; then
    echo "✅ pyproject.toml in correct location (backend/)"
elif [ -f "pyproject.toml" ]; then
    echo "❌ pyproject.toml should be in backend/ directory"
    ERRORS=$((ERRORS + 1))
fi

# Check for duplicate services structure (CRITICAL)
echo "Checking for architectural duplication..."
if [ -d "backend/app/domain/services" ] && [ -d "backend/app/services" ]; then
    echo "❌ CRITICAL: Duplicate services directories found"
    echo "   - backend/app/domain/services/ (hexagonal)"
    echo "   - backend/app/services/ (legacy)"
    echo "   This creates confusion and import conflicts"
    ERRORS=$((ERRORS + 1))
fi

if [ -d "backend/app/adapters/inbound" ] && [ -d "backend/app/controllers" ]; then
    echo "❌ WARNING: Mixed controller/adapter structure"
    echo "   - backend/app/adapters/inbound/ (hexagonal)"
    echo "   - backend/app/controllers/ (legacy)"
    echo "   Consider consolidating into adapters/inbound/"
    ERRORS=$((ERRORS + 1))
fi

# Check for required stack components
echo "Validating technology stack..."

if [ -f "backend/pyproject.toml" ]; then
    if grep -q "fastapi" backend/pyproject.toml; then
        echo "✅ FastAPI dependency found"
    else
        echo "❌ FastAPI not found in dependencies"
        ERRORS=$((ERRORS + 1))
    fi

    if grep -q "sqlalchemy" backend/pyproject.toml; then
        echo "✅ SQLAlchemy dependency found"
    else
        echo "❌ SQLAlchemy not found in dependencies"
        ERRORS=$((ERRORS + 1))
    fi

    if grep -q "alembic" backend/pyproject.toml; then
        echo "✅ Alembic dependency found"
    else
        echo "❌ Alembic not found in dependencies"
        ERRORS=$((ERRORS + 1))
    fi
fi

if [ $ERRORS -eq 0 ]; then
    echo "✅ Architecture validation passed"
    exit 0
else
    echo "❌ Architecture validation failed with $ERRORS errors"
    exit 1
fi