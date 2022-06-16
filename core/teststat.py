import requests

from core.utils import filter_param_set, reshape_param_set, get_innermost_value
from gui.utils import throw_message, MessageEnum

# Import conditional flags
from core.config import ALL, ANY, COMPARE, INCLUDE, INCLUDE_KEYS, \
                        MATCH, NOT_EMPTY, TRIM_AS

# Import parameter related definitions
from core.config import DATA_CALL_MAP, NESTED_PARAMS


class TestStat():

    def __init__(self, host, port, with_tls=True):

        protocol = "https" if with_tls else "http"
        host = host.lower().replace(' ', '')

        if (host == "127.0.0.1" or host == "localhost") and port.isdecimal():
            self.raw_query = f"http://127.0.0.1:{port}/data/"

        elif port is None:
            self.raw_query = f"{protocol}://{host}/data/"

        elif port.isdecimal():
            self.raw_query = f"{protocol}://{host}:{port}/data/"

        else:
            throw_message(
                MessageEnum.CRITICAL,
                "Port Error",
                "Port cannot include characters!"
            )

    def run_test(self, data_call, test_input, expected_output):

        try:
            request = f"{self.raw_query}{data_call}/data.json?{test_input}"
            response = requests.get(request, timeout=30)

        except requests.exceptions.ConnectionError:
            return MessageEnum.CONNECTION_ERROR

        except requests.exceptions.Timeout:
            return MessageEnum.TIMEOUT

        test_result = self.evaluate_result(
            data_call,
            response.json(),
            expected_output
        )

        return test_result

    def evaluate_result(self, data_call, test_output, expected_output):
        """
        Evaluates test result by comparing expected_output with test_output
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
                return all(
                    [val in output_value
                        for val in param_set[param].split(',')]
                )

            elif flag == INCLUDE_KEYS:
                return all(
                    [val in output_value.keys()
                        for val in param_set[param].split(',')]
                )

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
            Checks if all block fields match with the comparison criteria
            from top to bottom node, level by level and populates the list
            resulting_bools with evaluation results.
            """

            for field in current_level:

                if not isinstance(current_level[field], dict):

                    field_flags = get_innermost_value(
                        f"{current_identifier}->{field}",
                        DATA_CALL_MAP[data_call]["output_params"]
                    )
                    field_flags = field_flags.copy()
                    criteria = field_flags.pop(0)

                    if "->" in current_identifier:
                        current_identifier = "->".join(
                            current_identifier.split("->")[1:] + [field]
                        )
                        output_value = get_innermost_value(
                            current_identifier,
                            block
                        )
                        expected = fields[current_identifier.split("->")[0]]
                    else:
                        output_value = get_innermost_value(field, block)
                        expected = fields

                    # Apply filters before ANY/ALL if there are such
                    while criteria not in [ANY, ALL]:
                        _apply_flag(criteria, expected, field, output_value)
                        criteria = param_flags.pop(0)

                    bools = [
                        _apply_flag(flag, expected, field, output_value)
                        for flag in field_flags
                    ]

                    if criteria == ANY:
                        resulting_bools.append(any(bools))
                    elif criteria == ALL:
                        resulting_bools.append(all(bools))
                else:
                    _check_current_level(
                        current_level[field],
                        f"{current_identifier}->{field}"
                    )

        failed_params = {}

        # Nested parameters should be treated differently
        nested_params = {}

        # If status code is different than 200, directly return error message
        expected_status_code = expected_output.pop("status_code")
        if expected_status_code != str(test_output["status_code"]):
            failed_params["status_code"] = str(test_output["status_code"])
            error_type, error_message = test_output["messages"][0]
            failed_params[error_type] = error_message.split("\n")[0]
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
            param_flags = get_innermost_value(
                param,
                DATA_CALL_MAP[data_call]["output_params"]
            )
            param_flags = param_flags.copy()
            criteria = param_flags.pop(0)

            # Apply filters before ANY/ALL if there are such
            while criteria not in [ANY, ALL]:
                _apply_flag(
                    criteria,
                    expected_output,
                    param,
                    test_output_value
                )
                criteria = param_flags.pop(0)

            resulting_bools = [
                _apply_flag(flag, expected_output, param, test_output_value)
                for flag in param_flags
            ]

            if (criteria == ANY and any(resulting_bools)) or \
                    (criteria == ALL and all(resulting_bools)):
                continue

            failed_params[param] = test_output_value

        # After dealing with all regular parameters, nested parameters are
        # evaluated below.
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
                # all those block fields match with the comparison criteria.
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
                failed_params[nested_param] = (
                    "No item matching all"
                    "the expected inputs found!"
                )

        return failed_params
