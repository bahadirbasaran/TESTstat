import sys
import csv

from core.teststat import TestStat
from core.utils import MessageEnum


TEST_CASES_PATH = "data/test_cases_cicd.csv"


def run_cicd_tests(host):

    sys.stdout.flush()

    teststat = TestStat(host, cicd=True)

    failed_test_cases = []
    failed_data_calls = []
    timed_out_test_cases = []
    timed_out_data_calls = []

    with open(TEST_CASES_PATH) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')

        next(csv_reader)

        print("Host: ", host, '\n')

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

                timed_out_test_cases.append(str(row_index))

                if data_call not in timed_out_data_calls:
                    timed_out_data_calls.append(data_call.replace('-', ' ').title())

            elif test_output:
                print(f"----> Test Case {row_index} failed!")

                for param, value in expected_output.items():
                    print(f"------> Parameter {param}:")
                    param = param.split("->")[0] if "->" in param else param
                    print(f"------> Expected: {value} | Actual: {test_output[param]}")

                failed_test_cases.append(str(row_index))

                if data_call not in failed_data_calls:
                    failed_data_calls.append(data_call.replace('-', ' ').title())

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
            f"Timed-out Test Cases: {timed_out_test_cases}\n"
            f"Timed-out Data Calls: {timed_out_data_calls}"
        )

    if script_return:
        sys.exit(script_return)
    else:
        sys.exit(0)
