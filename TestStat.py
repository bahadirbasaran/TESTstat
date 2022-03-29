import requests

from test_suite import *
from utils import *


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
            elif isinstance(output_value, int) or isinstance(output_value, float):
                output_value = str(output_value)
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

            elif flag == COMPARE:
                if ">=" in param_set[param]:
                    expected_value = float(param_set[param].split(">=")[1])
                    if float(output_value) >= expected_value:
                        return True

                elif ">" in param_set[param]:
                    expected_value = float(param_set[param].split(">")[1])
                    if float(output_value) > expected_value:
                        return True

                elif "<=" in param_set[param]:
                    expected_value = float(param_set[param].split("<=")[1])
                    if float(output_value) <= expected_value:
                        return True

                elif "<" in param_set[param]:
                    expected_value = float(param_set[param].split("<")[1])
                    if float(output_value) < expected_value:
                        return True

            return False


        def _check_current_level(current_level, current_identifier):
            #current_identifier = "exact" - "stats->stripped"
            
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
        verbose_params = {}
        
        for param, value in expected_output.items():

            if param == "status_code":
                if expected_output["status_code"] != str(test_output["status_code"]):
                    failed_params["status_code"] = str(test_output["status_code"])
                    failed_params[test_output["messages"][0][0]] = test_output["messages"][0][1].split("\n")[0]
                    return failed_params
                continue

            if param.split("->")[0] in VERBOSE_PARAMS:
                verbose_params[param] = value
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

  
        for verbose_param, fields in reshape_param_set(verbose_params).items():

            # If checkbox "Not Empty" is checked for a verbose param,
            # check if the corresponding response list of the param is empty
            if fields == "notempty":
                if not test_output["data"][verbose_param]:
                    failed_params[verbose_param] = []
                continue
            
            is_match = False
            resulting_bools = []

            # Check if there is a block in test_output["data"][verbose_param] that match with all fields of same verbose_param
            for block in test_output["data"][verbose_param]:
                
                # Jump to next block if current one does not include all fields
                if not all(field in block for field in fields):
                    continue
                
                _check_current_level(fields, verbose_param)

                if all(resulting_bools):
                    is_match = True
                    break
                else:
                    resulting_bools.clear()

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