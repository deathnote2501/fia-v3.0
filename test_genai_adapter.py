#!/usr/bin/env python3
"""
Test script for Google GenAI adapter
"""
import asyncio
import sys
import os

# Add project path
sys.path.append('.')
sys.path.append('./backend')

from backend.app.infrastructure.adapters.vertex_ai_adapter import VertexAIAdapter, VertexAIError

async def test_genai_adapter():
    """Test the GenAI adapter configuration and basic functionality"""
    print("🧪 Testing Google GenAI Adapter...")
    
    try:
        # Initialize adapter
        adapter = VertexAIAdapter()
        print(f"✅ Adapter initialized")
        print(f"📊 Available: {adapter.is_available()}")
        print(f"📊 Model: {adapter.model_name}")
        
        if not adapter.is_available():
            print("❌ Adapter not available - check configuration")
            return False
        
        # Test simple content generation
        print("🚀 Testing content generation...")
        test_prompt = "Réponds uniquement avec le mot 'SUCCÈS' si tu reçois ce message."
        
        response = await adapter.generate_content(test_prompt)
        print(f"✅ Content generation test: {response[:100]}")
        
        # Test statistics
        stats = adapter.get_stats()
        print(f"📊 Stats: {stats}")
        
        return True
        
    except VertexAIError as e:
        print(f"❌ VertexAI Error: {e}")
        if e.original_error:
            print(f"   Original error: {e.original_error}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_genai_adapter())
    sys.exit(0 if result else 1)