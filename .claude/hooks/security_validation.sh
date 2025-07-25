#!/bin/bash

# Security and Validation Hook
# Ensures security best practices and data validation compliance

echo "🔒 Validating Security & Data Validation..."

ERRORS=0

# Check for hardcoded secrets/passwords
echo "Checking for hardcoded secrets..."

HARDCODED_PATTERNS=(
    "password.*=.*['\"][^'\"]{1,}"
    "secret.*=.*['\"][^'\"]{1,}"
    "api_key.*=.*['\"][^'\"]{1,}"
    "token.*=.*['\"][^'\"]{1,}"
    "DATABASE_URL.*=.*['\"].*://"
    "GEMINI_API_KEY.*=.*['\"][^'\"]{1,}"
)

for pattern in "${HARDCODED_PATTERNS[@]}"; do
    if find . -name "*.py" -o -name "*.js" -o -name "*.html" | xargs grep -l -E "$pattern" 2>/dev/null | grep -v .git | grep -q .; then
        echo "❌ Potential hardcoded secrets found:"
        find . -name "*.py" -o -name "*.js" -o -name "*.html" | xargs grep -H -E "$pattern" 2>/dev/null | grep -v .git | head -3
        ERRORS=$((ERRORS + 1))
    fi
done

# Check for environment variable usage
echo "Checking environment variable usage..."

if find backend -name "*.py" -exec grep -l "os.getenv\|os.environ\|settings\." {} \; 2>/dev/null | grep -q .; then
    echo "✅ Environment variables usage found"
else
    echo "⚠️  No environment variable usage found - ensure configuration is externalized"
fi

# Check for password hashing
echo "Checking password handling..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for plain text password storage
    PLAIN_PASSWORDS="password.*=.*request\.|password.*=.*form\."
    if find backend -name "*.py" -exec grep -l -E "$PLAIN_PASSWORDS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ Potential plain text password handling:"
        find backend -name "*.py" -exec grep -H -E "$PLAIN_PASSWORDS" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
    fi

    # Check for password hashing libraries
    HASH_PATTERNS="bcrypt|passlib|hashlib|pwd_context"
    if find backend -name "*.py" -exec grep -l -E "$HASH_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Password hashing library usage found"
    else
        echo "⚠️  No password hashing libraries found - ensure passwords are properly hashed"
    fi
fi

# Check for Pydantic validation
echo "Checking Pydantic validation..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for Pydantic imports
    if find backend -name "*.py" -exec grep -l "from pydantic\|import pydantic" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Pydantic validation found"
    else
        echo "⚠️  No Pydantic validation found - ensure data validation is implemented"
    fi

    # Check for BaseModel usage
    if find backend -name "*.py" -exec grep -l "BaseModel" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Pydantic BaseModel usage found"
    fi

    # Check for endpoints without validation
    ENDPOINT_PATTERNS="@.*\.(post|put|patch).*\("
    VALIDATION_PATTERNS=":\s*(BaseModel|.*Schema)"
    
    if find backend -name "*.py" -exec grep -l -E "$ENDPOINT_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ POST/PUT/PATCH endpoints found"
        
        # Check if these endpoints have validation
        for file in $(find backend -name "*.py" -exec grep -l -E "$ENDPOINT_PATTERNS" {} \; 2>/dev/null); do
            if ! grep -q -E "$VALIDATION_PATTERNS" "$file" 2>/dev/null; then
                echo "⚠️  Endpoint without validation in: $file"
            fi
        done
    fi
fi

# Check for SQL injection protection
echo "Checking SQL injection protection..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for dangerous SQL patterns
    DANGEROUS_SQL="execute.*%.*s|execute.*\+.*|execute.*f['\"]"
    if find backend -name "*.py" -exec grep -l -E "$DANGEROUS_SQL" {} \; 2>/dev/null | grep -q .; then
        echo "❌ Potential SQL injection vulnerability:"
        find backend -name "*.py" -exec grep -H -E "$DANGEROUS_SQL" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
    fi

    # Check for SQLAlchemy ORM usage (safer)
    if find backend -name "*.py" -exec grep -l "from sqlalchemy\|import sqlalchemy" {} \; 2>/dev/null | grep -q .; then
        echo "✅ SQLAlchemy ORM usage found"
    fi
fi

# Check for error information leakage
echo "Checking error handling..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for detailed error exposure
    ERROR_EXPOSURE="raise.*Exception.*request\.|return.*error.*traceback"
    if find backend -name "*.py" -exec grep -l -E "$ERROR_EXPOSURE" {} \; 2>/dev/null | grep -q .; then
        echo "⚠️  Potential error information leakage found"
        find backend -name "*.py" -exec grep -H -E "$ERROR_EXPOSURE" {} \; 2>/dev/null | head -3
    fi

    # Check for proper exception handling
    if find backend -name "*.py" -exec grep -l "try:\|except:" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Exception handling found"
    fi
fi

# Check for authentication implementation
echo "Checking authentication..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for FastAPI-Users or JWT implementation
    AUTH_PATTERNS="fastapi_users|jwt|token|authenticate"
    if find backend -name "*.py" -exec grep -l -E "$AUTH_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Authentication implementation found"
    else
        echo "⚠️  No authentication implementation found"
    fi

    # Check for protected endpoints
    PROTECTION_PATTERNS="Depends.*auth|Depends.*get_current"
    if find backend -name "*.py" -exec grep -l -E "$PROTECTION_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Protected endpoints found"
    fi
fi

# Check for CORS configuration
echo "Checking CORS configuration..."

if find backend -name "*.py" -exec grep -l "CORSMiddleware\|cors" {} \; 2>/dev/null | grep -q .; then
    echo "✅ CORS configuration found"
    
    # Check for wildcard CORS (security risk)
    if find backend -name "*.py" -exec grep -l "allow_origins.*\[\"\*\"\]" {} \; 2>/dev/null | grep -q .; then
        echo "⚠️  Wildcard CORS found - ensure it's only for development"
    fi
else
    echo "⚠️  No CORS configuration found"
fi

# Check frontend security
echo "Checking frontend security..."

if find frontend -name "*.js" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for XSS vulnerabilities
    XSS_PATTERNS="innerHTML.*\+|innerHTML.*user|eval\("
    if find frontend -name "*.js" -exec grep -l -E "$XSS_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ Potential XSS vulnerability in frontend:"
        find frontend -name "*.js" -exec grep -H -E "$XSS_PATTERNS" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
    fi

    # Check for safe DOM manipulation
    SAFE_PATTERNS="textContent|createElement|setAttribute"
    if find frontend -name "*.js" -exec grep -l -E "$SAFE_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Safe DOM manipulation patterns found"
    fi
fi

if [ $ERRORS -eq 0 ]; then
    echo "✅ Security validation passed"
    exit 0
else
    echo "❌ Security validation failed with $ERRORS errors"
    echo "Critical security issues found! Please fix before proceeding."
    exit 1
fi