"""
FIA v3.0 - Chart Generation Service
Service for generating chart configurations using VertexAI
"""

import logging
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.domain.ports.ai_adapter_port import AIAdapterPort, AIError
from app.domain.schemas.chart_generation import (
    ChartGenerationRequest, 
    ChartGenerationResponse, 
    ChartAnalysisResult,
    ChartConfig
)

logger = logging.getLogger(__name__)


class ChartGenerationService:
    """Service for generating chart configurations from slide content"""
    
    def __init__(self, ai_adapter: AIAdapterPort):
        """Initialize chart generation service with dependency injection"""
        self.ai_adapter = ai_adapter
        logger.info("🎯 CHART GENERATION [SERVICE] Initialized with AI adapter")
    
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
            
            # Call AI adapter for content generation
            response = await self.ai_adapter.generate_content(
                prompt=prompt,
                model_name="gemini-2.0-flash-001",
                temperature=0.3
            )
            response_text = response.get('text', '')
            
            # Log response information
            logger.info(f"🎯 CHART GENERATION [AI_RESPONSE] Received {len(response_text)} characters")
            
            # Parse structured output
            chart_analysis = self._parse_vertex_response(response_text)
            
            # Extract sources from descriptions as fallback
            chart_analysis = self._extract_sources_from_descriptions(chart_analysis)
            
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
        
        prompt = f"""
<ROLE>
Tu es un formateur pédagogue expert en visualisation de données avec accès à Google Search pour créer des graphiques factuels et pédagogiques.
</ROLE>

<OBJECTIF>
Créer {min(request.max_charts, 2)} graphiques personnalisés basés sur des données récentes et vérifiées pour enrichir le [SLIDE DE FORMATION] selon le [PROFIL APPRENANT].
</OBJECTIF>

<PROFIL_APPRENANT>
- Niveau : {profile_info['niveau']}
- Poste et secteur : {profile_info['poste_et_secteur']}
- Objectifs : {profile_info['objectifs']}
- Profil enrichi : {enriched_profile}
</PROFIL_APPRENANT>

<SLIDE_DE_FORMATION>
Titre: {request.slide_title or "Non spécifié"}
Contenu:
{request.slide_content}
</SLIDE_DE_FORMATION>

<STRATEGIE_DE_RECHERCHE>
1. ANALYSE le contenu du slide pour identifier les sujets nécessitant des données chiffrées
2. RECHERCHE sur Google des statistiques récentes (2023-2025) et des sources fiables 
3. PRIVILÉGIE les sources officielles : instituts statistiques, études sectorielles, rapports gouvernementaux
4. ADAPTE les données au niveau de compréhension du [PROFIL APPRENANT]
</STRATEGIE_DE_RECHERCHE>

<INSTRUCTIONS>
- Propose EXACTEMENT {min(request.max_charts, 2)} graphiques pertinents et complémentaires
- RECHERCHE OBLIGATOIREMENT des données actuelles si le slide manque de chiffres précis
- Utilise UNIQUEMENT ces types: "line" (évolution temporelle), "pie" (répartitions %), "radar" (comparaisons multi-critères)
- Crée des données RÉALISTES basées sur tes recherches web récentes
- INCLUS SYSTEMATIQUEMENT les sources dans la description de chaque graphique
- Adapte la complexité des données au niveau du [PROFIL APPRENANT]
</INSTRUCTIONS>

<CONSTRAINTS>
- Types de graphiques autorisés: "line", "pie", "radar" uniquement
- Sources obligatoires et récentes (2023-2025)
- Données factuelles et vérifiables
- Adaptation au niveau de l'apprenant
- Format JSON strict obligatoire
</CONSTRAINTS>

<FORMAT_DESCRIPTION_OBLIGATOIRE>
"[Explication pédagogique du graphique]. Données basées sur [Source précise + année]. Cette visualisation permet à l'apprenant de [valeur pédagogique]."
</FORMAT_DESCRIPTION_OBLIGATOIRE>

<STRUCTURE_JSON_ATTENDUE>
{{
  "recommended_charts": [
    {{
      "type": "line|pie|radar",
      "title": "Titre explicite et pédagogique",
      "description": "Explication + Source précise + Valeur pédagogique",
      "labels": ["Label1", "Label2", "Label3"],
      "data": [valeur1, valeur2, valeur3],
      "color_palette": "default"
    }}
  ]
}}
</STRUCTURE_JSON_ATTENDUE>

<RECAP>
POINTS CRITIQUES À RESPECTER :
- Exactement {min(request.max_charts, 2)} graphiques requis
- Recherche web obligatoire pour données récentes
- Sources précises dans chaque description
- Types autorisés: line, pie, radar uniquement
- Adaptation au profil {profile_info['niveau']} - {profile_info['poste_et_secteur']}
- Format JSON strict selon la structure attendue
</RECAP>

Génère maintenant les graphiques au format JSON selon la <STRUCTURE_JSON_ATTENDUE>.
"""

        return prompt
    
    def _parse_vertex_response(self, response_text: str) -> ChartAnalysisResult:
        """Parse VertexAI JSON response into structured result"""
        try:
            # Clean response text
            cleaned_response = response_text.strip()
            
            # Remove prefixes like "Here is the JSON requested:"
            if "```json" in cleaned_response:
                start_index = cleaned_response.find("```json") + 7
                cleaned_response = cleaned_response[start_index:]
            elif cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            
            # Remove markdown suffixes
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
            logger.error(f"❌ CHART GENERATION [JSON_ERROR] Cleaned response: {cleaned_response[:500]}...")
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
    
        """Add web sources from grounding metadata to chart configurations"""
        try:
                logger.info("🔍 CHART GENERATION [SOURCES] No grounding chunks found")
                return chart_analysis
            
            # Extract sources from grounding metadata
            sources = []
                if hasattr(chunk, 'web') and chunk.web:
                    source = {
                        "title": chunk.web.title or "Source web",
                        "url": chunk.web.uri or ""
                    }
                    sources.append(source)
                    logger.info(f"🔗 CHART GENERATION [SOURCES] Found source: {source['title']}")
            
            # Add sources to all charts
            for chart in chart_analysis.recommended_charts:
                chart.sources = sources
                logger.info(f"📊 CHART GENERATION [SOURCES] Added {len(sources)} sources to chart: {chart.title}")
            
            logger.info(f"✅ CHART GENERATION [SOURCES] Successfully added sources to {len(chart_analysis.recommended_charts)} charts")
            return chart_analysis
            
        except Exception as e:
            logger.error(f"❌ CHART GENERATION [SOURCES] Failed to add sources: {str(e)}")
            # Return original chart_analysis if source extraction fails
            return chart_analysis
    
    def _extract_sources_from_descriptions(self, chart_analysis: ChartAnalysisResult) -> ChartAnalysisResult:
        """Fallback method to extract sources mentioned in chart descriptions"""
        try:
            import re
            
            # Common patterns for source extraction
            source_patterns = [
                r'Données basées sur (.+?)(\.|\s|$)',
                r'Source[s]?\s*:\s*(.+?)(\.|\s|$)',
                r'Selon (.+?)(\.|\s|$)',
                r'D\'après (.+?)(\.|\s|$)',
                r'Rapport (.+?)(\.|\s|$)'
            ]
            
            for chart in chart_analysis.recommended_charts:
                sources = []
                
                if chart.description:
                    for pattern in source_patterns:
                        matches = re.findall(pattern, chart.description, re.IGNORECASE)
                        for match in matches:
                            source_text = match[0] if isinstance(match, tuple) else match
                            
                            # Nettoyer et créer la source
                            clean_source = source_text.strip()
                            if len(clean_source) > 5:  # Éviter les matches trop courts
                                source = {
                                    "title": clean_source,
                                    "url": ""  # Pas d'URL disponible depuis le texte
                                }
                                sources.append(source)
                                logger.info(f"🔗 CHART GENERATION [FALLBACK_SOURCES] Extracted source: {clean_source}")
                
                # Ajouter une source générique si mentionnée dans la description
                if 'IRENA' in chart.description:
                    sources.append({
                        "title": "IRENA - International Renewable Energy Agency",
                        "url": "https://www.irena.org"
                    })
                elif 'Statista' in chart.description:
                    sources.append({
                        "title": "Statista - Market Research",
                        "url": "https://www.statista.com"
                    })
                elif 'McKinsey' in chart.description:
                    sources.append({
                        "title": "McKinsey & Company",
                        "url": "https://www.mckinsey.com"
                    })
                
                chart.sources = sources
                if sources:
                    logger.info(f"📊 CHART GENERATION [FALLBACK_SOURCES] Added {len(sources)} fallback sources to chart: {chart.title}")
            
            return chart_analysis
            
        except Exception as e:
            logger.error(f"❌ CHART GENERATION [FALLBACK_SOURCES] Failed to extract sources from descriptions: {str(e)}")
            return chart_analysis
    
    def is_available(self) -> bool:
        """Check if chart generation service is available"""
        return True  # AI adapter is always available through dependency injection
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "service": "chart_generation",
            "vertex_ai_available": self.ai_adapter.is_available(),
            "supported_chart_types": ["line", "pie", "radar"],
            "max_charts_per_request": 5
        }