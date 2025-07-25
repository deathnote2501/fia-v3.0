#!/bin/bash

# Internationalization (i18n) Validation Hook
# Ensures English-first development with i18n architecture readiness

echo "🌐 Validating Internationalization (i18n)..."

ERRORS=0

# Check for English-first implementation
echo "Checking English-first implementation..."

# Check for hardcoded French text in UI
echo "Checking for hardcoded text in UI files..."

FRENCH_UI_TEXTS=(
    "Connexion" "Inscription" "Formateur" "Apprenant" "Formation"
    "Créer" "Modifier" "Supprimer" "Valider" "Annuler"
    "Tableau de bord" "Profil" "Session" "Cours" "Leçon"
    "Enregistrer" "Télécharger" "Charger" "Suivant" "Précédent"
)

if find frontend -name "*.html" -type f 2>/dev/null | head -1 | grep -q .; then
    for text in "${FRENCH_UI_TEXTS[@]}"; do
        if find frontend -name "*.html" -exec grep -l "$text" {} \; 2>/dev/null | grep -q .; then
            echo "❌ French UI text found: '$text'"
            find frontend -name "*.html" -exec grep -H "$text" {} \; 2>/dev/null | head -2
            ERRORS=$((ERRORS + 1))
        fi
    done
fi

# Check for hardcoded French text in JavaScript
if find frontend -name "*.js" -type f 2>/dev/null | head -1 | grep -q .; then
    for text in "${FRENCH_UI_TEXTS[@]}"; do
        if find frontend -name "*.js" -exec grep -l "$text" {} \; 2>/dev/null | grep -q .; then
            echo "❌ French UI text found in JS: '$text'"
            find frontend -name "*.js" -exec grep -H "$text" {} \; 2>/dev/null | head -2
            ERRORS=$((ERRORS + 1))
        fi
    done
fi

# Check for proper English UI texts
ENGLISH_UI_TEXTS=(
    "Login" "Registration" "Trainer" "Learner" "Training"
    "Create" "Edit" "Delete" "Validate" "Cancel"
    "Dashboard" "Profile" "Session" "Course" "Lesson"
    "Save" "Download" "Upload" "Next" "Previous"
)

ENGLISH_FOUND=false
if find frontend -name "*.html" -o -name "*.js" -type f 2>/dev/null | head -1 | grep -q .; then
    for text in "${ENGLISH_UI_TEXTS[@]}"; do
        if find frontend -name "*.html" -o -name "*.js" -exec grep -l "$text" {} \; 2>/dev/null | grep -q .; then
            ENGLISH_FOUND=true
            break
        fi
    done
    
    if [ "$ENGLISH_FOUND" = true ]; then
        echo "✅ English UI texts found"
    else
        echo "⚠️  No English UI texts found yet"
    fi
fi

# Check for i18n architecture readiness
echo "Checking i18n architecture readiness..."

# Check for translation file structure
if [ -d "frontend/src/i18n" ] || [ -d "frontend/locales" ] || [ -f "frontend/src/i18n.js" ]; then
    echo "✅ i18n structure found"
else
    echo "⚠️  No i18n structure found - should be prepared for future translations"
fi

# Check for i18n libraries
if find frontend -name "*.js" -exec grep -l "i18n\|translate\|locale" {} \; 2>/dev/null | grep -q .; then
    echo "✅ i18n library usage found"
else
    echo "⚠️  No i18n library found - consider preparing for future translations"
fi

# Check backend for English message patterns
echo "Checking backend messages..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for French error messages
    FRENCH_MESSAGES="\".*[Ee]rreur.*\"|\".*[Ss]uccès.*\"|\".*[Éé]chec.*\""
    if find backend -name "*.py" -exec grep -l -E "$FRENCH_MESSAGES" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French error messages found:"
        find backend -name "*.py" -exec grep -H -E "$FRENCH_MESSAGES" {} \; 2>/dev/null | head -3
        ERRORS=$((ERRORS + 1))
    fi

    # Check for English messages
    ENGLISH_MESSAGES="\".*[Ee]rror.*\"|\".*[Ss]uccess.*\"|\".*[Ff]ailed.*\""
    if find backend -name "*.py" -exec grep -l -E "$ENGLISH_MESSAGES" {} \; 2>/dev/null | grep -q .; then
        echo "✅ English messages found"
    fi

    # Check for message centralization patterns
    MESSAGE_PATTERNS="messages\.|constants\.|MESSAGES|ERROR_MESSAGES"
    if find backend -name "*.py" -exec grep -l -E "$MESSAGE_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Message centralization patterns found"
    else
        echo "⚠️  No message centralization found - consider centralizing for i18n"
    fi
fi

# Check for locale handling
echo "Checking locale handling..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for locale detection
    LOCALE_PATTERNS="locale|accept.*language|lang.*header"
    if find backend -name "*.py" -exec grep -l -E "$LOCALE_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Locale handling patterns found"
    else
        echo "⚠️  No locale handling found - should detect browser language"
    fi
fi

# Check for language-specific prompts (allowed exception)
echo "Checking AI prompt language handling..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for prompt templates or language-specific content
    PROMPT_PATTERNS="prompt.*french|prompt.*english|lang.*prompt|prompt.*{.*lang"
    if find backend -name "*.py" -exec grep -l -E "$PROMPT_PATTERNS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ Language-specific prompt handling found (allowed exception)"
    else
        echo "⚠️  No language-specific prompt handling - AI prompts should support target languages"
    fi
fi

# Check URL naming (should be English)
echo "Checking URL internationalization..."

if find backend -name "*.py" -type f 2>/dev/null | head -1 | grep -q .; then
    # Check for French URLs
    FRENCH_URLS="route.*formateur|route.*apprenant|route.*formation|path.*formateur"
    if find backend -name "*.py" -exec grep -l -E "$FRENCH_URLS" {} \; 2>/dev/null | grep -q .; then
        echo "❌ French URLs found:"
        find backend -name "*.py" -exec grep -H -E "$FRENCH_URLS" {} \; 2>/dev/null
        ERRORS=$((ERRORS + 1))
    fi

    # Check for English URLs
    ENGLISH_URLS="route.*trainer|route.*learner|route.*training|path.*trainer"
    if find backend -name "*.py" -exec grep -l -E "$ENGLISH_URLS" {} \; 2>/dev/null | grep -q .; then
        echo "✅ English URLs found"
    fi
fi

# Check frontend file naming
echo "Checking frontend file naming..."

if find frontend -name "*formateur*" -o -name "*apprenant*" -o -name "*formation*" 2>/dev/null | grep -q .; then
    echo "❌ French file names found:"
    find frontend -name "*formateur*" -o -name "*apprenant*" -o -name "*formation*" 2>/dev/null
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No French file names found"
fi

# Check for internationalization best practices
echo "Checking i18n best practices..."

# Check for date/time formatting
if find backend -name "*.py" -exec grep -l "datetime.*format\|strftime" {} \; 2>/dev/null | grep -q .; then
    echo "✅ Date formatting found - ensure locale-aware formatting"
fi

# Check for number formatting
if find backend -name "*.py" -exec grep -l "format.*currency\|locale.*format" {} \; 2>/dev/null | grep -q .; then
    echo "✅ Number formatting found"
fi

# Summary and recommendations
echo "Providing i18n recommendations..."

if [ ! -d "frontend/src/i18n" ]; then
    echo "📝 Recommendation: Create frontend/src/i18n/ structure for future translations"
fi

if [ ! -f "backend/app/i18n/messages.py" ]; then
    echo "📝 Recommendation: Create backend message centralization for i18n readiness"
fi

echo "📝 Remember: AI prompts are the ONLY exception - they can be in target languages (French, English, etc.)"

if [ $ERRORS -eq 0 ]; then
    echo "✅ i18n validation passed"
    exit 0
else
    echo "❌ i18n validation failed with $ERRORS errors"
    echo "English-first development violations found! Please fix before proceeding."
    exit 1
fi