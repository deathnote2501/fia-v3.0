#!/bin/bash

# Master Validation Hook
# Orchestrates all best practice validations for FIA v3.0

echo "🔍 FIA v3.0 - Best Practices Validation"
echo "======================================"

TOTAL_ERRORS=0
HOOK_DIR="$(dirname "$0")"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run a validation hook
run_validation() {
    local hook_name="$1"
    local hook_file="$2"
    local description="$3"
    
    echo -e "\n${BLUE}Running $hook_name...${NC}"
    echo "Description: $description"
    echo "----------------------------------------"
    
    if [ -f "$HOOK_DIR/$hook_file" ] && [ -x "$HOOK_DIR/$hook_file" ]; then
        if "$HOOK_DIR/$hook_file"; then
            echo -e "${GREEN}✅ $hook_name PASSED${NC}"
        else
            echo -e "${RED}❌ $hook_name FAILED${NC}"
            TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
        fi
    else
        echo -e "${YELLOW}⚠️  $hook_name hook not found or not executable${NC}"
    fi
}

# Run all validation hooks
echo "Starting comprehensive validation..."
echo "Checking compliance with SPEC.md best practices"

# 1. Architecture Validation
run_validation \
    "Architecture Validation" \
    "architecture_validation.sh" \
    "Validates hexagonal architecture and project structure"

# 2. Naming Conventions
run_validation \
    "Naming Conventions" \
    "naming_conventions.sh" \
    "Ensures English-first naming across codebase"

# 3. Security Validation
run_validation \
    "Security & Validation" \
    "security_validation.sh" \
    "Checks security practices and data validation"

# 4. Performance Validation
run_validation \
    "Performance & Scalability" \
    "performance_validation.sh" \
    "Validates performance optimizations and scalability"

# 5. Internationalization
run_validation \
    "Internationalization (i18n)" \
    "i18n_validation.sh" \
    "Ensures English-first development with i18n readiness"

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}VALIDATION SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $TOTAL_ERRORS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL VALIDATIONS PASSED!${NC}"
    echo -e "${GREEN}Your code complies with FIA v3.0 best practices.${NC}"
    echo ""
    echo "✅ Hexagonal architecture structure"
    echo "✅ English-first naming conventions"
    echo "✅ Security and validation practices"
    echo "✅ Performance optimization guidelines"
    echo "✅ Internationalization readiness"
    echo ""
    echo -e "${GREEN}Ready for development! 🚀${NC}"
    exit 0
else
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo -e "${RED}$TOTAL_ERRORS validation(s) failed${NC}"
    echo ""
    echo -e "${YELLOW}Please fix the issues above before proceeding.${NC}"
    echo ""
    echo "Key requirements from SPEC.md:"
    echo "• Use hexagonal architecture"
    echo "• English-first naming (except AI prompts)"
    echo "• No hardcoded secrets or passwords"
    echo "• Implement Pydantic validation"
    echo "• Use Gemini Context Caching with rate limiting"
    echo "• Bootstrap components only for UI"
    echo "• Poetry for dependency management"
    echo ""
    echo -e "${BLUE}For detailed requirements, check SPEC.md sections:${NC}"
    echo "- 🏗️ Architecture et Organisation"
    echo "- 🌐 Internationalisation (i18n)"
    echo "- 🔧 Configuration et Sécurité"
    echo "- ⚡ Performance et Scalabilité"
    echo "- 🤖 Intégration IA"
    echo "- 🔒 Sécurité et Validation"
    
    exit 1
fi