
import pytest  # Test framework
import json    # Parse JSON để verify
from app.genai.clients.mock_client import MockClient


class TestMockClient:
    """Test suite cho MockClient."""

    # Hàm này chạy TRƯỚC mỗi test method
    def setup_method(self):
        """Khởi tạo client cho mỗi test."""
        self.client = MockClient()
        # Bây giờ mọi test đều có self.client

    # Test 1: Health check
    @pytest.mark.asyncio  # PHẢI CÓ cho async function
    async def test_health_check_returns_true(self):
        """MockClient luôn healthy vì không cần API key."""

        # ACT: Gọi method cần test
        result = await self.client.health_check()

        # ASSERT: Kiểm tra kết quả
        assert result is True
        # Nếu False → test FAILED

    # Test 2: Configuration
    def test_is_configured_returns_true(self):
        """MockClient luôn configured."""

        result = self.client.is_configured()

        assert result is True

    # Test 3: Capabilities structure
    def test_get_capabilities_returns_correct_structure(self):
        """Verify capabilities có đúng keys và values."""

        caps = self.client.get_capabilities()

        # Check keys exist
        assert "provider" in caps
        assert "model" in caps
        assert "supports_json" in caps

        # Check specific values
        assert caps["provider"] == "mock"
        assert caps["model"] == "mock-v1.0"
        assert caps["supports_json"] is True

    # Test 4: Generate exam format
    @pytest.mark.asyncio
    async def test_generate_exam_returns_valid_format(self):
        """Kiểm tra generate_exam trả về đúng structure."""

        # ACT: Call với params
        result = await self.client.generate_exam(
            prompt="Generate 1 question about Python",
            temperature=0.7
        )

        # ASSERT: Check response structure
        assert "success" in result
        assert "raw_response" in result
        assert "metadata" in result
        assert "error" in result

        # Check values
        assert result["success"] is True
        assert result["error"] is None

        # raw_response phải là valid JSON string
        raw = result["raw_response"]
        parsed = json.loads(raw)  # Raises error if invalid JSON
        assert isinstance(parsed, list)
        assert len(parsed) > 0

    # Test 5: Metadata structure
    @pytest.mark.asyncio
    async def test_generate_exam_metadata(self):
        """Verify metadata có đủ thông tin."""

        result = await self.client.generate_exam(prompt="test")
        metadata = result["metadata"]

        assert metadata["ai_provider"] == "mock"
        assert metadata["model"] == "mock-v1.0"
        assert "generated_at" in metadata

