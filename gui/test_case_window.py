from gui.utils import throw_message, MessageEnum, StyleEnum
from core.config import DATA_CALL_MAP, ParamsCommons

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, \
    QTableWidgetItem, QCheckBox, QLineEdit, QFormLayout, QVBoxLayout, QScrollArea


class TestCaseWindow(QWidget):

    def __init__(self, main_ui):
        """Construct test case window"""

        super().__init__()

        self.main_ui = main_ui

        self.setWindowTitle("TESTstat")
        self.resize(500, 400)
        self.setStyleSheet(StyleEnum.UI)

        # Keep track of items in each view
        self.items_in_previous_view = []
        self.input_names_in_previous_view = []

    def setup_ui(self):
        """Set test case window up"""

        # Layouts and containers
        top_layout = QHBoxLayout()
        middle_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        middle_right_layout = QVBoxLayout()
        middle_right_main_layout = QVBoxLayout()
        middle_left_layout = QVBoxLayout()
        middle_left_main_layout = QVBoxLayout()
        test_case_outer_layout = QVBoxLayout()

        self.form_layout_input = QFormLayout()
        self.form_layout_output = QFormLayout()

        hbox_data_call_container = QWidget()
        hbox_data_call = QHBoxLayout(hbox_data_call_container)
        hbox_data_call.setContentsMargins(0, 0, 0, 0)

        hbox_cancel_save_container = QWidget()
        hbox_cancel_save = QHBoxLayout(hbox_cancel_save_container)
        hbox_cancel_save.setContentsMargins(0, 0, 0, 0)

        scroll_area_input = QScrollArea()
        scroll_area_input_container = QWidget()
        scroll_area_input_container.setObjectName("scroll_area_input_container")

        scroll_area_output = QScrollArea()
        scroll_area_output_container = QWidget()
        scroll_area_output_container.setObjectName("scroll_area_output_container")

        # Labels
        label_data_call = QLabel("Data Call:")
        label_test_input = QLabel("Test Input:")
        label_exp_output = QLabel("Expected Output:")
        label_status_code = QLabel("Status Code:")

        # Buttons
        btn_cancel = QPushButton("Cancel", clicked=lambda: self.close())
        btn_save = QPushButton("Save", clicked=lambda: self.on_btn_save_click())

        # Comboboxes
        combobox_data_call = QComboBox()
        combobox_data_call.setStyleSheet(StyleEnum.COMBOBOX)
        combobox_data_call.addItems([specs["data_call_name"] for _, specs in DATA_CALL_MAP.items()])
        combobox_data_call.setMaxVisibleItems(15)
        combobox_data_call.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        combobox_data_call.currentIndexChanged.connect(
            lambda: self.on_combobox_data_call_changed(combobox_data_call.currentText())
        )

        # Line Edits
        self.status_code = QLineEdit()
        self.status_code.setStyleSheet(StyleEnum.TABLE_LINE_EDIT)
        self.status_code.setPlaceholderText("200")

        # Wrap the test case window UI up
        for item in [label_data_call, label_test_input, label_exp_output, btn_cancel, btn_save]:
            item.setStyleSheet(StyleEnum.BTN_LABEL_CHECKBOX)

        for item in [scroll_area_input, scroll_area_output]:
            item.setWidgetResizable(True)
            item.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            item.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_area_input_container.setLayout(self.form_layout_input)
        scroll_area_input_container.setMaximumWidth(600)
        scroll_area_input_container.setMinimumWidth(400)
        scroll_area_input.setWidget(scroll_area_input_container)
        scroll_area_input.setMinimumWidth(450)

        scroll_area_output_container.setLayout(self.form_layout_output)
        scroll_area_output_container.setMaximumWidth(600)
        scroll_area_output_container.setMinimumWidth(400)
        scroll_area_output.setWidget(scroll_area_output_container)
        scroll_area_output.setMinimumWidth(450)

        top_layout.addWidget(label_data_call)
        top_layout.addWidget(combobox_data_call)
        top_layout.addStretch()

        middle_left_layout.addWidget(label_test_input)
        middle_left_main_layout.addWidget(scroll_area_input)
        middle_left_layout.addLayout(middle_left_main_layout)

        middle_right_layout.addWidget(label_exp_output)
        middle_right_main_layout.addWidget(scroll_area_output)
        middle_right_layout.addLayout(middle_right_main_layout)

        middle_layout.addLayout(middle_left_layout, 2)
        middle_layout.addLayout(middle_right_layout, 3)
        middle_layout.insertStretch(1, 3)
        middle_layout.insertStretch(3, 2)

        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_cancel)
        bottom_layout.addWidget(btn_save)

        test_case_outer_layout.addLayout(top_layout)
        test_case_outer_layout.addSpacing(20)
        test_case_outer_layout.addLayout(middle_layout)
        test_case_outer_layout.addLayout(bottom_layout)
        self.setLayout(test_case_outer_layout)

        self.form_layout_output.addRow(label_status_code, self.status_code)

        # Populate the UI with initial fields
        self.on_combobox_data_call_changed(combobox_data_call.currentText())

    # Combobox slots
    def on_combobox_data_call_changed(self, data_call):
        """
        Populate the test case window UI according to data call selected.

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
                reference_to_input.setStyleSheet(StyleEnum.TABLE_LINE_EDIT)

                self.form_layout_input.addRow(reference_to_label, reference_to_input)

        def _populate_output_area(param_set, parent_label=None, parent_var=None):
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
                if isinstance(value, dict) and (
                    param in ParamsCommons.NESTED_PARAMS
                    or f"{parent_label}->{param}" in ParamsCommons.NESTED_PARAMS
                ):

                    label_identifier = f"{param}:" if not parent_label \
                        else f"{parent_label}->{param}:"
                    var_identifier = param if not parent_label \
                        else f"{parent_var}_{param}"

                    cb_label = f"checkbox_label_{var_identifier}"
                    cb_input_name = f"checkbox_input_{var_identifier}"

                    setattr(self, cb_label, QLabel(label_identifier))
                    reference_to_label = getattr(self, cb_label)
                    if not parent_label:
                        reference_to_label.setStyleSheet(StyleEnum.BOLD)
                    self.items_in_previous_view.append(reference_to_label)

                    setattr(self, cb_input_name, QCheckBox("Not Empty"))
                    reference_to_input = getattr(self, cb_input_name)
                    reference_to_input.setObjectName(cb_input_name)
                    self.input_names_in_previous_view.append(cb_input_name)
                    self.items_in_previous_view.append(reference_to_input)

                    reference_to_input.stateChanged.connect(lambda: self.on_checkbox_change())

                    self.form_layout_output.addRow(reference_to_label, reference_to_input)

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
                    self.input_names_in_previous_view.append(f"expected_input_{var}")
                    reference_to_input.setStyleSheet(StyleEnum.TABLE_LINE_EDIT)
                    self.form_layout_output.addRow(reference_to_label, reference_to_input)
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
            self.label_required_params.setStyleSheet(StyleEnum.BOLD)
            self.form_layout_input.addRow(self.label_required_params)
            self.items_in_previous_view.append(self.label_required_params)

        # Populate the input area with required parameters
        _populate_input_area("required_params")

        # If there is any optional parameter, put the label after required ones
        if DATA_CALL_MAP[self.data_call]["optional_params"]:
            self.label_optional_params = QLabel("Optional Parameters:")
            self.label_optional_params.setStyleSheet(StyleEnum.BOLD)
            self.form_layout_input.addRow(self.label_optional_params)
            self.items_in_previous_view.append(self.label_optional_params)

        # Populate the input area with optional parameters
        _populate_input_area("optional_params")

        # Populate the output area with output parameters
        _populate_output_area(DATA_CALL_MAP[self.data_call]["output_params"])

    # Button slots
    def on_btn_save_click(self):
        """Save the created test case into the table in the main window"""

        def _get_input_params(param_set):

            test_input = []

            for param in param_set:
                reference_to_input = getattr(self, f"test_input_{param}")
                if reference_to_input.text() != '':
                    trimmed_input = reference_to_input.text().replace(' ', '')
                    test_input.append(f"{param} = {trimmed_input}")

            return test_input

        def _get_output_params(param_set, output_params, parent_label=None, parent_var=None):

            for param, value in param_set.items():

                label = parent_label + "->" + param if parent_label else param
                var = parent_var + "_" + param if parent_var else param

                if label in ParamsCommons.NESTED_PARAMS:
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
                    output_params = _get_output_params(param_set[param], output_params, label, var)

            return output_params

        # Check all required inputs, add the case to the table if all are set
        for param in DATA_CALL_MAP[self.data_call]["required_params"]:
            reference_to_input = getattr(self, f"test_input_{param}")
            if reference_to_input.text() == '':
                throw_message(MessageEnum.CRITICAL, "Error", "Missing required parameters!")
                return

        # Create a new row in the table
        row_count = self.main_ui.table_test_suite.rowCount()
        self.main_ui.table_test_suite.setRowCount(row_count + 1)

        test_input = _get_input_params(
            DATA_CALL_MAP[self.data_call]["required_params"]
            + DATA_CALL_MAP[self.data_call]["optional_params"]
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
        item_checkbox = QTableWidgetItem(None)
        item_data_call = QTableWidgetItem(self.data_call)
        item_test_input = QTableWidgetItem(test_input)
        item_expected_output = QTableWidgetItem(expected_output)
        item_test_output = QTableWidgetItem('')

        item_checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item_checkbox.setCheckState(Qt.Unchecked)

        # Set table items
        self.main_ui.table_test_suite.setItem(row_count, 0, item_checkbox)
        self.main_ui.table_test_suite.setItem(row_count, 1, item_data_call)
        self.main_ui.table_test_suite.setItem(row_count, 2, item_test_input)
        self.main_ui.table_test_suite.setItem(row_count, 3, item_expected_output)
        self.main_ui.table_test_suite.setItem(row_count, 4, item_test_output)

        self.main_ui.table_test_suite.resizeRowsToContents()

        # Update test case count in the main window
        self.main_ui.label_total_value.setText(f"{self.main_ui.table_test_suite.rowCount()}")

        self.close()

    # Checkbox slots
    def on_checkbox_change(self):

        checkbox_names = [cb for cb in self.input_names_in_previous_view if "checkbox" in cb]

        for cb in checkbox_names:
            getattr(self, cb).clicked.connect(
                lambda state,
                checkbox=getattr(self, cb),
                all_inputs=self.input_names_in_previous_view:
                    self.execute_checkbox_changes(checkbox, all_inputs)
            )

    def execute_checkbox_changes(self, checkbox, all_input_fields):

        checkbox_name = checkbox.objectName()

        for input_name in all_input_fields:

            reference_to_input = getattr(self, input_name)

            if input_name.startswith(checkbox_name.replace("checkbox", "expected") + '_'):
                if getattr(self, checkbox_name).isChecked():
                    reference_to_input.setEnabled(False)
                    reference_to_input.setText('')
                    reference_to_input.setStyleSheet(StyleEnum.INPUT_DISABLED)
                else:
                    reference_to_input.setEnabled(True)
                    reference_to_input.setStyleSheet(StyleEnum.INPUT_ENABLED)
            elif input_name.startswith(checkbox_name + '_'):
                if getattr(self, checkbox_name).isChecked():
                    reference_to_input.setChecked(True)
                    reference_to_input.setEnabled(False)
                else:
                    reference_to_input.setEnabled(True)
                    reference_to_input.setChecked(False)
