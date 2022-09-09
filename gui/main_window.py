import csv
import os

from core.teststat import TestStat
from core.utils import MessageEnum
from gui.utils import ReadOnlyDelegator, ColorEnum, StyleEnum, throw_message, \
    format_table_item, HOSTS
from gui.test_case_window import TestCaseWindow

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, \
    QProgressBar, QLineEdit, QApplication, QDialog, QCheckBox, QHeaderView


class MainWindow(QWidget):

    def __init__(self):
        """Construct main window"""

        super().__init__()

        self.setWindowTitle("TESTstat")
        self.resize(900, 500)
        self.setStyleSheet(StyleEnum.UI)

        # Active test results on the table
        self.previous_results = False

        # Default path of test cases
        self.test_cases_path = "data/test_cases_500.csv"

        # Early-stopping
        self.stop = False

    def setup_ui(self):
        """Set the main window up"""

        # Layouts
        top_left_layout = QGridLayout()
        top_center_layout = QGridLayout()
        top_right_layout = QGridLayout()
        top_layout = QHBoxLayout()
        middle_top_layout = QHBoxLayout()
        middle_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()
        outer_layout = QVBoxLayout()

        # Font
        font = QFont()
        font.setBold(True)
        font.setPointSize(16)

        # Test cases table
        self.table_test_suite = QTableWidget(0, 5)
        self.table_test_suite.setGeometry(QRect(50, 200, 1190, 470))
        self.table_test_suite.setColumnWidth(0, 20)
        self.table_test_suite.itemChanged.connect(self.count_selected_tests)
        header = self.table_test_suite.horizontalHeader()

        for index in range(1, 5):
            header.setSectionResizeMode(index, QHeaderView.Stretch)

        for index, col in enumerate(["", "Data Call", "Test Input", "Expected Output", "Output"]):
            item = QTableWidgetItem(col)
            item.setFont(font)
            self.table_test_suite.setHorizontalHeaderItem(index, item)

        # Make column 1 and 4 read-only
        delegator = ReadOnlyDelegator(self.table_test_suite)
        self.table_test_suite.setItemDelegateForColumn(1, delegator)
        self.table_test_suite.setItemDelegateForColumn(3, delegator)

        # Labels
        label_host = QLabel("Source:")
        label_total = QLabel("Tests:")
        label_selected = QLabel("Selected:")
        label_passed = QLabel("Passed:")
        label_failed = QLabel("Failed:")
        label_timeout = QLabel("Timed-out:")
        self.label_total_value = QLabel(f"{self.table_test_suite.rowCount()}")
        self.label_selected_value = QLabel("0")
        self.label_passed_value = QLabel("0")
        self.label_failed_value = QLabel("0")
        self.label_timed_out_value = QLabel("0")

        # Buttons
        btn_run = QPushButton(
            "Run Tests", clicked=lambda: self.on_btn_run_click()
        )
        btn_compare = QPushButton(
            "Compare Sources", clicked=lambda: self.on_btn_compare_sources_click()
        )
        btn_new_test = QPushButton(
            "Add Test", clicked=lambda: self.on_btn_new_test_click()
        )
        btn_remove_test = QPushButton(
            "Remove Test", clicked=lambda: self.on_btn_remove_test_click()
        )
        btn_load_test = QPushButton(
            "Load Tests", clicked=lambda: self.on_btn_load_tests_click()
        )
        btn_save_test = QPushButton(
            "Overwrite Tests", clicked=lambda: self.on_btn_save_tests_click()
        )
        btn_stop_test = QPushButton(
            "Stop Tests", clicked=lambda: self.stop_tests()
        )
        btn_clear_outputs = QPushButton(
            "Clear Outputs",
            clicked=lambda: self.reset_main_window(clear_tests=False, confirmation=False)
        )

        # Checkboxes
        self.checkbox_select_all = QCheckBox(
            "Select All",
            clicked=lambda: self.on_checkbox_select_all(),
            checked=False
        )

        # Comboboxes
        self.combobox_host = QComboBox()
        self.combobox_host.addItems(HOSTS)
        self.combobox_host.setStyleSheet(StyleEnum.COMBOBOX)
        self.combobox_host.currentIndexChanged.connect(
            lambda: self.on_combobox_host_changed(self.combobox_host, self.port)
        )

        # # Line Edits
        searchbar = QLineEdit()
        searchbar.setMaximumWidth(245)
        searchbar.setPlaceholderText("Search Data Call")
        searchbar.textChanged.connect(self.update_table_test_suite)

        self.port = QLineEdit("8000")
        self.port.setPlaceholderText("Port")

        # Other indicators
        self.progressbar = QProgressBar()
        self.progressbar.setProperty("value", 0)
        self.progressbar.setOrientation(Qt.Horizontal)
        self.progressbar.setInvertedAppearance(False)
        self.progressbar.setTextDirection(QProgressBar.TopToBottom)
        self.progressbar.hide()

        # Wrap the test case window UI up
        for item in [self.table_test_suite, searchbar, self.port]:
            item.setStyleSheet(StyleEnum.TABLE_LINE_EDIT)

        for item in [
            self.checkbox_select_all,
            label_host,
            btn_run,
            btn_compare,
            btn_new_test,
            btn_remove_test,
            btn_load_test,
            btn_save_test,
            btn_clear_outputs,
            btn_stop_test
        ]:
            item.setStyleSheet(StyleEnum.BTN_LABEL_CHECKBOX)

        for item in [
            label_total,
            self.label_total_value,
            label_selected,
            self.label_selected_value,
            label_passed,
            self.label_passed_value,
            label_failed,
            self.label_failed_value,
            label_timeout,
            self.label_timed_out_value
        ]:
            item.setFont(font)

        top_left_layout.addWidget(label_host, 0, 0)
        top_left_layout.addWidget(self.combobox_host, 0, 1, 1, 2)
        top_left_layout.addWidget(self.port, 0, 3)
        top_left_layout.addWidget(btn_run, 1, 0, 1, 2)
        top_left_layout.addWidget(btn_compare, 1, 2, 1, 2)
        top_left_layout.addWidget(self.progressbar, 2, 0, 1, 4)
        for index in range(4):
            top_left_layout.setColumnStretch(index, 3)

        top_center_layout.addWidget(btn_load_test, 0, 0)
        top_center_layout.addWidget(btn_new_test, 0, 1)
        top_center_layout.addWidget(btn_save_test, 1, 0)
        top_center_layout.addWidget(btn_remove_test, 1, 1)

        top_right_layout.addWidget(label_total, 0, 0, alignment=Qt.AlignLeft)
        top_right_layout.addWidget(self.label_total_value, 0, 1, alignment=Qt.AlignRight)
        top_right_layout.addWidget(label_selected, 1, 0, alignment=Qt.AlignLeft)
        top_right_layout.addWidget(self.label_selected_value, 1, 1, alignment=Qt.AlignRight)
        top_right_layout.addWidget(label_passed, 2, 0, alignment=Qt.AlignLeft)
        top_right_layout.addWidget(self.label_passed_value, 2, 1, alignment=Qt.AlignRight)
        top_right_layout.addWidget(label_failed, 3, 0, alignment=Qt.AlignLeft)
        top_right_layout.addWidget(self.label_failed_value, 3, 1, alignment=Qt.AlignRight)
        top_right_layout.addWidget(label_timeout, 4, 0, alignment=Qt.AlignLeft)
        top_right_layout.addWidget(self.label_timed_out_value, 4, 1, alignment=Qt.AlignRight)

        top_layout.addLayout(top_left_layout, 3)
        top_layout.insertStretch(1, 3)
        top_layout.addLayout(top_center_layout, 3)
        top_layout.insertStretch(3, 3)
        top_layout.addLayout(top_right_layout, 3)

        middle_top_layout.addWidget(self.checkbox_select_all)
        middle_top_layout.addWidget(searchbar)
        middle_top_layout.addStretch()
        middle_layout.addLayout(middle_top_layout)
        middle_layout.addWidget(self.table_test_suite)

        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_stop_test)
        bottom_layout.addWidget(btn_clear_outputs)

        outer_layout.addLayout(top_layout)
        outer_layout.insertSpacing(1, 20)
        outer_layout.addLayout(middle_layout)
        outer_layout.addLayout(bottom_layout)

        self.setLayout(outer_layout)

    # Utilization methods
    def count_selected_tests(self, item):
        """Check whether change occured in the 1st column (checkbox)"""

        if item.column() == 0:
            if self.table_test_suite.item(item.row(), 0) is not None:
                self.label_selected_value.setText(
                    f"{len(self.get_checked_row_indexes(return_all = False))}"
                )

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
        """Colorize given row's background and text"""

        for col_index in range(self.table_test_suite.columnCount()):
            self.table_test_suite.item(row_index, col_index).setForeground(QColor(text_color))
            self.table_test_suite.item(row_index, col_index).setBackground(QColor(background_color))

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

        # Restore the status labels
        self.label_total_value.setText(f"{self.table_test_suite.rowCount()}")
        for item in [self.label_passed_value, self.label_failed_value, self.label_timed_out_value]:
            item.setText("0")
            item.setStyleSheet(StyleEnum.UI)

        # Restore the progress bar
        self.progressbar.setProperty("value", 0)
        self.progressbar.hide()

        if clear_tests:
            self.table_test_suite.clearContents()
            self.table_test_suite.setRowCount(0)
            self.label_total_value.setText("0")
            QApplication.processEvents()
            return

        self.checkbox_select_all.setChecked(False)

        for row_index in range(self.table_test_suite.rowCount()):

            self.colorize_table_row(row_index, ColorEnum.UI_FONT, ColorEnum.WHITE, False)

            # Clear test outputs in each row
            self.table_test_suite.item(
                row_index,
                self.table_test_suite.columnCount() - 1
            ).setText('')

            if clear_checkboxes:
                checkbox = self.table_test_suite.item(row_index, 0)
                if checkbox.checkState() == Qt.Checked:
                    checkbox.setCheckState(Qt.Unchecked)

        self.table_test_suite.sortByColumn(1, Qt.AscendingOrder)

        QApplication.processEvents()

    def get_checked_row_indexes(self, return_all=True):
        """
        Return test case indexes checked by user.
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
                self.label_total_value.setText(f"{self.table_test_suite.rowCount()}")

            self.table_test_suite.resizeRowsToContents()

    def on_btn_load_tests_click(self):
        """Open dialog box to select test case source"""

        def _on_btn_load_click(widget, path):
            """Populate the table from test case source"""

            # Close the widget first
            widget.close()

            self.test_cases_path = path

            with open(path) as csv_file:
                header = csv_file.readline().strip()
                if header != "data_call,test_input,expected_output":
                    throw_message(MessageEnum.CRITICAL, "Import Error", f"{path} is malformed!")
                    return

                csv_row_count = len(csv_file.readlines())
                if csv_row_count < 1:
                    throw_message(
                        MessageEnum.CRITICAL,
                        "Import Error",
                        "No available test case to import!"
                    )
                    return

            with open(path) as csv_file:
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

                    item_checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    item_checkbox.setCheckState(Qt.Unchecked)

                    self.table_test_suite.setItem(index, 0, item_checkbox)
                    self.table_test_suite.setItem(index, 1, item_data_call)
                    self.table_test_suite.setItem(index, 2, item_test_input)
                    self.table_test_suite.setItem(index, 3, item_expected_output)
                    self.table_test_suite.setItem(index, 4, item_test_output)

                self.table_test_suite.resizeRowsToContents()

                self.label_total_value.setText(f"{self.table_test_suite.rowCount()}")

        if self.table_test_suite.rowCount():
            ret_val = throw_message(
                MessageEnum.WARNING,
                "Warning",
                "Are you sure you want to overwrite the test cases?"
            )
            if ret_val == MessageEnum.NO:
                return

            self.reset_main_window(clear_tests=True, confirmation=False)

        load_csv_widget = QDialog()
        load_csv_widget.setStyleSheet(StyleEnum.UI)
        load_csv_widget.setWindowTitle("Select Data Source")
        load_csv_widget_layout = QVBoxLayout(load_csv_widget)

        hbox_load_csv = QVBoxLayout()

        label_load_csv = QLabel("Data Source:")
        label_load_csv.setStyleSheet(StyleEnum.BTN_LABEL_CHECKBOX)

        combobox_load_csv = QComboBox()
        combobox_load_csv.setStyleSheet(StyleEnum.COMBOBOX)
        combobox_load_csv.addItems([csv for csv in os.listdir("data")])

        btn_load_csv = QPushButton(
            clicked=lambda: _on_btn_load_click(
                load_csv_widget,
                "data/" + combobox_load_csv.currentText()
            )
        )
        btn_load_csv.setText("Load")
        btn_load_csv.setStyleSheet(StyleEnum.BTN_LABEL_CHECKBOX)
        btn_load_csv.setMaximumWidth(200)

        hbox_load_csv.addWidget(label_load_csv, alignment=Qt.AlignCenter)
        hbox_load_csv.addWidget(combobox_load_csv)
        hbox_load_csv.addStretch()

        load_csv_widget_layout.addLayout(hbox_load_csv)
        load_csv_widget_layout.addWidget(btn_load_csv, alignment=Qt.AlignCenter)
        load_csv_widget_layout.addStretch()

        load_csv_widget.exec()

    def on_btn_save_tests_click(self):
        """Override test cases source by using the cases in the table"""

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

        with open(self.test_cases_path, 'w') as csv_file:

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
        Select/deselect all the currently visible tests. Applicable while searching
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
        """Run all/selected test cases in the table"""

        if not self.table_test_suite.rowCount():
            throw_message(MessageEnum.CRITICAL, "Run Error", "No available test case to run!")
            return

        self.reset_main_window(clear_tests=False, confirmation=False, clear_checkboxes=False)
        host = self.combobox_host.currentText()
        port = None if not self.port.text() else self.port.text()

        # Re-order the table
        for row in range(self.table_test_suite.rowCount()):
            if self.table_test_suite.item(row, 0).checkState() == Qt.Checked:
                self.table_test_suite.item(row, 0).setText("checked")

        self.table_test_suite.sortByColumn(1, Qt.AscendingOrder)
        self.table_test_suite.sortByColumn(0, Qt.DescendingOrder)

        for row in range(self.table_test_suite.rowCount()):
            if self.table_test_suite.item(row, 0).checkState() == Qt.Checked:
                self.table_test_suite.item(row, 0).setText("")

        self.label_passed_value.setStyleSheet(StyleEnum.STATS_PASSED)
        self.label_failed_value.setStyleSheet(StyleEnum.STATS_FAILURE)
        self.label_timed_out_value.setStyleSheet(StyleEnum.STATS_TIMEOUT)

        self.run_tests(self.get_checked_row_indexes(), host, port)

    def on_btn_compare_sources_click(self):
        """Open the comparison widget to choose a API source to compare"""

        def _on_btn_compare_click(widget, second_host, port_second_host):
            """
            Compare two API sources and lists only the test cases that
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

            self.reset_main_window(confirmation=False, clear_checkboxes=False)

            # Change the combobox on main window to indicate the host of second run
            self.combobox_host.setCurrentIndex(HOSTS.index(second_host))

            failed_tests_second_host = self.run_tests(
                tests_to_run,
                second_host,
                port_second_host,
                return_failed_tests=True
            )

            self.reset_main_window(confirmation=False, clear_checkboxes=False)

            failed_tests_main_host, failed_tests_second_host = (
                set(failed_tests_main_host) - set(failed_tests_second_host),
                set(failed_tests_second_host) - set(failed_tests_main_host)
            )

            for row_index in failed_tests_main_host:
                item_failed_output = QTableWidgetItem(f"Failed at {main_host}")
                self.table_test_suite.setItem(row_index, 4, item_failed_output)
                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.FAILURE)

            for row_index in failed_tests_second_host:
                item_failed_output = QTableWidgetItem(f"Failed at {second_host}")
                self.table_test_suite.setItem(row_index, 4, item_failed_output)
                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.FAILURE_SECOND_HOST)

            self.table_test_suite.resizeRowsToContents()

            if len(failed_tests_main_host) == 0 and len(failed_tests_second_host) == 0:
                throw_message(
                    MessageEnum.WARNING,
                    "Warning!",
                    "The sources are identical for the selected cases"
                )
                return

        if self.reset_main_window(clear_checkboxes=False) != MessageEnum.NO:

            main_host = self.combobox_host.currentText()

            comparison_widget = QDialog()
            comparison_widget.setStyleSheet(StyleEnum.UI)
            comparison_widget.setWindowTitle("Compare API Sources")
            comparison_widget_layout = QVBoxLayout(comparison_widget)

            # Layouts
            hbox_host_port = QHBoxLayout()

            # Labels
            label_instruction = QLabel(f"API Source to compare with {main_host}:")
            label_instruction.setStyleSheet(StyleEnum.INFO)

            # Buttons
            btn_run_comparison = QPushButton(
                clicked=lambda: _on_btn_compare_click(
                    comparison_widget,
                    combobox_second_host.currentText(),
                    port_second_host.text()
                )
            )
            btn_run_comparison.setText("Compare")
            btn_run_comparison.setStyleSheet(StyleEnum.BTN_LABEL_CHECKBOX)
            btn_run_comparison.setMaximumWidth(100)

            # Comboboxes
            combobox_second_host = QComboBox()
            combobox_second_host.setStyleSheet(StyleEnum.COMBOBOX)
            combobox_second_host.addItems([host for host in HOSTS if host != main_host])

            # Line Edits
            port_second_host = QLineEdit()
            port_second_host.setStyleSheet(StyleEnum.TABLE_LINE_EDIT)
            port_second_host.setMinimumWidth(100)
            port_second_host.setMaximumWidth(300)

            if combobox_second_host.currentText() == "Local Host":
                port_second_host.setText("8000")
            else:
                port_second_host.setText('')
                port_second_host.setPlaceholderText("Port")

            combobox_second_host.currentIndexChanged.connect(
                lambda: self.on_combobox_host_changed(combobox_second_host, port_second_host)
            )

            hbox_host_port.addWidget(combobox_second_host)
            hbox_host_port.addWidget(port_second_host)
            hbox_host_port.addStretch()

            comparison_widget_layout.addWidget(label_instruction)
            comparison_widget_layout.addLayout(hbox_host_port)
            comparison_widget_layout.addWidget(btn_run_comparison, alignment=Qt.AlignCenter)
            comparison_widget_layout.addStretch()

            comparison_widget.exec()

    def run_tests(self, tests_to_run, host, port, return_failed_tests=False):

        self.running = True
        num_tests_run = 0
        num_passed_tests = 0
        num_failed_tests = 0
        num_timed_out_tests = 0
        num_total_tests = len(tests_to_run)
        failed_tests = []

        self.progressbar.show()
        self.progressbar.setProperty("maximum", num_total_tests)

        self.label_passed_value.setText(f"{num_passed_tests}")

        teststat = TestStat(host, port)

        for row_index in tests_to_run:

            if self.stop:
                self.stop = False
                self.running = False
                break

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
                num_timed_out_tests += 1
                self.label_timed_out_value.setText(f"{num_timed_out_tests}")
                self.progressbar.setProperty("value", num_tests_run)

                timed_out_item = QTableWidgetItem("Error: Connection timed out!")
                self.table_test_suite.setItem(row_index, 4, timed_out_item)

                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.TIMEOUT)

                failed_tests.append(row_index)
                continue
            elif test_output == MessageEnum.CONNECTION_ERROR:
                throw_message(
                    MessageEnum.CRITICAL,
                    "Connection Error",
                    "Connection could not be established!"
                )
                self.reset_main_window(confirmation=False)
                return

            num_tests_run += 1
            self.progressbar.setProperty("value", num_tests_run)

            if not test_output:
                num_passed_tests += 1
                self.label_passed_value.setText(f"{num_passed_tests}")
                self.table_test_suite.setItem(row_index, 4, QTableWidgetItem(""))
                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.SUCCESS)
            else:
                num_failed_tests += 1
                self.label_failed_value.setText(f"{num_failed_tests}")
                failed_tests.append(row_index)
                failed_output = []
                for param, value in test_output.items():
                    failed_output.append(f"{param} = {value}")

                item_failed_output = QTableWidgetItem("\n".join(failed_output))
                self.table_test_suite.setItem(row_index, 4, item_failed_output)
                self.table_test_suite.resizeRowsToContents()
                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.FAILURE)

        self.running = False

        if return_failed_tests:
            return failed_tests

    def stop_tests(self):
        if self.running is True:
            self.stop = True
