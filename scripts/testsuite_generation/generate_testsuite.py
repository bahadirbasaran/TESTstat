# The following script aims to create a test suite to use in TESTstat
# There are three optional parameters for this script:
# 1. --dc datacall , which creates test suite only for the given datacall
# 2. --output output_filename sets the output filename
# 3. --mode 500 will set all status codes to 500. Such test suite is to be
# used for the jobs catching 500 errors.

# The basic logic here is: different combinations of required and optional
# parameters are created. This is based on the config_autogeneration_params.py.
# Next, different values are passed to the parameters according to the
# confid_autogeneration_param_values.py.
# Further, the cases are ordered alphabetically and passed to the output file.
# Each test case is mentioned only once in the test suite.

# Imports
import argparse
import itertools
from config_testsuite_param_values import *  # noqa: F403

# from config_testsuite_param_values import resource_groups
from config_testsuite_params import resource_params, optional_params

# Parsing inputs from the command line
parser = argparse.ArgumentParser()

parser.add_argument("--dc", help="Choose the datacall to create the test suite")
parser.add_argument("--output", help="Add the output filename")
parser.add_argument(
    "--mode",
    help="Add 500 to create test suite for 500 errors. \
        Values different to 500 will not have influence on the result.",
)

args = parser.parse_args()

if args.dc:
    keys = args.dc.split(",")
else:
    keys = resource_params.keys()

if args.output:
    output_filename = args.output
else:
    output_filename = "output_testsuite"

# Functions definitions


def output_code(code, mode, code_optional):
    """
    Defining the code for the test case.
    """
    code_to_insert = None
    if mode == "500":
        code_to_insert = 500
    elif code_optional:
        code_to_insert = code_optional
    else:
        code_to_insert = code
    return code_to_insert


def adding_opt_params(optional_params_for_dc, req_param_string, code, mode, vars):
    """
    Creating set of test cases by adding combinations of the optional parameters to the
    required parameters string.
    """
    output_set = set()
    for optional_param_for_dc in optional_params_for_dc:
        code_optional = None
        args_to_test = list()
        for i in range(0, len(optional_param_for_dc)):
            args_to_test.append(
                vars[f"config_testsuite_param_values.{optional_param_for_dc[i]}"]
            )
            args_to_test_final = list(itertools.product(*args_to_test))
        for id in range(0, len(args_to_test_final)):
            args_ind = args_to_test_final[id]
            code_optional = None
            opt_param_string = str()
            optional_param_for_dc_to_use = [
                optional_param_for_dc_ind[:-4]
                for optional_param_for_dc_ind in optional_param_for_dc
            ]
            for i in list(zip(optional_param_for_dc_to_use, args_ind)):
                if len(opt_param_string) < 1:
                    opt_param_string += f"{i[0]} = {i[1]}"
                else:
                    opt_param_string += f"; {i[0]} = {i[1]}"
            codes = [
                optional_param_for_dc_ind[-3:]
                for optional_param_for_dc_ind in optional_param_for_dc
            ]
            if any(c == "400" for c in codes):
                code_optional = 400
            code_to_insert = output_code(code, mode, code_optional)
            if len(req_param_string) < 1:
                output_set.add(
                    f"{k},{opt_param_string}, status_code = {code_to_insert}"
                )
            else:
                output_set.add(
                    f"{k},{req_param_string}; {opt_param_string}, status_code = {code_to_insert}"
                )
    return output_set


def creating_combs(resources):
    """
    Creating all possible combinations of input resources.
    """
    all_combs = list()
    all_combs_for_dc = list()
    for combination_length in range(1, len(resources) + 1):
        all_combs.extend(list(itertools.combinations(resources, combination_length)))
    for req_param_combination in all_combs:
        all_combs_for_dc.extend(
            list(
                itertools.product(
                    *[[f"{j}_400", f"{j}_200"] for j in req_param_combination]
                )
            )
        )
    return all_combs_for_dc


# Test suite creation

test_suite = set()
print(vars())
for k, v in resource_params.items():
    if k in keys:
        optional_params_for_dc = []
        if k in optional_params.keys():
            optional_params_for_dc = creating_combs(optional_params[k])
        # processing datacalls with one required input
        if sum(isinstance(i, list) for i in v) < 2:
            for group in resource_groups:  # noqa F405
                for element in group:
                    if args.mode == "500":
                        code = 500
                    elif element in v:
                        code = 200
                    else:
                        code = 400
                    if len(element) < 1:
                        req_param_string = ""
                    else:
                        req_param_string = f"resource = {element}"
                    test_suite.add(f"{k},{req_param_string}, status_code = {code}")
                    # adding optional parameters
                    test_test = list()
                    if len(optional_params_for_dc) > 0:
                        test_suite = test_suite.union(
                            adding_opt_params(
                                optional_params_for_dc,
                                req_param_string,
                                code,
                                args.mode,
                                vars(),
                            )
                        )
        # processing datacalls with more, than 1 required parameter
        else:
            resource_params_for_dc = [value for val in v for value in val]
            all_combs_for_dc = creating_combs(resource_params_for_dc)
            # adding required parameters
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
                    elif any(c == "400" for c in codes) or len(codes) < len(
                        resource_params_for_dc
                    ):
                        code = 400
                    for i in list(zip(req_param_for_dc_to_use, req_args_ind)):
                        if len(req_param_string) < 1:
                            if len(i[1]) > 0:
                                req_param_string += f"{i[0]} = {i[1]}"
                        else:
                            if len(i[1]) > 0:
                                req_param_string += f"; {i[0]} = {i[1]}"
                    codes = [
                        req_param_for_dc_ind[-3:]
                        for req_param_for_dc_ind in req_param_for_dc
                    ]
                    if args.mode == "500":
                        code = 500
                    elif any(c == "400" for c in codes) or len(codes) < len(
                        resource_params_for_dc
                    ):
                        code = 400
                    test_suite.add(f"{k}, {req_param_string}, status_code = {code}")
                    # adding optional parameters
                    if len(optional_params_for_dc) > 0:
                        test_suite = test_suite.union(
                            adding_opt_params(
                                optional_params_for_dc,
                                req_param_string,
                                code,
                                args.mode,
                                vars(),
                            )
                        )

# Writing to the output file
with open(output_filename, "w") as f:
    for line in sorted(list(test_suite)):
        f.write("%s\n" % line)
f.close()
