"""
FIA v3.0 - Cloudflare R2 Storage Adapter
S3-compatible storage adapter for persistent file storage on Railway
"""

import boto3
import logging
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Tuple
from uuid import UUID
from botocore.exceptions import ClientError, NoCredentialsError

from app.domain.ports.file_storage import FileStoragePort
from app.domain.ports.settings_port import SettingsPort

logger = logging.getLogger(__name__)


class CloudflareR2StorageAdapter(FileStoragePort):
    """Cloudflare R2 storage implementation using S3-compatible API"""
    
    def __init__(self, settings_port: SettingsPort):
        self.settings = settings_port
        
        # R2 configuration
        self.bucket_name = self.settings.get_r2_bucket_name()
        self.endpoint_url = self.settings.get_r2_endpoint_url()
        self.access_key = self.settings.get_r2_access_key()
        self.secret_key = self.settings.get_r2_secret_key()
        
        # Initialize S3 client for R2
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name='auto'  # R2 uses 'auto' region
            )
            logger.info("✅ R2 storage client initialized successfully")
        except NoCredentialsError:
            logger.error("❌ R2 credentials not found - using fallback local storage")
            self.s3_client = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize R2 client: {e}")
            self.s3_client = None
    
    def _generate_object_key(self, trainer_id: UUID, training_id: UUID, original_filename: str) -> str:
        """Generate S3 object key with organized structure"""
        file_extension = Path(original_filename).suffix.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{training_id}_{timestamp}{file_extension}"
        
        # Object key: trainings/{trainer_id}/{filename}
        return f"trainings/{trainer_id}/{filename}"
    
    async def store_training_file(
        self,
        trainer_id: UUID,
        training_id: UUID,
        file_content: BinaryIO,
        original_filename: str,
        mime_type: str
    ) -> Tuple[str, int]:
        """Store training file in Cloudflare R2"""
        
        if not self.s3_client:
            raise RuntimeError("R2 storage not available - check configuration")
        
        # Generate object key
        object_key = self._generate_object_key(trainer_id, training_id, original_filename)
        
        # Read content and get size
        file_content.seek(0)
        content = file_content.read()
        file_size = len(content)
        
        try:
            # Upload to R2
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=content,
                ContentType=mime_type,
                Metadata={
                    'trainer_id': str(trainer_id),
                    'training_id': str(training_id),
                    'original_filename': original_filename,
                    'upload_timestamp': datetime.now().isoformat()
                }
            )
            
            logger.info(f"✅ File uploaded to R2: {object_key} ({file_size} bytes)")
            return object_key, file_size
            
        except ClientError as e:
            logger.error(f"❌ R2 upload failed: {e}")
            raise RuntimeError(f"Failed to upload file to R2: {e}")
    
    async def get_training_file_path(self, file_path: str) -> str:
        """Return R2 object key (file_path is the object key)"""
        return file_path
    
    async def delete_training_file(self, file_path: str) -> bool:
        """Delete training file from R2"""
        
        if not self.s3_client:
            logger.error("❌ R2 storage not available for deletion")
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            logger.info(f"✅ File deleted from R2: {file_path}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ R2 deletion failed: {e}")
            return False
    
    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in R2"""
        
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"❌ R2 head_object failed: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """Get file information from R2"""
        
        if not self.s3_client:
            return {}
        
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            
            return {
                'size': response.get('ContentLength', 0),
                'modified': response.get('LastModified'),
                'content_type': response.get('ContentType'),
                'metadata': response.get('Metadata', {}),
                'exists': True
            }
            
        except ClientError as e:
            logger.error(f"❌ R2 get_file_info failed: {e}")
            return {}
    
    async def get_file_download_content(self, file_path: str) -> bytes:
        """Download file content from R2"""
        
        if not self.s3_client:
            raise RuntimeError("R2 storage not available")
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            
            content = response['Body'].read()
            logger.info(f"✅ File downloaded from R2: {file_path} ({len(content)} bytes)")
            return content
            
        except ClientError as e:
            logger.error(f"❌ R2 download failed: {e}")
            raise RuntimeError(f"Failed to download file from R2: {e}")
    
    def is_available(self) -> bool:
        """Check if R2 storage is properly configured and available"""
        return self.s3_client is not None
    
    async def health_check(self) -> dict:
        """Health check for R2 storage"""
        
        if not self.s3_client:
            return {
                'status': 'unavailable',
                'message': 'R2 client not initialized'
            }
        
        try:
            # Try to list bucket (basic connectivity test)
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            
            return {
                'status': 'healthy',
                'bucket': self.bucket_name,
                'endpoint': self.endpoint_url
            }
            
        except ClientError as e:
            return {
                'status': 'error',
                'message': f"R2 connectivity failed: {e}"
            }