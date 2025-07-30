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
    
    async def generate_charts(self, request: ChartGenerationRequest) -> ChartGenerationResponse:
        """
        Generate chart configurations from slide content
        
        Args:
            request: Chart generation request with slide content
            
        Returns:
            Chart generation response with configurations
        """
        start_time = time.time()
        
        try:
            logger.info(f"🎯 CHART GENERATION [START] Analyzing content: {len(request.slide_content)} chars")
            
            # Build prompt for VertexAI
            prompt = self._build_chart_generation_prompt(request)
            
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
            
            if not chart_analysis.charts_possible:
                return ChartGenerationResponse(
                    success=False,
                    charts=[],
                    message="No meaningful charts can be generated from this content",
                    processing_time_seconds=round(processing_time, 2)
                )
            
            # Validate and clean chart configurations
            validated_charts = self._validate_chart_configs(chart_analysis.recommended_charts)
            
            logger.info(f"✅ CHART GENERATION [SUCCESS] Generated {len(validated_charts)} charts in {processing_time:.2f}s")
            
            return ChartGenerationResponse(
                success=True,
                charts=validated_charts,
                message=f"Generated {len(validated_charts)} chart(s) successfully. {chart_analysis.reasoning}",
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
    
    def _build_chart_generation_prompt(self, request: ChartGenerationRequest) -> str:
        """Build optimized prompt for chart generation"""
        
        prompt = f"""Tu es un expert en visualisation de données éducatives. 

Analyse le contenu de formation suivant et détermine s'il est possible de créer des graphiques pertinents pour améliorer la compréhension.

CONTENU À ANALYSER:
Titre: {request.slide_title or "Non spécifié"}
Contenu: {request.slide_content}

INSTRUCTIONS:
1. Détermine si le contenu contient des informations qui peuvent être visualisées (données numériques, comparaisons, évolutions, répartitions, etc.)
2. Si OUI, propose jusqu'à {request.max_charts} graphiques pertinents
3. Utilise UNIQUEMENT ces types: "line" (évolution), "pie" (répartition), "radar" (comparaison multi-critères)
4. Crée des données réalistes et éducatives basées sur le contenu
5. Choisis des titres clairs et pédagogiques

TYPES DE DONNÉES VISUALISABLES:
- Statistiques, pourcentages, scores
- Évolutions temporelles
- Comparaisons entre éléments
- Répartitions ou distributions
- Performance, évaluations
- Concepts avec dimensions multiples

RÉPONSE ATTENDUE (JSON uniquement):
{{
  "charts_possible": true/false,
  "recommended_charts": [
    {{
      "type": "line|pie|radar",
      "title": "Titre explicite du graphique",
      "description": "Explication de ce que montre le graphique",
      "labels": ["Label1", "Label2", "Label3"],
      "data": [valeur1, valeur2, valeur3],
      "color_palette": "default"
    }}
  ],
  "reasoning": "Explication détaillée des choix de visualisation"
}}

IMPORTANT: 
- Si aucune visualisation pertinente n'est possible, retourne charts_possible: false
- Les données doivent être cohérentes avec le contenu éducatif
- Maximum {request.max_charts} graphiques
- Privilégie la qualité à la quantité"""

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