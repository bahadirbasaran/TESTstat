import os
import sys
import argparse

sys.path.append(os.path.abspath("."))


if __name__ == "__main__":

    # If there is a host name in arguments, run TESTstat for the CI job.
    # Otherwise initiate the GUI for manual usage.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        dest='host',
        type=str,
        help='Host to connect. Default: stat.ripe.net'
    )
    args = parser.parse_args()

    if args.host:
        from scripts.cicd import run_cicd_tests

        print(f"Host: {args.host}")
        run_cicd_tests(args.host)

    else:
        from PyQt5.QtWidgets import QApplication
        from gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setStyle("fusion")

        ui = MainWindow()
        ui.setup_ui()

        sys.exit(app.exec_())
