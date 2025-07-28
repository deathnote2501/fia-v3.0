"""
FIA v3.0 - Slide Generation Service
Service pour générer le contenu des slides individuelles avec VertexAI
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter, VertexAIError
from app.adapters.repositories.learner_training_plan_repository import LearnerTrainingPlanRepository
from app.adapters.repositories.learner_session_repository import LearnerSessionRepository
from app.adapters.repositories.training_slide_repository import TrainingSlideRepository
from app.infrastructure.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class SlideGenerationService:
    """Service pour générer le contenu des slides avec VertexAI"""
    
    def __init__(self):
        """Initialize slide generation service"""
        self.vertex_adapter = VertexAIAdapter()
        
        logger.info("🎯 SLIDE GENERATION [SERVICE] Initialized")
    
    async def generate_first_slide_content(self, learner_session_id: str) -> Dict[str, Any]:
        """
        Générer le contenu de la première slide d'un apprenant
        
        Args:
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant le contenu markdown de la slide
        """
        start_time = time.time()
        
        async with AsyncSessionLocal() as session:
            try:
                logger.info(f"🎯 SLIDE GENERATION [START] Generating first slide for session {learner_session_id}")
                
                # Initialize repositories with session
                learner_session_repo = LearnerSessionRepository(session)
                learner_plan_repo = LearnerTrainingPlanRepository(session)
                slide_repo = TrainingSlideRepository()
                slide_repo.set_session(session)
                
                # 1. Récupérer la session apprenant
                learner_session = await learner_session_repo.get_by_id(learner_session_id)
                if not learner_session:
                    raise ValueError(f"Learner session not found: {learner_session_id}")
                
                # 2. Récupérer le plan de formation personnalisé (le plus récent)
                training_plan = await learner_plan_repo.get_latest_by_learner_session_id(learner_session_id)
                if not training_plan:
                    raise ValueError(f"Training plan not found for session: {learner_session_id}")
                
                # 3. Récupérer la première slide
                first_slide = await slide_repo.get_first_slide(training_plan.id)
                if not first_slide:
                    raise ValueError(f"First slide not found for training plan: {training_plan.id}")
                
                # 4. Générer le contenu de la première slide si pas encore généré
                if not first_slide.content:
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] === GÉNÉRATION CONTENU SLIDE ===")
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] Slide title: {first_slide.title}")
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] Learner profile: {learner_session.email}")
                    
                    slide_content = await self._generate_slide_content(
                        slide_title=first_slide.title,
                        learner_profile=learner_session,
                        training_plan=training_plan,
                        slide_position="first"
                    )
                    
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] === CONTENU GÉNÉRÉ REÇU ===")
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] Content TYPE: {type(slide_content)}")
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] Content LONGUEUR: {len(slide_content) if slide_content else 'NULL'}")
                    logger.info(f"📝📝📝 SLIDE GENERATION [MAIN] Content PREVIEW (500 chars): {slide_content[:500] if slide_content else 'NULL'}")
                    
                    # 5. Sauvegarder le contenu généré
                    logger.info(f"💾💾💾 SLIDE GENERATION [MAIN] === SAUVEGARDE EN BASE ===")
                    logger.info(f"💾💾💾 SLIDE GENERATION [MAIN] Slide ID: {first_slide.id}")
                    logger.info(f"💾💾💾 SLIDE GENERATION [MAIN] Content à sauvegarder: {slide_content[:200]}...")
                    
                    await slide_repo.update_content(first_slide.id, slide_content)
                    first_slide.content = slide_content
                    first_slide.generated_at = datetime.now(timezone.utc)
                    
                    logger.info(f"✅✅✅ SLIDE GENERATION [MAIN] SAUVEGARDE TERMINÉE!")
                else:
                    logger.info(f"♻️♻️♻️ SLIDE GENERATION [MAIN] Slide déjà générée - MAIS VÉRIFICATION CONTENU...")
                    logger.info(f"♻️♻️♻️ SLIDE GENERATION [MAIN] Contenu existant LONGUEUR: {len(first_slide.content)}")
                    logger.info(f"♻️♻️♻️ SLIDE GENERATION [MAIN] Contenu existant PREVIEW: {first_slide.content[:200]}...")
                    
                    # CORRECTION : Vérifier si le contenu existant contient du JSON mal parsé
                    if first_slide.content and (first_slide.content.startswith('# Contenu de Formation\n\n[') or 
                                                 '"slide_content"' in first_slide.content):
                        logger.warning(f"🔧🔧🔧 SLIDE GENERATION [MAIN] CONTENU CORROMPU DÉTECTÉ - PARSING JSON...")
                        
                        # Essayer d'extraire le vrai contenu du JSON mal parsé
                        corrected_content = self._fix_corrupted_content(first_slide.content)
                        
                        if corrected_content != first_slide.content:
                            logger.info(f"🔧🔧🔧 SLIDE GENERATION [MAIN] CORRECTION APPLIQUÉE - SAUVEGARDE...")
                            await slide_repo.update_content(first_slide.id, corrected_content)
                            first_slide.content = corrected_content
                            logger.info(f"✅✅✅ SLIDE GENERATION [MAIN] CONTENU CORRIGÉ ET SAUVEGARDÉ!")
                        else:
                            logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [MAIN] IMPOSSIBLE DE CORRIGER LE CONTENU")
                
                duration = time.time() - start_time
                
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] === CONSTRUCTION RÉSULTAT FINAL ===")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Slide ID: {first_slide.id}")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Title: {first_slide.title}")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Content TYPE: {type(first_slide.content)}")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Content LONGUEUR: {len(first_slide.content) if first_slide.content else 'NULL'}")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Content FINAL PREVIEW (500 chars): {first_slide.content[:500] if first_slide.content else 'NULL'}")
                
                result = {
                    "slide_id": str(first_slide.id),
                    "title": first_slide.title,
                    "content": first_slide.content,
                    "order_in_submodule": first_slide.order_in_submodule,
                    "generated_at": first_slide.generated_at.isoformat() if first_slide.generated_at else None,
                    "generation_duration": round(duration, 2)
                }
                
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] RÉSULTAT DICT CRÉÉ:")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Result keys: {list(result.keys())}")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] Result content field: {result.get('content', 'MISSING')[:200]}...")
                
                logger.info(f"✅ SLIDE GENERATION [SUCCESS] First slide generated in {duration:.2f}s - {len(first_slide.content)} chars")
                logger.info(f"🏁🏁🏁 SLIDE GENERATION [RESULT] === RETOUR RÉSULTAT FINAL ===")
                return result
            
            except Exception as e:
                await session.rollback()
                duration = time.time() - start_time
                logger.error(f"❌ SLIDE GENERATION [ERROR] Failed after {duration:.2f}s: {str(e)}")
                raise
    
    async def _generate_slide_content(
        self,
        slide_title: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str = "first"
    ) -> str:
        """
        Générer le contenu markdown d'une slide avec VertexAI
        
        Args:
            slide_title: Titre de la slide
            learner_profile: Profil de l'apprenant (LearnerSession)
            training_plan: Plan de formation (LearnerTrainingPlan)
            slide_position: Position de la slide ("first", "middle", "last")
            
        Returns:
            Contenu markdown de la slide
        """
        try:
            # Construire le prompt personnalisé
            prompt = self._build_slide_prompt(
                slide_title=slide_title,
                learner_profile=learner_profile,
                training_plan=training_plan,
                slide_position=slide_position
            )
            
            # Configuration pour génération de contenu (VertexAI retourne du JSON)
            generation_config = {
                "temperature": 0.7,  # Créativité modérée pour contenu pédagogique
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048,  # Suffisant pour une slide
                "response_mime_type": "application/json"  # VertexAI retourne du JSON
            }
            
            logger.info(f"🚀 SLIDE GENERATION [AI] Calling VertexAI for slide content generation...")
            
            # Appeler VertexAI pour générer le contenu
            raw_content = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            # Parser le JSON et extraire le content markdown
            content = self._extract_content_from_json(raw_content)
            
            # Nettoyer et valider le contenu
            cleaned_content = self._clean_markdown_content(content)
            
            logger.info(f"✅ SLIDE GENERATION [AI] Content generated - {len(cleaned_content)} characters")
            return cleaned_content
            
        except Exception as e:
            logger.error(f"❌ SLIDE GENERATION [AI] Failed to generate content: {str(e)}")
            raise VertexAIError(f"Slide content generation failed: {str(e)}", original_error=e)
    
    def _build_slide_prompt(
        self,
        slide_title: str,
        learner_profile: Any,
        training_plan: Any,
        slide_position: str
    ) -> str:
        """Construire le prompt personnalisé pour générer le contenu de la slide"""
        
        # Extraire les informations du profil apprenant
        profile_info = {
            "niveau": learner_profile.experience_level or "débutant",
            "style_apprentissage": learner_profile.learning_style or "visuel",
            "poste": learner_profile.job_position or "non spécifié",
            "secteur": learner_profile.activity_sector or "non spécifié",
            "langue": learner_profile.language or "français"
        }
        
        # Extraire des informations du plan de formation
        plan_context = ""
        if hasattr(training_plan, 'plan_data') and training_plan.plan_data:
            try:
                plan_data = training_plan.plan_data if isinstance(training_plan.plan_data, dict) else json.loads(training_plan.plan_data)
                if 'formation_plan' in plan_data:
                    plan_context = f"Contexte du plan de formation : {plan_data['formation_plan'].get('objectifs_generaux', 'Formation personnalisée')}"
            except (json.JSONDecodeError, KeyError, AttributeError):
                plan_context = "Formation personnalisée selon le profil apprenant"
        
        prompt = f"""Tu es un expert pédagogue qui crée du contenu de formation personnalisé.

CONTEXTE :
- Titre de la slide : "{slide_title}"
- Position : {slide_position} slide de la formation
- {plan_context}

PROFIL APPRENANT :
- Niveau d'expérience : {profile_info['niveau']}
- Style d'apprentissage : {profile_info['style_apprentissage']}
- Poste : {profile_info['poste']}
- Secteur d'activité : {profile_info['secteur']}
- Langue : {profile_info['langue']}

INSTRUCTIONS :
1. Crée le contenu d'une slide de formation en markdown
2. Adapte le contenu au profil de l'apprenant (niveau, style, contexte professionnel)
3. Structure pédagogique claire avec titre, sous-titres, points clés
4. Inclus des éléments visuels (listes, citations, exemples)
5. Longueur appropriée pour une slide (300-800 mots)
6. Style engageant et professionnel

CONTRAINTES :
- Réponds UNIQUEMENT avec le contenu markdown de la slide
- Commence directement par le contenu, pas de préambule
- Utilise des éléments markdown : # ## ### - > ** *
- Adapte les exemples au secteur d'activité si pertinent

Génère maintenant le contenu de la slide :"""

        return prompt
    
    def _extract_content_from_json(self, json_response: str) -> str:
        """Extraire le contenu markdown du JSON retourné par VertexAI"""
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] === DÉBUT EXTRACTION ===")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] JSON brut TYPE: {type(json_response)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] JSON brut LONGUEUR: {len(json_response) if json_response else 'NULL'}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] JSON brut PREVIEW (500 chars): {json_response[:500] if json_response else 'NULL'}")
        
        try:
            # Parser le JSON
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [JSON-EXTRACTION] PARSING JSON avec json.loads()...")
            response_data = json.loads(json_response)
            logger.info(f"✅✅✅ SLIDE GENERATION [JSON-EXTRACTION] JSON PARSÉ AVEC SUCCÈS!")
            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Parsed data TYPE: {type(response_data)}")
            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Parsed data IS LIST?: {isinstance(response_data, list)}")
            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Parsed data IS DICT?: {isinstance(response_data, dict)}")
            
            if isinstance(response_data, list):
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] ARRAY détecté - LONGUEUR: {len(response_data)}")
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] ARRAY COMPLET: {response_data}")
            elif isinstance(response_data, dict):
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] DICT détecté - KEYS: {list(response_data.keys())}")
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] DICT COMPLET: {response_data}")
            
            # Cas 1: Array avec slide_content (nouveau format détecté dans les logs)
            if isinstance(response_data, list) and len(response_data) > 0:
                logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] BRANCHE 1: ARRAY avec {len(response_data)} éléments")
                first_item = response_data[0]
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Premier élément TYPE: {type(first_item)}")
                logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Premier élément: {first_item}")
                
                if isinstance(first_item, dict):
                    logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Premier élément KEYS: {list(first_item.keys())}")
                    if 'slide_content' in first_item:
                        content = first_item['slide_content']
                        logger.info(f"✅✅✅ SLIDE GENERATION [JSON-EXTRACTION] TROUVÉ slide_content dans array[0]!")
                        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content TYPE: {type(content)}")
                        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content LONGUEUR: {len(content) if content else 'NULL'}")
                        logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content PREVIEW (200 chars): {content[:200] if content else 'NULL'}")
                        logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] RETOUR content depuis array[0].slide_content")
                        return content
                    else:
                        logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] Pas de 'slide_content' dans array[0]")
                else:
                    logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] Premier élément n'est pas un dict")
                    
            # Cas 2: Dict avec structure classique
            elif isinstance(response_data, dict):
                logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] BRANCHE 2: DICT avec keys: {list(response_data.keys())}")
                
                # 2a: Structure avec slide.content
                if 'slide' in response_data and isinstance(response_data['slide'], dict) and 'content' in response_data['slide']:
                    content = response_data['slide']['content']
                    logger.info(f"✅✅✅ SLIDE GENERATION [JSON-EXTRACTION] TROUVÉ slide.content!")
                    logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content: {content[:200] if content else 'NULL'}")
                    logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] RETOUR content depuis slide.content")
                    return content
                    
                # 2b: Structure avec slide_content direct
                elif 'slide_content' in response_data:
                    content = response_data['slide_content']
                    logger.info(f"✅✅✅ SLIDE GENERATION [JSON-EXTRACTION] TROUVÉ root.slide_content!")
                    logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content: {content[:200] if content else 'NULL'}")
                    logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] RETOUR content depuis root.slide_content")
                    return content
                    
                # 2c: Structure avec content direct
                elif 'content' in response_data:
                    content = response_data['content']
                    logger.info(f"✅✅✅ SLIDE GENERATION [JSON-EXTRACTION] TROUVÉ root.content!")
                    logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] Content: {content[:200] if content else 'NULL'}")
                    logger.info(f"🎯🎯🎯 SLIDE GENERATION [JSON-EXTRACTION] RETOUR content depuis root.content")
                    return content
                else:
                    logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] AUCUN champ content trouvé dans le dict")
                    logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] FALLBACK: utilisation réponse brute")
                    return json_response
            else:
                logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] Type non supporté: {type(response_data)}")
                logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [JSON-EXTRACTION] FALLBACK: utilisation réponse brute")
                return json_response
                
        except json.JSONDecodeError as e:
            logger.error(f"❌❌❌ SLIDE GENERATION [JSON-EXTRACTION] ERREUR PARSING JSON: {e}")
            logger.info(f"🔍🔍🔍 SLIDE GENERATION [JSON-EXTRACTION] JSON brut qui a échoué: {json_response[:500]}...")
            # Fallback: utiliser la réponse brute
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [JSON-EXTRACTION] FALLBACK: utilisation réponse brute")
            return json_response
        except Exception as e:
            logger.error(f"❌❌❌ SLIDE GENERATION [JSON-EXTRACTION] ERREUR INATTENDUE: {e}")
            logger.error(f"❌❌❌ SLIDE GENERATION [JSON-EXTRACTION] STACK: {str(e)}")
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [JSON-EXTRACTION] FALLBACK: utilisation réponse brute")
            return json_response
    
    def _clean_markdown_content(self, content: str) -> str:
        """Nettoyer et valider le contenu markdown généré"""
        logger.info(f"🧹🧹🧹 SLIDE GENERATION [MARKDOWN-CLEAN] === DÉBUT NETTOYAGE ===")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Content INPUT TYPE: {type(content)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Content INPUT NULL?: {content is None}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Content INPUT LONGUEUR: {len(content) if content else 'NULL'}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Content INPUT PREVIEW (300 chars): {content[:300] if content else 'NULL'}")
        
        if not content:
            logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [MARKDOWN-CLEAN] CONTENU VIDE - Retour message par défaut")
            default_content = "# Contenu en cours de génération...\n\nVeuillez patienter pendant que nous préparons votre contenu personnalisé."
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] DEFAULT CONTENT: {default_content}")
            return default_content
        
        # Nettoyer les balises potentielles
        logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] ÉTAPE 1: strip()...")
        cleaned = content.strip()
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Après strip - LONGUEUR: {len(cleaned)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Après strip - PREVIEW: {cleaned[:200]}")
        
        # Supprimer les balises markdown code si présentes
        logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] ÉTAPE 2: Vérification balises markdown...")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Commence par ```markdown?: {cleaned.startswith('```markdown')}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Commence par ```?: {cleaned.startswith('```')}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Finit par ```?: {cleaned.endswith('```')}")
        
        if cleaned.startswith('```markdown'):
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] SUPPRESSION ```markdown au début")
            cleaned = cleaned[11:]
        elif cleaned.startswith('```'):
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] SUPPRESSION ``` au début")
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] SUPPRESSION ``` à la fin")
            cleaned = cleaned[:-3]
        
        logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] ÉTAPE 3: strip() final...")
        cleaned = cleaned.strip()
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Après suppression balises - LONGUEUR: {len(cleaned)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Après suppression balises - PREVIEW: {cleaned[:300]}")
        
        # Validation basique : doit contenir au moins un titre markdown
        logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] ÉTAPE 4: Validation titre markdown...")
        lines = cleaned.split('\n')
        has_title = any(line.startswith('#') for line in lines)
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Contient titre markdown?: {has_title}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Nombre de lignes: {len(lines)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Premières lignes: {lines[:5]}")
        
        if not has_title:
            logger.info(f"🔄🔄🔄 SLIDE GENERATION [MARKDOWN-CLEAN] AJOUT titre par défaut")
            # Ajouter un titre si manquant
            cleaned = f"# Contenu de Formation\n\n{cleaned}"
            logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] Après ajout titre - LONGUEUR: {len(cleaned)}")
        
        logger.info(f"✅✅✅ SLIDE GENERATION [MARKDOWN-CLEAN] NETTOYAGE TERMINÉ!")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] RÉSULTAT FINAL - TYPE: {type(cleaned)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] RÉSULTAT FINAL - LONGUEUR: {len(cleaned)}")
        logger.info(f"🔍🔍🔍 SLIDE GENERATION [MARKDOWN-CLEAN] RÉSULTAT FINAL - PREVIEW (400 chars): {cleaned[:400]}")
        logger.info(f"🧹🧹🧹 SLIDE GENERATION [MARKDOWN-CLEAN] === FIN NETTOYAGE ===")
        
        return cleaned
    
    def _fix_corrupted_content(self, corrupted_content: str) -> str:
        """Corriger le contenu corrompu qui contient du JSON au lieu de markdown pur"""
        logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] === DÉBUT CORRECTION CONTENU CORROMPU ===")
        logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] Contenu corrompu LONGUEUR: {len(corrupted_content)}")
        logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] Contenu corrompu PREVIEW: {corrupted_content[:300]}")
        
        try:
            # Cas 1: Contenu commence par "# Contenu de Formation\n\n[" 
            if corrupted_content.startswith('# Contenu de Formation\n\n['):
                logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] DÉTECTION: Format avec titre par défaut + JSON")
                
                # Extraire la partie JSON (tout après "# Contenu de Formation\n\n")
                json_part = corrupted_content[len('# Contenu de Formation\n\n'):]
                logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] JSON part: {json_part[:200]}...")
                
                # Parser le JSON
                parsed_json = json.loads(json_part)
                logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] JSON parsé: {type(parsed_json)}")
                
                if isinstance(parsed_json, list) and len(parsed_json) > 0:
                    first_item = parsed_json[0]
                    if isinstance(first_item, dict) and 'slide_content' in first_item:
                        markdown_content = first_item['slide_content']
                        logger.info(f"✅✅✅ SLIDE GENERATION [FIX] MARKDOWN EXTRAIT: {markdown_content[:200]}...")
                        return self._clean_markdown_content(markdown_content)
            
            # Cas 2: Contenu contient directement "slide_content" dans le JSON
            elif '"slide_content"' in corrupted_content:
                logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] DÉTECTION: Format JSON direct avec slide_content")
                
                # Essayer de parser tout le contenu comme JSON
                parsed_json = json.loads(corrupted_content)
                logger.info(f"🔧🔧🔧 SLIDE GENERATION [FIX] JSON parsé: {type(parsed_json)}")
                
                if isinstance(parsed_json, list) and len(parsed_json) > 0:
                    first_item = parsed_json[0]
                    if isinstance(first_item, dict) and 'slide_content' in first_item:
                        markdown_content = first_item['slide_content']
                        logger.info(f"✅✅✅ SLIDE GENERATION [FIX] MARKDOWN EXTRAIT: {markdown_content[:200]}...")
                        return self._clean_markdown_content(markdown_content)
                elif isinstance(parsed_json, dict) and 'slide_content' in parsed_json:
                    markdown_content = parsed_json['slide_content']
                    logger.info(f"✅✅✅ SLIDE GENERATION [FIX] MARKDOWN EXTRAIT: {markdown_content[:200]}...")
                    return self._clean_markdown_content(markdown_content)
            
            logger.warning(f"⚠️⚠️⚠️ SLIDE GENERATION [FIX] FORMAT NON RECONNU - Retour contenu original")
            return corrupted_content
            
        except json.JSONDecodeError as e:
            logger.error(f"❌❌❌ SLIDE GENERATION [FIX] ERREUR JSON: {e}")
            return corrupted_content
        except Exception as e:
            logger.error(f"❌❌❌ SLIDE GENERATION [FIX] ERREUR INATTENDUE: {e}")
            return corrupted_content
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du service"""
        return {
            "service": "SlideGenerationService",
            "vertex_ai_available": self.vertex_adapter.is_available(),
            "vertex_ai_stats": self.vertex_adapter.get_stats()
        }