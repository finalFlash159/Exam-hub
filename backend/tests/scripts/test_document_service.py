import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import get_db_session
from app.services.document_service import DocumentService
from app.repositories.file_repository import FileRepository

async def test_document_service():
    
    # Get database session
    async for session in get_db_session():
        try:
            # Tạo DocumentService
            doc_service = DocumentService(session)
            file_repo = FileRepository(session)
            
            print("🧪 Testing DocumentService...")
            
            # Test 1: Kiểm tra file có sẵn trong database
            print("\n📁 Test 1: Checking existing files...")
            user_files = await file_repo.get_user_files("test-user-id", limit=5)
            print(f"Found {len(user_files)} files in database")
            
            if user_files:
                file_record = user_files[0]
                print(f"Testing with file: {file_record.original_filename}")
                print(f"File ID: {file_record.id}")
                print(f"Processing status: {file_record.processing_status}")
                
                # Test 2: Process file
                print(f"\n🔄 Test 2: Processing file...")
                result = await doc_service.process_uploaded_file(
                    file_record.id, 
                    file_record.owner_id
                )
                print(f"Processing result: {result}")
                
                # Test 3: Get content
                print(f"\n📄 Test 3: Getting file content...")
                content = await doc_service.get_file_content(
                    file_record.id,
                    file_record.owner_id
                )
                if content:
                    print(f"Content length: {len(content)} characters")
                    print(f"First 100 chars: {content[:100]}...")
                else:
                    print("No content found")
                    
                # Test 4: Get status
                print(f"\n📊 Test 4: Getting processing status...")
                status = await doc_service.get_processing_status(
                    file_record.id,
                    file_record.owner_id
                )
                print(f"Status: {status}")
                
            else:
                print("❌ No files found in database to test with")
                
            print("\n✅ All tests completed!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(test_document_service())