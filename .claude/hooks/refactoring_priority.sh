#!/bin/bash

# Refactoring Priority Analysis Hook
# Identifie et priorise les violations pour refactorisation SMART KISS

echo "🔧 FIA v3.0 - Refactoring Priority Analysis"
echo "==========================================="

# Initialisation
CRITICAL_ISSUES=0
IMPORTANT_ISSUES=0
MINOR_ISSUES=0

# Couleurs
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "\n${BLUE}🎯 ANALYSE DES VIOLATIONS POUR REFACTORISATION${NC}"
echo "==============================================="

# 1. VIOLATIONS CRITIQUES (Risque casse: 80-95%)
echo -e "\n${RED}🔴 VIOLATIONS CRITIQUES (Urgent - Risque élevé)${NC}"
echo "------------------------------------------------"

# Services dupliqués
if [ -d "backend/app/domain/services" ] && [ -d "backend/app/services" ]; then
    echo "❌ CRITIQUE: Services dupliqués (Risque: 95%)"
    echo "   - backend/app/domain/services/ (13 services)"
    echo "   - backend/app/services/ (10 services)"
    echo "   Impact: Import conflicts, confusion architecture"
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi

# Controllers dupliqués
if [ -d "backend/app/adapters/inbound" ] && [ -d "backend/app/controllers" ]; then
    echo "❌ CRITIQUE: Controllers dupliqués (Risque: 60%)"
    echo "   - backend/app/adapters/inbound/ (hexagonal)"
    echo "   - backend/app/controllers/ (legacy)"
    echo "   Impact: Routes conflicts, architecture mixte"
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi

# Imports infrastructure dans domain
INFRA_IMPORTS=$(find backend/app/domain -name "*.py" -exec grep -l "from app\.infrastructure" {} \; 2>/dev/null | wc -l)
if [ "$INFRA_IMPORTS" -gt 0 ]; then
    echo "❌ CRITIQUE: $INFRA_IMPORTS domain services importent infrastructure (Risque: 80%)"
    echo "   Impact: Violation hexagonale, tests impossibles isolation"
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
fi

# 2. VIOLATIONS IMPORTANTES (Risque modéré: 40-60%)
echo -e "\n${YELLOW}🟡 VIOLATIONS IMPORTANTES (À planifier)${NC}"
echo "----------------------------------------------"

# FastAPI imports dans domain
FASTAPI_IMPORTS=$(find backend/app/domain -name "*.py" -exec grep -l "fastapi" {} \; 2>/dev/null | wc -l)
if [ "$FASTAPI_IMPORTS" -gt 0 ]; then
    echo "⚠️  IMPORTANT: $FASTAPI_IMPORTS fichiers avec imports FastAPI dans domain"
    echo "   Impact: Coupling framework, authentification fragile"
    IMPORTANT_ISSUES=$((IMPORTANT_ISSUES + 1))
fi

# Pagination manquante
PAGINATION_COUNT=$(find backend/app/adapters/repositories -name "*.py" -exec grep -l "\.limit\|\.offset" {} \; 2>/dev/null | wc -l)
if [ "$PAGINATION_COUNT" -lt 3 ]; then
    echo "⚠️  IMPORTANT: Pagination manquante dans repositories ($PAGINATION_COUNT/8)"
    echo "   Impact: Performance dégradée, scalabilité limitée"
    IMPORTANT_ISSUES=$((IMPORTANT_ISSUES + 1))
fi

# Index database manquants
INDEX_COUNT=$(find backend/alembic/versions -name "*.py" -exec grep -l "create_index\|Index(" {} \; 2>/dev/null | wc -l)
if [ "$INDEX_COUNT" -lt 2 ]; then
    echo "⚠️  IMPORTANT: Index database manquants ($INDEX_COUNT migrations avec index)"
    echo "   Impact: Requêtes lentes, performance DB"
    IMPORTANT_ISSUES=$((IMPORTANT_ISSUES + 1))
fi

# 3. VIOLATIONS MINEURES (Tolérables: <20%)
echo -e "\n${GREEN}🟢 VIOLATIONS MINEURES (Tolérables temporairement)${NC}"
echo "----------------------------------------------------"

# Termes français
FRENCH_COUNT=$(find backend/app/domain -name "*.py" -exec grep -l "formateur\|apprenant\|formation" {} \; 2>/dev/null | wc -l)
if [ "$FRENCH_COUNT" -gt 0 ]; then
    echo "📝 MINEUR: $FRENCH_COUNT fichiers avec termes français"
    echo "   Impact: Cosmétique, lisibilité internationale"
    MINOR_ISSUES=$((MINOR_ISSUES + 1))
fi

# Logs français
LOGS_FRENCH=$(find backend -name "*.py" -exec grep -l "logger.*['\"].*[àéèêç]" {} \; 2>/dev/null | wc -l)
if [ "$LOGS_FRENCH" -gt 0 ]; then
    echo "📝 MINEUR: $LOGS_FRENCH fichiers avec logs en français"
    echo "   Impact: Maintenance internationale"
    MINOR_ISSUES=$((MINOR_ISSUES + 1))
fi

# 4. CALCUL PRIORITÉS REFACTORISATION
echo -e "\n${BLUE}📊 PRIORISATION REFACTORISATION${NC}"
echo "================================="

TOTAL_ISSUES=$((CRITICAL_ISSUES + IMPORTANT_ISSUES + MINOR_ISSUES))
REFACTOR_SCORE=$((CRITICAL_ISSUES * 10 + IMPORTANT_ISSUES * 5 + MINOR_ISSUES * 1))

echo "Issues Critiques: $CRITICAL_ISSUES (×10 = $((CRITICAL_ISSUES * 10)) points)"
echo "Issues Importantes: $IMPORTANT_ISSUES (×5 = $((IMPORTANT_ISSUES * 5)) points)"
echo "Issues Mineures: $MINOR_ISSUES (×1 = $MINOR_ISSUES points)"
echo "Score Total: $REFACTOR_SCORE/100"

# 5. RECOMMANDATION STRATÉGIE
echo -e "\n${BLUE}🎯 STRATÉGIE RECOMMANDÉE${NC}"
echo "========================="

if [ $CRITICAL_ISSUES -gt 0 ]; then
    echo -e "${RED}🚨 URGENT: Refactorisation nécessaire${NC}"
    echo "• Commencer par violations critiques"
    echo "• Développement parallèle recommandé"
    echo "• Tests de régression intensifs"
elif [ $IMPORTANT_ISSUES -gt 2 ]; then
    echo -e "${YELLOW}⚠️  PLANIFIÉ: Refactorisation recommandée${NC}"
    echo "• Planifier refactorisation par phases"
    echo "• Tests unitaires avant modifications"
elif [ $TOTAL_ISSUES -gt 0 ]; then
    echo -e "${GREEN}✅ STABLE: Améliorations cosmétiques${NC}"
    echo "• Corrections mineures en continu"
    echo "• Pas de refactorisation urgente"
else
    echo -e "${GREEN}🎉 EXCELLENT: Architecture compliant${NC}"
    echo "• Aucune refactorisation nécessaire"
fi

# 6. COMPOSANTS INDÉPENDANTS IDENTIFIÉS
echo -e "\n${BLUE}🔧 COMPOSANTS REFACTORISABLES INDÉPENDAMMENT${NC}"
echo "==================================================="

echo "✅ Composants SAFE (refactorisation sans risque):"
echo "  • Naming conventions (termes français → anglais)"
echo "  • Logging format (français → anglais)" 
echo "  • Documentation (commentaires → anglais)"
echo "  • Tests (variables → anglais)"

echo ""
echo "⚠️  Composants MODERATE (tests requis):"
echo "  • Repository pagination (ajout limit/offset)"
echo "  • Database indexes (nouvelles migrations)"
echo "  • Domain imports (refactoring ports)"

echo ""
echo "🔴 Composants RISKY (développement parallèle):"
echo "  • Services duplication (consolidation)"
echo "  • Controllers structure (unification)"
echo "  • Architecture hexagonale (domain purity)"

# Exit avec code basé sur criticité
if [ $CRITICAL_ISSUES -gt 0 ]; then
    exit 2  # Critique
elif [ $IMPORTANT_ISSUES -gt 2 ]; then
    exit 1  # Important
else
    exit 0  # OK
fi