from os import getenv
from typing import Union

HACKBOT_PORT = int(getenv("HACKBOT_PORT", "443"))
HACKBOT_ADDRESS = getenv("HACKBOT_ADDRESS", "https://app.hackbot.co")


def url_format(address: str, port: Union[int, None]) -> str:
    """Format the URL for the hackbot service."""
    scheme = address.split(":")[0]
    if len(address.split(":")) > 1:
        rest = ":".join(address.split(":")[1:])
    else:
        # No protocol specified, assume by port number if exists
        rest = ""
        if port is not None:
            if port == 80:
                return f"http://{address}"
            else:
                return f"https://{address}:{port}"
        else:
            return f"http://{address}"
    assert scheme in ["http", "https"], "Invalid URI scheme"
    return f"{scheme}:{rest}:{port}" if (port is not None) else f"{scheme}:{rest}"


HACKBOT_URL_BASE = url_format(HACKBOT_ADDRESS, HACKBOT_PORT)


MODES = {
    "local": {
        "address": "http://localhost",
        "port": 5000,
    },
    "dev": {
        "address": "https://dev-app.hackbot.co",
        "port": 443,
    },
}


def set_mode(mode: str):
    """Set the mode for the hackbot service."""
    global HACKBOT_URL_BASE
    global HACKBOT_ADDRESS
    global HACKBOT_PORT
    HACKBOT_ADDRESS = MODES[mode]["address"]  # type:ignore
    HACKBOT_PORT = MODES[mode]["port"]  # type:ignore
    HACKBOT_URL_BASE = url_format(HACKBOT_ADDRESS, HACKBOT_PORT)  # type:ignore


def set_local_mode():
    """Set the local mode for the hackbot service."""
    set_mode("local")


def set_dev_mode():
    """Set the dev mode for the hackbot service."""
    set_mode("dev")


def format_hackbot_url(endpoint_name: str) -> str:
    """Format the URL for the hackbot service."""
    return f"{HACKBOT_URL_BASE}/{endpoint_name}"
