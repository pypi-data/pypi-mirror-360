import sys
import time
import threading
import shutil
from typing import Any
from loguru import logger as log


class Spinner(object):
    def __init__(self, description: str, post_msg: str):
        self.running = None
        self.thread = None

        self.spinner_symbols = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
        self.description = description
        self.post_msg = post_msg
        self.start_time = None

    def __enter__(self):
        self.running = True

        def spinner():
            spinner_subdiv_time = 10
            symbol_inx = 0
            waited_steps = 0
            timestep = 0.2 / spinner_subdiv_time

            def out_str_formatter(desc: str):
                return f"\r{desc} {self.spinner_symbols[symbol_inx // spinner_subdiv_time]} (waited {waited_steps * timestep:.2f}s)"

            is_interactive = sys.stdout.isatty()
            while self.running:
                if is_interactive:
                    try:
                        terminal_width = shutil.get_terminal_size().columns
                    except OSError:
                        terminal_width = 80
                    if terminal_width > 0:
                        out_str = out_str_formatter(self.description)
                        # If possible to cur self.description down, do it
                        if len(out_str) > terminal_width:
                            if len(out_str) - len(self.description) < terminal_width:
                                out_str = out_str_formatter(
                                    self.description[: terminal_width - len(out_str)]
                                )
                            else:
                                # Need to just truncate the entire formatted string
                                out_str = out_str_formatter("")[:terminal_width]
                        sys.stdout.write(out_str)
                        sys.stdout.flush()
                time.sleep(timestep)
                waited_steps += 1
                symbol_inx = waited_steps % (len(self.spinner_symbols) * spinner_subdiv_time)

            sys.stdout.write("\r")

        self.start_time = time.time()
        self.thread = threading.Thread(target=spinner)
        self.thread.start()

    def __exit__(self, _exc_type: Any, _exc_value: Any, _traceback: Any):
        self.running = False
        if self.thread is not None:
            self.thread.join()
            taken_time = time.time() - self.start_time if self.start_time is not None else 0
            log.debug(self.post_msg.format(taken_time=taken_time))
