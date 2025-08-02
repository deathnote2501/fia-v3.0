"""
FIA v3.0 - Slide Content Modifier
Service pour modifier le contenu des slides existantes (simplification/approfondissement)
"""

import logging
import json
import time
from typing import Dict, Any

from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter, VertexAIError
from app.domain.services.slide_prompt_builder import SlidePromptBuilder

logger = logging.getLogger(__name__)


class SlideContentModifier:
    """Service pour modifier le contenu des slides existantes avec IA"""
    
    def __init__(self):
        """Initialize slide content modifier"""
        self.vertex_adapter = VertexAIAdapter()
        self.prompt_builder = SlidePromptBuilder()
        logger.info("🔧 SLIDE CONTENT MODIFIER [SERVICE] Initialized")
    
    async def simplify_slide_content(
        self,
        current_content: str,
        learner_profile: Any,
        learner_session_id: str
    ) -> Dict[str, Any]:
        """
        Simplifier le contenu d'une slide existante
        
        Args:
            current_content: Contenu actuel de la slide
            learner_profile: Profil de l'apprenant
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant le contenu simplifié et les métadonnées
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [SIMPLIFY] Simplifying content for session {learner_session_id}")
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [SIMPLIFY] Original content length: {len(current_content)} chars")
            
            # Valider les paramètres d'entrée
            if not self.prompt_builder.validate_prompt_input(
                "modification", 
                action="simplifier", 
                current_content=current_content, 
                learner_profile=learner_profile
            ):
                raise ValueError("Invalid parameters for slide simplification")
            
            # Construire le prompt de simplification
            prompt = self.prompt_builder.build_modification_prompt(
                action="simplifier",
                current_content=current_content,
                learner_profile=learner_profile
            )
            
            # Configurer VertexAI pour simplification
            vertex_config = {
                "temperature": 0.6,  # Moins de créativité pour rester fidèle au contenu
                "max_output_tokens": 1024,
                "top_p": 0.8,
                "top_k": 30,
                "response_mime_type": "application/json"  # Forcer la réponse JSON
            }
            
            # Générer le contenu simplifié avec VertexAI
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [AI] Calling VertexAI for simplification")
            response = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=vertex_config
            )
            
            # Extraire le contenu du JSON
            simplified_content = self._extract_json_content(response, "simplification")
            
            duration = time.time() - start_time
            
            # Construire la réponse
            result = {
                "slide_content": simplified_content,
                "original_length": len(current_content),
                "simplified_length": len(simplified_content),
                "reduction_percentage": round((1 - len(simplified_content) / len(current_content)) * 100, 1),
                "modification_type": "simplification",
                "generation_duration": round(duration, 2),
                "learner_session_id": learner_session_id
            }
            
            logger.info(f"✅ SLIDE CONTENT MODIFIER [SUCCESS] Simplification completed in {duration:.2f}s")
            logger.info(f"✅ SLIDE CONTENT MODIFIER [STATS] Reduced by {result['reduction_percentage']}% ({result['original_length']} → {result['simplified_length']} chars)")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ SLIDE CONTENT MODIFIER [ERROR] Simplification failed after {duration:.2f}s: {str(e)}")
            
            # Retourner un fallback
            return self._generate_simplification_fallback(current_content, learner_profile, learner_session_id, duration)
    
    async def deepen_slide_content(
        self,
        current_content: str,
        learner_profile: Any,
        learner_session_id: str
    ) -> Dict[str, Any]:
        """
        Approfondir le contenu d'une slide existante
        
        Args:
            current_content: Contenu actuel de la slide
            learner_profile: Profil de l'apprenant
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant le contenu approfondi et les métadonnées
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [DEEPEN] Deepening content for session {learner_session_id}")
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [DEEPEN] Original content length: {len(current_content)} chars")
            
            # Valider les paramètres d'entrée
            if not self.prompt_builder.validate_prompt_input(
                "modification", 
                action="approfondir", 
                current_content=current_content, 
                learner_profile=learner_profile
            ):
                raise ValueError("Invalid parameters for slide deepening")
            
            # Construire le prompt d'approfondissement
            prompt = self.prompt_builder.build_modification_prompt(
                action="approfondir",
                current_content=current_content,
                learner_profile=learner_profile
            )
            
            # Configurer VertexAI pour approfondissement
            vertex_config = {
                "temperature": 0.7,  # Plus de créativité pour enrichir le contenu
                "max_output_tokens": 1536,  # Plus de tokens pour le contenu étendu
                "top_p": 0.9,
                "top_k": 40,
                "response_mime_type": "application/json"  # Forcer la réponse JSON
            }
            
            # Générer le contenu approfondi avec VertexAI
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [AI] Calling VertexAI for deepening")
            response = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=vertex_config
            )
            
            # Extraire le contenu du JSON
            deepened_content = self._extract_json_content(response, "approfondissement")
            
            duration = time.time() - start_time
            
            # Construire la réponse
            result = {
                "slide_content": deepened_content,
                "original_length": len(current_content),
                "deepened_length": len(deepened_content),
                "expansion_percentage": round((len(deepened_content) / len(current_content) - 1) * 100, 1),
                "modification_type": "approfondissement",
                "generation_duration": round(duration, 2),
                "learner_session_id": learner_session_id
            }
            
            logger.info(f"✅ SLIDE CONTENT MODIFIER [SUCCESS] Deepening completed in {duration:.2f}s")
            logger.info(f"✅ SLIDE CONTENT MODIFIER [STATS] Expanded by {result['expansion_percentage']}% ({result['original_length']} → {result['deepened_length']} chars)")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ SLIDE CONTENT MODIFIER [ERROR] Deepening failed after {duration:.2f}s: {str(e)}")
            
            # Retourner un fallback
            return self._generate_deepening_fallback(current_content, learner_profile, learner_session_id, duration)
    
    async def modify_slide_content(
        self,
        modification_type: str,
        current_content: str,
        learner_profile: Any,
        learner_session_id: str
    ) -> Dict[str, Any]:
        """
        Modifier le contenu d'une slide (méthode générique)
        
        Args:
            modification_type: "simplifier" ou "approfondir"
            current_content: Contenu actuel de la slide
            learner_profile: Profil de l'apprenant
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant le contenu modifié et les métadonnées
        """
        logger.info(f"🔧 SLIDE CONTENT MODIFIER [MODIFY] Type: {modification_type}, Session: {learner_session_id}")
        
        if modification_type == "simplifier":
            return await self.simplify_slide_content(current_content, learner_profile, learner_session_id)
        elif modification_type == "approfondir":
            return await self.deepen_slide_content(current_content, learner_profile, learner_session_id)
        else:
            raise ValueError(f"Modification type '{modification_type}' not supported. Use 'simplifier' or 'approfondir'.")
    
    # ===== Méthodes privées d'extraction et utilitaires =====
    
    def _extract_json_content(self, response: Any, modification_type: str) -> str:
        """
        Extraire le contenu JSON de la réponse VertexAI
        
        Args:
            response: Réponse de VertexAI
            modification_type: Type de modification pour le logging
            
        Returns:
            Contenu markdown extrait du JSON
        """
        try:
            # Extraire le texte de la réponse
            if hasattr(response, 'text'):
                response_text = response.text.strip()
            elif isinstance(response, str):
                response_text = response.strip()
            else:
                response_text = str(response).strip()
            
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [JSON] Raw response length: {len(response_text)} chars")
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [JSON] Response preview: {response_text[:200]}...")
            
            # Parser le JSON
            try:
                json_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Essayer de nettoyer le JSON si malformé
                cleaned_response = self._clean_json_response(response_text)
                json_data = json.loads(cleaned_response)
            
            # Extraire le contenu de la slide
            if "slide_content" in json_data:
                content = json_data["slide_content"]
                logger.info(f"✅ SLIDE CONTENT MODIFIER [JSON] Successfully extracted content: {len(content)} chars")
                return content.strip()
            else:
                logger.error(f"❌ SLIDE CONTENT MODIFIER [JSON] No 'slide_content' key found in response")
                raise KeyError("Missing 'slide_content' key in JSON response")
            
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.error(f"❌ SLIDE CONTENT MODIFIER [JSON] Failed to extract content: {e}")
            raise ValueError(f"Failed to extract JSON content for {modification_type}: {str(e)}")
    
    def _clean_json_response(self, response_text: str) -> str:
        """Nettoyer une réponse JSON potentiellement malformée"""
        # Supprimer les préfixes/suffixes courants
        response_text = response_text.strip()
        
        # Supprimer les blocs de code markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        # Trouver le premier { et le dernier }
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}")
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = response_text[start_idx:end_idx + 1]
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [CLEAN] Cleaned JSON: {len(cleaned)} chars")
            return cleaned
        
        # Si on ne peut pas nettoyer, retourner tel quel
        return response_text
    
    def _generate_simplification_fallback(
        self,
        current_content: str,
        learner_profile: Any,
        learner_session_id: str,
        duration: float
    ) -> Dict[str, Any]:
        """Générer un contenu de fallback pour la simplification"""
        logger.info(f"🔧 SLIDE CONTENT MODIFIER [FALLBACK] Generating simplification fallback")
        
        # Simplification basique : raccourcir les phrases et supprimer les détails
        lines = current_content.split('\n')
        simplified_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Garder les titres
            if line.startswith('#'):
                simplified_lines.append(line)
            # Simplifier les listes
            elif line.startswith('-') or line.startswith('*'):
                # Raccourcir les éléments de liste
                if len(line) > 50:
                    line = line[:47] + "..."
                simplified_lines.append(line)
            # Simplifier les paragraphes
            else:
                # Raccourcir les phrases longues
                if len(line) > 80:
                    line = line[:77] + "..."
                simplified_lines.append(line)
        
        fallback_content = '\n'.join(simplified_lines)
        
        return {
            "slide_content": fallback_content,
            "original_length": len(current_content),
            "simplified_length": len(fallback_content),
            "reduction_percentage": round((1 - len(fallback_content) / len(current_content)) * 100, 1),
            "modification_type": "simplification",
            "generation_duration": round(duration, 2),
            "learner_session_id": learner_session_id,
            "fallback": True
        }
    
    def _generate_deepening_fallback(
        self,
        current_content: str,
        learner_profile: Any,
        learner_session_id: str,
        duration: float
    ) -> Dict[str, Any]:
        """Générer un contenu de fallback pour l'approfondissement"""
        logger.info(f"🔧 SLIDE CONTENT MODIFIER [FALLBACK] Generating deepening fallback")
        
        # Approfondissement basique : ajouter des détails génériques
        profile_context = getattr(learner_profile, 'job_and_sector', 'votre domaine professionnel')
        
        lines = current_content.split('\n')
        deepened_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            deepened_lines.append(line)
            
            # Ajouter des détails après les titres principaux
            if line.startswith('# ') and not line.startswith('## '):
                deepened_lines.append(f"*Approfondissement adapté à {profile_context}*")
                deepened_lines.append("")
            
            # Ajouter des exemples après les listes
            elif line.startswith('-') or line.startswith('*'):
                if "exemple" not in line.lower():
                    deepened_lines.append(f"  - Exemple concret dans {profile_context}")
        
        # Ajouter une section d'approfondissement à la fin
        deepened_lines.extend([
            "",
            "## Pour aller plus loin",
            f"- Applications spécifiques à {profile_context}",
            "- Ressources complémentaires",
            "- Exercices pratiques avancés"
        ])
        
        fallback_content = '\n'.join(deepened_lines)
        
        return {
            "slide_content": fallback_content,
            "original_length": len(current_content),
            "deepened_length": len(fallback_content),
            "expansion_percentage": round((len(fallback_content) / len(current_content) - 1) * 100, 1),
            "modification_type": "approfondissement",
            "generation_duration": round(duration, 2),
            "learner_session_id": learner_session_id,
            "fallback": True
        }
    
    def get_modification_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du modificateur"""
        return {
            "supported_modifications": ["simplifier", "approfondir"],
            "ai_provider": "VertexAI (Google Gemini)",
            "output_format": "JSON avec slide_content",
            "simplification_config": {
                "temperature": 0.6,
                "max_tokens": 1024,
                "goal": "Réduction 20-40% du contenu"
            },
            "deepening_config": {
                "temperature": 0.7,
                "max_tokens": 1536,
                "goal": "Expansion 30-60% du contenu"
            },
            "fallback_available": True,
            "metrics_tracked": [
                "original_length",
                "modified_length", 
                "percentage_change",
                "generation_duration"
            ]
        }
    
    def validate_content_for_modification(self, content: str) -> bool:
        """Valider si le contenu peut être modifié"""
        if not content or not content.strip():
            logger.error("❌ SLIDE CONTENT MODIFIER [VALIDATE] Empty content cannot be modified")
            return False
        
        if len(content.strip()) < 10:
            logger.error("❌ SLIDE CONTENT MODIFIER [VALIDATE] Content too short for modification")
            return False
        
        return True
    
    async def add_more_details_to_slide(
        self,
        current_content: str,
        learner_profile: Any,
        learner_session_id: str
    ) -> Dict[str, Any]:
        """
        Ajouter plus de détails au contenu d'une slide existante
        
        Args:
            current_content: Contenu actuel de la slide
            learner_profile: Profil de l'apprenant
            learner_session_id: ID de la session apprenant
            
        Returns:
            Dict contenant le contenu enrichi et les métadonnées
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [MORE_DETAILS] Adding details for session {learner_session_id}")
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [MORE_DETAILS] Original content length: {len(current_content)} chars")
            
            # Valider les paramètres d'entrée
            if not self.prompt_builder.validate_prompt_input(
                "modification", 
                action="approfondir", 
                current_content=current_content, 
                learner_profile=learner_profile
            ):
                raise ValueError("Invalid parameters for slide enhancement")
            
            # Construire le prompt d'approfondissement
            prompt = self.prompt_builder.build_modification_prompt(
                action="approfondir",
                current_content=current_content,
                learner_profile=learner_profile
            )
            
            # Configurer VertexAI pour approfondissement
            vertex_config = {
                "temperature": 0.7,  # Plus de créativité pour enrichir le contenu
                "max_output_tokens": 2048,  # Plus de tokens pour plus de détails
                "top_p": 0.9,
                "top_k": 40,
                "response_mime_type": "application/json"  # Forcer la réponse JSON
            }
            
            # Générer le contenu enrichi avec VertexAI
            logger.info(f"🔧 SLIDE CONTENT MODIFIER [AI] Calling VertexAI for enhancement")
            ai_response = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=vertex_config
            )
            
            # Extraire et valider le contenu généré
            if isinstance(ai_response, str):
                enhanced_content = ai_response.strip()
            else:
                enhanced_content = str(ai_response).strip()
            
            if not enhanced_content:
                raise ValueError("VertexAI returned empty enhanced content")
            
            # Tenter de parser le JSON si possible
            try:
                content_json = json.loads(enhanced_content)
                if "slide_content" in content_json:
                    enhanced_content = content_json["slide_content"]
            except json.JSONDecodeError:
                logger.info("🔧 SLIDE CONTENT MODIFIER [PARSE] Content not in JSON format, using as-is")
            
            generation_time = time.time() - start_time
            
            logger.info(f"✅ SLIDE CONTENT MODIFIER [MORE_DETAILS] Enhanced content generated")
            logger.info(f"✅ SLIDE CONTENT MODIFIER [MORE_DETAILS] Enhanced content length: {len(enhanced_content)} chars")
            logger.info(f"✅ SLIDE CONTENT MODIFIER [MORE_DETAILS] Generation time: {generation_time:.2f}s")
            
            return {
                "enhanced_content": enhanced_content,
                "original_length": len(current_content),
                "enhanced_length": len(enhanced_content),
                "generation_time_seconds": generation_time,
                "action": "add_more_details",
                "learner_session_id": learner_session_id
            }
            
        except VertexAIError as e:
            logger.error(f"❌ SLIDE CONTENT MODIFIER [MORE_DETAILS] VertexAI error: {e}")
            raise RuntimeError(f"AI enhancement failed: {e}")
        except Exception as e:
            logger.error(f"❌ SLIDE CONTENT MODIFIER [MORE_DETAILS] Error: {e}")
            raise