from gui.utils import throw_message, MessageEnum
from core.config import DATA_CALL_MAP, NESTED_PARAMS

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, \
                            QLabel, QComboBox, QTableWidgetItem, QCheckBox, \
                            QLineEdit, QFormLayout, QScrollArea


class TestCaseWindow():

    def __init__(self, main_ui):

        self.main_ui = main_ui

        self.test_case_window = QMainWindow()
        self.test_case_window.setWindowTitle("New Test Case")
        self.test_case_window.resize(900, 512)
        self.test_case_window.setStyleSheet((
            "background-color: rgb(235, 236, 244);"
            "color: rgb(66, 77, 112);"
        ))

        # Keep track of items in each view
        self.items_in_previous_view, self.input_names_in_previous_view = [], []

    def setup_ui(self):
        """Sets test case window up"""

        # Containers

        central_widget = QWidget(self.test_case_window)
        self.test_case_window.setCentralWidget(central_widget)

        layout_widget = QWidget(central_widget)
        layout_widget.setGeometry(QRect(614, 450, 216, 32))

        hbox_data_call_container = QWidget(central_widget)
        hbox_data_call_container.setGeometry(QRect(50, 25, 320, 40))
        hbox_data_call = QHBoxLayout(hbox_data_call_container)
        hbox_data_call.setContentsMargins(0, 0, 0, 0)

        hbox_cancel_save_container = QWidget(central_widget)
        hbox_cancel_save_container.setGeometry(QRect(600, 425, 250, 40))
        hbox_cancel_save = QHBoxLayout(hbox_cancel_save_container)
        hbox_cancel_save.setContentsMargins(0, 0, 0, 0)

        scroll_area_input_container = QWidget()
        scroll_area_input_container.setObjectName(
            "scroll_area_input_container"
        )
        scroll_area_input = QScrollArea(central_widget)
        scroll_area_input.setWidgetResizable(True)
        scroll_area_input.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area_input.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area_input.setGeometry(QRect(50, 110, 370, 310))

        scroll_area_output_container = QWidget()
        scroll_area_output_container.setObjectName(
            "scroll_area_output_container"
        )
        scroll_area_output = QScrollArea(central_widget)
        scroll_area_output.setWidgetResizable(True)
        scroll_area_output.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area_output.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area_output.setGeometry(QRect(480, 110, 370, 310))

        self.form_layout_input = QFormLayout()
        self.form_layout_output = QFormLayout()

        # Labels

        label_test_input = QLabel(central_widget)
        label_test_input.setGeometry(QRect(50, 80, 68, 16))
        label_test_input.setStyleSheet("font-weight: bold;")
        label_test_input.setText("Test Input:")

        label_expected_output = QLabel(central_widget)
        label_expected_output.setGeometry(QRect(480, 80, 112, 16))
        label_expected_output.setStyleSheet("font-weight: bold;")
        label_expected_output.setText("Expected Output:")

        label_status_code = QLabel("Status Code:")

        # Buttons

        btn_cancel_new_test = QPushButton(
            layout_widget,
            clicked=lambda: self.test_case_window.close()
        )
        btn_cancel_new_test.setStyleSheet("font-weight: bold;")
        btn_cancel_new_test.setText("Cancel")

        btn_save_new_test = QPushButton(
            layout_widget,
            clicked=lambda: self.on_btn_save_new_test_click()
        )
        btn_save_new_test.setStyleSheet("font-weight: bold;")
        btn_save_new_test.setText("Save")

        self.label_data_call = QLabel()
        self.label_data_call.setStyleSheet("font-weight: bold;")
        self.label_data_call.setText("Data Call:")

        # Comboboxes

        combobox_data_call = QComboBox()
        combobox_data_call.setStyleSheet("QComboBox { combobox-popup: 0; }")
        combobox_data_call.setMaxVisibleItems(15)
        combobox_data_call.view().setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )
        combobox_data_call.addItems(
            [specs["data_call_name"] for _, specs in DATA_CALL_MAP.items()]
        )
        combobox_data_call.currentIndexChanged.connect(
            lambda: self.on_combobox_data_call_changed(
                combobox_data_call.currentText()
            )
        )

        # Line Edits

        self.status_code = QLineEdit()
        self.status_code.setGeometry(QRect(150, 10, 125, 21))
        self.status_code.setStyleSheet("background-color: rgb(255,255,255);")
        self.status_code.setPlaceholderText("200")

        # Set the test case window UI up

        hbox_cancel_save.addWidget(btn_cancel_new_test)
        hbox_cancel_save.addWidget(btn_save_new_test)
        hbox_data_call.addWidget(self.label_data_call)
        hbox_data_call.addWidget(combobox_data_call)

        scroll_area_input_container.setLayout(self.form_layout_input)
        scroll_area_output_container.setLayout(self.form_layout_output)
        scroll_area_input.setWidget(scroll_area_input_container)
        scroll_area_output.setWidget(scroll_area_output_container)

        self.form_layout_output.addRow(label_status_code, self.status_code)

        # Manually populate the UI with initial fields
        self.on_combobox_data_call_changed(combobox_data_call.currentText())

        self.test_case_window.show()

    # Combobox slots

    def on_combobox_data_call_changed(self, data_call):
        """
        Populates the test case window UI according to data call selected.

        Since the UI is populated based on core/config.py instead of static
        definition, input items are created/accessed using referencing.
        Because of the same reason, variables "items_in_previous_view" and
        "input_names_in_previous_view" are used to keep track of objects.
        """

        def _populate_input_area(param_set):

            for param in DATA_CALL_MAP[self.data_call][param_set]:
                setattr(self, f"test_label_{param}", QLabel(f"{param}:"))
                reference_to_label = getattr(self, f"test_label_{param}")
                self.items_in_previous_view.append(reference_to_label)

                setattr(self, f"test_input_{param}", QLineEdit())
                reference_to_input = getattr(self, f"test_input_{param}")
                reference_to_input.setObjectName(f"test_input_{param}")
                self.items_in_previous_view.append(reference_to_input)
                reference_to_input.setStyleSheet(
                    "background-color: rgb(255,255,255);"
                )
                self.form_layout_input.addRow(
                    reference_to_label,
                    reference_to_input
                )

        def _populate_output_area(
            param_set,
            parent_label=None,
            parent_var=None
        ):
            """
            There are 3 possible scenarios for a parameter in DATA_CALL_MAP:
                1) It carries a list of conditional flags used while testing:
                    e.g. "abuse_contacts" in "abuse-contact-finder"
                2) It carries a dictionary of parameter(s) those carry either
                    lists of conditional flags, or dictionary to recur:
                    e.g. "stripped" in "as-path-length" or
                    "parameters" in "abuse-contact-finder"
                3) It carries a nested parameter. Those params can include same
                    set of keys multiple times with different values.
                    e.g. "exact" in "address-space-hierarchy"

            Each parameter has an input field. Nested parameters also have a
            checkbox beside regular input fields. The first block below creates
            a checkbox for nested parameters first, then fields are created.
            """

            for param, value in param_set.items():

                # Create first a checkbox "Not Empty" for nested parameters
                if isinstance(value, dict) and \
                    (param in NESTED_PARAMS or
                        f"{parent_label}->{param}" in NESTED_PARAMS):

                    label_identifier = f"{param}:" if not parent_label \
                        else f"{parent_label}->{param}:"
                    var_identifier = param if not parent_label \
                        else f"{parent_var}_{param}"

                    cb_label = f"checkbox_label_{var_identifier}"
                    cb_input_name = f"checkbox_input_{var_identifier}"

                    setattr(self, cb_label, QLabel(label_identifier))
                    reference_to_label = getattr(self, cb_label)
                    if not parent_label:
                        reference_to_label.setStyleSheet("font-weight: bold;")
                    self.items_in_previous_view.append(reference_to_label)

                    setattr(self, cb_input_name, QCheckBox("Not Empty"))
                    reference_to_input = getattr(self, cb_input_name)
                    reference_to_input.setObjectName(cb_input_name)
                    self.input_names_in_previous_view.append(cb_input_name)
                    self.items_in_previous_view.append(reference_to_input)

                    reference_to_input.clicked.connect(
                        lambda: self.on_checkbox_change()
                    )

                    self.form_layout_output.addRow(
                        reference_to_label,
                        reference_to_input
                    )

                # Regular label-input fields creation

                label = parent_label + "->" + param if parent_label else param
                var = parent_var + "_" + param if parent_var else param

                # Scenario 1
                if isinstance(value, list):
                    setattr(self, f"expected_label_{var}", QLabel(f"{label}:"))
                    reference_to_label = getattr(self, f"expected_label_{var}")
                    self.items_in_previous_view.append(reference_to_label)

                    setattr(self, f"expected_input_{var}", QLineEdit())
                    reference_to_input = getattr(self, f"expected_input_{var}")
                    reference_to_input.setObjectName(f"expected_input_{var}")
                    self.items_in_previous_view.append(reference_to_input)
                    self.input_names_in_previous_view.append(
                        f"expected_input_{var}"
                    )
                    reference_to_input.setStyleSheet(
                        "background-color: rgb(255,255,255);"
                    )
                    self.form_layout_output.addRow(
                        reference_to_label,
                        reference_to_input
                    )
                # Scenario 2
                else:
                    _populate_output_area(param_set[param], label, var)

        # e.g. data call name in combobox: Abuse Contact Finder
        # convert it to abuse-contact-finder to seek it in DATA_CALL_MAP
        self.data_call = data_call.replace(' ', '-').lower()

        # Clear the remaining items from previous view if any
        while self.items_in_previous_view:
            item_to_del = self.items_in_previous_view.pop()
            item_to_del.deleteLater()
        self.input_names_in_previous_view.clear()

        # If there is no optional parameter defined for a data call, skip the
        # "Required Parameters:" label to make it more simple
        if DATA_CALL_MAP[self.data_call]["optional_params"]:
            self.label_required_params = QLabel("Required Parameters:")
            self.label_required_params.setStyleSheet("font-weight: bold;")
            self.form_layout_input.addRow(self.label_required_params)
            self.items_in_previous_view.append(self.label_required_params)

        # Populate the input area with required parameters
        _populate_input_area("required_params")

        # If there is any optional parameter, put the label after required ones
        if DATA_CALL_MAP[self.data_call]["optional_params"]:
            self.label_optional_params = QLabel("Optional Parameters:")
            self.label_optional_params.setStyleSheet("font-weight: bold;")
            self.form_layout_input.addRow(self.label_optional_params)
            self.items_in_previous_view.append(self.label_optional_params)

        # Populate the input area with optional parameters
        _populate_input_area("optional_params")

        # Populate the output area with output parameters
        _populate_output_area(DATA_CALL_MAP[self.data_call]["output_params"])

    # Button slots

    def on_btn_save_new_test_click(self):
        """Saves the created test case into the table in the main window"""

        def _get_input_params(param_set):

            test_input = []

            for param in param_set:
                reference_to_input = getattr(self, f"test_input_{param}")
                if reference_to_input.text() != '':
                    trimmed_input = reference_to_input.text().replace(' ', '')
                    test_input.append(f"{param} = {trimmed_input}")

            return test_input

        def _get_output_params(
            param_set,
            output_params,
            parent_label=None,
            parent_var=None
        ):
            for param, value in param_set.items():

                label = parent_label + "->" + param if parent_label else param
                var = parent_var + "_" + param if parent_var else param

                if label in NESTED_PARAMS:
                    if getattr(self, f"checkbox_input_{var}").isChecked():
                        output_params.append(f"{label} = not empty")

                if isinstance(value, list):
                    reference_to_input = getattr(self, f"expected_input_{var}")

                    if reference_to_input.text() != '':
                        input = reference_to_input.text()
                        trimmed_input = input.replace(' ', '')
                        trimmed_input = trimmed_input.lower()

                        if trimmed_input == "notempty":
                            output_params.append(f"{label} = not empty")
                        elif trimmed_input == "null":
                            output_params.append(f"{label} = none")
                        else:
                            output_params.append(f"{label} = {trimmed_input}")

                # Scenario 2 described in the function _populate_output_area
                else:
                    output_params = _get_output_params(
                        param_set[param],
                        output_params,
                        label,
                        var
                    )

            return output_params

        # Check all required inputs, add the case to the table if all are set
        for param in DATA_CALL_MAP[self.data_call]["required_params"]:
            reference_to_input = getattr(self, f"test_input_{param}")
            if reference_to_input.text() == '':
                throw_message(
                    MessageEnum.CRITICAL,
                    "Error",
                    "Missing required parameters!"
                )
                return

        # Create a new row in the table
        row_count = self.main_ui.table_test_suite.rowCount()
        self.main_ui.table_test_suite.setRowCount(row_count + 1)

        test_input = _get_input_params(
            DATA_CALL_MAP[self.data_call]["required_params"] +
            DATA_CALL_MAP[self.data_call]["optional_params"]
        )

        # If user does not type an input for status code, it is 200 by default
        if self.status_code.text() == '':
            params = ["status_code = 200"]
        else:
            status_code = self.status_code.text().replace(' ', '')
            params = [f"status_code = {status_code}"]

        expected_output = _get_output_params(
            DATA_CALL_MAP[self.data_call]["output_params"],
            params
        )

        test_input = "\n".join(test_input)
        expected_output = "\n".join(expected_output)

        # Create table items
        item_data_call = QTableWidgetItem(self.data_call)
        item_test_input = QTableWidgetItem(test_input)
        item_expected_output = QTableWidgetItem(expected_output)
        item_test_output = QTableWidgetItem("")

        item_data_call.setFlags(
            Qt.ItemIsUserCheckable |
            Qt.ItemIsEnabled |
            Qt.ItemIsEditable
        )
        item_data_call.setCheckState(Qt.Unchecked)

        # Set table items
        self.main_ui.table_test_suite.setItem(row_count, 0, item_data_call)
        self.main_ui.table_test_suite.setItem(row_count, 1, item_test_input)
        self.main_ui.table_test_suite.setItem(
            row_count,
            2,
            item_expected_output
        )
        self.main_ui.table_test_suite.setItem(row_count, 3, item_test_output)

        self.main_ui.table_test_suite.resizeRowsToContents()

        # Update test case count in the main window
        self.main_ui.label_status.setText(
            f"Tests: {self.main_ui.table_test_suite.rowCount()}"
        )

        self.test_case_window.close()

    # Checkbox slots

    def on_checkbox_change(self):

        checkbox_names = [
            cb for cb in self.input_names_in_previous_view if "checkbox" in cb
        ]

        for checkbox_name in checkbox_names:

            for input_name in self.input_names_in_previous_view:

                reference_to_input = getattr(self, input_name)

                if input_name.startswith(
                    checkbox_name.replace("checkbox", "expected") + '_'
                ):

                    if getattr(self, checkbox_name).isChecked():
                        reference_to_input.setEnabled(False)
                        reference_to_input.setText('')
                        reference_to_input.setStyleSheet(
                            "background-color: rgb(225, 226, 232);"
                        )
                    else:
                        reference_to_input.setEnabled(True)
                        reference_to_input.setStyleSheet(
                            "background-color: rgb(255, 255, 255);"
                        )
                elif input_name.startswith(checkbox_name + '_'):
                    if getattr(self, checkbox_name).isChecked():
                        reference_to_input.setChecked(True)


