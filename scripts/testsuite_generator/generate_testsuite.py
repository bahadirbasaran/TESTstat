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
from config_testsuite_params import resource_params, optional_params


def add_optional_params(optional_params_for_dc, req_param_string, code, mode, vars):
    """
    Create set of test cases by adding optional parameter combinations to the
    required parameters string.
    """

    output_set = set()

    for optional_param_for_dc in optional_params_for_dc:

        args_to_test = []

        for i in range(0, len(optional_param_for_dc)):
            args_to_test.append(vars[f"{optional_param_for_dc[i]}"])
            args_to_test_final = list(itertools.product(*args_to_test))

        for id in range(0, len(args_to_test_final)):
            args_ind = args_to_test_final[id]
            opt_param_string = ""
            optional_param_for_dc_to_use = [
                optional_param_for_dc_ind[:-4]
                for optional_param_for_dc_ind in optional_param_for_dc
            ]

            for i in list(zip(optional_param_for_dc_to_use, args_ind)):
                if len(opt_param_string) < 1:
                    opt_param_string += f"{i[0]} = {i[1]}"
                else:
                    opt_param_string += f";{i[0]} = {i[1]}"

            codes = [
                optional_param_for_dc_ind[-3:]
                for optional_param_for_dc_ind in optional_param_for_dc
            ]

            code_optional = 400 if any(c == "400" for c in codes) else None
            if mode == "500":
                status_code = 500
            elif code_optional:
                status_code = code_optional
            else:
                status_code = code

            if len(req_param_string) < 1:
                output_set.add(f"{dc},{opt_param_string},status_code = {status_code}")
            else:
                output_set.add(
                    f"{dc},{req_param_string};{opt_param_string},status_code = {status_code}"
                )

    return output_set


def create_combinations(resources):
    """Create all possible combinations of given input resources"""

    raw_combinations = []
    all_combinations = []

    for combination_length in range(1, len(resources) + 1):
        raw_combinations.extend(list(itertools.combinations(resources, combination_length)))

    for req_param_combination in raw_combinations:
        all_combinations.extend(
            list(itertools.product(*[[f"{j}_400", f"{j}_200"] for j in req_param_combination]))
        )

    return all_combinations


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
    args = parser.parse_args()

    if args.preferred_data_calls[0]:
        data_calls = args.preferred_data_calls.pop().split()
    else:
        data_calls = resource_params.keys()

    test_suite = set()

    for dc, dc_param_values in resource_params.items():

        if dc in data_calls:
            optional_params_for_dc = []
            if dc in optional_params.keys():
                optional_params_for_dc = create_combinations(optional_params[dc])

            # Process data calls with one required input
            if sum(isinstance(i, list) for i in dc_param_values) < 2:
                for group in resource_groups:  # noqa F405
                    for element in group:
                        if args.mode == "500":
                            status_code = 500
                        elif element in dc_param_values:
                            status_code = 200
                        else:
                            status_code = 400
                        if len(element) < 1:
                            req_param_string = ""
                        else:
                            req_param_string = f"resource = {element}"
                        test_suite.add(f"{dc},{req_param_string},status_code = {status_code}")

                        # Add optional parameters
                        if len(optional_params_for_dc) > 0:
                            test_suite = test_suite.union(
                                add_optional_params(
                                    optional_params_for_dc,
                                    req_param_string,
                                    status_code,
                                    args.mode,
                                    vars(),
                                )
                            )

            # Process data calls with more than 1 required parameter
            else:
                resource_params_for_dc = [value for val in dc_param_values for value in val]
                all_combs_for_dc = create_combinations(resource_params_for_dc)

                # Add required parameters
                for req_param_for_dc in all_combs_for_dc:
                    req_args_to_test = list()

                    for i in range(0, len(req_param_for_dc)):
                        req_args_to_test.append(vars()[req_param_for_dc[i]])
                        req_args_to_test_final = list(itertools.product(*req_args_to_test))

                    for req_args_ind in req_args_to_test_final:
                        code = 200
                        req_param_string = str()
                        req_param_for_dc_to_use = [
                            req_param_for_dc_ind[:-4]
                            for req_param_for_dc_ind in req_param_for_dc
                        ]
                        codes = [
                            req_param_for_dc_ind[-3:]
                            for req_param_for_dc_ind in req_param_for_dc
                        ]

                        if args.mode == "500":
                            code = 500
                        elif any(c == "400" for c in codes) or \
                                len(codes) < len(resource_params_for_dc):
                            code = 400

                        for i in list(zip(req_param_for_dc_to_use, req_args_ind)):
                            if len(req_param_string) < 1:
                                if len(i[1]) > 0:
                                    req_param_string += f"{i[0]} = {i[1]}"
                            else:
                                if len(i[1]) > 0:
                                    req_param_string += f";{i[0]} = {i[1]}"

                        codes = [
                            req_param_for_dc_ind[-3:]
                            for req_param_for_dc_ind in req_param_for_dc
                        ]

                        if args.mode == "500":
                            code = 500
                        elif any(c == "400" for c in codes) or \
                                len(codes) < len(resource_params_for_dc):
                            code = 400

                        test_suite.add(f"{dc},{req_param_string},status_code = {code}")

                        # Add optional parameters
                        if len(optional_params_for_dc) > 0:
                            test_suite = test_suite.union(
                                add_optional_params(
                                    optional_params_for_dc,
                                    req_param_string,
                                    code,
                                    args.mode,
                                    vars(),
                                )
                            )

    with open(args.output, "w") as file_writer:
        file_writer.write("data_call,test_input,expected_output")
        for line in sorted(list(test_suite)):
            file_writer.write(f"\n{line}")
