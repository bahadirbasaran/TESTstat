import sys
import csv
import asyncio
from math import ceil
from collections import namedtuple

from core.teststat import TestStat
from core.utils import MessageEnum, MATTERMOST_NEWLINE, MATTERMOST_TABLE_FRAME, \
                        get_batch, post_message, process_stats


async def run_cicd_tests(host, mode, batch_size, preferred_data_calls):
    """Run CICD test cases for given host in given mode"""

    async def _run_routine(row_index, row, dc_version):

        data_call = row[0]
        test_input = row[1].replace(' ', '').replace(';', '&')
        if dc_version:
            test_input += f"&preferred_version={dc_version}"

        expected_output = {}
        for param_value_pair in row[2].split(';'):
            param, value = param_value_pair.replace(' ', '').split('=', 1)
            expected_output[param] = value.replace('&', ',')

        test_output, url = await teststat.run_test(data_call, test_input, expected_output, True)

        data_call = data_call.replace('-', ' ').title()
        if dc_version:
            data_call += f" (v{dc_version})"

        if test_output == MessageEnum.TIMEOUT:
            stat = TimeoutStat(
                test_case=row_index,
                data_call=data_call,
                url=url,
                expected_output=expected_output
            )
            stats["time_out"].append(stat)

        elif test_output == MessageEnum.BAD_GATEWAY:
            stat = FailureStat(
                test_case=row_index,
                data_call=data_call,
                url=url,
                expected_output=expected_output,
                actual_output={"error": "502 Bad Gateway"}
            )
            stats["failure"].append(stat)

        elif test_output:
            stat = FailureStat(
                test_case=row_index,
                data_call=data_call,
                url=url,
                expected_output=expected_output,
                actual_output=test_output
            )
            stats["failure"].append(stat)

    teststat = TestStat(host, cicd=True)

    test_cases_path = "data/test_cases_500.csv" if mode == "500" else "data/test_cases.csv"

    sys.stdout.flush()
    print("\n", "#" * 100, "\n\n")
    print(f"Host: {host} | Mode: {mode} | Data Source: {test_cases_path}\n\n")

    header = f"**Host:** {host} | **Mode:** {mode} | **Data Source:** {test_cases_path}\n\n"

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

        # Filter data calls if specified.
        # e.g. preferred_data_calls = ['prefix-count_1.2', 'abuse-contact-finder_2.0_2.1', 'bgplay']
        if preferred_data_calls:
            dc_version_map = {
                dc_and_versions.split('_')[0]: dc_and_versions.split('_')[1:]
                for dc_and_versions in preferred_data_calls
            }
            csv_reader = filter(lambda row: row[0] in dc_version_map, list(csv_reader))

            test_cases = []
            for row in list(enumerate(csv_reader, 1)):
                if not dc_version_map[row[1][0]]:
                    test_cases.append((row[0], row[1], None))
                else:
                    for version in dc_version_map[row[1][0]]:
                        test_cases.append((row[0], row[1], version))
        else:
            test_cases = [(row[0], row[1], None) for row in list(enumerate(csv_reader, 1))]

        total_test_cases = len(test_cases)
        num_batches = ceil(total_test_cases / int(batch_size))

        # Create an event loop for a batch of coroutines, and proceed to the next when it's done
        for batch_index, batch in enumerate(get_batch(test_cases, int(batch_size)), 1):

            await asyncio.gather(
                *[_run_routine(row_index, row, version) for row_index, row, version in batch]
            )
            print(f"Batch {batch_index}/{num_batches} has been completed!")

        # Close the session when all batches are done
        await teststat.session.close()

    stats["failure"].sort(key=lambda tuple: tuple.test_case)
    stats["time_out"].sort(key=lambda tuple: tuple.test_case)

    if stats["failure"]:

        print("\nFAILED TEST CASES:\n")

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
            print("\n", "-" * 100, "\n")
        print("TIMED-OUT TEST CASES:\n")

        for tuple in stats["time_out"]:
            print(
                f"\nTest Case: {tuple.test_case} | Data Call: {tuple.data_call} | URL: {tuple.url}"
            )
            for param, expected_value in tuple.expected_output.items():
                print(f"--> Parameter '{param}' | Expected: {expected_value}")

    num_failure = len(stats["failure"])
    num_time_out = len(stats["time_out"])

    print("\n", "#" * 100, "\n")
    print("Test Cases:           ", total_test_cases)
    print("Failed Test Cases:    ", num_failure)
    print("Timed-out Test Cases: ", num_time_out, "\n")

    # Prepare a message to be post in Mattermost channel
    header += "**- Total Test Cases:**           " + str(total_test_cases) + "\n"
    header += "**- Failed Test Cases:**         " + str(num_failure)
    header += "     :flan_cool:\n" if not num_failure else "\n"
    header += "**- Timed-out Test Cases:** " + str(num_time_out)
    header += "     :flan_cool:\n\n" if not num_time_out else "\n\n"

    if num_failure or num_time_out:
        processed_stats = process_stats(stats)

        msg_table = MATTERMOST_TABLE_FRAME

        for data_call, data_call_stats in processed_stats.items():

            num_failure = len(data_call_stats["failed_queries"])
            num_time_out = len(data_call_stats["timed_out_queries"])

            data_call_stats["failed_queries"] = [
                f"**F:**[{url}]({url})" for url in data_call_stats["failed_queries"]
            ]
            data_call_stats["timed_out_queries"] = [
                f"**T:**[{url}]({url})" for url in data_call_stats["timed_out_queries"]
            ]

            failed_queries = MATTERMOST_NEWLINE.join(data_call_stats["failed_queries"])
            timed_out_queries = MATTERMOST_NEWLINE.join(data_call_stats["timed_out_queries"])

            if num_failure and num_time_out:
                queries = failed_queries + MATTERMOST_NEWLINE + timed_out_queries
            elif num_failure:
                queries = failed_queries
            else:
                queries = timed_out_queries

            msg_table += f"| {data_call} | {num_failure} | {num_time_out} | {queries} |\n"

        post_message(header + msg_table)
        sys.exit(1)
    else:
        post_message(header)
        sys.exit(0)
