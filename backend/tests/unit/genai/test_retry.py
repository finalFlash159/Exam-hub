import pytest
import asyncio
from unittest.mock import AsyncMock
from app.genai.utils.retry import retry_with_backoff, RetryConfig


class TestRetryLogic:
    """Test retry mechanism và backoff."""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt_no_retry(self):
        """Success ngay lần đầu → không retry."""

        # ARRANGE: Mock function luôn success
        mock_func = AsyncMock(return_value="success")

        # ACT: Call với retry wrapper
        result = await retry_with_backoff(
            mock_func,
            config=RetryConfig(max_attempts=3),
            context="test"
        )

        # ASSERT
        assert result == "success"
        assert mock_func.call_count == 1  # Chỉ gọi 1 lần

    @pytest.mark.asyncio
    async def test_retry_until_success(self):
        """Fail 2 lần, success lần 3 → có retry."""

        # ARRANGE: Mock fails twice then succeeds
        mock_func = AsyncMock(side_effect=[
            Exception("Network error"),  # Attempt 1: Fail
            Exception("Timeout"),         # Attempt 2: Fail
            "success"                     # Attempt 3: Success
        ])

        # ACT
        result = await retry_with_backoff(
            mock_func,
            config=RetryConfig(
                max_attempts=3,
                initial_delay=0.01  # Fast for testing
            ),
            context="test"
        )

        # ASSERT
        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_max_attempts_exhausted_raises_exception(self):
        """Fail hết max_attempts → raise exception."""

        # ARRANGE: Mock luôn fail
        mock_func = AsyncMock(side_effect=Exception("Always fail"))

        # ACT & ASSERT: Expect exception
        with pytest.raises(Exception, match="Always fail"):
            await retry_with_backoff(
                mock_func,
                config=RetryConfig(
                    max_attempts=2,
                    initial_delay=0.01
                ),
                context="test"
            )

        # Verify đã thử đủ số lần
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_timeout_raises_timeout_error(self):
        """Function chạy quá timeout → TimeoutError."""

        # ARRANGE: Slow function (10 seconds)
        async def slow_function():
            await asyncio.sleep(10)
            return "too slow"

        # ACT & ASSERT: Expect timeout
        with pytest.raises(asyncio.TimeoutError):
            await retry_with_backoff(
                slow_function,
                config=RetryConfig(
                    max_attempts=1,
                    timeout=0.1  # 100ms timeout
                ),
                context="test"
            )

    def test_exponential_backoff_delay_calculation(self):
        """Test delay được tính đúng công thức: delay = initial * (base ^ attempt)."""

        config = RetryConfig(
            initial_delay=0.1,
            exponential_base=2.0
        )

        # Công thức: 0.1 * (2 ^ attempt)
        assert config.get_delay(0) == 0.1   # 0.1 * 2^0 = 0.1
        assert config.get_delay(1) == 0.2   # 0.1 * 2^1 = 0.2
        assert config.get_delay(2) == 0.4   # 0.1 * 2^2 = 0.4
        assert config.get_delay(3) == 0.8   # 0.1 * 2^3 = 0.8

    def test_max_delay_cap(self):
        """Delay không vượt quá max_delay."""

        config = RetryConfig(
            initial_delay=1.0,
            max_delay=5.0,
            exponential_base=2.0
        )

        # After nhiều attempts, delay should cap
        # 1.0 * 2^10 = 1024, nhưng max = 5.0
        assert config.get_delay(10) == 5.0

    @pytest.mark.asyncio
    async def test_retry_with_specific_exceptions_only(self):
        """Chỉ retry cho exception types được chỉ định."""

        # Mock raises ValueError
        mock_func = AsyncMock(side_effect=ValueError("Specific error"))

        # Config chỉ retry cho TypeError (không phải ValueError)
        with pytest.raises(ValueError):
            await retry_with_backoff(
                mock_func,
                config=RetryConfig(max_attempts=3),
                retryable_exceptions=(TypeError,),  # Chỉ retry TypeError
                context="test"
            )

        # Không retry → chỉ gọi 1 lần
        assert mock_func.call_count == 1