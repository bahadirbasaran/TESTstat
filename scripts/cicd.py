import sys
import csv
import asyncio
import json
from math import ceil
from collections import namedtuple, defaultdict

from core.teststat import TestStat
from core.utils import MessageEnum, get_batch

import requests


MATTERMOST_URL = "https://mattermost.ripe.net/hooks/6xp8tt93i3fwde5d43jegsxi8a"
MATTERMOST_CHANNEL = "teststat"


def post_message(message, url=MATTERMOST_URL, channel=MATTERMOST_CHANNEL):
    """Post given message to the Mattermost channel hooked with the given URL"""

    frame = "### **#### TESTstat Summary ####**\n"
    payload = {
        "channel": channel,
        "text": frame + message
    }
    requests.post(url, data=json.dumps(payload))


def get_insight(stats):

    insight_failure = defaultdict(int)
    insight_time_out = defaultdict(int)

    total_failures = len(stats["failure"])
    total_time_outs = len(stats["time_out"])

    for stat_failure in stats["failure"]:
        insight_failure[stat_failure.data_call] += 1
    for stat_time_out in stats["time_out"]:
        insight_time_out[stat_time_out.data_call] += 1

    failure_counter = [(data_call, count) for data_call, count in insight_failure.items()]
    failure_counter.sort(key=lambda tuple: tuple[1], reverse=True)
    time_out_counter = [(data_call, count) for data_call, count in insight_time_out.items()]
    time_out_counter.sort(key=lambda tuple: tuple[1], reverse=True)

    insight_failure.clear()
    insight_time_out.clear()

    for tuple in failure_counter:
        insight_failure[tuple[0]] = f"{tuple[1]} ({round(tuple[1] * 100 / total_failures)}%)"
    for tuple in time_out_counter:
        insight_time_out[tuple[0]] = f"{tuple[1]} ({round(tuple[1] * 100 / total_time_outs)}%)"

    output = ""

    if insight_failure:

        max_dc_length = len(max(failure_counter, key=lambda tuple: len(tuple[0]))[0]) + 1

        output += "\nFailed Data Calls:\n\n"

        for key, value in insight_failure.items():
            pad = max_dc_length - len(key)
            output += f"- {key}:{pad*' '}{value}\n"
        output += "\n"

    if insight_time_out:

        max_dc_length = len(max(time_out_counter, key=lambda tuple: len(tuple[0]))[0]) + 1

        output += "\nTimed-out Data Calls:\n"

        for key, value in insight_time_out.items():
            pad = max_dc_length - len(key)
            output += f"- {key}:{pad*' '}{value}\n"
        output += "\n"

    return output


async def run_cicd_tests(host, mode, file_name, preferred_version, batch_size):
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

    header = f"Host: {host} | Mode: {mode}"
    if test_cases_path:
        header += f" | Tests: {test_cases_path}"
    if preferred_version != "default":
        header += f" | Preferred Version: {preferred_version}"
    header += f" | Batch Size: {batch_size}"

    print(header, "\n")

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

    total_failures = len(stats["failure"])
    total_time_outs = len(stats["time_out"])

    msg_insight = get_insight(stats)

    print("\n", "#" * 150, "\n")
    print("Test Cases:           ", total_test_cases)
    print("Failed Test Cases:    ", total_failures)
    print("Timed-out Test Cases: ", total_time_outs, "\n")
    print(msg_insight)

    # Prepare a message to be post in Mattermost channel
    msg_header = header + "\n\n"
    msg_total = "**- Total Test Cases:**           " + str(total_test_cases) + "\n"
    msg_failure = "**- Failed Test Cases:**         " + str(total_failures)
    msg_failure += "     :flan_cool:\n" if not total_failures else "\n"
    msg_time_out = "**- Timed-out Test Cases:** " + str(total_time_outs)
    msg_time_out += "     :flan_cool:\n" if not total_time_outs else "\n"
    post_message(msg_header + msg_total + msg_failure + msg_time_out + msg_insight)

    if stats["time_out"] or stats["failure"]:
        sys.exit(1)
    else:
        sys.exit(0)
