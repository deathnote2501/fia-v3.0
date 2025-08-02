#!/bin/bash

# Naming Conventions Validation Hook
# Ensures English-first naming conventions across the codebase

echo "📝 Validating Naming Conventions..."

ERRORS=0

# Check for French words in file names (SPEC-compliant filtering)
echo "Checking file naming conventions..."

# Only check truly French words - exclude English terms
FRENCH_ONLY_PATTERNS=(
    "formateur" "apprenant" "formation" "cours" "lecon" "exercice" "evaluation"
    "connexion" "authentification" "inscription" "tableau" "profil"
)

# English terms that are acceptable (don't flag these)
ENGLISH_TERMS=(
    "session"      # English: session (meeting, training session)
    "user"         # English: user  
    "profile"      # English: profile
    "module"       # English: module
    "trainer"      # English: trainer
    "learner"      # English: learner
    "training"     # English: training
)

echo "ℹ️  Checking for French-only terms (excluding valid English words)..."

for pattern in "${FRENCH_ONLY_PATTERNS[@]}"; do
    if find . -name "*${pattern}*" -type f 2>/dev/null | grep -v node_modules | grep -v .git | grep -v __pycache__ | grep -v ".pdf" | grep -q .; then
        echo "❌ French naming found in files containing '$pattern'"
        find . -name "*${pattern}*" -type f 2>/dev/null | grep -v node_modules | grep -v .git | grep -v __pycache__ | grep -v ".pdf" | head -3
        ERRORS=$((ERRORS + 1))
    fi
done

# Check for English terms to validate they're used correctly
echo "ℹ️  Validating English terms usage..."
ENGLISH_FOUND=0
for term in "${ENGLISH_TERMS[@]}"; do
    if find backend -name "*${term}*" -type f 2>/dev/null | grep -q .; then
        ENGLISH_FOUND=$((ENGLISH_FOUND + 1))
    fi
done

if [ $ENGLISH_FOUND -gt 0 ]; then
    echo "✅ Found $ENGLISH_FOUND English naming patterns (session, training, etc.)"
fi

# Check Python files for naming conventions
echo "Checking Python naming conventions..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check class names (should be PascalCase English) - Only truly French terms
    FRENCH_CLASS_PATTERNS="(class.*(Formateur|Apprenant|Formation|Utilisateur|Cours|Profil))"
    if find backend -name "*.py" -exec grep -l -E "$FRENCH_CLASS_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French class names found:"
        find backend -name "*.py" -exec grep -H -E "$FRENCH_CLASS_PATTERNS" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
    fi

    # Check variable names (should be snake_case English) - Only truly French terms
    FRENCH_VAR_PATTERNS="(def|=|:).*\b(formateur|apprenant|formation|utilisateur|cours|profil)\b"
    if find backend -name "*.py" -exec grep -l -E "$FRENCH_VAR_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French variable names found:"
        find backend -name "*.py" -exec grep -H -E "$FRENCH_VAR_PATTERNS" {} \; 2>/dev/null | head -5
        ERRORS=$((ERRORS + 1))
    fi

    # Check for non-English table names in models - Only truly French terms
    TABLE_PATTERNS="__tablename__.*=.*['\"].*formateur|apprenant|formation|utilisateur.*['\"]"
    if find backend -name "*.py" -exec grep -l -E "$TABLE_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French table names found:"
        find backend -name "*.py" -exec grep -H -E "$TABLE_PATTERNS" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
    fi
    
    # Validate English table names are present
    ENGLISH_TABLE_PATTERNS="__tablename__.*=.*['\"].*(training|learner|trainer|session).*['\"]"
    if find backend -name "*.py" -exec grep -l -E "$ENGLISH_TABLE_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ English table names found (training, learner, session, etc.)"
    fi

    # Check for correct English naming patterns
    echo "Validating English naming patterns..."
    
    # Look for correct patterns (this won't fail, just inform)
    CORRECT_PATTERNS=(
        "trainer" "learner" "training" "session" "user"
        "profile" "course" "lesson" "module" "exercise" "assessment"
        "login" "authentication" "registration" "dashboard"
    )
    
    FOUND_CORRECT=false
    for pattern in "${CORRECT_PATTERNS[@]}"; do
        if find backend -name "*.py" -exec grep -l "$pattern" {} \; 2>/dev/null | grep -q .; then
            FOUND_CORRECT=true
        fi
    done
    
    if [ "$FOUND_CORRECT" = true ]; then
        echo "✅ English naming patterns found"
    fi
fi

# Check route naming conventions
echo "Checking route naming conventions..."

if find backend -name "*.py" -exec grep -l "@.*router\|@app\." {} \; 2>/dev/null | grep -q .; then
    # Check for French routes - Only truly French terms
    FRENCH_ROUTES="(get|post|put|delete|patch).*['\"].*/(formateur|apprenant|formation|utilisateur|cours)"
    if find backend -name "*.py" -exec grep -l -E "$FRENCH_ROUTES" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French route names found:"
        find backend -name "*.py" -exec grep -H -E "$FRENCH_ROUTES" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
    fi
    
    # Validate English routes are present
    ENGLISH_ROUTES="(get|post|put|delete|patch).*['\"].*/((training|learner|trainer|session))"
    if find backend -name "*.py" -exec grep -l -E "$ENGLISH_ROUTES" {} \; 2>/dev/null | grep -q .; then
        echo "✅ English route names found (/training, /session, etc.)"
    fi

    # Check for kebab-case in routes (should be /api/training-sessions not /api/training_sessions)
    SNAKE_CASE_ROUTES="['\"]/.*/[a-z]+_[a-z]+"
    if find backend -name "*.py" -exec grep -l -E "$SNAKE_CASE_ROUTES" {} \; 2>/dev/null | grep -q .; then
        echo "⚠️  Snake_case found in routes (should be kebab-case):"
        find backend -name "*.py" -exec grep -H -E "$SNAKE_CASE_ROUTES" {} \; 2>/dev/null
    fi
fi

# Check JavaScript naming conventions
echo "Checking JavaScript naming conventions..."

if find frontend -name "*.js" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for French variable names in JS - Only truly French terms
    JS_FRENCH_PATTERNS="(const|let|var|function).*\b(formateur|apprenant|formation|utilisateur|cours)\b"
    if find frontend -name "*.js" -exec grep -l -E "$JS_FRENCH_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French naming in JavaScript files:"
        find frontend -name "*.js" -exec grep -H -E "$JS_FRENCH_PATTERNS" {} \; 2>/dev/null | head -5
        ERRORS=$((ERRORS + 1))
    fi
    
    # Validate English JS patterns
    JS_ENGLISH_PATTERNS="(const|let|var|function).*\b(trainer|learner|training|session|user)\b"
    if find frontend -name "*.js" -exec grep -l -E "$JS_ENGLISH_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ English naming in JavaScript files (trainer, session, etc.)"
    fi
fi

# Check HTML naming conventions
echo "Checking HTML naming conventions..."

if find frontend -name "*.html" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for French IDs and classes
    HTML_FRENCH_PATTERNS="(id|class)=['\"][^'\"]*formateur|apprenant|formation"
    if find frontend -name "*.html" -exec grep -l -E "$HTML_FRENCH_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French IDs/classes in HTML files:"
        find frontend -name "*.html" -exec grep -H -E "$HTML_FRENCH_PATTERNS" {} \; 2>/dev/null | head -5
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check database migration files
echo "Checking database migration naming..."

if find backend/alembic -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for French table/column names in migrations
    MIGRATION_FRENCH="(create_table|add_column|drop_table).*formateur|apprenant|formation"
    if find backend/alembic -name "*.py" -exec grep -l -E "$MIGRATION_FRENCH" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French naming in database migrations:"
        find backend/alembic -name "*.py" -exec grep -H -E "$MIGRATION_FRENCH" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
    fi
fi

if [ $ERRORS -eq 0 ]; then
    echo "✅ Naming conventions validation passed"
    exit 0
else
    echo "❌ Naming conventions validation failed with $ERRORS errors"
    echo "Remember: Use English names for all variables, classes, tables, routes, and identifiers"
    echo "Exception: AI prompts can be in target languages (French, English, etc.)"
    exit 1
fi