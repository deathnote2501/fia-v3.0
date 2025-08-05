#!/usr/bin/env python3
"""
Test script pour vérifier la configuration Cloudflare R2
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.adapters.outbound.settings_adapter import SettingsAdapter
from app.adapters.outbound.storage_factory import StorageFactory
from app.adapters.outbound.cloudflare_r2_storage_adapter import CloudflareR2StorageAdapter

async def test_r2_configuration():
    """Test complet de la configuration R2"""
    
    print("🧪 TESTING CLOUDFLARE R2 CONFIGURATION")
    print("=" * 50)
    
    # 1. Test des Settings
    print("\n1️⃣ Testing Settings...")
    settings = SettingsAdapter()
    
    storage_type = settings.get_storage_type()
    print(f"   Storage Type: {storage_type}")
    
    if storage_type.lower() != "r2":
        print("   ⚠️  STORAGE_TYPE is not 'r2' - using local storage")
        print("   💡 Set STORAGE_TYPE='r2' in .env to test R2")
        return
    
    # 2. Test des Variables R2
    print("\n2️⃣ Testing R2 Variables...")
    bucket = settings.get_r2_bucket_name()
    endpoint = settings.get_r2_endpoint_url()
    access_key = settings.get_r2_access_key()
    secret_key = settings.get_r2_secret_key()
    
    print(f"   Bucket: {bucket}")
    print(f"   Endpoint: {endpoint}")
    print(f"   Access Key: {access_key[:10]}..." if access_key else "   Access Key: NOT SET")
    print(f"   Secret Key: {'SET' if secret_key else 'NOT SET'}")
    
    if not all([bucket, endpoint, access_key, secret_key]):
        print("   ❌ Missing R2 configuration variables")
        print("   💡 Check your .env file for R2_* variables")
        return
    
    # 3. Test de la Factory
    print("\n3️⃣ Testing Storage Factory...")
    try:
        storage = StorageFactory.create_storage_adapter(settings)
        print(f"   Storage Adapter: {type(storage).__name__}")
        
        if isinstance(storage, CloudflareR2StorageAdapter):
            print("   ✅ R2 Storage Adapter created")
        else:
            print("   ⚠️  Fallback to local storage (R2 config issue)")
            return
            
    except Exception as e:
        print(f"   ❌ Factory creation failed: {e}")
        return
    
    # 4. Test de Connectivité R2
    print("\n4️⃣ Testing R2 Connectivity...")
    try:
        health_check = await storage.health_check()
        print(f"   Health Check: {health_check}")
        
        if health_check.get('status') == 'healthy':
            print("   ✅ R2 connection successful!")
        else:
            print(f"   ❌ R2 connection failed: {health_check.get('message', 'Unknown error')}")
            return
            
    except Exception as e:
        print(f"   ❌ Connectivity test failed: {e}")
        return
    
    # 5. Test d'Upload (optionnel)
    print("\n5️⃣ Testing R2 Upload (Optional)...")
    try:
        # Create a test file
        test_content = b"Hello from FIA v3.0 R2 test!"
        from io import BytesIO
        from uuid import uuid4
        
        # Simulate file upload
        trainer_id = uuid4()
        training_id = uuid4()
        file_obj = BytesIO(test_content)
        
        object_key, file_size = await storage.store_training_file(
            trainer_id=trainer_id,
            training_id=training_id,
            file_content=file_obj,
            original_filename="test.txt",
            mime_type="text/plain"
        )
        
        print(f"   ✅ Upload successful!")
        print(f"      Object Key: {object_key}")
        print(f"      File Size: {file_size} bytes")
        
        # Test file existence
        exists = await storage.file_exists(object_key)
        print(f"   ✅ File exists check: {exists}")
        
        # Cleanup test file
        deleted = await storage.delete_training_file(object_key)
        print(f"   ✅ Cleanup successful: {deleted}")
        
    except Exception as e:
        print(f"   ⚠️  Upload test failed: {e}")
        print("   💡 This might be a permissions issue")
    
    print("\n" + "=" * 50)
    print("🎉 R2 CONFIGURATION TEST COMPLETE!")
    print("\n📋 Next Steps:")
    print("   1. If tests passed: Set the same variables on Railway")
    print("   2. Deploy your application") 
    print("   3. Test via: https://your-app.railway.app/api/storage/status")

if __name__ == "__main__":
    asyncio.run(test_r2_configuration())