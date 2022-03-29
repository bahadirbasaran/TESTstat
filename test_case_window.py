import sys

from utils import throw_message
from test_suite import DATA_CALL_MAP, VERBOSE_PARAMS

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TestCaseWindow(object):

    def __init__(self, main_ui):

        self.main_ui = main_ui
        
        self.TestCaseWindow = QtWidgets.QMainWindow()
        self.TestCaseWindow.setWindowTitle("New Test Case")
        self.TestCaseWindow.resize(900, 512)
        self.TestCaseWindow.setStyleSheet("background-color: rgb(235, 236, 244); color: rgb(66, 77, 112);")

        self.centralwidget = QtWidgets.QWidget(self.TestCaseWindow)
        self.TestCaseWindow.setCentralWidget(self.centralwidget)

        # self.menubar = QtWidgets.QMenuBar(self.TestCaseWindow)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 24))
        # self.TestCaseWindow.setMenuBar(self.menubar)

        # self.statusbar = QtWidgets.QStatusBar(self.TestCaseWindow)
        # self.TestCaseWindow.setStatusBar(self.statusbar)

        self.items_in_previous_view = []
        self.input_names_in_previous_view = []


    def setupUi(self):

        self.label_test_input = QtWidgets.QLabel(self.centralwidget)
        self.label_test_input.setGeometry(QtCore.QRect(50, 80, 68, 16))
        self.label_test_input.setStyleSheet("font-weight: bold;")
        self.label_test_input.setText("Test Input:")

        self.label_expected_output = QtWidgets.QLabel(self.centralwidget)
        self.label_expected_output.setGeometry(QtCore.QRect(480, 80, 112, 16))
        self.label_expected_output.setStyleSheet("font-weight: bold;")
        self.label_expected_output.setText("Expected Output:")

        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(614, 450, 216, 32))
        
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)

        self.btn_cancel_new_test = QtWidgets.QPushButton(
            self.layoutWidget,
            clicked=lambda: self.TestCaseWindow.close()
        )
        self.btn_cancel_new_test.setStyleSheet("font-weight: bold;")
        self.btn_cancel_new_test.setText("Cancel")
        self.horizontalLayout_2.addWidget(self.btn_cancel_new_test)

        self.btn_save_new_test = QtWidgets.QPushButton(
            self.layoutWidget,
            clicked=lambda: self.on_btn_save_new_test_click()
        )
        self.btn_save_new_test.setStyleSheet("font-weight: bold;")
        self.btn_save_new_test.setText("Save")
        self.horizontalLayout_2.addWidget(self.btn_save_new_test)

        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(50, 30, 249, 28))

        self.formLayout_data_call = QtWidgets.QFormLayout(self.layoutWidget1)
        self.formLayout_data_call.setContentsMargins(0, 0, 0, 0)

        self.label_data_call = QtWidgets.QLabel(self.layoutWidget1)
        self.label_data_call.setStyleSheet("font-weight: bold;")
        self.label_data_call.setText("Data Call:")

        self.combobox_data_call = QtWidgets.QComboBox(self.layoutWidget1)
        self.combobox_data_call.addItems([specs["data_call_name"] for _, specs in DATA_CALL_MAP.items()])
        self.combobox_data_call.currentIndexChanged.connect(
            self.on_combobox_data_call_changed
        )

        self.formLayout_data_call.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_data_call)
        self.formLayout_data_call.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.combobox_data_call)

        self.input_scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.input_scrollArea.setWidgetResizable(True)
        self.input_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.input_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.input_scrollArea.setGeometry(QtCore.QRect(50, 110, 350, 310))
        self.input_scrollAreaWidgetContents = QtWidgets.QWidget()
        # self.input_scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 348, 308))
        self.input_scrollAreaWidgetContents.setObjectName("input_scrollAreaWidgetContents")

        self.output_scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.output_scrollArea.setWidgetResizable(True)
        self.output_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.output_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.output_scrollArea.setGeometry(QtCore.QRect(480, 110, 350, 310))
        self.output_scrollAreaWidgetContents = QtWidgets.QWidget()
        # self.output_scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 348, 308))

        self.input_formLayout = QtWidgets.QFormLayout()
        self.output_formLayout = QtWidgets.QFormLayout()
        # self.label_spacer = self.row_spacer = QtWidgets.QSpacerItem(150, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self.label_status_code = QtWidgets.QLabel("Status Code:")
        self.status_code = QtWidgets.QLineEdit()
        self.status_code.setGeometry(QtCore.QRect(150, 10, 125, 21))
        self.status_code.setStyleSheet("background-color: rgb(255,255,255);")
        self.status_code.setPlaceholderText("200")
        self.output_formLayout.addRow(self.label_status_code, self.status_code)

        self.on_combobox_data_call_changed()

        self.input_scrollAreaWidgetContents.setLayout(self.input_formLayout)
        self.output_scrollAreaWidgetContents.setLayout(self.output_formLayout)

        self.input_scrollArea.setWidget(self.input_scrollAreaWidgetContents)
        self.output_scrollArea.setWidget(self.output_scrollAreaWidgetContents)       

        QtCore.QMetaObject.connectSlotsByName(self.TestCaseWindow)


    def show(self):
        self.TestCaseWindow.show()


    def on_checkbox_change(self):

        checkbox_names = [item for item in self.input_names_in_previous_view if "checkbox" in item]

        for checkbox_name in checkbox_names:

            for input_name in self.input_names_in_previous_view:

                if input_name.startswith(checkbox_name.replace("checkbox", "expected")):

                    reference_to_input = getattr(self, input_name)
                    
                    if getattr(self, checkbox_name).isChecked():
                        reference_to_input.setEnabled(False)
                        reference_to_input.setStyleSheet("background-color: rgb(225, 226, 232);")
                    else:
                        reference_to_input.setEnabled(True)
                        reference_to_input.setStyleSheet("background-color: rgb(255, 255, 255);")


    def on_combobox_data_call_changed(self):

        def _populate_input_area(param_set):

            for param in DATA_CALL_MAP[self.data_call][param_set]:
                setattr(self, f"test_label_{param}", QtWidgets.QLabel(f"{param}:"))
                reference_to_label = getattr(self, f"test_label_{param}")
                self.items_in_previous_view.append(reference_to_label)

                setattr(self, f"test_input_{param}", QtWidgets.QLineEdit())
                reference_to_input = getattr(self, f"test_input_{param}")
                reference_to_input.setObjectName(f"test_input_{param}")
                self.items_in_previous_view.append(reference_to_input)
                reference_to_input.setStyleSheet("background-color: rgb(255,255,255);")

                self.input_formLayout.addRow(reference_to_label, reference_to_input)

        def _populate_output_area(param_set, parent_label=None, parent_var=None):

            for param, value in param_set.items():
                
                if param in VERBOSE_PARAMS and isinstance(value, dict):
                    setattr(self, f"checkbox_label_{param}", QtWidgets.QLabel(f"{param}:"))
                    reference_to_label = getattr(self, f"checkbox_label_{param}")
                    self.items_in_previous_view.append(reference_to_label)

                    setattr(self, f"checkbox_input_{param}", QtWidgets.QCheckBox("Not Empty"))
                    reference_to_input = getattr(self, f"checkbox_input_{param}")
                    reference_to_input.setObjectName(f"checkbox_input_{param}")
                    reference_to_input.toggled.connect(lambda: self.on_checkbox_change())
                    self.items_in_previous_view.append(reference_to_input)
                    self.input_names_in_previous_view.append(f"checkbox_input_{param}")

                    self.output_formLayout.addRow(reference_to_label, reference_to_input)

                label = parent_label + "->" + param if parent_label else param
                var = parent_var + "_" + param if parent_var else param

                if isinstance(value, list):
                    setattr(self, f"expected_label_{var}", QtWidgets.QLabel(f"{label}:"))
                    reference_to_label = getattr(self, f"expected_label_{var}")
                    self.items_in_previous_view.append(reference_to_label)

                    setattr(self, f"expected_input_{var}", QtWidgets.QLineEdit())
                    reference_to_input = getattr(self, f"expected_input_{var}")
                    reference_to_input.setObjectName(f"expected_input_{var}")
                    self.items_in_previous_view.append(reference_to_input)
                    self.input_names_in_previous_view.append(f"expected_input_{var}")
                    reference_to_input.setStyleSheet("background-color: rgb(255,255,255);")

                    self.output_formLayout.addRow(reference_to_label, reference_to_input)

                else:
                    _populate_output_area(param_set[param], label, var)


        self.data_call = self.combobox_data_call.currentText().replace(' ', '-').lower()

        while self.items_in_previous_view:
            item_to_del = self.items_in_previous_view.pop()
            item_to_del.deleteLater()

        self.input_names_in_previous_view.clear()

        if DATA_CALL_MAP[self.data_call]["optional_params"]:
            self.label_required_params = QtWidgets.QLabel("Required Parameters:")
            self.label_required_params.setStyleSheet("font-weight: bold;")
            self.input_formLayout.addRow(self.label_required_params)
            self.items_in_previous_view.append(self.label_required_params)

        _populate_input_area("required_params")

        if DATA_CALL_MAP[self.data_call]["optional_params"]:
            self.label_optional_params = QtWidgets.QLabel("Optional Parameters:")
            self.label_optional_params.setStyleSheet("font-weight: bold;")
            self.input_formLayout.addRow(self.label_optional_params)
            self.items_in_previous_view.append(self.label_optional_params)

        _populate_input_area("optional_params")

        _populate_output_area(DATA_CALL_MAP[self.data_call]["output_params"])


    def on_btn_save_new_test_click(self):

        def _get_input_params(param_set):

            test_input = []

            for param in param_set:
                reference_to_input = getattr(self, f"test_input_{param}")
                
                if reference_to_input.text() != '':
                    test_input.append(f"{param}: {reference_to_input.text().lower().replace(' ', '')}")

            return test_input

        def _get_output_params(param_set, output_params, parent_label=None, parent_var=None):
            
            for param, value in param_set.items():

                label = parent_label + "->" + param if parent_label else param
                var = parent_var + "_" + param if parent_var else param

                if isinstance(value, list):
                    reference_to_input = getattr(self, f"expected_input_{var}")

                    if reference_to_input.text() != '':
                        if reference_to_input.text().lower() == "not empty":
                            output_params.append(f"{label}: {reference_to_input.text().lower()}")
                        else:
                            output_params.append(f"{label}: {reference_to_input.text().lower().replace(' ', '')}")
                
                else:
                    if param in VERBOSE_PARAMS and getattr(self, f"checkbox_input_{param}").isChecked():
                        output_params.append(f"{param}: not empty")
                        continue
                    output_params = _get_output_params(param_set[param], output_params, label, var)

            return output_params


        # Check all required inputs, add new test case to the test suite if all set
        for param in DATA_CALL_MAP[self.data_call]["required_params"]:
            reference_to_input = getattr(self, f"test_input_{param}")
            if reference_to_input.text() == '':
                throw_message("critical", "Error", "Missing required parameters!")
                return

        row_count = self.main_ui.table_test_suite.rowCount()
        self.main_ui.table_test_suite.setRowCount(row_count + 1)

        test_input = _get_input_params(
            DATA_CALL_MAP[self.data_call]["required_params"] +
            DATA_CALL_MAP[self.data_call]["optional_params"]
        )

        expected_output = _get_output_params(
            DATA_CALL_MAP[self.data_call]["output_params"],
            ["status_code: 200" if self.status_code.text() == '' else f"status_code: {self.status_code.text().lower().replace(' ', '')}"]
        )

        test_input = "\n".join(test_input)
        expected_output = "\n".join(expected_output)

        item_data_call = QtWidgets.QTableWidgetItem(self.data_call)
        item_test_input = QtWidgets.QTableWidgetItem(test_input)
        item_expected_output = QtWidgets.QTableWidgetItem(expected_output)

        item_data_call.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        item_data_call.setCheckState(QtCore.Qt.Unchecked)

        self.main_ui.table_test_suite.setItem(row_count, 0, item_data_call)
        self.main_ui.table_test_suite.setItem(row_count, 1, item_test_input)
        self.main_ui.table_test_suite.setItem(row_count, 2, item_expected_output)

        self.main_ui.table_test_suite.resizeRowsToContents()

        self.main_ui.num_test_case += 1
        self.main_ui.status.setText(f"Test cases: {self.main_ui.num_test_case}")

        self.TestCaseWindow.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")    

    ui = Ui_TestCaseWindow()
    ui.setupUi()
    ui.show()
    
    sys.exit(app.exec_())
