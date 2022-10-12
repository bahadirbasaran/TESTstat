import sys
import csv
import asyncio
from collections import namedtuple

from core.teststat import TestStat
from core.utils import MessageEnum


async def run_cicd_tests(host, mode):
    """Run CICD test cases for given host in given mode"""

    async def _run_routine(row_index, row):

        data_call = row[0]
        test_input = row[1].replace(' ', '').replace(';', '&')
        expected_output = {}
        for param_value_pair in row[2].split(';'):
            param, value = param_value_pair.replace(' ', '').split('=', 1)
            expected_output[param] = value.replace('&', ',')

        test_output, url = await teststat.run_test(data_call, test_input, expected_output, True)

        if test_output == MessageEnum.TIMEOUT:
            stat = TimeoutStat(
                test_case=row_index,
                data_call=data_call.replace('-', ' ').title(),
                url=url,
                expected_output=expected_output
            )
            stats["time_out"].append(stat)

        elif test_output == MessageEnum.BAD_GATEWAY:
            stat = FailureStat(
                test_case=row_index,
                data_call=data_call.replace('-', ' ').title(),
                url=url,
                expected_output=expected_output,
                actual_output={"error": "502 Bad Gateway"}
            )
            stats["failure"].append(stat)

        elif test_output:
            stat = FailureStat(
                test_case=row_index,
                data_call=data_call.replace('-', ' ').title(),
                url=url,
                expected_output=expected_output,
                actual_output=test_output
            )
            stats["failure"].append(stat)

    test_cases_path = "data/test_cases_500.csv" if mode == "500" else "data/test_cases.csv"

    sys.stdout.flush()
    print("#" * 170, "\n")
    print(f"Host: {host} | Test Cases: {test_cases_path} | Mode: {mode}\n")

    teststat = TestStat(host, cicd=True)

    stats = {"failure": [], "time_out": []}
    FailureStat = namedtuple(
        "Failure",
        ["test_case", "data_call", "url", "expected_output", "actual_output"]
    )
    TimeoutStat = namedtuple("Timeout", ["test_case", "data_call", "url", "expected_output"])

    with open(test_cases_path) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')
        # Skip the header
        next(csv_reader)

        # Create an event loop for all the coroutines, and proceed when all done
        await asyncio.gather(
            *[_run_routine(row_index, row) for row_index, row in enumerate(csv_reader, 1)]
        )
        await teststat.session.close()

    stats["failure"].sort(key=lambda tuple: tuple.test_case)
    stats["time_out"].sort(key=lambda tuple: tuple.test_case)

    if stats["failure"]:

        print("FAILED TEST CASES:\n")

        for tuple in stats["failure"]:
            print(
                f"\nTest Case: {tuple.test_case} | Data Call: {tuple.data_call} | URL: {tuple.url}"
            )

            if "status_code" in tuple.actual_output:
                print("--> Status Code: ", tuple.actual_output["status_code"])

            if "error" in tuple.actual_output:
                for param, expected_value in tuple.expected_output.items():
                    print(f"--> Parameter '{param}' | Expected: {expected_value}")
                print("   --> Error: ", tuple.actual_output["error"])
            else:
                for param, expected_value in tuple.expected_output.items():
                    print(
                        f"--> Parameter '{param}':"
                        f"   --> Expected: {expected_value} | Actual: {tuple.actual_output[param]}"
                    )

    if stats["time_out"]:

        if stats["failure"]:
            print("\n", "-" * 170, "\n")
        print("TIMED-OUT TEST CASES:\n")

        for tuple in stats["time_out"]:
            print(f"\nTest Case: {tuple.test_case} | Data Call: {tuple.data_call} | URL: {tuple.url}")
            for param, expected_value in tuple.expected_output.items():
                print(f"--> Parameter '{param}' | Expected: {expected_value}")

    print("\n", "#" * 170, "\n")
    print("Number of Failed Test Cases:    ", len(stats["failure"]))
    print("Number of Timed-out Test Cases: ", len(stats["time_out"]), "\n")

    if stats["time_out"] or stats["failure"]:
        sys.exit(1)
    else:
        sys.exit(0)
