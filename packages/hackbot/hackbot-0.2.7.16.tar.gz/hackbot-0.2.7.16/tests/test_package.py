import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.hackbot.commands import hackbot_run
from src.hackbot.hack import (
    authenticate,
    do_post,
    HackbotAuthError,
)
from src.hackbot.utils import compress_source_code, Endpoint
import os
from typing import Dict, Any, List, Tuple


@pytest.fixture
def mock_invocation_args() -> Dict[str, Any]:
    return {
        "command": "run",
        "model": "gpt-4o-mini",
        "profile": "plus",
        "debug": None,
    }


@pytest.fixture
def test_params(mock_invocation_args: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "address": "https://app.hackbot.co",
        "port": None,
        "api_key": "test_api_key",
        "source": "test_source",
        "endpoint": Endpoint.RUN,
        "invocation_args": mock_invocation_args,
    }


@pytest.fixture
def mock_repo_info() -> Dict[str, str]:
    return {
        "source_root": "test_source_root",
        "repo_name": "test_repo_name",
        "commit_hash": "test_commit_hash",
        "repo_owner": "test_repo_owner",
        "branch_name": "test_branch_name",
    }


@pytest.fixture
def mock_args(test_params: Dict[str, Any]) -> MagicMock:
    args = MagicMock()
    args.api_key = test_params["api_key"]
    args.source = test_params["source"]
    args.output = None
    args.auth_only = False
    args.issues_repo = None
    args.github_api_key = None
    args.command = "run"
    return args


@pytest.mark.asyncio
@patch("src.hackbot.hack.aiohttp.ClientSession")
async def test_authenticate_success(mock_session: MagicMock, test_params: Dict[str, Any]) -> None:
    # Create mock response
    mock_response = MagicMock()
    mock_response.status = 200

    # Setup session context manager
    mock_session_context = MagicMock()
    mock_session_context.__aenter__.return_value = mock_session_context
    mock_session_context.get.return_value.__aenter__.return_value = mock_response
    mock_session.return_value = mock_session_context

    result = await authenticate(test_params["api_key"])
    assert result is None

    # Verify correct URL and headers
    expected_url = f"{test_params['address']}:443/api/authenticate"
    expected_headers = {"X-API-KEY": test_params["api_key"]}
    mock_session_context.get.assert_called_with(
        expected_url,
        headers=expected_headers,
    )


@pytest.mark.asyncio
@patch("hackbot.hack.aiohttp.ClientSession")
async def test_authenticate_failure(mock_session: MagicMock, test_params: Dict[str, Any]) -> None:
    mock_response = MagicMock()
    mock_response.status = 401
    mock_response.text = AsyncMock(return_value="Authentication failed")

    mock_session_context = MagicMock()
    mock_session_context.__aenter__.return_value = mock_session_context
    mock_session_context.get.return_value.__aenter__.return_value = mock_response
    mock_session.return_value = mock_session_context

    result = await authenticate(test_params["api_key"])
    assert isinstance(result, HackbotAuthError)


def test_compress_source_code(tmp_path: Any) -> None:
    """Test source code compression with temp directory"""
    # Create test files
    source_dir = tmp_path / "test_src"
    source_dir.mkdir()
    test_file = source_dir / "test_file.txt"
    test_file.write_text("Test content")

    zip_path = tmp_path / "src.zip"
    compress_source_code(str(source_dir), str(zip_path))

    assert zip_path.exists()
    assert zip_path.stat().st_size > 0

    # Test size limit
    big_file = source_dir / "big.txt"
    big_file.write_bytes(b"0" * (300 * 1024 * 1024))  # 300MB file

    with pytest.raises(RuntimeError, match="too large"):
        compress_source_code(str(source_dir), str(zip_path))


@pytest.mark.asyncio
@patch("src.hackbot.hack.aiohttp.ClientSession")
@patch("src.hackbot.hack.get_repo_info")
@patch("src.hackbot.hack.compress_source_code")
@patch("git.Repo")
async def test_cli_run(
    mock_repo_class: MagicMock,
    mock_compress_source_code: MagicMock,
    mock_get_repo_info: MagicMock,
    mock_session: MagicMock,
    test_params: Dict[str, Any],
    mock_repo_info: Dict[str, str],
) -> None:
    """Test the cli_run function with mocked responses"""
    # Setup mock response for HTTP
    mock_response = MagicMock()
    mock_response.status = 200

    # Mock the iter_chunks method to return the expected data format
    # Each chunk is a tuple of (data, end_of_http_chunk)
    mock_chunks: List[Tuple[bytes, bool]] = [
        (b'data: {"message": "Starting analysis"}\n\n', True),
        (b'data: {"title": "Test Bug Found"}\n\n', True),
    ]

    async def mock_iter_chunks():
        for chunk in mock_chunks:
            yield chunk

    mock_response.content.iter_chunks = mock_iter_chunks

    # Create a proper async context manager for the session and post response
    mock_session_instance = MagicMock()
    mock_session_instance.post.return_value.__aenter__.return_value = mock_response
    mock_session.return_value.__aenter__.return_value = mock_session_instance

    # Set up mock repo
    mock_repo = MagicMock()
    mock_repo.working_dir = "/mock/repo/path"
    mock_repo_class.return_value = mock_repo

    # Set the return value for get_repo_info
    mock_get_repo_info.return_value = mock_repo_info
    mock_compress_source_code.return_value = b"compressed_code"

    results: List[str] = []
    async for result in do_post(
        api_key=test_params["api_key"],
        endpoint=test_params["endpoint"],
        invocation_args=test_params["invocation_args"],
        source_path=os.path.abspath(test_params["source"]),
    ):
        results.append(result)

    assert len(results) == 2
    assert '{"message": "Starting analysis"}' in results
    assert '{"title": "Test Bug Found"}' in results


@patch("src.hackbot.commands.os.path.exists")
@patch("src.hackbot.commands.authenticate")
@patch("src.hackbot.commands.cli_run")
@patch("src.hackbot.commands.cli_price")
@patch("src.hackbot.commands.Path")
def test_hackbot_run(
    mock_path_class: MagicMock,
    mock_cli_price: MagicMock,
    mock_cli_run: MagicMock,
    mock_auth: MagicMock,
    mock_exists: MagicMock,
    mock_args: MagicMock,
) -> None:
    """Test the main hackbot run command"""
    # Set up Path mock
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.absolute.return_value = mock_path
    mock_path_class.return_value = mock_path
    mock_path_class.resolve.return_value = mock_path

    # Mock scope.txt existence and content
    def mock_exists_side_effect(path: Any) -> bool:
        if str(path).endswith("scope.txt"):
            return True
        if str(path).endswith("test.sol"):
            return True
        return True

    mock_exists.side_effect = mock_exists_side_effect

    # Mock file reading
    def mock_read_text() -> str:
        if str(mock_path).endswith("scope.txt"):
            return "test.sol"
        if str(mock_path).endswith("test.sol"):
            return "contract Test {}"
        return ""

    mock_path.read_text.side_effect = mock_read_text

    # Mock the coroutines with AsyncMock
    mock_auth.return_value = None  # Success case returns None
    mock_cli_run.return_value = [{"bug_id": "TEST-1"}]
    mock_cli_price.return_value = 100  # Return a valid price

    result = hackbot_run(mock_args)
    assert result == 0

    mock_auth.assert_called_once()
    mock_cli_run.assert_called_once()

    # Test authentication failure
    mock_auth.return_value = HackbotAuthError("Authentication failed")
    result = hackbot_run(mock_args)
    assert result == 1

    # Test with auth_only flag
    mock_args.auth_only = True
    mock_auth.return_value = None  # Success case returns None
    result = hackbot_run(mock_args)
    assert result == 0
    assert mock_cli_run.call_count == 2
