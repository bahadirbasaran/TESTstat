import sys
import csv
import asyncio
import json
from math import ceil
from datetime import datetime
from collections import namedtuple

from core.teststat import TestStat
from core.utils import MessageEnum, get_batch

import requests


MATTERMOST_URL = "https://mattermost.ripe.net/hooks/6xp8tt93i3fwde5d43jegsxi8a"
MATTERMOST_CHANNEL = "ripestat-teststat"
MATTERMOST_NEWLINE = "` `  "


def post_message(message, url=MATTERMOST_URL, channel=MATTERMOST_CHANNEL):
    """Post given message to the Mattermost channel hooked with the given URL"""

    current_date = datetime.now().strftime("%d/%m/%y")
    frame = f"### TESTstat Report - {current_date}\n"
    payload = {
        "channel": channel,
        "text": frame + message
    }
    requests.post(url, data=json.dumps(payload))


def process_stats(stats):
    """Process stats and return relevant URLs for each data call"""

    processed_stats = {}

    for tuple in stats["failure"]:
        if tuple.data_call not in processed_stats:
            processed_stats[tuple.data_call] = {
                "failed_queries": [tuple.url],
                "timed_out_queries": []
            }
        else:
            processed_stats[tuple.data_call]["failed_queries"].append(tuple.url)

    for tuple in stats["time_out"]:
        if tuple.data_call not in processed_stats:
            processed_stats[tuple.data_call] = {
                "failed_queries": [],
                "timed_out_queries": [tuple.url]
            }
        else:
            processed_stats[tuple.data_call]["timed_out_queries"].append(tuple.url)

    # Sort data calls in reverse order, prioritize failures over time-outs
    data_calls_in_order = list(
        sorted(
            processed_stats,
            key=lambda data_call: (
                len(processed_stats[data_call]["failed_queries"]),
                len(processed_stats[data_call]["timed_out_queries"])
            ),
            reverse=True
        )
    )

    return {data_call: processed_stats[data_call] for data_call in data_calls_in_order}


async def run_cicd_tests(host, mode, file_name, preferred_data_call, preferred_version, batch_size):
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
    # test_cases_path = "data/" + file_name if mode != "500" else ""

    sys.stdout.flush()
    print("\n", "#" * 150, "\n")

    header = f"**Host:**    {host}\n**Mode:**  {mode}"
    if test_cases_path:
        header += f"\n**Data:**    {test_cases_path}"
    if preferred_version != "default":
        header += f"\n**Version:** {preferred_version}"
    header += f"\n**Batch Size:** {batch_size}\n\n"
    print(header)

    if preferred_version == "default":
        teststat = TestStat(host, cicd=True)
    else:
        teststat = TestStat(host, cicd=True, preferred_version=preferred_version)

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

        if preferred_data_call:
            csv_reader = filter(lambda row: row[0] == preferred_data_call, list(csv_reader))

        test_cases = list(enumerate(csv_reader, 1))
        total_test_cases = len(test_cases)
        num_batches = ceil(total_test_cases / int(batch_size))

        for batch_index, batch in enumerate(get_batch(test_cases, int(batch_size)), 1):

            coroutines_batch = [_run_routine(row_index, row) for row_index, row in batch]

            # Create an event loop for a batch of coroutines, and proceed to the next when it's done
            await asyncio.gather(*coroutines_batch)

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
            print("\n", "-" * 150, "\n")
        print("TIMED-OUT TEST CASES:\n")

        for tuple in stats["time_out"]:
            print(
                f"\nTest Case: {tuple.test_case} | Data Call: {tuple.data_call} | URL: {tuple.url}"
            )
            for param, expected_value in tuple.expected_output.items():
                print(f"--> Parameter '{param}' | Expected: {expected_value}")

    num_failure = len(stats["failure"])
    num_time_out = len(stats["time_out"])

    print("\n", "#" * 150, "\n")
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

        msg_table = (
            "| Data Call | Failures | Timeouts | Failed & Timed-out URLs |\n"
            "|:----------|:--------:|:--------:|:------------------------|\n"
        )

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
