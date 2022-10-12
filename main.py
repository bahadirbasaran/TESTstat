import os
import sys
import argparse
import asyncio


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
    args = parser.parse_args()

    # If there is a host name in arguments, run TESTstat for the CI job.
    # Otherwise setup and initiate the GUI for manual usage.
    if args.host:
        from scripts.cicd import run_cicd_tests

        asyncio.run(run_cicd_tests(args.host, args.mode))
    else:
        from PyQt5.QtWidgets import QApplication
        from gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setStyle("fusion")

        ui = MainWindow()
        ui.setup_ui()
        ui.show()

        sys.exit(app.exec_())
