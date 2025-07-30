import argparse
from contextlib import contextmanager
import json
import os
import tempfile
from pathlib import Path
from loguru import logger as log
from typing import Union, cast, Optional, Tuple, Generator
from urllib.parse import urlparse, ParseResult
from git import Repo

from .utils import get_version, Endpoint
from .config import set_local_mode, set_dev_mode

__version__ = get_version()

GREEN = "\033[1;32m"
RED = "\033[1;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
GREY = "\033[1;90m"
BOLD = "\033[1m"
END = "\033[0m"


def add_common_arguments(parser: argparse.ArgumentParser, hide_dev_tool_help: bool = True):
    """Add common arguments to a parser."""
    parser.add_argument(
        "--auth-only", action="store_true", help="Only verify API key authentication"
    )
    parser.add_argument(
        "-s",
        "--source",
        default=".",
        help=f"Path to folder containing {YELLOW}foundry.toml{END} (default: current directory).",
    )
    parser.add_argument("--output", help="Path to save analysis results")

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet mode, no interactive prompts",
    )

    def help_mode(description: str):
        if hide_dev_tool_help:
            return argparse.SUPPRESS
        else:
            return description

    parser.add_argument(
        "--debug",
        type=str,
        default=None,
        help=help_mode(
            'Send debug json to server. Can\'t use nested entries. Example: --debug \'{"admin": "true"}\' if you have admin privileges.'
        ),
    )

    parser.add_argument(
        "--local",
        action="store_true",
        help=help_mode("Run with local backend (http://localhost, port 5000)"),
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help=help_mode("Run with development backend (https://dev-server.hackbot.co, port 443)"),
    )

    parser.add_argument(
        "--skip-forge-build", action="store_true", help=help_mode("Skip forge build check")
    )

    parser.add_argument(
        "--skip-local-clone",
        action="store_true",
        help=help_mode("Skip local clone of github repo"),
    )


def add_learn_arguments(parser: argparse.ArgumentParser):
    """Add learn arguments to a parser."""
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help=f"The URL provided by the user, to generate a {YELLOW}checklist.json{END} file, which is used to teach the hackbot about the types of vulnerabilities to look out for.",
    )
    parser.add_argument(
        "--merge", action="store_true", help="Merge the new checklist with the existing one"
    )


def add_api_key_argument(parser: argparse.ArgumentParser):
    """Add API key argument to a parser."""
    parser.add_argument(
        "--api-key",
        default=os.getenv("HACKBOT_API_KEY"),
        help=f"API key for authentication (default: {BLUE}HACKBOT_API_KEY{END} environment variable)",
    )


def setup_parser(
    hide_dev_tool_help: bool = True, return_run_parser: bool = False
) -> Union[argparse.ArgumentParser, tuple[argparse.ArgumentParser, argparse.ArgumentParser]]:
    """Parse the command line arguments."""
    description = (
        f"{RED}Hackbot{END} - ♨️ Kiss Solidity bugs Goodbye. "
        f"Visit {GREEN}https://hackbot.co{END} to get your API key and more information."
        f" Documentation: {GREEN}https://docs.hackbot.co{END}"
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-v", "--version", action="version", version=f"GatlingX Hackbot v{__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Description", required=True)

    # Create parsers for each command
    run_parser = subparsers.add_parser(
        Endpoint.RUN.value,
        help=f"{GREEN}Run analysis on foundry repository codebase. Require a `foundry.toml` file in the root of the repository{END}",
    )

    scope_parser = subparsers.add_parser(
        Endpoint.SCOPE.value,
        help=f"{GREY}Analyze the codebase and dump `scope.txt` file with the list of files that will be scanned in `hackbot run`{END}",
    )
    learn_parser = subparsers.add_parser(
        Endpoint.LEARN.value,
        help=f"{GREY}Analyze a link and generate a checklist.json file that can be used to teach the hackbot things to watch out for during `hackbot run` to improve the accuracy of the analysis{END}",
    )
    price_parser = subparsers.add_parser(
        Endpoint.PRICE.value,
        help=f"{GREY}Get the cost for running hackbot in your repo{END}",
    )
    report_parser = subparsers.add_parser(
        Endpoint.REPORT.value,
        help=f"{GREY}Generate a PDF report of bugs/POCs from a previous session{END}",
    )

    # Add API key to all command parsers that need it
    for cmd_parser in [run_parser, scope_parser, learn_parser, price_parser, report_parser]:
        cmd_parser.add_argument("-hh", "--hidden-help", action="store_true", help=argparse.SUPPRESS)
        add_api_key_argument(cmd_parser)
        add_common_arguments(cmd_parser, hide_dev_tool_help=hide_dev_tool_help)

    # Add only-dir argument to scope parser
    scope_parser.add_argument(
        "-o",
        "--only-dir",
        type=str,
        help="Filter scope.txt to only include files in the specified directory subtree (relative to source path)",
    )

    add_learn_arguments(learn_parser)

    # Add session name argument for report command
    report_parser.add_argument(
        "session",
        type=str,
        help="Name of the session to generate report for",
    )

    run_parser.add_argument(
        "--checklist",
        type=str,
        required=False,
        help=f"A {YELLOW}checklist.json{END} file a list of issues the hackbot should pay further attention to, generated from {CYAN}hackbot learn --url <url>{END}",
    )

    if return_run_parser:
        return parser, run_parser
    return parser


def get_args() -> Union[argparse.Namespace, int]:
    """Parse the command line arguments."""
    parser = setup_parser(hide_dev_tool_help=True)
    assert isinstance(parser, argparse.ArgumentParser)
    args = parser.parse_args()

    if args.hidden_help:
        parsers = setup_parser(hide_dev_tool_help=False, return_run_parser=True)
        assert isinstance(parsers, tuple)
        parsers[1].print_help()
        return 0

    if args.command == Endpoint.RUN.value:
        ret = check_run_args(args)
    elif args.command == Endpoint.SCOPE.value:
        ret = check_scope_args(args)
    elif args.command == Endpoint.LEARN.value:
        ret = check_learn_args(args)
    elif args.command == Endpoint.PRICE.value:
        ret = check_price_args(args)
    elif args.command == Endpoint.REPORT.value:
        ret = check_report_args(args)
    else:
        raise ValueError(f"Invalid command: {args.command}")

    if isinstance(ret, int):
        return ret
    else:
        args = ret

    if args.local:
        log.info("Running in local server mode!")
        set_local_mode()
    elif args.dev:
        log.info("Running in development server mode!")
        set_dev_mode()

    if args.skip_local_clone:
        log.info(f"Skipping local clone of github repo! Will ask backend to clone {args.source} for us")

    return args


def parse_github_url(url: str) -> Optional[Tuple[str, str, str]]:
    """
    Parse a GitHub repository URL and return its components.

    Args:
        url: The GitHub repository URL to parse

    Returns:
        Tuple of (owner, repo_name, clone_url) if valid GitHub URL, None otherwise
    """
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return None

        # Handle both https://github.com/owner/repo and git@github.com:owner/repo.git formats
        if result.netloc == "github.com":
            path_parts = result.path.strip("/").split("/")
            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo_name = path_parts[1].replace(".git", "")

                clone_url = f"https://github.com/{owner}/{repo_name}.git"
                return owner, repo_name, clone_url
        elif result.netloc == "github.com:" or result.netloc == "github.com":
            # Handle SSH format: git@github.com:owner/repo.git
            path_parts = result.path.strip("/").split("/")
            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo_name = path_parts[1].replace(".git", "")
                clone_url = f"https://github.com/{owner}/{repo_name}.git"
                return owner, repo_name, clone_url
    except Exception:
        log.error(
            f"❌ Error: Invalid GitHub URL: {url}\n"
            "          - Please provide a valid GitHub URL in the format: https://github.com/owner/repo or git@github.com:owner/repo.git"
        )
    return None


def check_foundry_toml(source: Path | str) -> bool:
    """Check if foundry.toml exists in the source path.
    Treats Path as local paths, strings as links (so no checking for foundry.toml)
    """
    if isinstance(source, str):
        return True
    # Handle local paths only
    source_path = source.resolve()

    # Check if foundry.toml exists
    if source_path.exists() and (source_path / "foundry.toml").exists():
        return True
    else:
        log.error(f"❌ Error: No foundry.toml found in {source_path}!")
        return False


@contextmanager
def check_source_folder(source: str, skip_local_clone: bool = False) -> Generator[Path | str, None, None]:
    # Contextmanager that makes sure if the passed string is a github URL, it will be cloned to a temporary directory, which is what's returned
    # Check if source is a github URL
    github_info = parse_github_url(source)
    if github_info and not skip_local_clone:
        owner, repo_name, clone_url = github_info
        # If it's a GitHub URL, clone it to a temporary directory
        with tempfile.TemporaryDirectory(prefix="hb_source_") as temp_dir:
            try:
                log.info(f"Cloning repository {owner}/{repo_name} from {clone_url}")
                # Initialize/fetch submodules as well
                Repo.clone_from(clone_url, temp_dir, recursive=True)
            except Exception as e:
                log.error(f"❌ Error cloning repository: {e}")
                raise
            source_path = Path(temp_dir)
            yield source_path.resolve()
    else:
        if skip_local_clone:
            # Validate that it is a github URL
            if not parse_github_url(source):
                log.error(f"❌ Error: {source} is not a valid github URL")
                raise ValueError(f"❌ Error: {source} is not a valid github URL")
            yield str(source)
        else:
            yield Path(source).resolve()


def check_common_args(args: argparse.Namespace) -> Union[argparse.Namespace, int]:
    """Check and validate commandline arguments for the run, scope and hack commands."""

    if not args.api_key:
        log.error(
            f"❌ Error: API key is required (either via --api-key or {BLUE}HACKBOT_API_KEY{END} environment variable)"
        )
        return 1

    try:
        if args.debug is not None:
            args.debug = json.loads(args.debug)
    except Exception:
        log.error(
            f"❌ Error: Invalid debug argument / JSON parse error on debug string: {args.debug}"
        )
        return 1

    return args


def check_scope_args(args: argparse.Namespace) -> Union[argparse.Namespace, int]:
    """Check and validate commandline arguments for the scope command. API key is NOT required."""
    # Validate only-dir argument if provided
    if args.only_dir:
        only_dir_path = Path(args.source) / args.only_dir
        if not only_dir_path.exists():
            log.error(f"❌ Error: Directory {args.only_dir} does not exist in {args.source}")
            return 1
        if not only_dir_path.is_dir():
            log.error(f"❌ Error: {args.only_dir} is not a directory")
            return 1
    return args


def check_run_args(args: argparse.Namespace) -> Union[argparse.Namespace, int]:
    """Check and validate commandline arguments for the run command."""
    return check_common_args(args)


def check_learn_args(args: argparse.Namespace) -> Union[argparse.Namespace, int]:
    """Check and validate commandline arguments for the learn command."""
    if not args.url:
        log.error("❌ Error: URL is required for learn command")
        return 1

    if not args.api_key:
        log.error(
            "❌ Error: API key is required (either via --api-key or HACKBOT_API_KEY environment variable)"
        )
        return 1

    try:
        result: ParseResult = cast(ParseResult, urlparse(args.url))
        if not all([result.scheme, result.netloc]):
            log.error("❌ Error: Invalid URL format")
            return 1
    except Exception:
        log.error("❌ Error: Invalid URL")
        return 1

    if (Path.cwd() / "checklist.json").exists():
        if not args.merge:
            log.error("❌ Error: checklist.json already exists.")
            log.error("          - Either remove checklist.json and run hackbot learn again.")
            log.error(
                "          - Or run hackbot learn --merge to merge the new checklist with the existing one."
            )
            return 1
    else:
        if args.merge:
            log.error("❌ Error: No existing checklist.json found, cannot merge.")
            return 1

    return args


def check_price_args(_args: argparse.Namespace) -> Union[argparse.Namespace, int]:
    """Check and validate commandline arguments for the price command."""
    return _args


def check_report_args(args: argparse.Namespace) -> Union[argparse.Namespace, int]:
    """Check and validate commandline arguments for the report command."""
    if not args.api_key:
        log.error(
            f"❌ Error: API key is required (either via --api-key or {BLUE}HACKBOT_API_KEY{END} environment variable)"
        )
        return 1

    if not args.session:
        log.error("❌ Error: Session name is required")
        return 1

    return args
