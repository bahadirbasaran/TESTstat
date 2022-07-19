import sys
import csv

from core.teststat import TestStat


TEST_CASES_PATH = "data/cicd_test_cases.csv"


def run_cicd_tests(host):

    teststat = TestStat(host, cicd=True)

    failed_calls = []

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

            print(f"Test Case {row_index}:", end=' ')

            test_output = teststat.run_test(data_call, test_input, expected_output)

            print("----> Expected: ", row[2].replace(';', ' | '), end='\n\n')

            if test_output:
                for param, value in expected_output.items():
                    print(f"Parameter {param}:")
                    print(f"Expected: {value} - Actual: {test_output[param]}")

                # sys.exit(f"Job failed at Test Case {row_index}!")
                if data_call not in failed_calls:
                    failed_calls.append(data_call)

    if failed_calls:
        sys.exit(failed_calls)
    else:
        sys.exit(0)
