#!/bin/bash

# Quick Hook Test - Non-blocking version for development
# Tests hooks with reduced scope for faster validation

echo "🧪 FIA v3.0 - Quick Hook Test"
echo "============================="

ERRORS=0

# Test 1: Architecture - Critical violations only
echo "🏗️ Testing Architecture (Critical only)..."
if [ -d "backend/app/domain/services" ] && [ -d "backend/app/services" ]; then
    echo "❌ CRITICAL: Duplicate services directories"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ Services structure OK"
fi

# Test 2: Domain purity - Infrastructure imports  
echo "🎯 Testing Domain Purity..."
if find backend/app/domain -name "*.py" -exec grep -l "from app\.infrastructure" {} \; 2>/dev/null | grep -q .; then
    echo "❌ Infrastructure imports in domain:"
    find backend/app/domain -name "*.py" -exec grep -H "from app\.infrastructure" {} \; 2>/dev/null | head -2
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No infrastructure imports in domain"
fi

# Test 3: Performance - Context cache and rate limiting
echo "⚡ Testing Performance..."
if find backend -name "*.py" -exec grep -l "context_cache\|ContextCacheService" {} \; 2>/dev/null | grep -q .; then
    echo "✅ Context caching found"
else
    echo "⚠️  Context caching not detected"
fi

if find backend -name "*.py" -exec grep -l "rate_limiter\|gemini_rate_limiter" {} \; 2>/dev/null | grep -q .; then
    echo "✅ Rate limiting found"
else
    echo "⚠️  Rate limiting not detected"
fi

# Test 4: Naming - French terms (reduced scope)
echo "📝 Testing Naming (French terms)..."
FRENCH_COUNT=$(find backend/app/domain -name "*.py" -exec grep -l "formateur\|apprenant\|formation" {} \; 2>/dev/null | wc -l)
if [ "$FRENCH_COUNT" -gt 0 ]; then
    echo "⚠️  $FRENCH_COUNT files with French terms in domain"
else
    echo "✅ No French terms in domain layer"
fi

# Summary
echo ""
echo "📊 QUICK TEST SUMMARY"
echo "===================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ Quick validation passed! ($ERRORS critical errors)"
    echo "🚀 Ready for development"
else
    echo "❌ $ERRORS critical errors found"
    echo "⚠️  Fix critical issues before proceeding"
fi

exit $ERRORS