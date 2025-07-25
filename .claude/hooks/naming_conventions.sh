#!/bin/bash

# Naming Conventions Validation Hook
# Ensures English-first naming conventions across the codebase

echo "📝 Validating Naming Conventions..."

ERRORS=0

# Check for French words in file names
echo "Checking file naming conventions..."

FRENCH_PATTERNS=(
    "formateur" "apprenant" "formation" "session" "utilisateur" 
    "profil" "cours" "lecon" "module" "exercice" "evaluation"
    "connexion" "authentification" "inscription" "tableau"
)

for pattern in "${FRENCH_PATTERNS[@]}"; do
    if find . -name "*${pattern}*" -type f 2>/dev/null | grep -v node_modules | grep -v .git | grep -q .; then
        echo "❌ French naming found in files containing '$pattern'"
        find . -name "*${pattern}*" -type f 2>/dev/null | grep -v node_modules | grep -v .git
        ERRORS=$((ERRORS + 1))
    fi
done

# Check Python files for naming conventions
echo "Checking Python naming conventions..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check class names (should be PascalCase English)
    FRENCH_CLASS_PATTERNS="(class.*(Formateur|Apprenant|Formation|Session|Utilisateur|Profil))"
    if find backend -name "*.py" -exec grep -l -E "$FRENCH_CLASS_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French class names found:"
        find backend -name "*.py" -exec grep -H -E "$FRENCH_CLASS_PATTERNS" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
    fi

    # Check variable names (should be snake_case English)
    FRENCH_VAR_PATTERNS="(def|=|:).*\b(formateur|apprenant|formation|session|utilisateur|profil)\b"
    if find backend -name "*.py" -exec grep -l -E "$FRENCH_VAR_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French variable names found:"
        find backend -name "*.py" -exec grep -H -E "$FRENCH_VAR_PATTERNS" {} \; 2>/dev/null | head -5
        ERRORS=$((ERRORS + 1))
    fi

    # Check for non-English table names in models
    TABLE_PATTERNS="__tablename__.*=.*['\"].*formateur|apprenant|formation|session.*['\"]"
    if find backend -name "*.py" -exec grep -l -E "$TABLE_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French table names found:"
        find backend -name "*.py" -exec grep -H -E "$TABLE_PATTERNS" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
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
    # Check for French routes
    FRENCH_ROUTES="(get|post|put|delete|patch).*['\"].*/(formateur|apprenant|formation)"
    if find backend -name "*.py" -exec grep -l -E "$FRENCH_ROUTES" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French route names found:"
        find backend -name "*.py" -exec grep -H -E "$FRENCH_ROUTES" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
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
    # Check for French variable names in JS
    JS_FRENCH_PATTERNS="(const|let|var|function).*\b(formateur|apprenant|formation|session|utilisateur)\b"
    if find frontend -name "*.js" -exec grep -l -E "$JS_FRENCH_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French naming in JavaScript files:"
        find frontend -name "*.js" -exec grep -H -E "$JS_FRENCH_PATTERNS" {} \; 2>/dev/null | head -5
        ERRORS=$((ERRORS + 1))
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