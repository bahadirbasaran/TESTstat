import sys
import csv

from core.teststat import TestStat


TEST_CASES_PATH = "data/cicd_test_cases.csv"


def run_cicd_tests(host):

    teststat = TestStat(host, cicd=True)

    failed_test_cases = []
    failed_data_calls = []

    with open(TEST_CASES_PATH) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')

        next(csv_reader)

        for row_index, row in enumerate(csv_reader, 1):

            data_call = row[0]
            test_input = row[1].replace(' ', '').replace(';', '&')
            expected_output = {}
            for param_value_pair in row[2].split(';'):
                param, value = param_value_pair.replace(' ', '').split('=', 1)
                expected_output[param] = value.replace('&', ',')

            print(f"Test Case {row_index} ->", end=' ')

            test_output = teststat.run_test(data_call, test_input, expected_output, debug=True)

            print("--> Expected: ", row[2].replace(';', ' | '))

            if test_output:
                print(f"----> Test Case {row_index} failed!")

                for param, value in expected_output.items():
                    print(f"------> Parameter {param}:")
                    print(f"------> Expected: {value} | Actual: {test_output[param]}")

                failed_test_cases.append(str(row_index))

                if data_call not in failed_data_calls:
                    failed_data_calls.append(data_call.replace('-', ' ').title())

            print("\n")

    if failed_data_calls:
        failed_test_cases = ', '.join(failed_test_cases)
        failed_data_calls = ', '.join(failed_data_calls)

        script_return = (
            f"Failed Test Cases: {failed_test_cases}\n"
            f"Failed Data Calls: {failed_data_calls}"
        )

        sys.exit(script_return)
    else:
        sys.exit(0)
