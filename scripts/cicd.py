import sys
import csv

from core.teststat import TestStat
from core.utils import MessageEnum


def run_cicd_tests(host, mode):
    """Run CICD test cases for given host in given mode"""

    def _place_stats(stat_type):

        if stat_type == "timeout":
            target_index_list = timed_out_test_cases
            target_dc_list = timed_out_data_calls
        elif stat_type == "failure":
            target_index_list = failed_test_cases
            target_dc_list = failed_data_calls

        target_index_list.append(str(row_index))

        data_call_repr = data_call.replace('-', ' ').title()
        if data_call_repr not in target_dc_list:
            target_dc_list.append(data_call_repr)

    test_cases_path = "data/test_cases_500.csv" if mode == "500" else "data/test_cases_cicd.csv"

    sys.stdout.flush()
    print(f"Host: {host}\nTest Cases: {test_cases_path}\nMode: {mode}")

    teststat = TestStat(host, cicd=True)

    failed_test_cases = []
    failed_data_calls = []
    timed_out_test_cases = []
    timed_out_data_calls = []

    with open(test_cases_path) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')

        next(csv_reader)

        for row_index, row in enumerate(csv_reader, 1):

            data_call = row[0]
            test_input = row[1].replace(' ', '').replace(';', '&')
            expected_output = {}
            for param_value_pair in row[2].split(';'):
                param, value = param_value_pair.replace(' ', '').split('=', 1)
                expected_output[param] = value.replace('&', ',')

            print(f"Test Case {row_index}:")

            test_output = teststat.run_test(data_call, test_input, expected_output)

            print("--> Expected: ", row[2].replace(';', ' | '))

            if test_output == MessageEnum.TIMEOUT:
                print(f"----> Test Case {row_index} timed-out!")
                _place_stats("timeout")

            elif "error" in test_output or (mode == "500" and not test_output):
                print(f"----> Test Case {row_index} failed!")
                _place_stats("failure")

            elif mode == "complete" and test_output:
                print(f"----> Test Case {row_index} failed!")

                for param, value in expected_output.items():
                    print(f"------> Parameter {param}:")
                    param = param.split("->")[0]
                    print(f"------> Expected: {value} | Actual: {test_output[param]}")

                _place_stats("failure")

            print("\n")

    script_return = ""

    if failed_data_calls:

        failed_test_cases = ', '.join(failed_test_cases)
        failed_data_calls = ', '.join(failed_data_calls)

        script_return += (
            f"Failed Test Cases: {failed_test_cases}\n"
            f"Failed Data Calls: {failed_data_calls}\n"
        )

    if timed_out_data_calls:
        timed_out_test_cases = ', '.join(timed_out_test_cases)
        timed_out_data_calls = ', '.join(timed_out_data_calls)

        script_return += (
            f"\nTimed-out Test Cases: {timed_out_test_cases}\n"
            f"Timed-out Data Calls: {timed_out_data_calls}"
        )

    if script_return:
        frame_length = min(max(len(failed_data_calls), len(timed_out_data_calls)) + 19, 170)
        output_frame = "\n\n" + '#' * frame_length + "\n\n"
        script_return = f"{output_frame}{script_return}{output_frame}"

    if script_return:
        sys.exit(script_return)
    else:
        sys.exit(0)
