"""
FIA v3.0 - Slide Structure Formatter
Service pour formater les slides de structure (PLAN/STAGE/MODULE) sans IA
"""

import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SlideStructureFormatter:
    """Service pour formater les slides de structure basées sur le plan JSON"""
    
    def __init__(self):
        """Initialize slide structure formatter"""
        logger.info("🏗️ SLIDE STRUCTURE FORMATTER [SERVICE] Initialized")
    
    def format_plan_slide(self, training_plan: Any, slide_title: str) -> str:
        """
        Formater une slide PLAN : Vue d'ensemble complète de la formation
        
        Structure :
        - Étapes en titre 1 : #
        - Modules en titre 2 : ##
        - Sous-modules en liste : -
        
        Args:
            training_plan: Plan de formation entity
            slide_title: Titre de la slide
            
        Returns:
            Contenu markdown formaté
        """
        logger.info(f"🏗️ SLIDE STRUCTURE FORMATTER [PLAN] Formatting plan slide: {slide_title}")
        
        # Extraire la structure du plan
        plan_structure = self._extract_plan_data(training_plan)
        if not plan_structure:
            return self._format_fallback_plan(slide_title)
        
        # Construire le markdown
        markdown_lines = [f"# {slide_title}", ""]
        
        stages = plan_structure.get("stages", [])
        for stage in stages:
            stage_number = stage.get("stage_number", "?")
            stage_title = stage.get("title", "Étape sans titre")
            
            # Étape en titre 1
            markdown_lines.append(f"# Étape {stage_number}: {stage_title}")
            
            modules = stage.get("modules", [])
            for module in modules:
                module_name = module.get("module_name", "Module sans nom")
                
                # Module en titre 2
                markdown_lines.append(f"## {module_name}")
                
                submodules = module.get("submodules", [])
                for submodule in submodules:
                    submodule_name = submodule.get("submodule_name", "Sous-module sans nom")
                    
                    # Sous-module en liste
                    markdown_lines.append(f"- {submodule_name}")
                
                if submodules:
                    markdown_lines.append("")  # Ligne vide après les sous-modules
        
        result = "\n".join(markdown_lines).strip()
        logger.info(f"✅ SLIDE STRUCTURE FORMATTER [PLAN] Generated {len(result)} characters")
        return result
    
    def format_stage_slide(self, training_plan: Any, slide_title: str) -> str:
        """
        Formater une slide ÉTAPE : Introduction d'une étape spécifique
        
        Structure :
        - Modules en titre 1 : #
        - Sous-modules en titre 2 : ##
        - Slides en liste : -
        
        Args:
            training_plan: Plan de formation entity
            slide_title: Titre de la slide
            
        Returns:
            Contenu markdown formaté
        """
        logger.info(f"🏗️ SLIDE STRUCTURE FORMATTER [STAGE] Formatting stage slide: {slide_title}")
        
        # Extraire les données de l'étape
        stage_data = self._extract_stage_data(training_plan, slide_title)
        if not stage_data:
            return self._format_fallback_stage(slide_title)
        
        # Construire le markdown
        stage_number = stage_data.get("stage_number", "?")
        stage_title_clean = stage_data.get("title", "Étape")
        
        markdown_lines = [
            f"# Étape {stage_number}: {stage_title_clean}",
            ""
        ]
        
        modules = stage_data.get("modules", [])
        for module in modules:
            module_name = module.get("module_name", "Module sans nom")
            
            # Module en titre 1
            markdown_lines.append(f"# {module_name}")
            
            submodules = module.get("submodules", [])
            for submodule in submodules:
                submodule_name = submodule.get("submodule_name", "Sous-module sans nom")
                
                # Sous-module en titre 2
                markdown_lines.append(f"## {submodule_name}")
                
                slide_titles = submodule.get("slide_titles", [])
                for slide_title_item in slide_titles:
                    # Slide en liste
                    markdown_lines.append(f"- {slide_title_item}")
                
                if slide_titles:
                    markdown_lines.append("")  # Ligne vide après les slides
        
        result = "\n".join(markdown_lines).strip()
        logger.info(f"✅ SLIDE STRUCTURE FORMATTER [STAGE] Generated {len(result)} characters")
        return result
    
    def format_module_slide(
        self, 
        training_plan: Any, 
        slide_title: str, 
        learner_profile: Any,
        ai_introduction: Optional[str] = None
    ) -> str:
        """
        Formater une slide MODULE : Introduction d'un module spécifique
        
        Structure :
        - Introduction de l'IA (texte personnalisé)
        - Sous-modules en titre 1 : #
        - Slides en liste : -
        
        Args:
            training_plan: Plan de formation entity
            slide_title: Titre de la slide
            learner_profile: Profil de l'apprenant pour l'introduction IA
            ai_introduction: Introduction générée par l'IA (optionnel)
            
        Returns:
            Contenu markdown formaté
        """
        logger.info(f"🏗️ SLIDE STRUCTURE FORMATTER [MODULE] Formatting module slide: {slide_title}")
        
        # Extraire les données du module
        module_data = self._extract_module_data(training_plan, slide_title)
        if not module_data:
            return self._format_fallback_module(slide_title, ai_introduction)
        
        # Construire le markdown
        module_name = module_data.get("module_name", "Module")
        
        markdown_lines = [f"# {module_name}", ""]
        
        # Ajouter l'introduction IA si fournie
        if ai_introduction:
            markdown_lines.extend([ai_introduction, ""])
        else:
            # Introduction par défaut
            learner_context = getattr(learner_profile, 'job_and_sector', 'votre contexte professionnel')
            default_intro = f"Dans ce module, vous allez découvrir les concepts essentiels adaptés à {learner_context}. Chaque sous-module vous permettra de progresser étape par étape."
            markdown_lines.extend([default_intro, ""])
        
        submodules = module_data.get("submodules", [])
        for submodule in submodules:
            submodule_name = submodule.get("submodule_name", "Sous-module sans nom")
            
            # Sous-module en titre 1
            markdown_lines.append(f"# {submodule_name}")
            
            slide_titles = submodule.get("slide_titles", [])
            for slide_title_item in slide_titles:
                # Slide en liste
                markdown_lines.append(f"- {slide_title_item}")
            
            if slide_titles:
                markdown_lines.append("")  # Ligne vide après les slides
        
        result = "\n".join(markdown_lines).strip()
        logger.info(f"✅ SLIDE STRUCTURE FORMATTER [MODULE] Generated {len(result)} characters")
        return result
    
    # ===== Méthodes privées d'extraction =====
    
    def _extract_plan_data(self, training_plan: Any) -> Optional[Dict[str, Any]]:
        """Extraire les données du plan de formation"""
        if not hasattr(training_plan, 'plan_data') or not training_plan.plan_data:
            return None
        
        try:
            plan_data = training_plan.plan_data if isinstance(training_plan.plan_data, dict) else json.loads(training_plan.plan_data)
            return plan_data.get("training_plan", {})
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"❌ SLIDE STRUCTURE FORMATTER [ERROR] Failed to parse plan data: {e}")
            return None
    
    def _extract_stage_data(self, training_plan: Any, slide_title: str) -> Optional[Dict[str, Any]]:
        """Extraire les données d'une étape spécifique"""
        plan_data = self._extract_plan_data(training_plan)
        if not plan_data:
            return None
        
        stages = plan_data.get("stages", [])
        
        # Chercher l'étape correspondante au titre
        for stage in stages:
            stage_title = stage.get("title", "")
            stage_number = stage.get("stage_number", 0)
            
            # Vérifier la correspondance avec le titre de la slide
            if (stage_title.lower() in slide_title.lower() or 
                f"étape {stage_number}" in slide_title.lower() or
                f"stage {stage_number}" in slide_title.lower()):
                return stage
        
        # Si aucune correspondance, retourner la première étape
        return stages[0] if stages else None
    
    def _extract_module_data(self, training_plan: Any, slide_title: str) -> Optional[Dict[str, Any]]:
        """Extraire les données d'un module spécifique"""
        plan_data = self._extract_plan_data(training_plan)
        if not plan_data:
            return None
        
        stages = plan_data.get("stages", [])
        
        # Parcourir toutes les étapes et modules pour trouver une correspondance
        for stage in stages:
            modules = stage.get("modules", [])
            for module in modules:
                module_name = module.get("module_name", "")
                
                # Vérifier la correspondance avec le titre de la slide
                if (module_name.lower() in slide_title.lower() or 
                    any(word in slide_title.lower() for word in module_name.lower().split() if len(word) > 3)):
                    return module
        
        # Si aucune correspondance, retourner le premier module de la première étape
        if stages and stages[0].get("modules"):
            return stages[0]["modules"][0]
        
        return None
    
    # ===== Méthodes de fallback =====
    
    def _format_fallback_plan(self, slide_title: str) -> str:
        """Format de fallback pour une slide PLAN"""
        return f"""# {slide_title}

# Étape 1: Mise en contexte
## Introduction au domaine
- Présentation des enjeux
- Objectifs de la formation

# Étape 2: Acquisition des fondamentaux
## Concepts de base
- Notions essentielles
- Méthodes principales

# Étape 3: Construction progressive
## Approfondissement
- Techniques avancées
- Cas pratiques

# Étape 4: Maîtrise
## Pratique autonome
- Exercices d'application
- Projets personnels

# Étape 5: Validation
## Évaluation finale
- Quiz de validation
- Bilan des acquis"""
    
    def _format_fallback_stage(self, slide_title: str) -> str:
        """Format de fallback pour une slide ÉTAPE"""
        return f"""# {slide_title}

# Module principal
## Sous-module 1
- Concept fondamental
- Application pratique

## Sous-module 2
- Approfondissement
- Exercices"""
    
    def _format_fallback_module(self, slide_title: str, ai_introduction: Optional[str]) -> str:
        """Format de fallback pour une slide MODULE"""
        intro = ai_introduction or "Dans ce module, vous découvrirez les concepts essentiels pour progresser dans votre apprentissage."
        
        return f"""# {slide_title}

{intro}

# Concepts fondamentaux
- Notions de base
- Principes essentiels

# Applications pratiques
- Exemples concrets
- Exercices d'application"""
    
    def get_formatting_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du formateur"""
        return {
            "supported_types": ["PLAN", "STAGE", "MODULE"],
            "plan_structure": "étapes → #, modules → ##, sous-modules → -",
            "stage_structure": "modules → #, sous-modules → ##, slides → -", 
            "module_structure": "introduction IA + sous-modules → #, slides → -",
            "ai_required": "Only for MODULE slide introduction"
        }