import traceback
from hackbot.commands import (
    hackbot_run,
    price_run,
    report_run,
    learn_run,
    scope_run,
)
from hackbot.cli_args import get_args, Endpoint, check_source_folder, check_foundry_toml
from hackbot.log_utils import setup_loguru
from loguru import logger as log
from hackbot.hack import CLIVersionMismatchError


def _run():
    setup_loguru()
    args = get_args()
    # Error code from get_args
    if isinstance(args, int):
        exit(args)
    try:
        if args.command == Endpoint.LEARN.value:
            exit_code = learn_run(args)
        elif args.command == Endpoint.REPORT.value:
            exit_code = report_run(args)
        else:
            with check_source_folder(args.source, skip_local_clone=args.skip_local_clone) as source_path:
                if not check_foundry_toml(source_path):
                    exit(1)
                args.source = source_path
                if args.command == Endpoint.PRICE.value:
                    exit_code, _ = price_run(args)
                elif args.command == Endpoint.SCOPE.value:
                    exit_code = scope_run(args)
                elif args.command == Endpoint.RUN.value:
                    exit_code = hackbot_run(args)
                else:
                    log.error(f"❌ Error: Invalid command: {args.command}")
                    exit(1)
    except CLIVersionMismatchError:
        # Already logged, just exit cleanly
        exit_code = 1
    except Exception as e:
        log.error(f"❌ Error: {e}")
        log.error(traceback.format_exc())
        exit_code = 1

    # We fail with working+error if nonzero exit code
    exit_emoji = "✅" if exit_code == 0 else "⚠️"
    log.info(
        f"\n{exit_emoji} Hackbot done!{' (with exit code ' + str(exit_code) + ')' if exit_code != 0 else ''}"
    )
    exit(exit_code)


if __name__ == "__main__":
    _run()
