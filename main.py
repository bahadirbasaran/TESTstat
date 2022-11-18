import os
import sys
import argparse
import asyncio

from core.config import BATCH_SIZE
from scripts.cicd import run_cicd_tests
from scripts.compare_dc_versions import run_version_comparison


if os.path.abspath(".") not in sys.path:
    sys.path.append(os.path.abspath('.'))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        type=str,
        choices=["stat.ripe.net"] + [f"dev00{n}.stat.ripe.net" for n in range(1, 9)],
        help="Host to connect"
    )
    parser.add_argument(
        "--batch_size",
        type=str,
        default=str(BATCH_SIZE),
        help="Batch size. 100 by default."
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
        default=None,
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
        "--mode",
        type=str,
        default="500"
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
    args = parser.parse_args()

    if int(args.batch_size) < 0 or int(args.batch_size) > 200:
        parser.error("Batch size should be in the range [0, 200]!")

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
                int(args.batch_size),
                args.path,
                args.limit,
                args.preferred_data_calls.pop(),
                args.comparison_fields.pop()
            )
        )

    elif args.host:

        if not args.path:
            args.path = "data/test_cases_500.csv"

        # The asyncio.run() function was added in Python 3.7
        # asyncio.run(run_cicd_tests(args.host, args.mode))
        # The solution below is for compatibility concerns for the systems with Python < 3.7
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            run_cicd_tests(
                args.host,
                int(args.batch_size),
                args.path,
                int(args.random),
                args.preferred_data_calls.pop()
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
