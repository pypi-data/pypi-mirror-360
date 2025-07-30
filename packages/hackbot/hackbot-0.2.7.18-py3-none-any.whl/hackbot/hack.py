from typing import Optional, List, Dict, Any, Literal, AsyncGenerator, Tuple, Union
import base64
from dataclasses import dataclass
import aiohttp
import json
import tempfile
from pathlib import Path
from loguru import logger as log
from termcolor import colored
from hackbot.config import format_hackbot_url
from .utils import (
    compress_source_code,
    get_repo_info,
    postprocess_scope_results,
    postprocess_learn_results,
    Endpoint,
    validate_checklist_file,
    get_version,
)
from hackbot.spinner import Spinner
from hackbot.cli_args import (
    GREEN,
    YELLOW,
    CYAN,
    GREY,
    BOLD,
    END,
)


@dataclass
class HackBotClientMessage:
    """A message sent to the hackbot client."""

    type: Literal["message", "progress", "error", "scope"]
    message: str

    def log(self) -> None:
        """Log the message to the console."""
        if self.type == "message":
            log.info(self.message)
        elif self.type == "progress":
            log.info(self.message, extra={"progress": True})
        elif self.type == "scope":
            log.info(self.message, extra={"scope": True})
        elif self.type == "error":
            log.error(self.message)

def is_valid_json(s: str) -> bool:
    """Check if a string is valid JSON."""
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False


def log_scope_files(scope_files: List[str], source_path: Union[Path, str]) -> None:
    def format_scope_file(scope_file: str) -> str:
        # Takes one line from scopefile, produces nice info entry about file
        if isinstance(source_path, str):
            # Github url
            return f"{GREY}{scope_file}{END}"
        else:
            scopefile_realpath = source_path / scope_file
            with open(scopefile_realpath, "r") as f:
                n_lines = len(f.readlines())
            return f"{GREY}{scope_file}{END} ({n_lines} lines)"

    # Display contents of scope.txt in a pretty way (bolded list of each line in the scope_file, also line-count for each file)
    log.info(f"{BOLD}Scope.txt:{END}")
    for line_index, line in enumerate(scope_files):
        log.info(f"{BOLD}{line_index + 1}. {format_scope_file(line)}{END}")



async def process_stream(response: aiohttp.ClientResponse) -> AsyncGenerator[str, None]:
    """Process the streaming response from the hackbot service."""
    buffer: bytes = b""

    async for data, end_of_http_chunk in response.content.iter_chunks():
        buffer += data
        if end_of_http_chunk:
            s = buffer.decode("utf-8")
            if "\n\n" in s:
                pieces = s.split("\n\n")
                for index, piece in enumerate(pieces):
                    if piece.strip() == "":
                        continue
                    if piece.startswith("data: "):
                        piece = piece[5:].strip()
                        if is_valid_json(piece):
                            yield piece
                        else:
                            buffer = ("data: " + piece).encode("utf-8")
                            assert index == len(pieces) - 1, "Invalid ending before last piece"
                            break
                    else:
                        log.error("Invalid piece, debugging info below:")
                        log.info(f"Invalid piece: {piece}")
                        log.info(f"Buffer: {buffer}")
                        log.info(f"Pieces: {pieces}")
                        raise ValueError(f"Invalid piece: {piece}. Doesn't start with 'data: '")
                else:
                    buffer = b""
    if buffer != b"":
        log.warning("Buffer not empty, debugging info below:")
        log.warning(f"Buffer: {buffer}")


class CLIVersionMismatchError(Exception):
    def __init__(self, message: str, your_version: str, server_version: str):
        super().__init__(message)
        self.your_version = your_version
        self.server_version = server_version
        self.message = message

async def handle_version_mismatch(resp: aiohttp.ClientResponse) -> None:
    if resp.status == 426:
        try:
            data = await resp.json()
        except Exception:
            log.error("Version mismatch error, but no JSON data received")
            raise CLIVersionMismatchError("Version mismatch error, but no JSON data received", "unknown", "unknown")

        yours = data.get("your_version", "unknown")
        server = data.get("server_version", "unknown")
        msg = data.get("error", "CLI version mismatch.")
        log.error(f"\n[ERROR] {msg}\nYour CLI version: {yours}\nServer version: {server}\nPlease upgrade your CLI to match the server version.\n")
        raise CLIVersionMismatchError(msg, yours, server)


async def do_post(
    invocation_args: Dict[str, Any],
    api_key: Optional[str],
    endpoint: Endpoint,
    source_path: str = ".",
    output: Optional[str] = None,
    checklist: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Analyze the target source code using the hackbot service.
    Available endpoints:
    - Endpoint.RUN: Run all checks (scope + hack)
    - Endpoint.SCOPE: Analyze the scope of the code
    - Endpoint.LEARN: Invalid in do_post as it uses a different POST request
    Args:
        address: The hackbot service address
        port: The service port number
        api_key: Authentication API key
        endpoint: The endpoint to use
        source_path: Path to the source code to analyze
        output: Optional path to save results
        checklist: Optional checklist file generated by hackbot learn

    Returns:
        List of analysis results
    """

    assert endpoint != Endpoint.LEARN, "Invalid endpoint for do_post"

    # Search for closest enclosing git repo and info from there, can be None
    if isinstance(source_path, Path):
        repo_info = get_repo_info(source_path)
    else:
        repo_info = None
    # Compress the source code into a tempfile
    with tempfile.NamedTemporaryFile(delete=True, suffix=".zip") as temp_zip:
        # Prepare the form data
        data = aiohttp.FormData()
        if isinstance(source_path, Path):
            compress_source_code(source_path, temp_zip.name, git_info=repo_info)

            data.add_field(
                "file",
                open(temp_zip.name, "rb"),
                filename="compressed_source_code.zip",
                content_type="application/zip",
            )
        else:
            data.add_field("repo_uri", source_path)

        url = format_hackbot_url(f"api/{endpoint.value}")
        headers = {"Connection": "keep-alive", "X-CLI-VERSION": get_version()}
        if api_key:
            headers["X-API-KEY"] = api_key

        if repo_info:
            for key, value in repo_info.items():
                if key and value:
                    data.add_field(f"repo_info_{key}", value)

        # Invocation args into invocation_arg_* keys
        for key, value in invocation_args.items():
            data.add_field(f"invocation_arg_{key}", value)

        if checklist:
            checklist_data = validate_checklist_file(Path(checklist))
            data.add_field("checklist", json.dumps(checklist_data), content_type="application/json")

        results: List[Dict[str, Any]] = []
        timeout = aiohttp.ClientTimeout(total=None)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, data=data, headers=headers) as response:
                await handle_version_mismatch(response)
                if response.status != 200:
                    raise RuntimeError(
                        f"Hack request failed with status {response.status}, and error: {await response.text()}"
                    )

                async for result in process_stream(response):
                    try:
                        res_json = json.loads(result)
                    except json.JSONDecodeError:
                        log.debug(f"Invalid received JSON: {result}")
                        continue
                    results.append(res_json)
                    # The type of result is indeed str, and json can only have string keys
                    assert isinstance(result, str)
                    yield result

                # Save results if output path specified
                if output:
                    output_path = Path(output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, "w") as f:
                        json.dump(results, f, indent=2)


async def cli_scope(
    invocation_args: Dict[str, Any],
    source_path: str = ".",
    output: Optional[str] = None,
    show_success_message: bool = True,
    only_dir: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Tuple[List[str], List[str]]:

    scope_files: List[str] = []
    ambiguous_files: List[str] = []
    with Spinner("Analyzing scope...", "Scope analysis done in {taken_time:.2f}s"):
        async for report in do_post(invocation_args=invocation_args, api_key=api_key, endpoint=Endpoint.SCOPE, source_path=source_path, output=output):
            result_json = json.loads(report)
            if result_json.get("message") is not None:
                log.info(result_json.get("message"))
            elif result_json.get("scope") is not None:
                scope_files.extend(result_json.get("scope"))
                ambiguous_files.extend(result_json.get("ambiguity"))
            elif result_json.get("error") is not None:
                log.error(result_json.get("error"))
                return scope_files, ambiguous_files

    if isinstance(source_path, Path):
        all_good = postprocess_scope_results(
            source_path, scope_files, ambiguous_files, only_dir=only_dir
        )
    else:
        all_good = True
    if show_success_message and all_good:
        log.info(
            f"{GREEN}✅ Scope analysis completed successfully. Now try running {CYAN}hackbot run{GREEN} to run the hackbot campaign."
        )
        log_scope_files(scope_files, source_path)
        
    return scope_files, ambiguous_files


def handle_pdf(pdf_content: str) -> None:
    """Handle the PDF content."""
    # Take base64-encoded pdf and save to disk at (first free index) of report.pdf
    pdf_path = Path("report.pdf")
    if pdf_path.exists():
        for file_index in range(2, 1000):
            pdf_path = Path(f"report_{file_index}.pdf")
            if not pdf_path.exists():
                break
        else:
            log.error("Failed to find a free PDF filename")
            return
    else:
        pass

    log.info(
        f"Created vulnerability report PDF at {pdf_path}, (absolute path {pdf_path.absolute()})"
    )

    with open(pdf_path, "wb") as f:
        f.write(base64.b64decode(pdf_content))


async def cli_run(
    api_key: str,
    source_path: str,
    output: Optional[str] = None,
    invocation_args: Optional[Dict[str, Any]] = None,
    checklist: Optional[str] = None,
    actual_price: int = 0,
) -> List[Dict[str, Any]]:

    results: List[Dict[str, Any]] = []
    invocation_args = invocation_args or {}
    with Spinner("Analyzing code...", "Code analysis done in {taken_time:.2f}s"):
        async for report in do_post(
            invocation_args, api_key, Endpoint.RUN, source_path, output, checklist
        ):
            result_json = json.loads(report)
            results.append(result_json)
            if result_json.get("message") is not None:
                log.info(result_json.get("message"))
            elif result_json.get("progress") is not None:
                log.info(result_json.get("progress").get("message"))
            elif result_json.get("title") is not None:
                log.info("\U0001f41b Finding: " + result_json.get("title"))
            elif result_json.get("price") is not None:
                # Not logged bc is same as they've already seen
                pass
            elif result_json.get("error") is not None:
                log.error(result_json.get("error"))
                return results
            elif result_json.get("pdf") is not None:
                assert (
                    "pdf" in result_json
                    and isinstance(result_json["pdf"], bool)
                    and "content" in result_json
                    and isinstance(result_json["content"], str)
                ), "Invalid PDF response"
                log.info("Received vulnerability report PDF.")
                # Take base64-encoded pdf and save to disk at (first free index) of report.pdf
                handle_pdf(result_json.get("content"))

    log.info("✅ Code analysis done!")
    log.info(
        f"{GREEN}💰 Total cost{END}: {YELLOW}${actual_price}{END}. This will be billed automatically to your account."
    )

    if len(results) == 0:
        log.info(
            colored(
                "✅ No issues found",
                "green",
            )
        )

    return results


async def do_learn_post(
    api_key: str,
    user_url: str,
    merge: bool = False,
) -> AsyncGenerator[str, None]:
    url = format_hackbot_url(f"api/{Endpoint.LEARN.value}")
    headers = {"Content-Type": "application/json", "X-API-KEY": api_key, "Connection": "keep-alive", "X-CLI-VERSION": get_version()}

    existing_checklist = ""
    json_args: Dict[str, Any] = {
        "url": user_url,
    }
    if merge is True:
        existing_checklist = validate_checklist_file(Path.cwd() / "checklist.json")
        json_args["existing_checklist"] = existing_checklist
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers=headers, json=json_args) as response:
            try:
                await handle_version_mismatch(response)
            except CLIVersionMismatchError:
                # Info already logged
                raise
            assert response.status == 200, f"Failed to run learn : HTTP code {response.status} "

            async for result in process_stream(response):
                yield result


async def cli_learn(
    api_key: str,
    user_url: str,
    merge: bool = False,
) -> None:
    checklist: Union[Any, None] = None
    with Spinner("🧠 Learning from url...", "Learning from url done in {taken_time:.2f}s"):
        async for report in do_learn_post(api_key, user_url, merge):
            result_json = json.loads(report)
            if result_json.get("message") is not None:
                log.info(result_json.get("message"))
            elif result_json.get("checklist") is not None:
                # Because it comes from a json encoded string already
                checklist = json.loads(result_json.get("checklist", "{}"))
                log.info("Received checklist data")
            elif result_json.get("error") is not None:
                log.error(result_json.get("error"))
                return

    log.info(
        f"{GREEN}✅ Learning from url done! Go check {CYAN}checklist.json{END} for the digested knowledge as a checklist, and then run {CYAN}hackbot run --checklist checklist.json{END} to run the hackbot campaign."
    )

    if checklist:
        postprocess_learn_results(checklist)
    return


async def cli_price(
    api_key: str,
    scope_file: List[str],
    source_path: Union[Path, str] = Path("."),
) -> Optional[int]:
    """Get pricing information for analyzing the files listed in scope.txt."""

    # We have it on local disk
    # If it's a github url, we don't have it on local disk so we just give list of files to check once backend has cloned repo
    files: Union[Dict[str, str], List[str]] = {}
    if isinstance(source_path, Path):
        # Check and go through scope.txt
        scope_file_path = source_path / "scope.txt"
        if not scope_file_path.exists():
            log.error(f"Scope file {scope_file_path} does not exist, cannot get pricing information")
            return

        # Read the scope file, one file per line, ignoring empty lines and comments
        with open(scope_file_path, "r") as f:
            files_list = [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.strip().startswith("#")
            ]

        invalid_files = [file for file in files_list if not (Path(source_path) / file).exists()]
        if invalid_files:
            log.error(f"Files {invalid_files} do not exist, cannot get pricing information")
            return

        files = {file: (Path(source_path) / file).read_text() for file in files_list}
    else:
        files = scope_file

    with Spinner(
        "Getting pricing information...", "Pricing information retrieved in {taken_time:.2f}s"
    ):
        url = format_hackbot_url(f"api/{Endpoint.PRICE.value}")
        headers = {"Connection": "keep-alive", "X-CLI-VERSION": get_version()}
        if api_key:
            headers["X-API-KEY"] = api_key

        # Files is filename -> file contents or list of files. We send as json
        json_args: Dict[str, Any] = {
            "files": files,
        }

        if isinstance(source_path, str):
            json_args["is_github_url"] = True
            json_args["repo_uri"] = source_path

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=json_args) as response:
                try:
                    await handle_version_mismatch(response)
                except CLIVersionMismatchError:
                    # Info already logged
                    raise
                assert (
                    response.status == 200
                ), f"Failed to run price : HTTP code {response.status}, and error: {await response.text()}"

                results: Dict[str, Any] = await response.json()
                assert isinstance(results, dict)
                assert "price" in results, f"Price not found in response {results}."
                log.info(
                    f"{GREEN}💰 Estimated cost{END}: {YELLOW}${results.get('price')}{END} based on total token/LOC number for {len(files)} files in scope. You will not be billed unless the run finishes successfully.{END}"
                )

                return results.get("price")


class HackbotAuthError(Exception):
    """Exception raised for authentication errors with the hackbot service."""

    def __init__(self, message: str):
        self.message = message


async def authenticate(api_key: str) -> Union[HackbotAuthError, None]:
    """Verify API key authentication with the hackbot service.
    Responds either with None (auth success) or a HackbotAuthError (auth failure)"""
    url = format_hackbot_url("api/authenticate")
    headers = {"X-API-KEY": api_key, "X-CLI-VERSION": get_version()}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                await handle_version_mismatch(response)
            except CLIVersionMismatchError:
                # Info already logged
                raise
            if response.status == 200:
                return None
            else:
                return HackbotAuthError(
                    f"Authentication failed: HTTP code {response.status}, and error: {await response.text()}"
                )


async def cli_report(
    api_key: str,
    invocation_args: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Generate a PDF report of bugs/POCs from a previous session.

    Args:
        api_key: Authentication API key
        invocation_args: Additional arguments to pass to the server

    Returns:
        List of report results
    """
    results: List[Dict[str, Any]] = []
    with Spinner("Generating report...", "Report generation done in {taken_time:.2f}s"):
        url = format_hackbot_url(f"api/{Endpoint.REPORT.value}")
        headers = {"X-API-KEY": api_key, "Connection": "keep-alive", "X-CLI-VERSION": get_version()}

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=invocation_args) as response:
                await handle_version_mismatch(response)
                assert (
                    response.status == 200
                ), f"Failed to generate report: HTTP code {response.status}"

                pdf_chunks: List[str] = []

                async for result in process_stream(response):
                    result_json = json.loads(result)
                    results.append(result_json)
                    if result_json.get("message") is not None:
                        log.info(result_json.get("message"))
                    elif result_json.get("error") is not None:
                        log.error(result_json.get("error"))
                        return results
                    elif result_json.get("pdf") is not None:
                        assert (
                            "pdf" in result_json
                            and isinstance(result_json["pdf"], bool)
                            and "content" in result_json
                            and isinstance(result_json["content"], str)
                        ), "Invalid PDF response"

                        pdf_chunks.append(result_json.get("content"))

                        if result_json.get("is_last", False):
                            assert len(pdf_chunks) == result_json.get(
                                "total_chunks", 1
                            ), f"Expected {result_json.get('total_chunks', 1)} chunks, got {len(pdf_chunks)}"
                            log.info("Received vulnerability report PDF.")
                            # Take base64-encoded pdf and save to disk at (first free index) of report.pdf
                            total_pdf = "".join(pdf_chunks)
                            handle_pdf(total_pdf)

    log.info("✅ Report generation done!")
    return results
