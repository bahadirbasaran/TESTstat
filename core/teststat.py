import requests

from core.utils import MessageEnum, filter_param_set, reshape_param_set, get_innermost_value

# Import conditional flags
from core.config import ALL, ANY, COMPARE, INCLUDE, INCLUDE_KEYS, MATCH, NOT_EMPTY, TRIM_AS

# Import parameter related definitions
from core.config import DATA_CALL_MAP, NESTED_PARAMS


class TestStat():

    def __init__(self, host, port=None, with_tls=True, cicd=False):

        # gui/utils.py imports PyQt5 package underneath. This is an unnecessary
        # load for CI/CD tasks, because there is no need to install PyQt5 each
        # time for running all the test cases without the GUI.
        if not cicd:
            from gui.utils import throw_message

        protocol = "https" if with_tls else "http"
        host = host.lower().replace(' ', '')

        if (host == "127.0.0.1" or host == "localhost") and port.isdecimal():
            self.raw_query = f"http://127.0.0.1:{port}/data/"

        elif port is None:
            self.raw_query = f"{protocol}://{host}/data/"

        elif port.isdecimal():
            self.raw_query = f"{protocol}://{host}:{port}/data/"

        else:
            throw_message(MessageEnum.CRITICAL, "Port Error", "Port cannot include characters!")

    def run_test(self, data_call, test_input, expected_output):

        try:
            request = f"{self.raw_query}{data_call}/data.json?{test_input}"

            print(request)

            response = requests.get(request, timeout=30)

        except requests.exceptions.ConnectionError:
            return MessageEnum.CONNECTION_ERROR

        except requests.exceptions.Timeout:
            return MessageEnum.TIMEOUT

        test_result = self.evaluate_result(data_call, response.json(), expected_output)

        return test_result

    def evaluate_result(self, data_call, test_output, expected_output):
        """
        Evaluate test result by comparing expected_output with test_output
        for given data_call. Returns:
            {}  -> test is successful
            int -> test could not be executed (connection error, timeout)
            {param: val} -> test output that does not match with expected
        """

        def _apply_flag(flag, param_set, param, output_value):
            """
            Returns True if expected value (param_set[param]) is compatible
            with output_value based on given flag. Otherwise returns False.
            """

            if flag == TRIM_AS:
                if param_set[param].startswith('as'):
                    param_set[param] = param_set[param][2:]

            elif flag == NOT_EMPTY:
                return param_set[param] == "notempty" and output_value

            elif flag == INCLUDE:
                return all([val in output_value for val in param_set[param].split(',')])

            elif flag == INCLUDE_KEYS:
                return all([val in output_value.keys() for val in param_set[param].split(',')])

            elif flag == MATCH:
                return param_set[param] == output_value

            elif flag == COMPARE:
                if ">=" in param_set[param]:
                    expected_value = float(param_set[param].split(">=")[1])
                    return float(output_value) >= expected_value

                elif ">" in param_set[param]:
                    expected_value = float(param_set[param].split(">")[1])
                    return float(output_value) > expected_value

                elif "<=" in param_set[param]:
                    expected_value = float(param_set[param].split("<=")[1])
                    return float(output_value) <= expected_value

                elif "<" in param_set[param]:
                    expected_value = float(param_set[param].split("<")[1])
                    return float(output_value) < expected_value

        def _check_current_level(current_level, current_identifier):
            """
            Check if all block fields match with the comparison rule
            from top to bottom node, level by level and populates the list
            resulting_bools with evaluation results.
            """

            for field in current_level:

                if not isinstance(current_level[field], dict):

                    # Get the output value from the data call response block
                    if "->" in current_identifier:
                        current_identifier_short = "->".join(
                            current_identifier.split("->")[1:] + [field]
                        )
                        output_value = get_innermost_value(current_identifier_short, block)
                    else:
                        output_value = get_innermost_value(field, block)

                    # Checking for the "notempty" flag or the output and
                    # expected parameters "notempty" could be applied to a
                    # nested parameter, such as "prefix->timelines". In this
                    # case the output_value is a list. Alternatively, notempty
                    # could be applied to a non-nested parameter. In this case
                    # the output_value is a string to satisfy the possibilities
                    # above, the length of the output_value is checked.
                    if current_level[field] == "notempty":
                        if len(output_value) > 0:
                            resulting_bools.append(True)
                        else:
                            resulting_bools.append(False)
                    else:
                        field_flags = get_innermost_value(
                            f"{current_identifier}->{field}",
                            DATA_CALL_MAP[data_call]["output_params"]
                        )
                        field_flags = field_flags.copy()

                        rule = field_flags.pop(0)

                        if "->" in current_identifier:
                            expected = fields[current_identifier_short.split("->")[0]]
                        else:
                            expected = fields

                        # Apply filters before ANY/ALL if there are such
                        while rule not in [ANY, ALL]:
                            _apply_flag(rule, expected, field, output_value)
                            rule = param_flags.pop(0)

                        bools = [
                            _apply_flag(flag, expected, field, output_value) for flag in field_flags
                        ]

                        if rule == ANY:
                            resulting_bools.append(any(bools))
                        elif rule == ALL:
                            resulting_bools.append(all(bools))

                        if not all(resulting_bools):
                            break
                else:
                    _check_current_level(current_level[field], f"{current_identifier}->{field}")

        failed_params = {}

        # Nested parameters should be treated differently
        nested_params = {}

        # If status code is different than 200, directly return error message
        expected_status_code = expected_output.pop("status_code")
        if expected_status_code == "200":
            if expected_status_code != str(test_output["status_code"]):
                failed_params["status_code"] = str(test_output["status_code"])
                error_type, error_message = test_output["messages"][0]
                failed_params[error_type] = error_message.split("\n")[0]
                return failed_params
        else:
            if expected_status_code != str(test_output["status_code"]):
                failed_params["status_code"] = str(test_output["status_code"])
                if len(test_output["messages"]) > 0:
                    error_type, error_message = test_output["messages"][0]
                    failed_params[error_type] = error_message.split("\n")[0]
                else:
                    failed_params["error"] = "Status code is 200 and differes from the expected."
                return failed_params

        # In some data call responses, 'data' is wrapped with 'results' key.
        # Extract this key if in such case.
        if "results" in test_output["data"]:
            for key, value in test_output["data"]["results"].items():
                test_output["data"][key] = value

            del test_output["data"]["results"]

        # Make all items of test_output["data"] lower case, trim whitespaces
        # and convert bools&numbers into string representations.
        test_output["data"] = filter_param_set(test_output["data"].copy())

        for param, value in expected_output.items():

            if param.split("->")[0] not in test_output["data"]:
                failed_params[param] = "The output does not include this key!"
                continue

            # Seperate nested parameters from regular parameters
            if param.split("->")[0] in NESTED_PARAMS:
                nested_params[param] = value
                continue

            test_output_value = get_innermost_value(param, test_output["data"])
            param_flags = get_innermost_value(param, DATA_CALL_MAP[data_call]["output_params"])
            param_flags = param_flags.copy()
            rule = param_flags.pop(0)

            # Apply filters before ANY/ALL if there are such
            while rule not in [ANY, ALL]:
                _apply_flag(rule, expected_output, param, test_output_value)
                rule = param_flags.pop(0)

            resulting_bools = [
                _apply_flag(flag, expected_output, param, test_output_value) for flag in param_flags
            ]

            if (rule == ANY and any(resulting_bools)) or (rule == ALL and all(resulting_bools)):
                continue

            failed_params[param] = test_output_value

        # After dealing with all regular parameters, nested parameters are
        # evaluated below. The following evaluation is based on the highest
        # nested parameter in the hierarchy.
        # Example: prefixes->timelines->startdate the nested param is prefixes
        for nested_param, fields in reshape_param_set(nested_params).items():

            # If a checkbox "Not Empty" is checked for a nested parameter,
            # check if the corresponding response list of parameter is empty
            if fields == "notempty":
                if not test_output["data"][nested_param]:
                    failed_params[nested_param] = []
                continue

            is_match = False
            resulting_bools = []

            # Check if there is a block in test_output["data"][nested_param]
            # that match with all fields of the same nested_param (expected)
            for block in test_output["data"][nested_param]:

                # Jump to next block if current one does not include all fields
                if not all([field in block for field in fields]):
                    continue

                # At this point, current block includes all the fields in the
                # corresponding fields of the nested parameter. Then, check if
                # all those block fields match with the comparison rule.
                # The function below populates the list resulting_bools.
                _check_current_level(fields, nested_param)

                # If resulting_bools is consist of True bools only, this means
                # we have a match, therefore the test case is successful.
                if all(resulting_bools):
                    is_match = True
                    break
                else:
                    resulting_bools.clear()

            if not is_match:
                failed_params[nested_param] = "No item matching all the expected inputs found!"

        return failed_params
