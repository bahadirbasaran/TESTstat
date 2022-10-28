import os
import sys
import argparse
import asyncio

from core.utils import BATCH_SIZE


if os.path.abspath(".") not in sys.path:
    sys.path.append(os.path.abspath('.'))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        dest="host",
        type=str,
        choices=["stat.ripe.net"] + [f"dev00{n}.stat.ripe.net" for n in range(1, 9)],
        help="Host to connect"
    )
    parser.add_argument(
        "--mode",
        dest="mode",
        type=str,
        choices=["default", "500"],
        default="default",
        help="Test mode. 'default' for the default run, '500' for 500-only testing"
    )
    parser.add_argument(
        "--batch_size",
        dest="batch_size",
        type=str,
        default=str(BATCH_SIZE),
        help=f"Batch size. {BATCH_SIZE} by default."
    )
    parser.add_argument(
        "--dc",
        dest="preferred_data_calls",
        type=str,
        nargs='*',
        default=[],
        help=(
            "Preferred data call(s) and versions to run the tests for."
            "Example syntax: --dc bgplay network-info_1.0 abuse-contact-finder_2.0_2.1"
        )
    )
    args = parser.parse_args()

    # If there is a host name in arguments, run TESTstat for the CI job.
    # Otherwise setup and initiate the GUI for manual usage.
    if args.host:
        from scripts.cicd import run_cicd_tests

        # The asyncio.run() function was added in Python 3.7
        # asyncio.run(run_cicd_tests(args.host, args.mode))
        # The solution below is for compatibility concerns for the systems with Python < 3.7
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            run_cicd_tests(
                args.host,
                args.mode,
                args.batch_size,
                args.preferred_data_calls
            )
        )
    else:
        from PyQt5.QtWidgets import QApplication
        from gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setStyle("fusion")

        ui = MainWindow()
        ui.setup_ui()
        ui.show()

        sys.exit(app.exec_())
