import argparse
from datetime import datetime

import config_testsuite_params as ctp
from config_testsuite_param_values import *


def generate_combinations(params, current_param_index=0, current_combination=""):

    combinations = []

    # Base case: If all parameters have been processed
    if current_param_index == len(params):

        # If there's a combination, remove the trailing semicolon and add it to the list
        if current_combination:
            combinations.append(current_combination[:-1])

        return combinations

    current_param = params[current_param_index]

    # Check if the variable exists in the global namespace
    if f"{current_param}_200" in globals():

        # Access the variable using globals() and construct the variable name dynamically
        param_values = globals()[f"{current_param}_200"]

        for val in param_values:
            new_combination = f"{current_combination}{current_param} = {val};"

            # Recursively call the function for the next parameter and extend the list of combinations
            combinations.extend(generate_combinations(params, current_param_index + 1, new_combination))
    else:
        # If the variable doesn't exist, skip it and move to the next parameter
        combinations.extend(generate_combinations(params, current_param_index + 1, current_combination))

    return combinations


def get_tests_for_dc(data_call):

    tests = []

    dc_required_params = ctp.resource_params[data_call]

    # If data call is among the exceptions (rpki-validation and whois-object-last-updated)
    if any(isinstance(param, list) for param in dc_required_params):
        params = [param[0] for param in dc_required_params]

        combinations = generate_combinations(params)

        for combination in combinations:
            tests.append(f"{data_call},{combination},status_code = 200")

    # If data call has no required parameter
    elif not dc_required_params:
        tests.append(f"{data_call},,status_code = 200")

    else:
        for resource_val in dc_required_params:
            tests.append(f"{data_call},resource = {resource_val},status_code = 200")

    return tests


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
        default=f"data/test_cases_regression_{current_date}.csv",
        help="Output file name."
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
        data_calls = ctp.resource_params.keys()

    with open(args.output, "w") as file_writer:
        file_writer.write("data_call,test_input,expected_output")
        for dc in data_calls:
            for line in get_tests_for_dc(dc):
                file_writer.write(f"\n{line}")