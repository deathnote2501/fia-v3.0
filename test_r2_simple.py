#!/usr/bin/env python3
"""
Test script simple pour vérifier la configuration Cloudflare R2 - Sans DB
"""

import os
import asyncio
import boto3
from io import BytesIO
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_r2_simple():
    """Test direct de la configuration R2 sans imports complexes"""
    
    print("🧪 TESTING CLOUDFLARE R2 CONFIGURATION (SIMPLE)")
    print("=" * 60)
    
    # 1. Récupérer les variables d'environnement
    print("\n1️⃣ Reading Environment Variables...")
    
    storage_type = os.getenv("STORAGE_TYPE", "local")
    bucket_name = os.getenv("R2_BUCKET_NAME", "")
    endpoint_url = os.getenv("R2_ENDPOINT_URL", "")
    access_key = os.getenv("R2_ACCESS_KEY", "")
    secret_key = os.getenv("R2_SECRET_KEY", "")
    
    print(f"   STORAGE_TYPE: {storage_type}")
    print(f"   R2_BUCKET_NAME: {bucket_name}")
    print(f"   R2_ENDPOINT_URL: {endpoint_url}")
    print(f"   R2_ACCESS_KEY: {access_key[:10]}..." if access_key else "   R2_ACCESS_KEY: NOT SET")
    print(f"   R2_SECRET_KEY: {'SET (' + str(len(secret_key)) + ' chars)' if secret_key else 'NOT SET'}")
    
    if not all([bucket_name, endpoint_url, access_key, secret_key]):
        print("   ❌ Missing R2 configuration!")
        print("   💡 Check your .env file")
        return False
    
    # 2. Test de création du client S3 (R2)
    print("\n2️⃣ Creating R2 (S3) Client...")
    
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'  # R2 uses 'auto' region
        )
        print("   ✅ R2 client created successfully")
    except Exception as e:
        print(f"   ❌ Failed to create R2 client: {e}")
        return False
    
    # 3. Test de connectivité (head_bucket)
    print("\n3️⃣ Testing R2 Connectivity...")
    
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"   ✅ Successfully connected to bucket '{bucket_name}'")
    except Exception as e:
        print(f"   ❌ Failed to connect to bucket: {e}")
        print("   💡 Check bucket name and permissions")
        return False
    
    # 4. Test d'upload/download
    print("\n4️⃣ Testing Upload/Download...")
    
    test_key = f"test/fia-v3-test-{uuid4()}.txt"
    test_content = b"Hello from FIA v3.0 R2 test! This is a test file."
    
    try:
        # Upload test file
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain',
            Metadata={
                'test': 'fia-v3-r2-test',
                'timestamp': str(asyncio.get_event_loop().time())
            }
        )
        print(f"   ✅ Upload successful: {test_key}")
        
        # Check if file exists
        s3_client.head_object(Bucket=bucket_name, Key=test_key)
        print("   ✅ File exists check passed")
        
        # Download and verify content
        response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
        downloaded_content = response['Body'].read()
        
        if downloaded_content == test_content:
            print("   ✅ Download and content verification passed")
        else:
            print("   ❌ Content verification failed")
            return False
        
        # Get file info
        head_response = s3_client.head_object(Bucket=bucket_name, Key=test_key)
        file_size = head_response.get('ContentLength', 0)
        content_type = head_response.get('ContentType', 'unknown')
        print(f"   📊 File info: {file_size} bytes, {content_type}")
        
    except Exception as e:
        print(f"   ❌ Upload/Download test failed: {e}")
        return False
    
    # 5. Cleanup
    print("\n5️⃣ Cleaning up test file...")
    
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("   ✅ Test file deleted successfully")
    except Exception as e:
        print(f"   ⚠️  Cleanup failed: {e}")
    
    # 6. Summary
    print("\n" + "=" * 60)
    print("🎉 R2 CONFIGURATION TEST COMPLETE!")
    print("\n✅ ALL TESTS PASSED!")
    print("\n📋 Your R2 configuration is working correctly:")
    print(f"   • Bucket: {bucket_name}")
    print(f"   • Endpoint: {endpoint_url}")
    print(f"   • Upload/Download: Working")
    print(f"   • Permissions: Correct")
    
    print("\n🚀 Next Steps:")
    print("   1. Set STORAGE_TYPE='r2' in your .env")
    print("   2. Deploy to Railway with the same variables")
    print("   3. Test via: https://jeromeiavarone.fr/api/storage/status")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_r2_simple())
    if success:
        print("\n🎯 Ready for production deployment!")
    else:
        print("\n❌ Fix configuration issues before deploying")