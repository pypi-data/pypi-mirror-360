import pytest
from activefence_client_sdk.utils import async_retry_with_exponential_backoff, retry_with_exponential_backoff

# Constants for test values
MAX_RETRIES = 3
MAX_RETRIES_FAIL = 2
EXPECTED_CALLS = 3


def test_retry_with_exponential_backoff_success() -> None:
    calls = {"count": 0}

    @retry_with_exponential_backoff(max_retries=MAX_RETRIES, base_delay=0.01)
    def flaky() -> str:
        calls["count"] += 1
        if calls["count"] < EXPECTED_CALLS:
            raise ValueError("fail")
        return "ok"

    assert flaky() == "ok"
    assert calls["count"] == EXPECTED_CALLS


def test_retry_with_exponential_backoff_raises() -> None:
    @retry_with_exponential_backoff(max_retries=MAX_RETRIES_FAIL, base_delay=0.01)
    def always_fail() -> None:
        raise RuntimeError("fail always")

    with pytest.raises(RuntimeError):
        always_fail()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_retry_with_exponential_backoff_success() -> None:
    calls = {"count": 0}

    @async_retry_with_exponential_backoff(max_retries=MAX_RETRIES, base_delay=0.01)
    async def flaky_async() -> str:
        calls["count"] += 1
        if calls["count"] < EXPECTED_CALLS:
            raise ValueError("fail")
        return "ok"

    result = await flaky_async()
    assert result == "ok"
    assert calls["count"] == EXPECTED_CALLS


@pytest.mark.asyncio  # type: ignore[misc]
async def test_async_retry_with_exponential_backoff_raises() -> None:
    @async_retry_with_exponential_backoff(max_retries=MAX_RETRIES_FAIL, base_delay=0.01)
    async def always_fail_async() -> None:
        raise RuntimeError("fail always")

    with pytest.raises(RuntimeError):
        await always_fail_async()
