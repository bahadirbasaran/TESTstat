import os
import sys

sys.path.append(os.path.abspath("."))

from gui.main_window import MainWindow

from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle("fusion")

    ui = MainWindow()
    ui.setup_ui()

    sys.exit(app.exec_())