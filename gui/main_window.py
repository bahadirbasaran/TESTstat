from cProfile import label
import csv

from gui.test_case_window import TestCaseWindow
from core.teststat import TestStat
from gui.utils import MessageEnum, ColorEnum, throw_message

from PyQt5.QtCore import Qt, QRect, QMetaObject
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QWidget, QGroupBox, QHBoxLayout, \
                            QLabel, QPushButton, QComboBox, QTableWidget, \
                            QTableWidgetItem, QProgressBar, QLineEdit, \
                            QApplication, QDialog, QToolButton


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


class MainWindow():

    def __init__(self):

        self.MainWindow = QMainWindow()
        self.MainWindow.setWindowTitle("TESTstat")
        self.MainWindow.resize(1280, 800)
        self.MainWindow.setStyleSheet("background-color: rgb(235, 236, 244); color: rgb(66, 77, 112);")
        self.centralwidget = QWidget(self.MainWindow)

        self.num_test_case = 0


    def setup_ui(self):
    
        self.groupbox_config = QGroupBox(self.centralwidget)
        self.groupbox_config.setGeometry(QRect(50, 44, 430, 130))
        #self.groupbox_config.setStyleSheet("background-color: rgb(235, 236, 244);")

        self.layoutWidget = QWidget(self.groupbox_config)
        self.layoutWidget.setGeometry(QRect(20, 20, 389, 32))

        self.horizontal_layout = QHBoxLayout(self.layoutWidget)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)

        self.label_host = QLabel(self.layoutWidget)
        self.label_host.setText("API Source:")
        self.label_host.setStyleSheet("font-weight: bold;")
        self.horizontal_layout.addWidget(self.label_host)

        self.btn_run = QPushButton(self.groupbox_config, clicked=lambda: self.on_btn_run_click())
        self.btn_run.setText("Run Tests")
        self.btn_run.setStyleSheet("font-weight: bold;")
        self.btn_run.setGeometry(QRect(20, 70, 111, 32))

        self.btn_compare = QPushButton(self.groupbox_config, clicked=lambda: self.on_btn_compare_click())
        self.btn_compare.setText("Compare")
        self.btn_compare.setStyleSheet("font-weight: bold;")
        self.btn_compare.setGeometry(QRect(144, 70, 111, 32))

        self.status = QLabel(self.groupbox_config)
        self.status.setGeometry(QRect(255, 70, 150, 32))
        self.status.setText(f"Tests: {self.num_test_case}")
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        self.status.setFont(font)
        self.status.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.combobox_host = QComboBox(self.layoutWidget)
        self.combobox_host.addItems(HOSTS)
        self.combobox_host.currentIndexChanged.connect(
            lambda:self.on_combobox_host_changed(self.combobox_host, self.port)
        )
        self.horizontal_layout.addWidget(self.combobox_host)

        self.port = QLineEdit(self.layoutWidget)
        self.port.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.port.setPlaceholderText("Port")
        self.port.setText("8000")
        self.horizontal_layout.addWidget(self.port)

        self.table_test_suite = QTableWidget(self.centralwidget)
        self.table_test_suite.setGeometry(QRect(50, 200, 1171, 470))
        self.table_test_suite.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.table_test_suite.setColumnCount(4)
        self.table_test_suite.setRowCount(0)
        self.table_test_suite.setColumnWidth(0, 200)
        self.table_test_suite.setColumnWidth(1, 322)
        self.table_test_suite.setColumnWidth(2, 322)
        self.table_test_suite.setColumnWidth(3, 322)

        for index, column_name in enumerate(["Data Call", "Test Input", "Expected Output", "Output"]):
            item = QTableWidgetItem(column_name)
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            item.setFont(font)
            self.table_test_suite.setHorizontalHeaderItem(index, item)

        self.btn_new_test = QPushButton(self.centralwidget, clicked=lambda: self.on_btn_new_test_click())
        self.btn_new_test.setText("New Test Case")
        self.btn_new_test.setGeometry(QRect(950, 700, 130, 32))
        self.btn_new_test.setStyleSheet("font-weight: bold;")

        self.btn_remove_test = QPushButton(self.centralwidget, clicked=lambda: self.on_btn_remove_test_click())
        self.btn_remove_test.setText("Remove Test Case")
        self.btn_remove_test.setGeometry(QRect(1090, 700, 130, 32))
        self.btn_remove_test.setStyleSheet("font-weight: bold;")

        self.btn_load_test = QPushButton(self.centralwidget, clicked=lambda: self.on_btn_load_test_click())
        self.btn_load_test.setText("Load Test Suite")
        self.btn_load_test.setGeometry(QRect(50, 700, 111, 32))
        self.btn_load_test.setStyleSheet("font-weight: bold;")

        self.btn_save_test = QPushButton(self.centralwidget, clicked=lambda: self.on_btn_save_test_click())
        self.btn_save_test.setText("Save Test Suite")
        self.btn_save_test.setGeometry(QRect(170, 700, 111, 32))
        self.btn_save_test.setStyleSheet("font-weight: bold;")

        self.progress_bar = QProgressBar(self.groupbox_config)
        self.progress_bar.setGeometry(QRect(20, 107, 390, 13))
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setOrientation(Qt.Horizontal)
        self.progress_bar.setInvertedAppearance(False)
        self.progress_bar.setTextDirection(QProgressBar.TopToBottom)
        self.progress_bar.hide()
        
        self.MainWindow.setCentralWidget(self.centralwidget)

        QMetaObject.connectSlotsByName(self.MainWindow)


    def show(self):

        self.MainWindow.show()


    def colorize_table_row(self, row_index, text_color, background_color):

        for col_index in range(self.table_test_suite.columnCount()):
            self.table_test_suite.item(row_index, col_index).setForeground(text_color)
            self.table_test_suite.item(row_index, col_index).setBackground(background_color)

    
    def reset_test_suite(self, confirmation=True):

         # Check if there is a result on the table remaining from a previous run
        if confirmation and '/' in self.status.text():
            ret_val = throw_message("warning", "Warning", "Are you sure you want to discard the test result?")
            if ret_val == MessageEnum.NO:
                return ret_val
            
        for row_index in range(self.table_test_suite.rowCount()):
            self.colorize_table_row(row_index, ColorEnum.UI_FONT, ColorEnum.WHITE)
            self.table_test_suite.item(row_index, self.table_test_suite.columnCount() - 1).setText('')
            # if self.table_test_suite.item(row_index, 0).checkState() == Qt.Checked:
            #     self.table_test_suite.item(row_index, 0).setCheckState(Qt.Unchecked)

        self.status.setText(f"Test cases: {self.num_test_case}")
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.hide()


    def get_checked_data_calls_indexes(self):

        checked_data_calls_indexes = []

        for row_index in range(self.table_test_suite.rowCount()):
            if self.table_test_suite.item(row_index, 0).checkState() == Qt.Checked:
                checked_data_calls_indexes.append(row_index)

        return checked_data_calls_indexes


    def on_combobox_host_changed(self, combobox, port):
        
        if combobox.currentText() == "Local Host":
            port.setText("8000")
        else:
            port.setText("")
            port.setPlaceholderText("Port")


    def on_btn_new_test_click(self):

        if ('/' in self.status.text() and 
                self.reset_test_suite() != MessageEnum.NO) or \
                    '/' not in self.status.text():
            self.test_case_ui = TestCaseWindow(self)
            self.test_case_ui.setup_ui()
            self.test_case_ui.show()


    def on_btn_remove_test_click(self):

        rows_to_remove = self.get_checked_data_calls_indexes()

        if not self.table_test_suite.rowCount():
            throw_message("critical", "Error", "There is no test case to remove!")
            return
        elif not rows_to_remove:
            throw_message("critical", "Error", "No test case selected!")
            return
        
        if self.reset_test_suite() != MessageEnum.NO:
            for row_index in reversed(rows_to_remove):
                self.table_test_suite.removeRow(row_index)
                self.num_test_case -= 1
                self.status.setText(f"Test cases: {self.num_test_case}")


    def on_btn_load_test_click(self):

        if self.table_test_suite.rowCount():
            ret_val = throw_message("warning", "Warning", "Are you sure you want to override the test suite?")
            if ret_val == MessageEnum.NO:
                return
            self.table_test_suite.clearContents()
            self.table_test_suite.setRowCount(0)
            self.num_test_case = 0
            self.status.setText(f"Test cases: {self.num_test_case}")

        self.progress_bar.hide()

        with open(TEST_CASES_PATH) as csv_file:
            if csv_file.readline().strip() != "data_call,test_input,expected_output":
                throw_message("critical", "Import Error", "The test suite is malformed!")
                return
            if len(csv_file.readlines()) < 1:
                throw_message("critical", "Import Error", "There is no available test case to load!")
                return
            
        with open(TEST_CASES_PATH) as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=',')

            next(csv_reader)

            for index, row in enumerate(csv_reader):
                self.table_test_suite.setRowCount(index + 1)

                item_data_call = QTableWidgetItem(row[0])
                item_test_input = QTableWidgetItem(row[1].replace(';', "\n").replace('&', ','))
                item_expected_output = QTableWidgetItem(row[2].replace(';', "\n").replace('&', ','))
                item_test_output = QTableWidgetItem("")

                item_data_call.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                item_data_call.setCheckState(Qt.Unchecked)
                
                self.table_test_suite.setItem(index, 0, item_data_call)
                self.table_test_suite.setItem(index, 1, item_test_input)
                self.table_test_suite.setItem(index, 2, item_expected_output)
                self.table_test_suite.setItem(index, 3, item_test_output)

                self.table_test_suite.resizeRowsToContents()

                self.num_test_case += 1
                self.status.setText(f"Test cases: {self.num_test_case}")


    def on_btn_save_test_click(self):

        if not self.table_test_suite.rowCount():
            throw_message("critical", "Save Error", "There is no available test case to save!")
            return

        rows_to_save = self.get_checked_data_calls_indexes()
        if not rows_to_save:
            rows_to_save = [row_index for row_index in range(self.table_test_suite.rowCount())]

        ret_val = throw_message("warning", "Warning", "Are you sure you want to override the test cases?")
        if ret_val == MessageEnum.NO:
            return

        with open(TEST_CASES_PATH, 'w') as csv_file:

            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow(["data_call", "test_input" , "expected_output"])

            for row_index in rows_to_save:
                data_call = self.table_test_suite.item(row_index, 0).text()
                test_input = self.table_test_suite.item(row_index, 1).text().replace("\n", ';').replace(',', '&')
                expected_output = self.table_test_suite.item(row_index, 2).text().replace("\n", ';').replace(',', '&')

                csv_writer.writerow([data_call, test_input, expected_output])
        

    def on_btn_run_click(self):

        if not self.table_test_suite.rowCount():
            throw_message("critical", "Run Error", "There is no available test case to run!")
            return

        tests_to_run = self.get_checked_data_calls_indexes()
        # If there is no test case selected, run all
        if not tests_to_run:
            tests_to_run = [row_index for row_index in range(self.table_test_suite.rowCount())]

        host = self.combobox_host.currentText()
        port = None if not self.port.text() else self.port.text()

        self.run_tests(tests_to_run, host, port)

    
    def run_tests(self, tests_to_run, host, port, return_failed_tests=False):

        num_passed_tests = 0
        num_tests_run = 0
        num_total_tests = len(tests_to_run)
        failed_tests = []

        self.progress_bar.show()
        self.progress_bar.setProperty("maximum", num_total_tests)
        self.status.setText(f"{num_passed_tests} / {num_total_tests} passed")

        teststat = TestStat(host, port)

        for row_index in tests_to_run:

            data_call = self.table_test_suite.item(row_index, 0).text()
            test_input = self.table_test_suite.item(row_index, 1).text().replace("\n", '&').replace(' ', '')
            
            expected_output = {}
            for param_value_pair in self.table_test_suite.item(row_index, 2).text().replace(' ', '').split("\n"):
                param, value = param_value_pair.split('=', 1)
                expected_output[param] = value

            print(f"Test Case {row_index+1} ({num_tests_run+1}/{num_total_tests}):", end=' ')

            test_output = teststat.run_test(data_call, test_input, expected_output)

            if isinstance(test_output, str):
                if test_output == "timeout":
                    timed_out_item = QTableWidgetItem("Error: Connection timed out!")
                    self.table_test_suite.setItem(row_index, 3, timed_out_item)
                    self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.TIMEOUT)
                    #throw_message("critical", f"Test Case {row_index+1}", f"Test Case {row_index+1} could not run because of time out!")
                    num_tests_run += 1
                    self.progress_bar.setProperty("value", num_tests_run)
                    failed_tests.append(row_index)
                    continue
                else:
                    throw_message("critical", "Connection Error", test_output)
                    self.status.setText(f"Test cases: {self.num_test_case}")
                    self.progress_bar.setProperty("value", 0)
                    self.progress_bar.hide()
                    return

            num_tests_run += 1
            self.progress_bar.setProperty("value", num_tests_run)

            if not test_output:
                num_passed_tests += 1
                self.status.setText(f"{num_passed_tests} / {num_total_tests} passed")

                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.SUCCESS)
            
            else:
                failed_tests.append(row_index)
                failed_output = []
                for param, value in test_output.items():
                    failed_output.append(f"{param} = {value}")

                item_failed_output = QTableWidgetItem("\n".join(failed_output))
                self.table_test_suite.setItem(row_index, 3, item_failed_output)

                self.table_test_suite.resizeRowsToContents()

                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.FAILURE)

            QApplication.processEvents()

        if return_failed_tests:
            return failed_tests


    def on_btn_compare_click(self):

        if self.reset_test_suite() != MessageEnum.NO:

            main_host = self.combobox_host.currentText()

            comparison_widget = QDialog()
            comparison_widget.setWindowTitle("Compare API Sources")
            
            label_instruction = QLabel(comparison_widget)
            label_instruction.setText(
                f"API Source to compare with {main_host}:"
            )
            label_instruction.setGeometry(QRect(20, 20, 350, 30))

            horizontal_layout = QHBoxLayout(comparison_widget)
            horizontal_layout.setContentsMargins(20, 60, 30, 100)

            label_second_host = QLabel()
            label_second_host.setText("API Source 2:")
            label_second_host.setStyleSheet("font-weight: bold;")


            combobox_second_host = QComboBox()
            hosts_but_main = [host for host in HOSTS if host != main_host]
            combobox_second_host.addItems(hosts_but_main)

            port_second_host = QLineEdit()
            port_second_host.setStyleSheet("background-color: rgb(255, 255, 255);")
            if combobox_second_host.currentText() == "Local Host":
                port_second_host.setText("8000")
            else:
                port_second_host.setText("")
                port_second_host.setPlaceholderText("Port")

            combobox_second_host.currentIndexChanged.connect(
                lambda: self.on_combobox_host_changed(
                    combobox_second_host, 
                    port_second_host
                )
            )

            horizontal_layout.addWidget(label_second_host)
            horizontal_layout.addWidget(combobox_second_host)
            horizontal_layout.addWidget(port_second_host)

            btn_run_comparison = QPushButton(
                comparison_widget, 
                clicked=lambda: self.on_btn_run_comparison_click(
                    comparison_widget,
                    combobox_second_host.currentText(),
                    port_second_host.text()
                )
            )
            btn_run_comparison.setText("Compare")
            btn_run_comparison.setStyleSheet("font-weight: bold;")
            # Temporary solution. This will be auto-arranged placement
            btn_run_comparison.setGeometry(QRect(155, 110, 111, 32))

            comparison_widget.exec()


    def on_btn_run_comparison_click(self, widget, second_host, port_second_host):

        widget.close()

        if not self.table_test_suite.rowCount():
            throw_message("critical", "Run Error", "There is no available test case to run!")
            return

        tests_to_run = self.get_checked_data_calls_indexes()
        # If there is no test case selected, run all
        if not tests_to_run:
            tests_to_run = [row_index for row_index in range(self.table_test_suite.rowCount())]

        main_host = self.combobox_host.currentText()
        port_main_host = None if not self.port.text() else self.port.text()
        port_second_host = None if not port_second_host else port_second_host

        failed_tests_main_host = self.run_tests(
            tests_to_run, 
            main_host, 
            port_main_host,
            return_failed_tests=True
        )

        self.reset_test_suite(confirmation=False)

        self.combobox_host.setCurrentIndex(HOSTS.index(second_host))

        failed_tests_second_host = self.run_tests(
            tests_to_run, 
            second_host, 
            port_second_host,
            return_failed_tests=True
        )

        self.reset_test_suite(confirmation=False)

        failed_tests_main_host, failed_tests_second_host = (
            set(failed_tests_main_host) - set(failed_tests_second_host),
            set(failed_tests_second_host) - set(failed_tests_main_host)
        )

        for row_index in failed_tests_main_host:
            item_failed_output = QTableWidgetItem(f"Failed at {main_host}")
            self.table_test_suite.setItem(row_index, 3, item_failed_output)

            self.table_test_suite.resizeRowsToContents()

            self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.FAILURE)

            QApplication.processEvents()

        for row_index in failed_tests_second_host:
            item_failed_output = QTableWidgetItem(f"Failed at {second_host}")
            self.table_test_suite.setItem(row_index, 3, item_failed_output)

            self.table_test_suite.resizeRowsToContents()

            self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.FAILURE_SECOND_HOST)

            QApplication.processEvents()

