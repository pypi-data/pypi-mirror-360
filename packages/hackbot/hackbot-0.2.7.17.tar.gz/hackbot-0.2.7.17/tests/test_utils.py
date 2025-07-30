import pytest
import zipfile
from git import Repo, NoSuchPathError
from hackbot.config import url_format
from hackbot.utils import (
    compress_source_code,
    get_repo_info,
)
from pytest_mock import MockerFixture
from typing import Optional


@pytest.mark.parametrize(
    "address,port,expected",
    [
        ("localhost", None, "http://localhost"),
        ("localhost", 80, "http://localhost"),
        ("localhost", 443, "https://localhost:443"),
        ("localhost", 8080, "https://localhost:8080"),
        ("http://localhost", None, "http://localhost"),
        ("https://localhost", None, "https://localhost"),
        ("http://localhost", 8080, "http://localhost:8080"),
        ("https://localhost", 8080, "https://localhost:8080"),
        ("http://example.com:8080", None, "http://example.com:8080"),
        ("https://example.com:8080", None, "https://example.com:8080"),
    ],
)
def test_url_format(address: str, port: Optional[int], expected: str):
    assert url_format(address, port) == expected


def test_url_format_invalid_scheme():
    with pytest.raises(AssertionError, match="Invalid URI scheme"):
        url_format("ftp://localhost", None)


@pytest.fixture
def mock_git_repo_multiple_remotes(tmp_path, mocker: MockerFixture):
    # Create a temporary directory structure
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Mock Repo class
    mock_repo = mocker.MagicMock()

    # Add working_dir property to mock
    mock_repo.working_dir = str(source_dir)

    # Mock branches
    mock_main = mocker.MagicMock()
    mock_main.name = "main"
    mock_dev = mocker.MagicMock()
    mock_dev.name = "dev"
    mock_repo.branches = [mock_main, mock_dev]
    mock_repo.active_branch = mock_main

    # Define URLs directly in the fixture
    git_urls = ["git@github.com:GatlingX/some_repo.git", "https://github.com/GatlingX/some_repo"]

    # Mock remote URLs
    mock_repo.remotes = []
    for git_url in git_urls:
        mock_github_remote = mocker.MagicMock()
        mock_github_remote.url = git_url
        mock_repo.remotes.append(mock_github_remote)

    # Patch the Repo constructor
    mocker.patch("hackbot.utils.Repo", return_value=mock_repo)

    return source_dir


@pytest.fixture
def create_test_repo(tmp_path):
    # Create a temporary directory structure
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Initialize real git repo
    repo = Repo.init(source_dir)

    # Create and commit first two files
    (source_dir / "committed.py").write_text("committed file")
    (source_dir / "committed2.py").write_text("another committed file")
    repo.index.add(["committed.py", "committed2.py"])
    repo.index.commit("Initial commit with two files")

    # Create and stage two more files (but don't commit)
    (source_dir / "staged.py").write_text("staged but not committed")
    (source_dir / "staged2.py").write_text("also staged not committed")
    repo.index.add(["staged.py", "staged2.py"])

    # Create two untracked files
    (source_dir / "untracked1.py").write_text("untracked file 1")
    (source_dir / "untracked2.py").write_text("untracked file 2")

    return source_dir


def test_compress_source_code_with_git(tmp_path, create_test_repo):
    zip_path = tmp_path / "output.zip"

    # Call function with git info
    compress_source_code(
        str(create_test_repo), str(zip_path), git_info={"repo_root": str(create_test_repo)}
    )

    # Verify zip contents
    with zipfile.ZipFile(zip_path) as zf:
        files = zf.namelist()
        assert "committed.py" in files
        assert "committed2.py" in files
        assert "staged.py" in files
        assert "staged2.py" in files
        assert "untracked1.py" in files
        assert "untracked2.py" in files


def test_compress_source_code_without_git(tmp_path):
    # Create source directory with files
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "file1.py").write_text("test file 1")
    (source_dir / "file2.py").write_text("test file 2")

    zip_path = tmp_path / "output.zip"

    # Call function without git info
    compress_source_code(str(source_dir), str(zip_path))

    # Verify zip contains all files
    with zipfile.ZipFile(zip_path) as zf:
        files = zf.namelist()
        assert "file1.py" in files
        assert "file2.py" in files


def test_get_repo_info_valid_repo(mocker: MockerFixture):
    mock_repo = mocker.MagicMock()

    # Mock branches
    mock_main = mocker.MagicMock()
    mock_main.name = "main"
    mock_main.commit.hexsha = "1234567890"
    mock_dev = mocker.MagicMock()
    mock_dev.name = "dev"
    mock_dev.commit.hexsha = "1234567891"
    mock_repo.head.commit = mock_main.commit
    mock_repo.branches = [mock_main, mock_dev]
    mock_repo.active_branch = mock_main

    # Define URLs directly in the fixture
    git_urls = ["git@github.com:GatlingX/some_repo.git", "https://github.com/GatlingX/some_repo"]

    # Mock remote URLs
    mock_repo.remotes = []
    for git_url in git_urls:
        mock_github_remote = mocker.MagicMock()
        mock_github_remote.url = git_url
        mock_repo.remotes.append(mock_github_remote)

    # Patch the Repo constructor
    mocker.patch("hackbot.utils.Repo", return_value=mock_repo)

    repo_info = get_repo_info(mock_repo)

    assert repo_info is not None
    assert "source_root" in repo_info
    assert "repo_name" in repo_info
    assert repo_info["repo_name"] == "some_repo"
    assert "repo_owner" in repo_info
    assert repo_info["repo_owner"] == "GatlingX"
    assert "branch_name" in repo_info
    assert repo_info["branch_name"] == "main"
    assert "commit_hash" in repo_info
    assert repo_info["commit_hash"] == "1234567890"

    mock_repo.head.commit = mock_dev.commit
    repo_info = get_repo_info(mock_repo)

    assert repo_info is not None
    assert "source_root" in repo_info
    assert "repo_name" in repo_info
    assert repo_info["repo_name"] == "some_repo"
    assert "repo_owner" in repo_info
    assert repo_info["repo_owner"] == "GatlingX"
    assert "branch_name" in repo_info
    assert repo_info["branch_name"] == "dev"
    assert "commit_hash" in repo_info
    assert repo_info["commit_hash"] == "1234567891"

    mock_repo.remotes = []
    mock_repo.remotes.append(mocker.MagicMock())
    mock_repo.remotes[0].url = "https://github.com/GatlingX/some_repo"
    repo_info = get_repo_info(mock_repo)

    assert repo_info is not None
    assert "source_root" in repo_info
    assert "repo_name" in repo_info
    assert repo_info["repo_name"] == "some_repo"
    assert "repo_owner" in repo_info
    assert repo_info["repo_owner"] == "GatlingX"
    assert "branch_name" in repo_info
    assert repo_info["branch_name"] == "dev"
    assert "commit_hash" in repo_info
    assert repo_info["commit_hash"] == "1234567891"

    mock_repo.remotes = []
    mock_repo.remotes.append(mocker.MagicMock())
    mock_repo.remotes[0].url = "https://github.com/GatlingX/someRepo"
    repo_info = get_repo_info(mock_repo)

    assert repo_info is not None
    assert "source_root" in repo_info
    assert "repo_name" in repo_info
    assert repo_info["repo_name"] == "someRepo"
    assert "repo_owner" in repo_info
    assert repo_info["repo_owner"] == "GatlingX"
    assert "branch_name" in repo_info
    assert repo_info["branch_name"] == "dev"
    assert "commit_hash" in repo_info
    assert repo_info["commit_hash"] == "1234567891"


def test_get_repo_info_nonexistent_path():
    # Try to get repo info from nonexistent path
    with pytest.raises(NoSuchPathError):
        get_repo_info("/path/does/not/exist")
