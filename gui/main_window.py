import csv

from core.teststat import TestStat
from gui.test_case_window import TestCaseWindow
from gui.utils import MessageEnum, ColorEnum, throw_message, format_table_item

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, \
    QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, \
    QProgressBar, QLineEdit, QApplication, QDialog, QCheckBox, \
    QStyledItemDelegate, QVBoxLayout, QGridLayout, QHeaderView


TEST_CASES_PATH = "data/test_cases.csv"
HOSTS = [
    "Local Host",
    "stat.ripe.net",
    "dev001.stat.ripe.net",
    "dev002.stat.ripe.net",
    "dev003.stat.ripe.net",
    "dev004.stat.ripe.net",
    "dev005.stat.ripe.net",
    "dev006.stat.ripe.net",
    "dev007.stat.ripe.net",
    "dev008.stat.ripe.net"
]


class ReadOnlyDelegate(QStyledItemDelegate):
    """
    Used to make columns read-only
    """
    def createEditor(self, parent, option, index):
        return


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TESTstat")
        self.outerLayout = QVBoxLayout()
        self.setStyleSheet((
            "background-color: rgb(235, 236, 244);"
            "color: rgb(66, 77, 112);"
        ))

        # Active test results on the table
        self.previous_results = False

    # Count selected tests
    # Should be here to get the item from the ItemChanged()
    # Checking whether change occured in the 1st column(checkbox)
    def count_selected(self, item):
        if item.column() == 0:
            if self.table_test_suite.item(item.row(), 0) is not None:
                self.label_selected.setText(
                    f"Selected tests: {len(self.get_checked_row_indexes(return_all = False))}"
                )

    def setup_ui(self):
        """Sets main window up"""
        # Creating layouts
        topLayout = QHBoxLayout()
        self.topleftLayout = QGridLayout()
        topcenterLayout = QGridLayout()
        toprightLayout = QGridLayout()
        middleLayout = QVBoxLayout()
        middleTopLayout = QHBoxLayout()
        bottomLayout = QHBoxLayout()

        # Font
        self.font = QFont()
        self.font.setBold(True)

        # Checkboxes
        self.checkbox_select_all = QCheckBox(
            clicked=lambda: self.on_checkbox_select_all()
        )
        self.checkbox_select_all.setText("Select All")
        self.checkbox_select_all.setChecked(False)
        self.checkbox_select_all.setStyleSheet("font-weight: bold; font-size:16px;")
        self.checkbox_select_all.setGeometry(QRect(268, 70, 111, 32))

        # Test cases table
        self.table_test_suite = QTableWidget()
        self.table_test_suite.setGeometry(QRect(50, 200, 1190, 470))
        self.table_test_suite.setColumnCount(5)
        self.table_test_suite.setRowCount(0)
        header = self.table_test_suite.horizontalHeader()
        self.table_test_suite.setColumnWidth(0, 20)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.table_test_suite.setStyleSheet("background-color: rgb(255, 255, 255); font-size:16px;")

        table_cols = ["", "Data Call", "Test Input", "Expected Output", "Output"]
        for index, column_name in enumerate(table_cols):
            item = QTableWidgetItem(column_name)
            self.font.setPointSize(16)
            item.setFont(self.font)
            self.table_test_suite.setHorizontalHeaderItem(index, item)

        # Make column 1 and 4 read-only
        delegate = ReadOnlyDelegate(self.table_test_suite)
        self.table_test_suite.setItemDelegateForColumn(1, delegate)
        self.table_test_suite.setItemDelegateForColumn(3, delegate)

        # Labels
        label_host = QLabel()
        label_host.setText("Source:")
        label_host.setStyleSheet("font-weight: bold; font-size:16px;")

        self.label_status = QLabel()
        self.label_status.setGeometry(QRect(392, 60, 150, 32))
        self.label_status.setText(f"Tests: {self.table_test_suite.rowCount()}")
        self.font.setPointSize(16)
        self.label_status.setFont(self.font)
        self.label_selected = QLabel()
        self.label_selected.setGeometry(QRect(392, 90, 150, 32))
        self.label_selected.setText(
            "Selected tests: 0"
        )
        self.label_selected.setFont(self.font)

        # Count and show number of selected tests
        self.table_test_suite.itemChanged.connect(
            self.count_selected
        )

        self.label_failed = QLabel()
        self.label_failed.setGeometry(QRect(392, 90, 150, 32))
        self.label_failed.setText(
            "Failed tests: 0"
        )
        self.label_failed.setFont(self.font)

        self.label_succesful = QLabel()
        self.label_succesful.setGeometry(QRect(392, 90, 150, 32))
        self.label_succesful.setText(
            "Successful tests: 0"
        )
        self.label_succesful.setFont(self.font)

        # Buttons
        btn_run = QPushButton(clicked=lambda: self.on_btn_run_click())
        btn_run.setText("Run Tests")
        btn_run.setStyleSheet("font-weight: bold; font-size:16px;")
        btn_run.setGeometry(QRect(20, 70, 111, 32))
        middleTopLayout.addWidget(self.checkbox_select_all)

        btn_compare = QPushButton(clicked=lambda: self.on_btn_compare_click())
        btn_compare.setText("Compare")
        btn_compare.setStyleSheet("font-weight: bold; font-size:16px;")
        btn_compare.setGeometry(QRect(144, 70, 111, 32))

        btn_new_test = QPushButton(clicked=lambda: self.on_btn_new_test_click())
        btn_new_test.setText("Add Test")
        btn_new_test.setGeometry(QRect(950, 700, 130, 32))
        btn_new_test.setStyleSheet("font-weight: bold; font-size:16px;")

        btn_remove_test = QPushButton(
            clicked=lambda: self.on_btn_remove_test_click()
        )
        btn_remove_test.setText("Remove Test")
        btn_remove_test.setGeometry(QRect(1090, 700, 130, 32))
        btn_remove_test.setStyleSheet("font-weight: bold; font-size:16px;")

        btn_load_test = QPushButton(clicked=lambda: self.on_btn_load_test_click())
        btn_load_test.setText("Load Tests")
        btn_load_test.setGeometry(QRect(50, 700, 111, 32))
        btn_load_test.setMaximumWidth(400)
        btn_load_test.setStyleSheet("font-weight: bold; font-size:16px;")

        btn_save_test = QPushButton(clicked=lambda: self.on_btn_save_test_click())
        btn_save_test.setText("Overwrite Tests")
        btn_save_test.setGeometry(QRect(170, 700, 111, 32))
        btn_save_test.setStyleSheet("font-weight: bold; font-size:16px;")

        btn_clear_outputs = QPushButton(
            clicked=lambda: self.reset_main_window(clear_tests=False, confirmation=False)
        )
        btn_clear_outputs.setText("Clear All Outputs")
        btn_clear_outputs.setGeometry(QRect(1090, 150, 130, 32))
        btn_clear_outputs.setStyleSheet("font-weight: bold; font-size:16px;")
        bottomLayout.addStretch()

        # Comboboxes
        self.combobox_host = QComboBox()
        self.combobox_host.addItems(HOSTS)
        self.combobox_host.setStyleSheet("background-color: rgb(255, 255, 255);font-size:16px;")
        self.combobox_host.currentIndexChanged.connect(
            lambda: self.on_combobox_host_changed(self.combobox_host, self.port)
        )

        # Searchbar
        self.searchbar = QLineEdit()
        self.searchbar.setGeometry(QRect(700, 100, 520, 32))
        self.searchbar.setMaximumWidth(600)
        self.searchbar.setStyleSheet("background-color: rgb(255, 255, 255);font-size:16px;")
        self.searchbar.textChanged.connect(self.update_table_test_suite)
        self.searchbar.setPlaceholderText("Search Data Call")

        # Line Edits
        self.port = QLineEdit()
        self.port.setStyleSheet("background-color: rgb(255, 255, 255);font-size:16px;")
        self.port.setPlaceholderText("Port")
        self.port.setText("8000")
        self.port.setMinimumWidth(100)

        # Other indicators
        self.progress_bar = QProgressBar()
        self.progress_bar.setGeometry(QRect(20, 107, 390, 13))
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setOrientation(Qt.Horizontal)
        self.progress_bar.setInvertedAppearance(False)
        self.progress_bar.setTextDirection(QProgressBar.TopToBottom)
        self.progress_bar.hide()

        # Set the main window UI up
        self.topleftLayout.addWidget(label_host, 0, 0)
        self.topleftLayout.addWidget(btn_run, 1, 0, 1, 2)
        self.topleftLayout.addWidget(btn_compare, 1, 2, 1, 2)      
        self.topleftLayout.addWidget(self.port, 0, 3)
        self.topleftLayout.addWidget(self.progress_bar, 2, 0, 1, 4)
        self.topleftLayout.addWidget(self.combobox_host, 0, 1, 1, 2)
        self.topleftLayout.setColumnStretch(0, 3)
        self.topleftLayout.setColumnStretch(1, 3)
        self.topleftLayout.setColumnStretch(2, 3)
        self.topleftLayout.setColumnStretch(3, 3)

        toprightLayout.addWidget(self.label_status, 0, 0, alignment=Qt.AlignLeft)
        toprightLayout.addWidget(self.label_selected, 1, 0, alignment=Qt.AlignLeft)
        toprightLayout.addWidget(self.label_failed, 3, 0, alignment=Qt.AlignLeft)
        toprightLayout.addWidget(self.label_succesful, 2, 0, alignment=Qt.AlignLeft)

        topcenterLayout.addWidget(btn_new_test, 0, 1)
        topcenterLayout.addWidget(btn_remove_test, 1, 1)
        topcenterLayout.addWidget(btn_load_test, 0, 0)
        topcenterLayout.addWidget(btn_save_test, 1, 0)

        topLayout.addLayout(self.topleftLayout, 3)
        topLayout.insertStretch(1, 3)
        topLayout.addLayout(topcenterLayout, 3)
        topLayout.insertStretch(3, 3)
        topLayout.addLayout(toprightLayout, 3)

        middleTopLayout.addWidget(self.searchbar)
        middleTopLayout.addWidget(self.checkbox_select_all)
        middleTopLayout.addStretch()
        middleLayout.addLayout(middleTopLayout)
        middleLayout.addWidget(self.table_test_suite)

        bottomLayout.addWidget(btn_clear_outputs)

        self.outerLayout.addLayout(topLayout)
        self.outerLayout.insertSpacing(1, 20)
        self.outerLayout.addLayout(middleLayout)
        self.outerLayout.addLayout(bottomLayout)
        self.setLayout(self.outerLayout)

    # Utilization methods

    def update_table_test_suite(self, text):
        """
        Dynamically update the table with tests corresponding to the string in
        the searchbar. Set the "Select All" checkbox unchecked with any change
        in search string, so any resulting tests can be selected in bulk.
        """

        self.checkbox_select_all.setChecked(False)

        for row in range(self.table_test_suite.rowCount()):
            if text.lower() in self.table_test_suite.item(row, 1).text():
                self.table_test_suite.showRow(row)
            else:
                self.table_test_suite.hideRow(row)

    def colorize_table_row(self, row_index, text_color, background_color, process_immediately=True):
        """Colorizes given row's background and text"""

        for col_index in range(self.table_test_suite.columnCount()):
            self.table_test_suite.item(row_index, col_index).setForeground(text_color)
            self.table_test_suite.item(row_index, col_index).setBackground(background_color)

        if process_immediately:
            QApplication.processEvents()

    def reset_main_window(self, clear_tests=False, confirmation=True, clear_checkboxes=True):

        if confirmation and self.previous_results:
            ret_val = throw_message(
                MessageEnum.WARNING,
                "Warning",
                "Are you sure you want to discard the test result?"
            )
            if ret_val == MessageEnum.NO:
                return ret_val

        self.previous_results = False

        # Restore the status label
        self.label_status.setText(f"Tests: {self.table_test_suite.rowCount()}")

        # Restore the progress bar
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.hide()

        if clear_tests:
            self.table_test_suite.clearContents()
            self.table_test_suite.setRowCount(0)
            self.label_status.setText("Tests: 0")
            QApplication.processEvents()
            return

        # Clear successful/failed tests
        self.label_succesful.setText("Successful tests: 0")
        self.label_failed.setText("Failed tests: 0")

        # Clear select all checkbox
        self.checkbox_select_all.setChecked(False)

        for row_index in range(self.table_test_suite.rowCount()):

            self.colorize_table_row(row_index, ColorEnum.UI_FONT, ColorEnum.WHITE, False)

            # Clear test outputs in each row
            self.table_test_suite.item(
                row_index,
                self.table_test_suite.columnCount() - 1
            ).setText('')

            # Clear checkboxes
            if clear_checkboxes:
                checkbox = self.table_test_suite.item(row_index, 0)
                if checkbox.checkState() == Qt.Checked:
                    checkbox.setCheckState(Qt.Unchecked)

        self.table_test_suite.sortByColumn(1, Qt.AscendingOrder)

        QApplication.processEvents()

    def get_checked_row_indexes(self, return_all=True):
        """
        Returns the test case indexes checked by user.
        If param return_all = True and if none checked, returns all indexes.
        """

        checked_row_indexes = []

        for row_index in range(self.table_test_suite.rowCount()):
            if self.table_test_suite.item(row_index, 0).checkState() == Qt.Checked:
                checked_row_indexes.append(row_index)

        if return_all and not checked_row_indexes:
            return list(range(self.table_test_suite.rowCount()))

        return checked_row_indexes

    # Combobox slots

    def on_combobox_host_changed(self, combobox, port):

        if combobox.currentText() == "Local Host":
            port.setText("8000")
        else:
            port.setText("")
            port.setPlaceholderText("Port")

    # Button slots

    def on_btn_new_test_click(self):

        if not self.previous_results or \
                (self.previous_results and self.reset_main_window() != MessageEnum.NO):
            self.test_case_window_ui = TestCaseWindow(self)
            self.test_case_window_ui.setup_ui()
            self.test_case_window_ui.show()

    def on_btn_remove_test_click(self):

        rows_to_remove = self.get_checked_row_indexes(return_all=False)

        if not self.table_test_suite.rowCount():
            throw_message(MessageEnum.CRITICAL, "Error", "There is no test case to remove!")
            return
        elif not rows_to_remove:
            throw_message(MessageEnum.CRITICAL, "Error", "No test case selected!")
            return

        if self.reset_main_window() != MessageEnum.NO:
            for row_index in reversed(rows_to_remove):
                self.table_test_suite.removeRow(row_index)
                self.label_status.setText(f"Tests: {self.table_test_suite.rowCount()}")

    def on_btn_load_test_click(self):
        """Populates the table from TEST_CASES_PATH"""

        if self.table_test_suite.rowCount():
            ret_val = throw_message(
                MessageEnum.WARNING,
                "Warning",
                "Are you sure you want to override the test suite?"
            )
            if ret_val == MessageEnum.NO:
                return

            self.reset_main_window(clear_tests=True, confirmation=False)

        with open(TEST_CASES_PATH) as csv_file:
            header = csv_file.readline().strip()
            if header != "data_call,test_input,expected_output":
                throw_message(MessageEnum.CRITICAL, "Import Error", "The test suite is malformed!")
                return
            if len(csv_file.readlines()) < 1:
                throw_message(
                    MessageEnum.CRITICAL,
                    "Import Error",
                    "No available test case to import!"
                )
                return

        with open(TEST_CASES_PATH) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            # Skip the header
            next(csv_reader)

            for index, row in enumerate(csv_reader):
                csv_data_call, csv_test_input, csv_expected_output = row

                # Insert a new row first
                self.table_test_suite.setRowCount(index + 1)

                # Create items for each column of the row
                item_checkbox = QTableWidgetItem(None)
                item_data_call = QTableWidgetItem(csv_data_call)
                item_test_input = QTableWidgetItem(format_table_item(csv_test_input))
                item_expected_output = QTableWidgetItem(format_table_item(csv_expected_output))
                item_test_output = QTableWidgetItem('')

                item_checkbox.setFlags(
                    Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
                )
                item_checkbox.setCheckState(Qt.Unchecked)

                self.table_test_suite.setItem(index, 0, item_checkbox)
                self.table_test_suite.setItem(index, 1, item_data_call)
                self.table_test_suite.setItem(index, 2, item_test_input)
                self.table_test_suite.setItem(index, 3, item_expected_output)
                self.table_test_suite.setItem(index, 4, item_test_output)

                self.table_test_suite.resizeRowsToContents()

                self.label_status.setText(f"Tests: {self.table_test_suite.rowCount()}")

    def on_btn_save_test_click(self):
        """Overrides TEST_CASES_PATH by using test cases in the table"""

        if not self.table_test_suite.rowCount():
            throw_message(MessageEnum.CRITICAL, "Save Error", "No available test case to save!")
            return

        ret_val = throw_message(
            MessageEnum.WARNING,
            "Warning",
            "Are you sure you want to override the test cases?"
        )
        if ret_val == MessageEnum.NO:
            return

        with open(TEST_CASES_PATH, 'w') as csv_file:

            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(["data_call", "test_input", "expected_output"])

            for row_index in self.get_checked_row_indexes():
                data_call = self.table_test_suite.item(row_index, 1).text()
                test_input = format_table_item(
                    self.table_test_suite.item(row_index, 2).text(),
                    csv_to_table=False
                )
                expected_output = format_table_item(
                    self.table_test_suite.item(row_index, 3).text(),
                    csv_to_table=False
                )

                csv_writer.writerow([data_call, test_input, expected_output])

    def on_checkbox_select_all(self):
        """
        Selects or deselects all the currently visible tests. Applicable while searching
        for tests using the searchbar and selecting all found tests in bulk.
        """

        if self.checkbox_select_all.isChecked():
            for row in range(self.table_test_suite.rowCount()):
                if not self.table_test_suite.isRowHidden(row):
                    self.table_test_suite.item(row, 0).setCheckState(Qt.Checked)
        else:
            for row in range(self.table_test_suite.rowCount()):
                if not self.table_test_suite.isRowHidden(row):
                    self.table_test_suite.item(row, 0).setCheckState(Qt.Unchecked)

    def on_btn_run_click(self):
        """Runs all/selected test cases in the table"""

        if not self.table_test_suite.rowCount():
            throw_message(MessageEnum.CRITICAL, "Run Error", "No available test case to run!")
            return

        self.reset_main_window(clear_tests=False, confirmation=False, clear_checkboxes=False)
        host = self.combobox_host.currentText()
        port = None if not self.port.text() else self.port.text()

        # Reoder the table
        for row in range(self.table_test_suite.rowCount()):
            if self.table_test_suite.item(row, 0).checkState() == Qt.Checked:
                self.table_test_suite.item(row, 0).setText("checked")

        self.table_test_suite.sortByColumn(1, Qt.AscendingOrder)
        self.table_test_suite.sortByColumn(0, Qt.DescendingOrder)

        for row in range(self.table_test_suite.rowCount()):
            if self.table_test_suite.item(row, 0).checkState() == Qt.Checked:
                self.table_test_suite.item(row, 0).setText("")

        self.run_tests(self.get_checked_row_indexes(), host, port)

    def on_btn_compare_click(self):
        """Opens the comparison widget to choose a API source to compare"""

        if self.reset_main_window() != MessageEnum.NO:

            main_host = self.combobox_host.currentText()

            comparison_widget = QDialog()
            comparison_widget.setWindowTitle("Compare API Sources")

            hbox_host_port = QHBoxLayout(comparison_widget)
            hbox_host_port.setContentsMargins(20, 60, 30, 100)

            # Labels

            label_instruction = QLabel(comparison_widget)
            label_instruction.setText(f"API Source to compare with {main_host}:")
            label_instruction.setGeometry(QRect(20, 20, 350, 30))

            label_second_host = QLabel()
            label_second_host.setText("API Source 2:")
            label_second_host.setStyleSheet("font-weight: bold; font-size:16px;")

            # Buttons

            btn_run_comparison = QPushButton(
                comparison_widget,
                clicked=lambda: self.on_btn_run_comparison_click(
                    comparison_widget,
                    combobox_second_host.currentText(),
                    port_second_host.text()
                )
            )
            btn_run_comparison.setText("Compare")
            btn_run_comparison.setStyleSheet("font-weight: bold; font-size:16px;")
            btn_run_comparison.setGeometry(QRect(155, 110, 111, 32))

            # Comboboxes

            combobox_second_host = QComboBox()
            hosts_but_main = [host for host in HOSTS if host != main_host]
            combobox_second_host.addItems(hosts_but_main)

            # Line Edits

            port_second_host = QLineEdit()
            port_second_host.setStyleSheet(
                "background-color: rgb(255, 255, 255);"
            )
            if combobox_second_host.currentText() == "Local Host":
                port_second_host.setText("8000")
            else:
                port_second_host.setText("")
                port_second_host.setPlaceholderText("Port")

            combobox_second_host.currentIndexChanged.connect(
                lambda: self.on_combobox_host_changed(combobox_second_host, port_second_host)
            )

            hbox_host_port.addWidget(label_second_host)
            hbox_host_port.addWidget(combobox_second_host)
            hbox_host_port.addWidget(port_second_host)
            comparison_widget.exec()

    def on_btn_run_comparison_click(self, widget, second_host, port_second_host):
        """
        Compares two API sources and lists only the test cases that
        fail on one source and pass on the other and vice versa
        """

        # Close the widget first
        widget.close()

        if not self.table_test_suite.rowCount():
            throw_message(MessageEnum.CRITICAL, "Run Error", "No available test case to run!")
            return

        tests_to_run = self.get_checked_row_indexes()

        main_host = self.combobox_host.currentText()
        port_main_host = None if not self.port.text() else self.port.text()
        port_second_host = None if not port_second_host else port_second_host

        failed_tests_main_host = self.run_tests(tests_to_run, main_host, port_main_host, True)

        self.reset_main_window(confirmation=False)

        # Change the combobox on main window to indicate the host of second run
        self.combobox_host.setCurrentIndex(HOSTS.index(second_host))

        failed_tests_second_host = self.run_tests(tests_to_run, second_host, port_second_host, True)

        self.reset_main_window(confirmation=False)

        failed_tests_main_host, failed_tests_second_host = (
            set(failed_tests_main_host) - set(failed_tests_second_host),
            set(failed_tests_second_host) - set(failed_tests_main_host)
        )

        for row_index in failed_tests_main_host:
            item_failed_output = QTableWidgetItem(f"Failed at {main_host}")
            self.table_test_suite.setItem(row_index, 3, item_failed_output)
            self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.FAILURE)

        for row_index in failed_tests_second_host:
            item_failed_output = QTableWidgetItem(f"Failed at {second_host}")
            self.table_test_suite.setItem(row_index, 3, item_failed_output)
            self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.FAILURE_SECOND_HOST)

        self.table_test_suite.resizeRowsToContents()

    def run_tests(self, tests_to_run, host, port, return_failed_tests=False):

        num_tests_run = 0
        num_passed_tests = 0
        num_failed_tests = 0
        num_total_tests = len(tests_to_run)
        failed_tests = []

        self.progress_bar.show()
        self.progress_bar.setProperty("maximum", num_total_tests)

        self.label_succesful.setText(f"Successful tests: {num_passed_tests}")

        teststat = TestStat(host, port)

        for row_index in tests_to_run:
            data_call = self.table_test_suite.item(row_index, 1).text()
            test_input = self.table_test_suite.item(row_index, 2).text()
            expected_output = self.table_test_suite.item(row_index, 3).text()

            # Format table items for the run_test method of the TestStat class
            test_input = test_input.replace("\n", '&').replace(' ', '')
            expected_pairs = expected_output.lower().replace(' ', '').split("\n")

            expected_output = {}
            for param_value_pair in expected_pairs:
                # Inputs may include more than one '='
                param, value = param_value_pair.split('=', 1)
                expected_output[param] = value

            print(f"Case {row_index+1} ({num_tests_run+1}/{num_total_tests}):", end=' ')

            # test_output:
            #   {}  -> test is successful
            #   int -> test could not be executed (connection error, timeout)
            #   {param: val} -> test output that does not match with expected
            test_output = teststat.run_test(data_call, test_input, expected_output)

            self.previous_results = True

            # Error handling

            if test_output == MessageEnum.TIMEOUT:
                num_tests_run += 1
                self.progress_bar.setProperty("value", num_tests_run)

                timed_out_item = QTableWidgetItem("Error: Connection timed out!")
                self.table_test_suite.setItem(row_index, 4, timed_out_item)

                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.TIMEOUT)

                failed_tests.append(row_index)
                continue
            elif test_output == MessageEnum.CONNECTION_ERROR:
                throw_message(MessageEnum.CRITICAL, "Connection Error", test_output)
                self.reset_main_window(confirmation=False)
                return

            num_tests_run += 1
            self.progress_bar.setProperty("value", num_tests_run)

            if not test_output:
                num_passed_tests += 1
                self.label_succesful.setText(f"Successful tests: {num_passed_tests}")
                self.table_test_suite.setItem(row_index, 4, QTableWidgetItem(""))
                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.SUCCESS)
            else:
                num_failed_tests += 1
                self.label_failed.setText(f"Failed tests: {num_failed_tests}")
                failed_tests.append(row_index)
                failed_output = []
                for param, value in test_output.items():
                    failed_output.append(f"{param} = {value}")

                item_failed_output = QTableWidgetItem("\n".join(failed_output))
                self.table_test_suite.setItem(row_index, 4, item_failed_output)
                self.table_test_suite.resizeRowsToContents()
                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.FAILURE)

        if return_failed_tests:
            return failed_tests
