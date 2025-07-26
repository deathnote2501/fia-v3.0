"""
FIA v3.0 - Training Controller
FastAPI routes for training management
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
import io
import logging
from pathlib import Path

from app.infrastructure.database import get_database_session
from app.infrastructure.auth import get_current_trainer
from app.domain.entities.trainer import Trainer
from app.domain.entities.training import Training
from app.domain.schemas.training import TrainingUpload, TrainingResponse, TrainingListResponse
from app.domain.services.file_storage_service import FileStorageService
from app.adapters.repositories.training_repository import TrainingRepository
from app.utils.file_validation import validate_training_file, get_file_type_from_extension, FileValidationError

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trainings", tags=["trainings"])


@router.post("/", response_model=TrainingResponse, status_code=status.HTTP_201_CREATED)
async def create_training(
    name: str = Form(..., min_length=1, max_length=200),
    description: Optional[str] = Form(None, max_length=1000),
    file: UploadFile = File(..., description="Training material (PDF, PPT, PPTX)"),
    current_trainer: Trainer = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """
    Create new training with file upload
    
    Supports multipart/form-data with:
    - name: Training name (required)
    - description: Training description (optional)
    - file: Training material file (PDF, PPT, PPTX, max 50MB)
    """
    
    try:
        # Validate uploaded file
        file_extension, mime_type = await validate_training_file(file)
        file_type = get_file_type_from_extension(file_extension)
        
        # Initialize services
        file_storage = FileStorageService()
        training_repo = TrainingRepository(db)
        
        # Create training entity first (for ID generation)
        training = Training(
            trainer_id=current_trainer.id,
            name=name.strip(),
            description=description.strip() if description else None,
            file_name=file.filename,
            file_type=file_type,
            mime_type=mime_type
        )
        
        # Start database transaction
        db.add(training)
        await db.flush()  # Get the training ID without committing
        
        try:
            # Store file using the generated training ID
            file_content = io.BytesIO(await file.read())
            file_path, file_size = await file_storage.store_training_file(
                trainer_id=current_trainer.id,
                training_id=training.id,
                file_content=file_content,
                original_filename=file.filename,
                mime_type=mime_type
            )
            
            # Update training with file information
            training.file_path = file_path
            training.file_size = file_size
            
            # Commit transaction
            await db.commit()
            await db.refresh(training)
            
            return training
            
        except Exception as storage_error:
            # Rollback database transaction
            await db.rollback()
            
            # Try to clean up any partially stored file
            try:
                if 'file_path' in locals():
                    await file_storage.delete_training_file(file_path)
            except:
                pass  # Ignore cleanup errors
            
            logger.error(f"File storage error during training creation: {str(storage_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File storage error occurred"
            )
            
    except FileValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Training creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Training creation failed"
        )


@router.get("/", response_model=List[TrainingListResponse])
async def list_trainings(
    current_trainer: Trainer = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """List all trainings for current trainer"""
    
    training_repo = TrainingRepository(db)
    trainings = await training_repo.get_by_trainer_id(current_trainer.id)
    return trainings


@router.get("/{training_id}", response_model=TrainingResponse)
async def get_training(
    training_id: UUID,
    current_trainer: Trainer = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """Get specific training by ID"""
    
    training_repo = TrainingRepository(db)
    training = await training_repo.get_by_id(training_id)
    
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )
    
    # Check ownership
    if training.trainer_id != current_trainer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return training


@router.delete("/{training_id}")
async def delete_training(
    training_id: UUID,
    current_trainer: Trainer = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """Delete training and associated file"""
    
    training_repo = TrainingRepository(db)
    training = await training_repo.get_by_id(training_id)
    
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )
    
    # Check ownership
    if training.trainer_id != current_trainer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Delete file first
        if training.file_path:
            file_storage = FileStorageService()
            await file_storage.delete_training_file(training.file_path)
        
        # Delete from database
        await training_repo.delete(training_id)
        await db.commit()
        
        return {"message": "Training deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Training deletion failed for training_id {training_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Training deletion failed"
        )


@router.get("/{training_id}/download")
async def download_training_file(
    training_id: UUID,
    current_trainer: Trainer = Depends(get_current_trainer),
    db: AsyncSession = Depends(get_database_session)
):
    """
    Download training file
    
    Returns the original training file with appropriate headers for download.
    Only the trainer who uploaded the file can download it.
    """
    
    training_repo = TrainingRepository(db)
    training = await training_repo.get_by_id(training_id)
    
    # Check if training exists
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )
    
    # Check ownership - only trainer who uploaded can download
    if training.trainer_id != current_trainer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only download your own training files"
        )
    
    # Check if file information exists
    if not training.file_path or not training.file_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training file not found"
        )
    
    # Get file storage service and check if file exists
    file_storage = FileStorageService()
    file_exists = await file_storage.file_exists(training.file_path)
    
    if not file_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training file not found on server"
        )
    
    try:
        # Get full file path
        full_file_path = await file_storage.get_training_file_path(training.file_path)
        
        # Determine content type
        content_type = training.mime_type or "application/octet-stream"
        
        # Create appropriate filename for download
        download_filename = training.file_name or f"training_{training_id}{Path(training.file_path).suffix}"
        
        # Return file using FileResponse for better performance
        return FileResponse(
            path=str(full_file_path),
            filename=download_filename,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=\"{download_filename}\"",
                "Content-Type": content_type,
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training file not found on server"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Permission denied accessing training file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading file: {str(e)}"
        )