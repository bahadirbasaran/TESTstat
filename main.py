import os
import sys
import argparse
import asyncio

from core.config import BATCH_SIZE, DC_IN_MAINTENANCE
from scripts.cicd import run_cicd_tests
from scripts.data_quality import run_rrc_check
from scripts.compare_dc_versions import run_version_comparison


if os.path.abspath(".") not in sys.path:
    sys.path.append(os.path.abspath('.'))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        type=str,
        choices=["localhost", "stat.ripe.net", "beta001.stat.ripe.net"] + 
            [f"dev00{n}.stat.ripe.net" for n in range(1, 10)],
        help="Host to connect"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=BATCH_SIZE,
        help="Batch size. 20 by default."
    )
    parser.add_argument(
        "--path",
        type=str,
        default="",
        help="File path to process"
    )
    parser.add_argument(
        "--limit",
        type=str,
        default="",
        help="Max number of lines or range to read. Example syntax: --limit 10 or --limit 10-20"
    )
    parser.add_argument(
        "--random",
        nargs='*',
        default=False,
        help="Sample a specific number of test cases per data call"
    )
    parser.add_argument(
        "--dc",
        dest="preferred_data_calls",
        type=str,
        nargs='*',
        default=[""],
        help=(
            "Preferred data call(s) and versions to run the tests for."
            "Example syntax: --dc bgplay abuse-contact-finder_2.0_2.1"
        )
    )
    parser.add_argument(
        "--maintenance",
        dest="excluded_data_calls",
        type=str,
        nargs='*',
        default=DC_IN_MAINTENANCE,
        help=(
            "Excluded data call(s) that are in maintenance"
            "Example syntax: --dc blocklist mlab-clients"
        )
    )
    parser.add_argument(
        "--compare_versions",
        type=bool,
        default=False,
        help="If True, TESTstat compares versions of DC passed by --dc"
    )
    parser.add_argument(
        "--comparison_fields",
        type=str,
        nargs='*',
        default=[""],
        help="Data fields to compare"
    )
    parser.add_argument(
        "--slack_hooks",
        action="store_true",
        help="If set, TESTstat will post messages to the configured Slack channel."
    )
    parser.add_argument(
        "--okr",
        type=bool,
        default=False,
        help="If True, TESTstat runs for OKRs"
    )
    parser.add_argument(
        "--dq",
        type=str,
        choices=["rrc"],
        help="Data quality test selection"
    )
    args = parser.parse_args()

    # Argument validation
    if int(args.batch_size) < 0 or int(args.batch_size) > 200:
        parser.error("Batch size should be in the range [0, 200]!")

    if args.random:
        try:
            args.random = int(args.random.pop())
        except ValueError:
            parser.error("random should be an integer!")

    if args.compare_versions:

        # Argument validation
        if not args.preferred_data_calls:
            parser.error("No data call found! Example syntax: --dc abuse-contact-finder_2.0_2.1")

        if len(args.preferred_data_calls) > 1:
            parser.error("Only one data call is allowed for comparison!")

        if args.preferred_data_calls[0].count('_') < 2:
            parser.error(
                "No enough versions to compare! Example syntax: --dc abuse-contact-finder_2.0_2.1"
            )

        if not args.path:
            parser.error("File Error: No data given!")

        if not args.path.endswith(".txt"):
            parser.error("File Error: Data source must be a text file!")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            run_version_comparison(
                args.host,
                args.batch_size,
                args.path,
                args.limit,
                args.preferred_data_calls.pop(),
                args.comparison_fields
            )
        )

    elif args.host:

        if not args.path:
            args.path = "data/service_reliability_tests/test_cases_200.csv"

        # If there is a preferred data call, ignore the randomness in any case
        if args.preferred_data_calls and args.preferred_data_calls[0]:
            args.random = False

        # If 'excluded_data_calls' is a type of list, this means arg '--maintenance' has been used in local run instead of Jenkins.
        # In such case, pass that list directly to test run and override DC_IN_MAINTENANCE in config.
        if not isinstance(args.excluded_data_calls, list) and args.excluded_data_calls:
            args.excluded_data_calls = args.excluded_data_calls.split(' ')

        loop = asyncio.get_event_loop()

        # The asyncio.run() function was added in Python 3.7
        # The solution below is for compatibility concerns for the systems with Python < 3.7

        if args.okr:
            # Import here to avoid matplotlib dependency on Jenkins
            from scripts.okr import run_okr_tests

            loop.run_until_complete(
                run_okr_tests(args.host, args.batch_size)
            )
        elif args.dq == "rrc":
            run_rrc_check(args.host, args.slack_hooks)
        else:
            loop.run_until_complete(
                run_cicd_tests(
                    args.host,
                    args.batch_size,
                    args.path,
                    args.random,
                    args.preferred_data_calls,
                    args.excluded_data_calls,
                    args.slack_hooks
                )
            )

    # GUI usage
    else:
        from PyQt5.QtWidgets import QApplication
        from gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setStyle("fusion")

        ui = MainWindow()
        ui.setup_ui()
        ui.show()

        sys.exit(app.exec_())
