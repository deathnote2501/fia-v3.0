"""
FIA v3.0 - OpenAI Outbound Adapter
Implementation of OpenAI image generation service interactions
"""

import base64
import logging
import time
import os
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import UUID

from openai import OpenAI

from app.domain.ports.outbound_ports import ImageGenerationServicePort
from app.infrastructure.settings import settings
from app.infrastructure.rate_limiter import openai_rate_limiter, RateLimitExceeded


logger = logging.getLogger(__name__)


class OpenAIAdapter(ImageGenerationServicePort):
    """Outbound adapter for OpenAI image generation service"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        # Initialize image storage path - make it absolute to avoid relative path issues
        self.image_storage_path = Path("uploads/images/slide_images").resolve()
        self.image_storage_path.mkdir(parents=True, exist_ok=True)
        
    async def generate_infographic(
        self,
        slide_content: str,
        slide_title: Optional[str] = None,
        learner_profile: Optional[Dict[str, Any]] = None,
        learner_session_id: Optional[UUID] = None,
        slide_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Generate educational infographic using OpenAI DALL-E"""
        try:
            # Apply rate limiting before API call
            await openai_rate_limiter.acquire()
            
            # Extract language from learner profile, default to French
            language = "french"  # Default for your use case
            if learner_profile and learner_profile.get("language"):
                language = learner_profile.get("language")
            
            # Build prompt for infographic generation
            prompt = self._build_infographic_prompt(slide_content, slide_title, learner_profile, language)
            
            logger.debug(f"Generating infographic with prompt: {prompt[:200]}...")
            
            # Generate image using OpenAI DALL-E 3 (fallback until organization is verified)
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",  # standard or hd
                n=1,
                response_format="b64_json"
            )
            
            # Extract image data
            image_data = response.data[0]
            image_base64 = image_data.b64_json
            
            # Save image to file if learner_session_id is provided
            image_path = None
            if learner_session_id:
                try:
                    image_path = await self._save_image_to_file(
                        image_base64,
                        learner_session_id,
                        slide_id
                    )
                    logger.info(f"Image saved to: {image_path}")
                except Exception as e:
                    logger.warning(f"Failed to save image to file: {str(e)}")
                    # Continue without saving - not critical for the response
            
            result = {
                "image_data": image_base64,  # Still return base64 for immediate display
                "image_path": image_path,  # File path for permanent storage
                "revised_prompt": image_data.revised_prompt or prompt,
                "metadata": {
                    "size": "1024x1024",
                    "quality": "standard",
                    "format": "png",
                    "model": "dall-e-3"
                }
            }
            
            logger.info(f"Successfully generated infographic (revised prompt: {image_data.revised_prompt[:100] if image_data.revised_prompt else 'None'}...)")
            
            return result
            
        except RateLimitExceeded as e:
            logger.warning(f"OpenAI rate limit exceeded: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating infographic: {str(e)}")
            raise Exception(f"Failed to generate infographic: {str(e)}")
    
    def _build_infographic_prompt(
        self, 
        slide_content: str,
        slide_title: Optional[str] = None,
        learner_profile: Optional[Dict[str, Any]] = None,
        language: str = "english"
    ) -> str:
        """Build optimized prompt for infographic generation"""
        
        # Base prompt for educational infographic
        base_prompt = f"""
<OBJECTIVE>
Design a ** simple square infographic (1:1 ratio) using **flat design** to visually explain this slide: {slide_title}.
</OBJECTIVE>

<SPECIFICATIONS>
The infographic should:
- Include **6 to 8 simple illustrations** in **outline style** (thin black, grey or blue #0d6efd lines, no fill)
- Follow a **grid layout** (2x3 or 3x3) with **equal spacing** and **aligned elements**
- Use **1 to 5 words** per illustration, in {language}, with a **clear sans-serif font**
- Have a **white background**, minimal padding around the edges, and consistent margins between elements
</SPECIFICATIONS>

<CONSTRAINTS>
- All text must be in {language}, using a simple **sans-serif** font (no serif, no cursive)
- Use only these authorized colors: **black, grey and blue #0d6efd**
- Apply **flat design principles**: no shadows, gradients, or 3D effects
- Maintain a **clear visual hierarchy**, with the main message easy to read
</CONSTRAINTS>

Create thios simple infographic strictly following these instructions.
"""
        
        # Add personalization if learner profile is available
        if learner_profile:
            learning_style = learner_profile.get("learning_style", "")
            level = learner_profile.get("level", "")
            
            personalization = ""
            if learning_style:
                personalization += f"\n- Adapt visual style for {learning_style} learning preference"
            if level:
                personalization += f"\n- Adjust complexity for {level} level"
                
            if personalization:
                base_prompt += f"\n\nPersonalization:{personalization}"
        
        return base_prompt
    
    async def _save_image_to_file(
        self,
        image_base64: str,
        learner_session_id: UUID,
        slide_id: Optional[UUID] = None
    ) -> str:
        """Save base64 image to file and return the file path"""
        try:
            # Create session-specific directory
            session_dir = self.image_storage_path / str(learner_session_id)
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            if slide_id:
                filename = f"slide_{slide_id}_image.png"
            else:
                import uuid
                filename = f"image_{uuid.uuid4()}.png"
            
            file_path = session_dir / filename
            
            # Remove existing image if it exists (one image per slide)
            if file_path.exists():
                logger.info(f"Removing existing image: {file_path}")
                file_path.unlink()
            
            # Decode base64 and save to file
            image_bytes = base64.b64decode(image_base64)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(image_bytes)
            
            # Return relative path for database storage
            try:
                relative_path = str(file_path.relative_to(Path.cwd()))
            except ValueError:
                # If relative_to fails, return the absolute path relative to backend directory
                backend_path = Path(__file__).parent.parent.parent
                try:
                    relative_path = str(file_path.relative_to(backend_path))
                except ValueError:
                    # Last resort - return absolute path
                    relative_path = str(file_path)
            
            logger.debug(f"Image saved successfully: {relative_path}")
            
            return relative_path
            
        except Exception as e:
            logger.error(f"Error saving image to file: {str(e)}")
            raise Exception(f"Failed to save image: {str(e)}")
    
    async def delete_slide_image(self, image_path: str) -> bool:
        """Delete a slide image file"""
        try:
            full_path = Path(image_path)
            if full_path.exists():
                full_path.unlink()
                logger.info(f"Deleted image file: {image_path}")
                return True
            else:
                logger.warning(f"Image file not found for deletion: {image_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting image file {image_path}: {str(e)}")
            return False