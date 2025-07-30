"""
FIA v3.0 - Chart Generation Service
Service for generating chart configurations using VertexAI
"""

import logging
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter
from app.domain.schemas.chart_generation import (
    ChartGenerationRequest, 
    ChartGenerationResponse, 
    ChartAnalysisResult,
    ChartConfig
)

logger = logging.getLogger(__name__)


class ChartGenerationService:
    """Service for generating chart configurations from slide content"""
    
    def __init__(self):
        """Initialize chart generation service"""
        self.vertex_adapter = VertexAIAdapter()
        logger.info("🎯 CHART GENERATION [SERVICE] Initialized with VertexAI adapter")
    
    async def generate_charts(self, request: ChartGenerationRequest, profile_info: dict = None, enriched_profile: str = None) -> ChartGenerationResponse:
        """
        Generate chart configurations from slide content
        
        Args:
            request: Chart generation request with slide content
            profile_info: Learner profile information (niveau, poste_et_secteur, objectifs)
            enriched_profile: Enriched learner profile data
            
        Returns:
            Chart generation response with configurations
        """
        start_time = time.time()
        
        try:
            logger.info(f"🎯 CHART GENERATION [START] Analyzing content: {len(request.slide_content)} chars")
            
            # Build prompt for VertexAI
            prompt = self._build_chart_generation_prompt(request, profile_info, enriched_profile)
            
            # Generate with structured output
            generation_config = {
                "temperature": 0.3,  # Lower for more consistent chart generation
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 4096,
                "response_mime_type": "application/json"
            }
            
            # Call VertexAI
            response_text = await self.vertex_adapter.generate_content(
                prompt=prompt,
                generation_config=generation_config
            )
            
            # Parse structured output
            chart_analysis = self._parse_vertex_response(response_text)
            
            # Build response
            processing_time = time.time() - start_time
            
            # Validate and clean chart configurations
            validated_charts = self._validate_chart_configs(chart_analysis.recommended_charts)
            
            # Check if any charts were generated
            if not validated_charts:
                return ChartGenerationResponse(
                    success=False,
                    charts=[],
                    message="No meaningful charts could be generated from this content",
                    processing_time_seconds=round(processing_time, 2)
                )
            
            logger.info(f"✅ CHART GENERATION [SUCCESS] Generated {len(validated_charts)} charts in {processing_time:.2f}s")
            
            return ChartGenerationResponse(
                success=True,
                charts=validated_charts,
                message=f"Generated {len(validated_charts)} chart(s) successfully",
                processing_time_seconds=round(processing_time, 2)
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ CHART GENERATION [ERROR] Failed after {processing_time:.2f}s: {str(e)}")
            
            return ChartGenerationResponse(
                success=False,
                charts=[],
                message="Failed to generate charts due to an internal error",
                processing_time_seconds=round(processing_time, 2)
            )
    
    def _build_chart_generation_prompt(self, request: ChartGenerationRequest, profile_info: dict = None, enriched_profile: str = None) -> str:
        """Build optimized prompt for chart generation"""
        
        # Handle default values for profile data
        if profile_info is None:
            profile_info = {
                'niveau': 'Non spécifié',
                'poste_et_secteur': 'Non spécifié', 
                'objectifs': 'Non spécifié'
            }
        
        if enriched_profile is None:
            enriched_profile = 'Aucun profil enrichi disponible'
        
        prompt = f"""[ROLE] :
Tu es un formateur pédagogue spécialisé dans la création de graphiques pour illustrer et enrichir un [SLIDE DE FORMATION].

[OBJECTIF] :
Créer un ou plusieurs graphiques personnalisés pour le [PROFIL APPRENANT] pour illustrer et enrichir le [SLIDE DE FORMATION] qu'il est en train de consulter ci-dessous.

[PROFIL APPRENANT] :
- Niveau : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs : {profile_info['objectifs']}
- Profil enrichi : {enriched_profile}

[SLIDE DE FORMATION] : 
Titre: {request.slide_title or "Non spécifié"}
Contenu:
{request.slide_content}

INSTRUCTIONS:
- En fonction du contenu de [SLIDE DE FORMATION], propose jusqu'à {request.max_charts} graphiques pertinents pour illustrer et enrichir ce slide en privilégie la qualité à la quantité 
- Si le [SLIDE DE FORMATION] ne contient pas de données chiffrées, base-toi sur tes connaissances générales pour créer des données réalistes, utiles pour la compréhension du sujet
- Utilise UNIQUEMENT ces types: "line" (évolution), "pie" (répartition), "radar" (comparaison multi-critères)
- Choisis des titres clairs et pédagogiques

RÉPONSE ATTENDUE (JSON uniquement):
{{
  "recommended_charts": [
    {{
      "type": "line|pie|radar",
      "title": "Titre explicite du graphique",
      "description": "Explication de ce que montre le graphique",
      "labels": ["Label1", "Label2", "Label3"],
      "data": [valeur1, valeur2, valeur3],
      "color_palette": "default"
    }}
  ]
}}
"""

        return prompt
    
    def _parse_vertex_response(self, response_text: str) -> ChartAnalysisResult:
        """Parse VertexAI JSON response into structured result"""
        try:
            # Clean response text
            cleaned_response = response_text.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            response_data = json.loads(cleaned_response)
            
            # Convert to Pydantic model for validation
            return ChartAnalysisResult(**response_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ CHART GENERATION [JSON_ERROR] Failed to parse response: {e}")
            logger.error(f"❌ CHART GENERATION [JSON_ERROR] Raw response: {response_text[:500]}...")
            raise ValueError(f"Invalid JSON response from VertexAI: {e}")
            
        except Exception as e:
            logger.error(f"❌ CHART GENERATION [PARSE_ERROR] Failed to parse response: {e}")
            raise ValueError(f"Failed to parse VertexAI response: {e}")
    
    def _validate_chart_configs(self, charts: List[ChartConfig]) -> List[ChartConfig]:
        """Validate and clean chart configurations"""
        validated_charts = []
        
        for chart in charts:
            try:
                # Data is already cleaned by Pydantic validator
                # Ensure data and labels match in length
                if len(chart.labels) != len(chart.data):
                    # Truncate to minimum length
                    min_length = min(len(chart.labels), len(chart.data))
                    chart.labels = chart.labels[:min_length]
                    chart.data = chart.data[:min_length]
                    logger.warning(f"⚠️ CHART GENERATION [VALIDATION] Adjusted data/labels length for chart: {chart.title}")
                
                # Ensure we have at least 2 data points
                if len(chart.data) < 2:
                    logger.warning(f"⚠️ CHART GENERATION [VALIDATION] Skipping chart with insufficient data: {chart.title}")
                    continue
                
                # Validate chart type
                if chart.type not in ["line", "pie", "radar"]:
                    logger.warning(f"⚠️ CHART GENERATION [VALIDATION] Invalid chart type: {chart.type}, defaulting to 'pie'")
                    chart.type = "pie"
                
                # Ensure positive values for pie charts
                if chart.type == "pie":
                    chart.data = [abs(value) for value in chart.data]
                
                validated_charts.append(chart)
                
            except Exception as e:
                logger.error(f"❌ CHART GENERATION [VALIDATION] Failed to validate chart: {chart.title}, error: {e}")
                continue
        
        logger.info(f"✅ CHART GENERATION [VALIDATION] Validated {len(validated_charts)} charts")
        return validated_charts
    
    def is_available(self) -> bool:
        """Check if chart generation service is available"""
        return self.vertex_adapter.is_available()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "service": "chart_generation",
            "vertex_ai_available": self.vertex_adapter.is_available(),
            "supported_chart_types": ["line", "pie", "radar"],
            "max_charts_per_request": 5
        }