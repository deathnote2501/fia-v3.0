#!/usr/bin/env python3
"""
Test script for Chart Generation Service
Usage: python test_chart_service.py
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('/home/jerome/MEGA/1_PRO/fia-v3.0/backend')

from app.services.chart_generation_service import ChartGenerationService
from app.domain.schemas.chart_generation import ChartGenerationRequest


async def test_chart_generation():
    """Test chart generation with various content types"""
    
    service = ChartGenerationService()
    
    # Test cases with different content types
    test_cases = [
        {
            "name": "Numerical data - Performance metrics",
            "request": ChartGenerationRequest(
                slide_content="""
                Performance des équipes en 2024:
                - Équipe Marketing: 85% de satisfaction client
                - Équipe Ventes: 92% d'objectifs atteints  
                - Équipe Support: 78% de résolution première fois
                - Équipe Technique: 96% de disponibilité système
                
                Ces métriques montrent l'évolution positive sur les 4 trimestres.
                """,
                slide_title="Performance Teams 2024",
                max_charts=2
            )
        },
        {
            "name": "Evolution data - Timeline",
            "request": ChartGenerationRequest(
                slide_content="""
                Évolution des ventes par trimestre:
                Q1 2024: 150 000€
                Q2 2024: 180 000€
                Q3 2024: 165 000€
                Q4 2024: 220 000€
                
                Croissance constante avec une accélération au Q4.
                """,
                slide_title="Sales Evolution 2024"
            )
        },
        {
            "name": "Distribution data - Market share",
            "request": ChartGenerationRequest(
                slide_content="""
                Répartition du marché français:
                - iOS: 25%
                - Android: 70%
                - Autres: 5%
                
                Android domine largement le marché français mobile.
                """,
                slide_title="Mobile OS Market Share"
            )
        },
        {
            "name": "Multi-dimensional - Skills assessment",
            "request": ChartGenerationRequest(
                slide_content="""
                Évaluation des compétences équipe:
                - Communication: 8/10
                - Technique: 9/10
                - Leadership: 6/10
                - Innovation: 7/10
                - Collaboration: 8/10
                
                Points forts en technique, amélioration nécessaire en leadership.
                """,
                slide_title="Team Skills Assessment"
            )
        },
        {
            "name": "Non-graphable content - Theory",
            "request": ChartGenerationRequest(
                slide_content="""
                Les principes de la communication efficace:
                
                La communication est un processus complexe qui implique plusieurs éléments:
                l'émetteur, le récepteur, le message, le canal et le feedback. Pour être
                efficace, une communication doit être claire, concise et adaptée au public cible.
                
                Les barrières à la communication peuvent être physiques, psychologiques ou
                sémantiques. Il est essentiel de les identifier pour les surmonter.
                """,
                slide_title="Communication Principles"
            )
        }
    ]
    
    print("🎯 CHART GENERATION TEST - Starting tests...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📊 Test {i}: {test_case['name']}")
        print("=" * 50)
        
        try:
            result = await service.generate_charts(test_case['request'])
            
            print(f"✅ Success: {result.success}")
            print(f"📈 Charts generated: {len(result.charts)}")
            print(f"⏱️  Processing time: {result.processing_time_seconds}s")
            print(f"💬 Message: {result.message}")
            
            if result.charts:
                for j, chart in enumerate(result.charts, 1):
                    print(f"\n   Chart {j}: {chart.type.upper()}")
                    print(f"   Title: {chart.title}")
                    print(f"   Labels: {chart.labels}")
                    print(f"   Data: {chart.data}")
                    print(f"   Colors: {chart.color_palette}")
                    if chart.description:
                        print(f"   Description: {chart.description}")
            
            print(f"\n{'✅ PASSED' if result.success or 'non-graphable' in result.message.lower() else '❌ FAILED'}")
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
        
        print("\n" + "="*70 + "\n")
    
    print("🎯 CHART GENERATION TEST - All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_chart_generation())