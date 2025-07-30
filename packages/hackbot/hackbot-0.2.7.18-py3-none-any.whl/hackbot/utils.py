import zipfile
import traceback
import subprocess
from typing import Union, Dict, List, Optional, Set
from git import Repo, InvalidGitRepositoryError
from loguru import logger as log
from pathlib import Path
import warnings

try:
    from tomllib import load as toml_load
except ImportError:
    from tomli import load as toml_load
import importlib.metadata
from termcolor import colored
from enum import Enum
import json
from pydantic import BaseModel, Field, ValidationError

GREEN = "\033[1;32m"
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
END = "\033[0m"


class Endpoint(str, Enum):
    RUN = "run"
    SCOPE = "scope"
    LEARN = "learn"
    PRICE = "price"
    REPORT = "report"


def compress_source_code(
    source_path: str,
    zip_path: str,
    size_limit: int = 256 * 1024 * 1024,
    git_info: Union[Dict[str, str], None] = None,
) -> None:
    """Compress the source code directory into a zip file.
    If git_info (from get_repo_info) is provided, we use git-commands to list all non-ignored files.
    Otherwise we use the entire directory"""
    # Filter out duplicate file warnings from zipfile
    warnings.filterwarnings("ignore", category=UserWarning, module="zipfile")

    # Either files to include, or whole directories to include
    path_list: List[Path] = []

    if git_info is not None:
        # Use git ls-files --directory --exclude-standard to get included/tracked files
        # Use git ls-files --directory --others --exclude-standard to get untracked files that are not ignored
        file_list: str = ""
        file_list += (
            subprocess.run(
                ["git", "ls-files", "--directory", "--exclude-standard", "--recurse-submodules"],
                cwd=source_path,
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            + "\n"
        )
        file_list += subprocess.run(
            [
                "git",
                "ls-files",
                "--directory",
                "--others",
                "--exclude-standard",
            ],
            cwd=source_path,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

        path_list = [
            Path(source_path) / Path(file) for file in file_list.splitlines() if file.strip()
        ]

        # And also add the, otherwise untracked, .git folder
        path_list.append(Path(source_path) / ".git")
    else:
        # Take directory
        path_list = [Path(source_path)]

    file_path_set: Set[Path] = set()
    for path in path_list:
        if path.is_file():
            file_path_set.add(path)
        elif path.is_dir():
            for subpath in path.rglob("**/*"):
                if subpath.is_file():
                    file_path_set.add(subpath)
        else:
            warnings.warn(f"Invalid path: '{path}'")
            continue

    file_path_list = [x.resolve() for x in file_path_set]

    try:
        zip_size = 0
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_path_list:
                arcname = file_path.relative_to(source_path)
                if not file_path.exists():
                    log.debug(
                        f"File not found (probably a broken symlink?), skipping sending to server: {file_path}"
                    )
                    continue
                zip_size += file_path.stat().st_size
                if zip_size > size_limit:
                    raise RuntimeError(
                        f"Source code archive is too large to be scanned. Must be less than 256MB, but after adding {file_path} it is {zip_size // 1024 // 1024}MB."
                    )
                zipf.write(str(file_path), str(arcname))
    except Exception:
        log.error(f"Failed to compress source code: {traceback.format_exc()}")
        raise


def get_repo_info(repo_path: Union[Path, str]) -> Union[Dict[str, str], None]:
    """Returns the repo info of a github (specifically) repo at repo_path, or None if the repo is not a github repo
    The info includes repo name, commit, repo owner, and branch name.
    Info also includes relative path from the real repo root (since we search parent directories for the repo) to the repo_path
    """
    if isinstance(repo_path, str):
        repo_path = Path(repo_path)
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        return None
    repo_info: Dict[str, str] = {}
    repo_info["source_root"] = str(repo_path.relative_to(repo.working_dir))
    for remote in repo.remotes:
        if "github.com" in remote.url:
            if "git@" in remote.url:
                mode = "ssh"
            else:
                mode = "http"

            # Example repo url: git@github.com:GatlingX/some_repo.git
            repo_info["repo_name"] = remote.url.split("/")[-1]
            repo_info["commit_hash"] = repo.head.commit.hexsha

            if mode == "http":
                # Example repo url: https://github.com/GatlingX/some_repo
                repo_info["repo_owner"] = remote.url.split("/")[-2]
            else:
                # Example repo url: git@github.com:GatlingX/some_repo.git
                repo_info["repo_owner"] = remote.url.split(":")[-1].split("/")[0]
                # Remove the .git from the end of the repo name
                repo_info["repo_name"] = repo_info["repo_name"][:-4]
            for branch in repo.branches:
                if branch.commit == repo.head.commit:
                    repo_info["branch_name"] = branch.name
                    break
                else:
                    repo_info["branch_name"] = "HEAD"
            break
    else:
        return None
    return repo_info


def get_version() -> str:
    """Get the version of the hackbot package."""
    # In development mode, we use the version from the pyproject.toml file
    try:
        with open(str(Path(__file__).parent.parent.parent / "pyproject.toml"), "rb") as f:
            return toml_load(f)["project"]["version"]
    except FileNotFoundError:
        # In production mode, we use the version from the package metadata
        return importlib.metadata.version("hackbot")


def postprocess_scope_results(
    source_path: Union[Path, str],
    scope_files: Union[List[str], None],
    ambiguous_files: Union[List[str], None],
    only_dir: Optional[str] = None,
) -> bool:
    """Postprocess the scope analysis results.

    Takes the scope and ambiguous files from the analysis and writes them to disk.
    If scope files exist, writes them to scope.txt and adds to git if in a repo.
    If ambiguous files exist, writes them to ambiguous.txt for manual review.

    Args:
        source_path: Path to the source code directory
        scope_files: List of files determined to be in scope
        ambiguous_files: List of files that need manual review
        only_dir: Optional directory to filter scope files to (relative to source_path)

    Returns:
        bool: True if processing was successful, False otherwise
    """
    if scope_files is None or len(scope_files) == 0 or scope_files[0] is None:  # type: ignore
        if ambiguous_files is None or len(ambiguous_files) == 0 or ambiguous_files[0] is None:  # type: ignore
            log.error(colored("❌ No files in scope", "red"))
        else:
            scope_files = ambiguous_files
            log.error(
                colored(
                    "⚠️ No files in scope, but ambiguous files found requiring manual review", "red"
                )
            )
        return False

    # Filter scope files if only_dir is specified
    filtered_scope_files: List[str] = scope_files
    if only_dir:
        source_path_obj = Path(source_path)
        only_dir_path = source_path_obj / only_dir
        filtered_scope_files = []
        for file in scope_files:
            file_path = source_path_obj / file
            try:
                if file_path.resolve().is_relative_to(only_dir_path):
                    filtered_scope_files.append(file)
            except ValueError:
                # File is not in the specified directory
                continue
        scope_files = filtered_scope_files
        if len(scope_files) == 0:
            log.error(f"❌ No files in scope in {only_dir}")
            return False
        log.info(f"Filtered scope to {len(scope_files)} files in {only_dir}")

    if (Path(source_path) / "scope.txt").exists():
        log.warning(f"❌ {Path(source_path) / 'scope.txt'} already exists, not overwriting")
        log.info(
            f"Keeping old scope.txt, but this scope run produced scope files: \n{chr(10).join(scope_files)}"
        )
        return True

    # Write the scope files to the scope.txt file
    with open(Path(source_path) / "scope.txt", "w") as f:
        for file in scope_files:
            f.write(file + "\n")

    repo_info = get_repo_info(source_path)
    if repo_info is not None:
        repo = Repo(source_path, search_parent_directories=True)
        repo.index.add([Path(source_path) / "scope.txt"])  # type: ignore

    return True


def postprocess_learn_results(checklist: Union[Dict[str, str], None]) -> None:
    if checklist is None or len(checklist) == 0:
        log.error(colored("❌ No checklist found", "red"))
    else:
        log.info(
            colored(
                "✅ Checklist analysis completed successfully, writing to checklist.json", "green"
            )
        )

    with open(Path.cwd() / "checklist.json", "w") as f:
        json.dump(checklist, f)


class UserChecklistItem(BaseModel):
    issue: str = Field(..., description="Issue related to solidity code vurnerabilitie.")
    description: str = Field(..., description="Description of the issue.")
    severity: str = Field(..., description="Severity of the issue.")
    reference: str = Field(..., description="Reference to the issue.")


class UserChecklist(BaseModel):
    items: List[UserChecklistItem] = Field(..., description="List of checklist items.")


def validate_checklist_file(checklist_path: Path) -> List[Dict[str, str]]:
    """Validate the checklist file."""
    try:
        with open(checklist_path, "r") as f:
            json_data = json.load(f)
            UserChecklist.model_validate(json_data)
            return json_data
    except FileNotFoundError:
        log.error(colored("❌ Error: checklist.json not found", "red"))
        raise
    except (json.JSONDecodeError, FileNotFoundError):
        log.error(colored("❌ Error: Could not parse existing checklist.json", "red"))
        raise
    except ValidationError as e:
        log.error(colored(f"❌ Error: Invalid checklist.json structure: {e}", "red"))
        raise
    except Exception as e:
        log.error(colored(f"❌ Error: Failed to send existing checklist.json: {e}", "red"))
        raise
