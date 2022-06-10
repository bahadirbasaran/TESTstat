import requests

from core.config import *
from core.utils import filter_param_set, reshape_param_set
from gui.utils import throw_message


class TestStat():

    def __init__(self, host, port, with_tls=True):

        self.host = host

        protocol = "https" if with_tls else "http"

        if (host == "127.0.0.1" or 
                host.lower().replace(' ', '') == "localhost") and \
                    port.isdecimal():
            self.raw_query = f"http://127.0.0.1:{port}/data/"

        elif port is None:
            self.raw_query = f"{protocol}://{host}/data/"

        elif port.isdecimal():
            self.raw_query = f"{protocol}://{host}:{port}/data/"

        else:
            throw_message("critical", "Port Error", "Port cannot include characters!")

    
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

            if flag == TRIM_AS:
                if param_set[param].startswith('as'):
                    param_set[param] = param_set[param][2:]

            elif flag == NOT_EMPTY:
                return param_set[param] == "notempty" and output_value

            elif flag == INCLUDE:
                return all([p in output_value for p in param_set[param].split(',')])

            elif flag == INCLUDE_KEYS:
                return all([p in output_value.keys() for p in param_set[param].split(',')])

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
            
            for field in current_level:

                if not isinstance(current_level[field], dict):

                    field_flags = _get_inner_param_value(f"{current_identifier}->{field}", DATA_CALL_MAP[data_call]["output_params"])
                    field_flags = field_flags.copy()
                    criteria = field_flags.pop(0)

                    if "->" in current_identifier:
                        current_identifier = "->".join(current_identifier.split("->")[1:] + [field])
                        output_value = _get_inner_param_value(current_identifier, block)
                        expected = fields[current_identifier.split("->")[0]]
                    else:
                        output_value = _get_inner_param_value(field, block)
                        expected = fields

                    # Apply filters before ANY/ALL if there are such
                    while criteria not in [ANY, ALL]:
                        _apply_flag(criteria, expected, field, output_value)
                        criteria = param_flags.pop(0)

                    bools = [_apply_flag(flag, expected, field, output_value) for flag in field_flags]

                    if criteria == ANY:
                        resulting_bools.append(any(bools))
                    elif criteria == ALL:
                        resulting_bools.append(all(bools))

                else:
                    _check_current_level(current_level[field], f"{current_identifier}->{field}")

        failed_params = {}
        nested_params = {}

        if expected_output.pop("status_code") != str(test_output["status_code"]):
            failed_params["status_code"] = str(test_output["status_code"])
            failed_params[test_output["messages"][0][0]] = test_output["messages"][0][1].split("\n")[0]
            return failed_params

        # In some data call responses, 'data' is wrapped with 'results'
        if "results" in test_output["data"]:
            for key, value in test_output["data"]["results"].items():
                test_output["data"][key] = value
            del test_output["data"]["results"]
        
        # Make all items of test_output["data"] lower case,
        # trim whitespaces, and convert bools into strings
        test_output["data"] = filter_param_set(test_output["data"].copy())
        
        for param, value in expected_output.items():

            if param.split("->")[0] not in test_output["data"]:
                failed_params[param] = f"The response does not include this key!"
                continue

            if param.split("->")[0] in NESTED_PARAMS:
                nested_params[param] = value
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


        for nested_param, fields in reshape_param_set(nested_params).items():

            # If checkbox "Not Empty" is checked for a nested param,
            # check if the corresponding response list of the param is empty
            if fields == "notempty":
                if not test_output["data"][nested_param]:
                    failed_params[nested_param] = []
                continue
            
            is_match = False
            resulting_bools = []

            # Check if there is a block in test_output["data"][nested_param] that match with all fields of same nested_param
            for block in test_output["data"][nested_param]:
                
                # Jump to next block if current one dos not include all fields
                if not all(field in block for field in fields):
                    continue
                
                _check_current_level(fields, nested_param)

                if all(resulting_bools):
                    is_match = True
                    break
                else:
                    resulting_bools.clear()

            if not is_match:
                failed_params[nested_param] = "No item matching all the expected inputs found!"

        return failed_params


    def run_test(self, data_call, test_input, expected_output):

        try:
            request = f"{self.raw_query}{data_call}/data.json?{test_input}"
            print(request)
            response = requests.get(request, timeout=30)

        except requests.exceptions.ConnectionError:
            return f"Connection to {self.host} could not be established!"
        
        except (requests.exceptions.Timeout, requests.exceptions.JSONDecodeError) as e:
            return "timeout"

        test_result = self.evaluate_result(data_call, response.json(), expected_output)

        return test_result