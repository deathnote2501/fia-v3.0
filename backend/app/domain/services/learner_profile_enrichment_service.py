"""
FIA v3.0 - Learner Profile Enrichment Service
Domain service for enriching learner profiles based on conversation interactions
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.domain.entities.learner_session import LearnerSession
from app.domain.ports.repositories import LearnerSessionRepositoryPort

logger = logging.getLogger(__name__)


class LearnerProfileEnrichmentService:
    """Service for enriching learner profiles progressively through conversations"""
    
    def __init__(self, learner_session_repository: LearnerSessionRepositoryPort):
        self.learner_session_repository = learner_session_repository
        logger.info("🧠 PROFILE_ENRICHMENT [SERVICE] Initialized")
    
    async def enrich_learner_profile(
        self,
        learner_session_id: UUID,
        new_profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich the learner profile with new insights from conversation
        
        Args:
            learner_session_id: ID of the learner session
            new_profile_data: New profile insights from AI conversation
            
        Returns:
            The updated enriched profile
        """
        try:
            # Get current learner session
            learner_session = await self.learner_session_repository.get_by_id(learner_session_id)
            if not learner_session:
                raise ValueError(f"LearnerSession with id {learner_session_id} not found")
            
            # Get current enriched profile or initialize empty
            current_profile = learner_session.enriched_profile or {}
            
            # Merge new insights with existing profile
            enriched_profile = self._merge_profile_insights(current_profile, new_profile_data)
            
            # Update the learner session
            learner_session.set_enriched_profile(enriched_profile)
            updated_session = await self.learner_session_repository.update(learner_session)
            
            logger.info(f"🧠 PROFILE_ENRICHMENT [UPDATE] Profile enriched for learner {learner_session_id}")
            logger.debug(f"New insights: {new_profile_data}")
            logger.debug(f"Merged profile preview: {str(enriched_profile)[:200]}...")
            
            return updated_session.enriched_profile
            
        except Exception as e:
            logger.error(f"❌ PROFILE_ENRICHMENT [ERROR] Failed to enrich profile: {str(e)}")
            raise
    
    def _merge_profile_insights(
        self, 
        current_profile: Dict[str, Any], 
        new_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Intelligently merge new profile insights with existing data
        
        Strategy:
        - Replace single values (learning_style_observed, comprehension_level, objectives, engagement_patterns)
        - Merge arrays (interests, blockers) removing duplicates
        - Add metadata about enrichment history
        """
        merged_profile = current_profile.copy()
        
        # Initialize structure if empty
        if not merged_profile:
            merged_profile = {
                "learning_style_observed": "",
                "comprehension_level": "",
                "interests": [],
                "blockers": [],
                "objectives": "",
                "engagement_patterns": "",
                "enrichment_history": {
                    "first_enriched_at": datetime.utcnow().isoformat(),
                    "total_enrichments": 0,
                    "last_updated_at": ""
                }
            }
        
        # Update single-value fields (most recent insight wins)
        for field in ["learning_style_observed", "comprehension_level", "objectives", "engagement_patterns"]:
            if field in new_insights and new_insights[field]:
                merged_profile[field] = new_insights[field]
        
        # Merge array fields (interests, blockers) avoiding duplicates
        for array_field in ["interests", "blockers"]:
            if array_field in new_insights and isinstance(new_insights[array_field], list):
                existing_items = set(merged_profile.get(array_field, []))
                new_items = set(new_insights[array_field])
                merged_profile[array_field] = list(existing_items.union(new_items))
        
        # Update enrichment metadata
        if "enrichment_history" not in merged_profile:
            merged_profile["enrichment_history"] = {
                "first_enriched_at": datetime.utcnow().isoformat(),
                "total_enrichments": 0
            }
        
        merged_profile["enrichment_history"]["total_enrichments"] += 1
        merged_profile["enrichment_history"]["last_updated_at"] = datetime.utcnow().isoformat()
        
        return merged_profile
    
    async def get_enriched_profile(self, learner_session_id: UUID) -> Optional[Dict[str, Any]]:
        """Get the current enriched profile for a learner session"""
        try:
            learner_session = await self.learner_session_repository.get_by_id(learner_session_id)
            if not learner_session:
                return None
            
            return learner_session.enriched_profile
            
        except Exception as e:
            logger.error(f"❌ PROFILE_ENRICHMENT [GET] Failed to get enriched profile: {str(e)}")
            return None
    
    def get_personalization_context(self, enriched_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract personalization context from enriched profile for slide generation
        
        Returns a clean context dict suitable for AI prompts
        """
        if not enriched_profile:
            return {}
        
        return {
            "preferred_learning_approach": enriched_profile.get("learning_style_observed", ""),
            "comprehension_level": enriched_profile.get("comprehension_level", ""),
            "key_interests": enriched_profile.get("interests", []),
            "known_blockers": enriched_profile.get("blockers", []),
            "learning_objectives": enriched_profile.get("objectives", ""),
            "engagement_style": enriched_profile.get("engagement_patterns", ""),
            "profile_maturity": enriched_profile.get("enrichment_history", {}).get("total_enrichments", 0)
        }