import csv

from gui.test_case_window import TestCaseWindow
from core.teststat import TestStat
from gui.utils import MessageEnum, ColorEnum, throw_message

from PyQt5.QtCore import Qt, QRect, QMetaObject
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QWidget, QGroupBox, QHBoxLayout, \
                            QLabel, QPushButton, QComboBox, QTableWidget, \
                            QTableWidgetItem, QProgressBar, QLineEdit, QApplication


TEST_CASES_PATH = "data/test_cases.csv"


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

        self.layoutWidget = QWidget(self.groupbox_config)
        self.layoutWidget.setGeometry(QRect(20, 20, 389, 32))

        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.label_host = QLabel(self.layoutWidget)
        self.label_host.setText("API Source:")
        self.label_host.setStyleSheet("font-weight: bold;")
        self.horizontalLayout.addWidget(self.label_host)

        self.btn_run = QPushButton(self.groupbox_config, clicked=lambda: self.on_btn_run_click())
        self.btn_run.setText("Run Tests")
        self.btn_run.setStyleSheet("font-weight: bold;")
        self.btn_run.setGeometry(QRect(20, 70, 111, 32))

        self.status = QLabel(self.groupbox_config)
        self.status.setGeometry(QRect(240, 70, 161, 32))
        self.status.setText(f"Test cases: {self.num_test_case}")
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        self.status.setFont(font)
        self.status.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.combobox_host = QComboBox(self.layoutWidget)
        self.combobox_host.addItems([
            "Localhost",
            "stat.ripe.net",
            "dev001.stat.ripe.net",
            "dev002.stat.ripe.net",
            "dev003.stat.ripe.net",
            "dev004.stat.ripe.net",
            "dev005.stat.ripe.net",
            "dev006.stat.ripe.net",
            "dev007.stat.ripe.net",
            "dev008.stat.ripe.net"
        ])
        self.combobox_host.currentIndexChanged.connect(
            self.on_combobox_host_changed,
            self.combobox_host.currentIndex()
        )
        self.horizontalLayout.addWidget(self.combobox_host)

        self.port = QLineEdit(self.layoutWidget)
        self.port.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.port.setPlaceholderText("Port (8000)")
        self.horizontalLayout.addWidget(self.port)

        self.table_test_suite = QTableWidget(self.centralwidget)
        self.table_test_suite.setGeometry(QRect(50, 200, 1171, 470))
        self.table_test_suite.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.table_test_suite.setColumnCount(4)
        self.table_test_suite.setRowCount(0)
        self.table_test_suite.setColumnWidth(0, 190)
        self.table_test_suite.setColumnWidth(1, 315)
        self.table_test_suite.setColumnWidth(2, 315)
        self.table_test_suite.setColumnWidth(3, 315)

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

    
    def reset_test_suite(self):

         # Check if there is a result on the table remaining from a previous run
        if '/' in self.status.text():
            ret_val = throw_message("warning", "Warning", "Are you sure you want to discard the test result?")
            if ret_val == MessageEnum.NO:
                return ret_val
            
            for row_index in range(self.table_test_suite.rowCount()):
                self.colorize_table_row(row_index, ColorEnum.UI_FONT, ColorEnum.WHITE)
                self.table_test_suite.item(row_index, self.table_test_suite.columnCount() - 1).setText('')

            self.status.setText(f"Test cases: {self.num_test_case}")
            self.progress_bar.setProperty("value", 0)
            self.progress_bar.hide()


    def get_checked_data_calls_indexes(self):

        checked_data_calls_indexes = []

        for row_index in range(self.table_test_suite.rowCount()):
            if self.table_test_suite.item(row_index, 0).checkState() == Qt.Checked:
                checked_data_calls_indexes.append(row_index)

        return checked_data_calls_indexes


    def on_combobox_host_changed(self, combobox_index):
        
        if combobox_index != 0:
            self.port.setDisabled(True)
            self.port.setPlaceholderText("")
            self.port.setStyleSheet("background-color: rgb(225, 226, 232);")
        else:
            self.port.setDisabled(False)
            self.port.setPlaceholderText("Port (8000)")
            self.port.setStyleSheet("background-color: rgb(255, 255, 255);")


    def on_btn_new_test_click(self):

        if self.reset_test_suite() != MessageEnum.NO:
            self.test_case_ui = TestCaseWindow(self)
            self.test_case_ui.setup_ui()
            self.test_case_ui.show()


    def on_btn_remove_test_click(self):

        rows_to_remove = self.get_checked_data_calls_indexes()

        if not rows_to_remove:
            throw_message("critical", "Error", "No test case selected!")
            return

        self.reset_test_suite()
        
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

                item_data_call.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                item_data_call.setCheckState(Qt.Unchecked)
                
                self.table_test_suite.setItem(index, 0, item_data_call)
                self.table_test_suite.setItem(index, 1, item_test_input)
                self.table_test_suite.setItem(index, 2, item_expected_output)

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

        rows_to_run = self.get_checked_data_calls_indexes()
        if not rows_to_run:
            rows_to_run = [row_index for row_index in range(self.table_test_suite.rowCount())]

        num_passed_tests = 0
        num_tests_run = 0
        num_total_tests = len(rows_to_run)
        host = self.combobox_host.currentText()

        self.progress_bar.show()
        self.progress_bar.setProperty("maximum", num_total_tests)
        self.status.setText(f"{num_passed_tests} / {num_total_tests} passed")

        if host == "Localhost":
            port = "8000" if not self.port.text() else self.port.text()

            if not port.isdecimal():
                throw_message("critical", "Port Error", "Port cannot include any characters!")
                return

            teststat = TestStat("localhost", port)

        else:
            teststat = TestStat(host)

        for row_index in rows_to_run:

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
                    empty_item = QTableWidgetItem("error: connection timed out!")
                    self.table_test_suite.setItem(row_index, 3, empty_item)
                    self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.TIMEOUT)
                    throw_message("critical", f"Test Case {row_index+1}", f"Test Case {row_index+1} could not run because of time out!")
                    num_tests_run += 1
                    self.progress_bar.setProperty("value", num_tests_run)
                    continue
                else:
                    throw_message("critical", "Connection Error", test_output)
                    return

            num_tests_run += 1
            self.progress_bar.setProperty("value", num_tests_run)

            if not test_output:
                num_passed_tests += 1
                self.status.setText(f"{num_passed_tests} / {num_total_tests} passed")

                empty_item = QTableWidgetItem("")
                self.table_test_suite.setItem(row_index, 3, empty_item)

                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.SUCCESS)
            
            else:
                failed_output = []
                for param, value in test_output.items():
                    failed_output.append(f"{param} = {value}")

                failed_output = "\n".join(failed_output)
                item_failed_output = QTableWidgetItem(failed_output)
                self.table_test_suite.setItem(row_index, 3, item_failed_output)

                self.table_test_suite.resizeRowsToContents()

                self.colorize_table_row(row_index, ColorEnum.BLACK, ColorEnum.FAILURE)

            QApplication.processEvents()