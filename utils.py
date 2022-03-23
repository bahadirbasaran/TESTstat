from tabnanny import check
import requests

from PyQt5 import QtWidgets, QtGui

from test_suite import *


TEST_CASES_PATH = "test_cases.csv"


class MESSAGE_ENUM():
    NO = 65536
    YES = 16384

class COLOR_ENUM():
    FAILURE = QtGui.QColor("#FFB8B8")
    SUCCESS = QtGui.QColor("#D4FCD7")
    TIMEOUT = QtGui.QColor("F5B445")
    BLACK = QtGui.QColor("#000000")
    WHITE = QtGui.QColor("#FFFFFF")
    UI_FONT = QtGui.QColor("#424D70")

class TestStat():

    def __init__(self, api_source, port=8000):

        self.api_source = api_source
        self.query = f"https://127.0.0.1:{port}/data/" if api_source == "localhost" else f"https://{api_source}/data/"

    
    def evaluate_result(self, data_call, test_output, expected_output):

        def _get_inner_param_value(param, param_set):

            if "->" in param:
                for index, inner_param in enumerate(param.split("->")):
                    if index == 0:
                        inner_param_value = param_set[inner_param]
                    else:
                        inner_param_value = inner_param_value[inner_param]
            else:
                inner_param_value = param_set[param]

            return inner_param_value

        def _apply_flag(flag, param_set, param, output_value):

            if isinstance(output_value, str):
                output_value = output_value.lower().replace(' ', '')
            elif isinstance(output_value, list):
                output_value = [val.lower().replace(' ', '') for val in output_value]

            if flag == TRIM_AS:
                if param_set[param].startswith('as'):
                    param_set[param] = param_set[param][2:]
                return

            elif flag == NOT_EMPTY:
                if param_set[param] == "notempty" and output_value:
                    return True
                

            elif flag == INCLUDE:
                if all([p in output_value for p in param_set[param].split(',')]):
                    return True

            elif flag == MATCH:
                if param_set[param] == output_value:
                    return True

            elif flag == QUANTITATIVE:
                if ">=" in param_set[param]:
                    expected_value = float(param_set[param].split(">=")[1])
                    if float(test_output_value) >= expected_value:
                        return True

                elif ">" in param_set[param]:
                    expected_value = float(param_set[param].split(">")[1])
                    if float(test_output_value) > expected_value:
                        return True

                elif "<=" in param_set[param]:
                    expected_value = float(param_set[param].split("<=")[1])
                    if float(test_output_value) <= expected_value:
                        return True

                elif "<" in param_set[param]:
                    expected_value = float(param_set[param].split("<")[1])
                    if float(test_output_value) < expected_value:
                        return True

            return False


        failed_params = {}
        verbose_param_set = {}
        
        for param in expected_output:

            if param == "status_code":
                if expected_output["status_code"] != str(test_output["status_code"]):
                    failed_params["status_code"] = str(test_output["status_code"])
                    failed_params[test_output["messages"][0][0]] = test_output["messages"][0][1].split("\n")[0]
                    return failed_params
                continue
                
            if param.split("->")[0] in VERBOSE_PARAMS:

                if "->" in param:
                
                    if param.split("->")[0] not in verbose_param_set:
                        verbose_param_set.update({
                            param.split("->")[0]: {
                                param.split("->")[1]: expected_output[param]
                            }
                        })
                    else:
                        verbose_param_set[param.split("->")[0]].update({
                            param.split("->")[1]: expected_output[param]
                        })

                else:
                    verbose_param_set[param] = "notempty"
                    
                continue

            test_output_value = _get_inner_param_value(param, test_output["data"])
            param_flags = _get_inner_param_value(param, DATA_CALL_MAP[data_call]["output_params"])

            param_flags = param_flags.copy()
            criteria = param_flags.pop(0)

            # Apply filters before ANY/ALL if there are such
            while criteria not in [ANY, ALL]:
                _apply_flag(criteria, expected_output, param, test_output_value)
                criteria = param_flags.pop(0)

            if criteria == ANY and \
                any([_apply_flag(flag, expected_output, param, test_output_value) for flag in param_flags]):
                continue
            elif criteria == ALL and \
                all([_apply_flag(flag, expected_output, param, test_output_value) for flag in param_flags]):
                continue

            failed_params[param] = test_output_value


        for verbose_param, fields in verbose_param_set.items():
            # e.g.  exact         ->  {'inetnum': '1', 'netname': '2'}
            #       more_specific ->  {'inetnum': '3', 'org': '4'}

            # If checkbox "Not Empty" is checked for a verbose param,
            # check if the corresponding response list of the param is empty
            if fields == "notempty":
                if not test_output["data"][verbose_param]:
                    failed_params[verbose_param] = []
                continue
            
            is_match = False
            check_results = []

            # Check if there is a block in test_output["data"][verbose_param] that match with all fields of same verbose_param
            for block in test_output["data"][verbose_param]:
                
                # Jump to next block if current one does not include all fields
                if not all(field in block for field in fields):
                    continue

                for field in fields:
                    field_flags = _get_inner_param_value(f"{verbose_param}->{field}", DATA_CALL_MAP[data_call]["output_params"])

                    field_flags = field_flags.copy()
                    criteria = field_flags.pop(0)

                    # Apply filters before ANY/ALL if there are such
                    while criteria not in [ANY, ALL]:
                        _apply_flag(criteria, expected_output, param, test_output_value)
                        criteria = param_flags.pop(0)

                    if criteria == ANY:
                        check_results.append(
                            any([_apply_flag(flag=flag, param_set=fields, param=field, output_value=block[field]) for flag in field_flags])
                        )
                    elif criteria == ALL:
                        check_results.append(
                            all([_apply_flag(flag=flag, param_set=fields, param=field, output_value=block[field]) for flag in field_flags])
                        )

                if all(check_results):
                    is_match = True
                    break

            if not is_match:
                failed_params[verbose_param] = "No item matching all the expected inputs found!"

        return failed_params


    def run_test(self, data_call, test_input, expected_output):

        try:
            response = requests.get(f"{self.query}{data_call}/data.json?{test_input}")

        except requests.exceptions.ConnectionError:
            return f"Connection to {self.api_source} could not be established!"
        
        except requests.exceptions.Timeout:
            return "Connection timed out!"

        test_result = self.evaluate_result(data_call, response.json(), expected_output)

        return test_result


# Utility functions

def throw_message(type, title, message):

    msg = QtWidgets.QMessageBox()

    msg.setText(message)
    msg.setWindowTitle(title)

    if type == "critical":
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    elif type == "warning":
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
    
    ret_val = msg.exec_()

    return ret_val