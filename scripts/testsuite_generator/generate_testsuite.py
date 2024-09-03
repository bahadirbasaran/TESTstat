# The following script aims to create a test suite to be used in TESTstat
# There are three optional parameters for this script:
# 1. --dc: creates test suite only for given datacall(s)
# 2. --output: sets the output filename
# 3. --mode: Expected status code for test cases

# This script creates different combinations of required and optional
# parameters based on the config_autogeneration_params.py.
# The created tests are ordered alphabetically and written to the output file.


import argparse
import itertools
from datetime import datetime

from config_testsuite_param_values import *  # noqa: F403
from config_testsuite_params import resource_params, optional_params, param_names_conversion


class Value:
    def __init__(self, name, value, status):
        self.name = name
        self.value = value
        self.status = status


class Datacall:
    def __init__(self, name, required_parameters, optional_params, vars):        
        self.name = name
        self.required_parameters = self.create_list_of_parameters(required_parameters, vars)
        self.all_required_values = self.parse_parameters(self.required_parameters)
        self.required_params_combinations = self.create_combinations(self.required_parameters, len(self.required_parameters))
        self.optional_parameters = self.create_list_of_parameters(optional_params, vars)
        self.all_optional_values = self.parse_parameters(self.optional_parameters)
        self.optional_params_combinations = self.create_combinations(self.optional_parameters,  range(1, len(self.optional_parameters)+1)) if len(self.optional_parameters) > 0 else []

    def create_list_of_parameter_names(self, dc_param_values, vars):
        if len(dc_param_values) == 0:
            parameters_names = []
        elif sum(isinstance(i, list) for i in dc_param_values) > 1:
            parameters_names = [param_names_conversion[i[0]] if i[0] in param_names_conversion.keys() else i[0] for i in dc_param_values]
        elif dc_param_values[0] not in resource_universe:
            parameters_names = dc_param_values
        else:
            parameters_names = ["resource"]
        return parameters_names

    def create_list_of_parameters(self, dc_param_values, vars):
        parameters_names = self.create_list_of_parameter_names(dc_param_values, vars)
        parameters_list = []
        if parameters_names == ["resource"]:
            parameters_list.append(Parameter("resource", dc_param_values, list(set([val for val in resource_universe if val not in dc_param_values])), True))
        else:
            parameters_list = [(Parameter(parameter_name, vars[f"{parameter_name}_200"], vars[f"{parameter_name}_400"], False)) for parameter_name in parameters_names]
        return parameters_list

    def parse_parameters(self, parameters):
        all_values = []
        for param in parameters:
            for p in param.valid_vals:
                all_values.append(Value(param.name, p, 200))
            for p in param.invalid_vals:
                all_values.append(Value(param.name, p, 400))
        return all_values   
    
    def create_combinations(self, parameters_to_combine, lengths):
        raw_combinations = []
        if not isinstance(lengths, range):
            lengths = range(lengths, lengths+1)
        for comb_length in lengths:
            raw_combinations.extend(list(itertools.combinations(parameters_to_combine, comb_length)))
        all_combs = [list(itertools.product(*a)) for a in [[i.all_vals for i in combination] for combination in raw_combinations]] #rename
        all_combs = [i for inner_list in all_combs for i in inner_list]
        return all_combs


class Parameter:
    def __init__(self, name, valid_values, invalid_values, is_required):
        self.name = name
        self.valid_vals, self.invalid_vals = self.parse_values(valid_values, invalid_values)
        self.is_required = is_required
        self.all_vals = [Value(self.name, val, 400) for val in self.invalid_vals] + [Value(self.name, val, 200) for val in self.valid_vals]
    
    def parse_values(self, valid_values, invalid_values):
        if valid_values == [""]:
            valid_vals = valid_values + invalid_values
            invalid_vals = []
        else:
            valid_vals = valid_values
            invalid_vals = invalid_values
        return valid_vals, invalid_vals


class Result:
    def __init__(self, dc, required_outputs, optional_outputs, mode):
        self.dc_name = dc
        self.required_outputs = required_outputs
        self.req_string = self.create_string(required_outputs)
        self.optional_outputs = optional_outputs
        self.opt_string = self.create_string(optional_outputs)
        self.status_output = self.create_status(self.required_outputs, self.optional_outputs, mode)
        self.output_string = f"{self.dc_name},{self.req_string}{self.opt_string},status_code = {self.status_output}"

    def __eq__(self, counterpart):
        if isinstance(counterpart, Result):
            return self.output_string == counterpart.output_string
        return False
    
    def __hash__(self):
        return hash(self.output_string)

    def create_status(self, required_outputs, optional_outputs, mode):
        if mode == 500:
            return 500
        else:
            status_codes = [output.status for output in required_outputs] + ([output.status for output in optional_outputs] if optional_outputs is not None else [])
            try:
                return max(status_codes)
            except ValueError:
                return 400

    
    def create_string(self, outputs):
        out_string = ""
        if outputs is None:
            return out_string
        for output in outputs:
            if output.value != "":
                if output.name in param_names_conversion:
                    out_string += f"{param_names_conversion[output.name]} = {output.value}"
                else:
                    out_string += f"{output.name} = {output.value}"
                out_string += ";"
        return out_string

if __name__ == "__main__":

    current_date = datetime.now().strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dc",
        dest="preferred_data_calls",
        type=str,
        nargs='*',
        default=[""],
        help=(
            "Preferred data call(s) to create the tests for."
            "Example syntax: --dc bgplay abuse-contact-finder"
        )
    )
    parser.add_argument(
        "--output",
        type=str,
        default=f"data/test_cases_500_{current_date}.csv",
        help="Output file name."
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="500",
        help="Expected output status code. 500 by default."
    )
    
    parser.add_argument(
        "--no_optional",
        action="store_true",
        help="Setting to add to required inputs."
    )

    args = parser.parse_args()

    # We need a work-around solution here because in case of --dc DC1 DC2
    # Jenkins sets args.preferred_data_calls = ['DC1 DC2']
    # In local use, args.preferred_data_calls = ['DC1', 'DC2']
    if args.preferred_data_calls[0]:
        if len(args.preferred_data_calls) > 1:
            data_calls = args.preferred_data_calls
        else:
            data_calls = args.preferred_data_calls.pop().split()
    else:
        data_calls = resource_params.keys()

    test_suite = set()

    for dc in data_calls:

        try:
            dc_params = resource_params[dc]
        except KeyError:
            print(f"{dc} does not exist")
            continue

        datacall = Datacall(dc, dc_params, optional_params[dc] if dc in optional_params.keys() else [], vars())
        for required_params_combination in datacall.required_params_combinations:
            test_suite.add(Result(datacall.name, required_params_combination, None, int(args.mode)))
            if not args.no_optional:
                for optional_params_combination in datacall.optional_params_combinations:
                    test_suite.add(Result(datacall.name, required_params_combination, optional_params_combination, int(args.mode)))    

    with open(args.output, "w") as file_writer:
        file_writer.write("data_call,test_input,expected_output")
        for line in sorted([result.output_string for result in test_suite]):
            file_writer.write(f"\n{line}")
