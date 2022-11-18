import time
import asyncio
from math import ceil
from collections import namedtuple, Counter

from core.teststat import TestStat
from core.utils import MessageEnum, MATTERMOST_NEWLINE, MATTERMOST_TABLE_FRAME, \
    parse_csv, get_batch, post_message, process_stats


async def run_cicd_tests(host, batch_size, test_source, random, preferred_data_calls):
    """Run CICD test cases for given host and given test source"""

    async def _run_routine(row_index, row, dc_version):

        data_call = row[0]
        test_input = row[1].replace(' ', '').replace('&', ',').replace(';', '&')
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

    teststat = TestStat(host)

    stats = {"failure": [], "time_out": []}
    FailureStat = namedtuple(
        "Failure",
        ["test_case", "data_call", "url", "expected_output", "actual_output"]
    )
    TimeoutStat = namedtuple("Timeout", ["test_case", "data_call", "url", "expected_output"])

    test_cases = parse_csv(test_source, preferred_data_calls, random)

    test_counts_per_dc = Counter([test_case[0] for _, test_case, _ in test_cases])
    total_test_cases = len(test_cases)
    num_batches = ceil(total_test_cases / batch_size)

    print("\n", "#" * 100, "\n\n")
    print(f"Host: {host}   |   Test Source: {test_source}\n\n")

    start_time = time.time()

    # Create an event loop for a batch of coroutines, and proceed to the next when it's done
    for batch_index, batch in enumerate(get_batch(test_cases, batch_size), 1):

        await asyncio.gather(
            *[_run_routine(row_index, row, version) for row_index, row, version in batch]
        )
        print(f"-> Batch {batch_index}/{num_batches} has been completed!")

    # Close the session when all batches are done
    await teststat.session.close()

    stats["failure"].sort(key=lambda tuple: tuple.test_case)
    stats["time_out"].sort(key=lambda tuple: tuple.test_case)
    num_failure = len(stats["failure"])
    num_time_out = len(stats["time_out"])

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

    header = f"**Host:** {host}   |   **Test Source:** {test_source}\n\n"

    print("\n", "#" * 100, "\n")
    print(f"Test Cases:           {total_test_cases:,}")
    print(f"Failed Test Cases:    {num_failure:,}")
    print(f"Timed-out Test Cases: {num_time_out:,}\n")

    # Prepare a message to be posted in Mattermost channel
    header += f"**- Total Test Cases:**           {total_test_cases:,}" + "\n"
    header += f"**- Failed Test Cases:**         {num_failure:,}"
    header += "     :flan_cool:\n" if not num_failure else "\n"
    header += f"**- Timed-out Test Cases:** {str(num_time_out)}"
    header += "     :flan_cool:\n\n" if not num_time_out else "\n\n"

    if num_failure or num_time_out:
        processed_stats = process_stats(stats)

        msg_table = MATTERMOST_TABLE_FRAME

        for data_call, data_call_stats in processed_stats.items():

            num_tests = test_counts_per_dc[data_call]
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

            msg_table += f"|{data_call}|{num_tests:,}|{num_failure:,}|{num_time_out:,}|{queries}|\n"

        header += msg_table

    post_message(header)

    print("Elapsed time: ", time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)))
