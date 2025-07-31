"""
FIA v3.0 - Document Processor Service
Pure domain service for processing training documents (PDF/PPT/PPTX)
"""

import logging
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, Optional, Protocol

# Configure logger
logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Exception for document processing errors"""
    def __init__(self, message: str, file_path: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.file_path = file_path
        self.original_error = original_error


class VertexAIPort(Protocol):
    """Port interface for Vertex AI operations"""
    async def upload_file_with_retry(self, file_path: str, mime_type: str) -> Any: ...
    async def generate_content(self, prompt: str, generation_config: Optional[Dict[str, Any]] = None) -> str: ...
    async def generate_with_file(self, prompt: str, file_path: str, mime_type: str, 
                                generation_config: Optional[Dict[str, Any]] = None) -> str: ...


class DocumentProcessor:
    """Pure domain service for document processing"""
    
    # Supported file types and their MIME types
    SUPPORTED_MIME_TYPES = {
        '.pdf': 'application/pdf',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.md': 'text/markdown'
    }
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(self, vertex_ai_adapter: Optional[VertexAIPort] = None):
        """Initialize document processor with Vertex AI adapter"""
        self.vertex_ai_adapter = vertex_ai_adapter
        self.max_retries = 3
        
        logger.info("📄 DOCUMENT [PROCESSOR] initialized")
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate document file before processing"""
        file_path_obj = Path(file_path)
        
        # Check file existence
        if not file_path_obj.exists():
            raise DocumentProcessingError(
                f"Training file not found: {file_path}",
                file_path,
                FileNotFoundError(f"File not found: {file_path}")
            )
        
        # Check file size
        file_size = file_path_obj.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise DocumentProcessingError(
                f"File too large: {file_size} bytes (max {self.MAX_FILE_SIZE})",
                file_path
            )
        
        # Check file type
        file_extension = file_path_obj.suffix.lower()
        mime_type = self.SUPPORTED_MIME_TYPES.get(file_extension)
        if not mime_type:
            supported_types = ", ".join(self.SUPPORTED_MIME_TYPES.keys())
            raise DocumentProcessingError(
                f"Unsupported file type: {file_extension}. Supported: {supported_types}",
                file_path
            )
        
        return {
            "file_path": file_path,
            "file_name": file_path_obj.name,
            "file_size": file_size,
            "file_extension": file_extension,
            "mime_type": mime_type,
            "is_valid": True
        }
    
    def get_document_analysis_prompt(self) -> str:
        """Get the document analysis prompt"""
        return """
        Analyse ce document de formation et extrais les informations clés :
        
        1. Sujet principal et objectifs pédagogiques
        2. Concepts clés et notions importantes abordés
        3. Structure du contenu (chapitres, sections, modules)
        4. Niveau de complexité et prérequis apparents
        5. Exemples pratiques, cas d'usage ou exercices mentionnés
        6. Public cible suggéré par le contenu
        7. Durée estimée de formation basée sur la densité du contenu
        
        Fournis un résumé structuré et détaillé du contenu de formation qui servira 
        à créer un plan personnalisé pour l'apprenant.
        
        Format de réponse souhaité :
        - Sujet principal : [description]
        - Objectifs : [liste des objectifs]
        - Concepts clés : [liste des concepts]
        - Structure : [organisation du contenu]
        - Niveau : [débutant/intermédiaire/avancé]
        - Exemples pratiques : [présence et types]
        - Public cible : [profils recommandés]
        - Estimation durée : [heures/jours]
        """
    
    async def _process_markdown_file(self, file_path: str, file_info: Dict[str, Any]) -> str:
        """Process markdown file by reading its content directly"""
        try:
            start_time = time.time()
            
            # Read markdown file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content or len(content.strip()) < 10:
                raise DocumentProcessingError(
                    "Markdown file is empty or too short",
                    file_path
                )
            
            duration = time.time() - start_time
            
            # Create analysis based on markdown content
            analysis = f"""
            - Sujet principal : {file_info['file_name'].replace('.md', '').replace('_', ' ').title()}
            - Objectifs : Formation basée sur contenu markdown personnalisé
            - Concepts clés : Contenu défini dans le document markdown
            - Structure : Organisation selon le format du document markdown
            - Niveau : Adaptatif selon le profil de l'apprenant
            - Exemples pratiques : Intégrés dans le contenu markdown
            - Public cible : Défini selon les besoins spécifiques
            - Estimation durée : 1-3 heures selon la complexité
            
            Contenu du document :
            {content}
            """
            
            logger.info(f"✅ DOCUMENT [MARKDOWN] {file_info['file_name']} - "
                       f"{len(content)} chars read in {duration:.2f}s")
            
            return analysis.strip()
            
        except FileNotFoundError:
            raise DocumentProcessingError(
                f"Markdown file not found: {file_path}",
                file_path
            )
        except UnicodeDecodeError:
            raise DocumentProcessingError(
                f"Unable to read markdown file (encoding issue): {file_path}",
                file_path
            )
        except Exception as e:
            raise DocumentProcessingError(
                f"Error processing markdown file: {str(e)}",
                file_path,
                e
            )
    
    async def process_document(self, file_path: str) -> str:
        """
        Process document and extract content for plan generation
        
        Args:
            file_path: Path to the PDF, PowerPoint, or Markdown file
            
        Returns:
            Extracted content from the document
            
        Raises:
            DocumentProcessingError: If processing fails
        """
        # Validate file first
        file_info = self.validate_file(file_path)
        
        logger.info(f"📄 DOCUMENT [PROCESSING] {file_info['file_name']} "
                   f"(MIME: {file_info['mime_type']}, Size: {file_info['file_size']} bytes)")
        
        # Handle markdown files directly
        if file_info['mime_type'] == 'text/markdown':
            return await self._process_markdown_file(file_path, file_info)
        
        # For PDF/PPT/PPTX files, use Vertex AI
        if not self.vertex_ai_adapter:
            raise DocumentProcessingError(
                "Vertex AI adapter not configured for document processing",
                file_path
            )
        
        # Process with retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"📄 DOCUMENT [ATTEMPT] {attempt + 1}/{self.max_retries} - {file_info['file_name']}")
                
                start_time = time.time()
                
                # Get analysis prompt
                analysis_prompt = self.get_document_analysis_prompt()
                
                # Process document with Vertex AI
                response = await asyncio.wait_for(
                    self.vertex_ai_adapter.generate_with_file(
                        prompt=analysis_prompt,
                        file_path=file_path,
                        mime_type=file_info['mime_type']
                    ),
                    timeout=60.0  # 1 minute timeout
                )
                
                duration = time.time() - start_time
                
                # Validate response
                if not response or len(response.strip()) < 10:
                    raise DocumentProcessingError(
                        "Document processing returned empty or invalid response",
                        file_path
                    )
                
                # Log success
                logger.info(f"✅ DOCUMENT [SUCCESS] {file_info['file_name']} - "
                           f"{len(response)} chars in {duration:.2f}s")
                
                return response
                
            except asyncio.TimeoutError as e:
                last_error = e
                logger.warning(f"⏰ DOCUMENT [TIMEOUT] Attempt {attempt + 1} - {file_info['file_name']}")
                
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ DOCUMENT [ERROR] Attempt {attempt + 1} - {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = 2.0 * (attempt + 1)
                logger.info(f"🔄 DOCUMENT [RETRY] Waiting {wait_time}s before next attempt...")
                await asyncio.sleep(wait_time)
        
        # All attempts failed
        error_msg = f"Document processing failed after {self.max_retries} attempts"
        logger.error(f"❌ DOCUMENT [FAILED] {file_info['file_name']} - {error_msg}")
        
        raise DocumentProcessingError(
            error_msg,
            file_path,
            last_error
        )
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information without processing"""
        try:
            return self.validate_file(file_path)
        except DocumentProcessingError:
            # Return basic info even if validation fails
            file_path_obj = Path(file_path)
            return {
                "file_path": file_path,
                "file_name": file_path_obj.name,
                "file_extension": file_path_obj.suffix.lower(),
                "exists": file_path_obj.exists(),
                "is_valid": False
            }
    
    def is_supported_file(self, file_path: str) -> bool:
        """Check if file type is supported"""
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.SUPPORTED_MIME_TYPES
    
    def get_supported_types(self) -> Dict[str, str]:
        """Get supported file types and their MIME types"""
        return self.SUPPORTED_MIME_TYPES.copy()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            "max_file_size_mb": self.MAX_FILE_SIZE // (1024 * 1024),
            "supported_extensions": list(self.SUPPORTED_MIME_TYPES.keys()),
            "max_retries": self.max_retries,
            "vertex_ai_configured": self.vertex_ai_adapter is not None
        }