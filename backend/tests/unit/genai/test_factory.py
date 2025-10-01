import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.genai.clients.factory import AIClientFactory
from app.schemas.exam_schemas import AIProvider

async def test_factory():
    print("🧪 Testing Factory System...")
    
    # Test 1: Create mock client
    try:
        client = AIClientFactory.create_client(AIProvider.MOCK)
        print("✅ Mock client created successfully")
        
        # Test health check
        is_healthy = await client.health_check()
        print(f"✅ Health check: {is_healthy}")
        
        # Test capabilities
        capabilities = client.get_capabilities()
        print(f"✅ Capabilities: {capabilities['provider']}")
        
    except Exception as e:
        print(f"❌ Error creating client: {e}")
    
    # Test 2: Get available clients
    try:
        available = await AIClientFactory.get_available_clients()
        print(f"✅ Found {len(available)} providers")
        for client_info in available:
            status = "🟢" if client_info["is_healthy"] else "🔴"
            print(f"  {status} {client_info['provider']}: {client_info['status']}")
            
    except Exception as e:
        print(f"❌ Error getting available clients: {e}")

if __name__ == "__main__":
    asyncio.run(test_factory())