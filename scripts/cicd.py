import asyncio
from math import ceil
from collections import Counter
from datetime import datetime

from core.teststat import TestStat
from core.utils import (
    FailureStat,
    TimeoutStat,
    parse_csv,
    parse_row,
    get_batch,
    post_slack_message,
    process_stats,
    filter_repeating_stats)


async def run_cicd_tests(
    host,
    batch_size,
    test_source,
    random,
    preferred_data_calls,
    excluded_data_calls,
    slack_hooks
):
    """Run CICD test cases for given host and given test source"""

    async def _run_routine(row_index, row, dc_version):

        data_call, test_input, expected_output = parse_row(row)
        if dc_version:
            test_input += f"&preferred_version={dc_version}"

        test_output, url = await teststat.run_test(data_call, test_input, expected_output)

        if dc_version:
            data_call += f"_{dc_version}"

        # TODO: differentiate test_output for different kind of integers in MessageEnum
        if isinstance(test_output, int):
            stat = TimeoutStat(
                test_case=row_index,
                data_call=data_call,
                url=url,
                expected_output=expected_output
            )
            stats["time_out"].append(stat)

        elif (expected_output["status_code"] != "500" and test_output) or \
                ("status_code" in test_output and
                    (expected_output["status_code"] == str(test_output["status_code"]) == "500")):
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

    test_cases = parse_csv(test_source, preferred_data_calls, excluded_data_calls, random, shuffle=True)

    test_counts_per_dc = Counter(
        f"{test[0]}_{version}" if version else test[0] for _, test, version in test_cases
    )
    total_test_cases = len(test_cases)
    num_batches = ceil(total_test_cases / batch_size)

    if batch_size == 1:
        previous_batch_dc = None

    print("\n", "#" * 100, "\n\n")
    print(f"Host: {host}   |   Test Source: {test_source}\n\n")

    for test_run in range(1, 2):
        print(f"Initiating test run: {test_run}")
    
        # Create an event loop for a batch of coroutines, and proceed to the next when it's done
        for batch_index, batch in enumerate(get_batch(test_cases, batch_size), 1):

            # In synchronous run (regression testing), sleep more between test cases with data calls
            # that would use the same backend to avoid rate limiting applied by the relevant backend.
            if batch_size == 1:
                current_batch_dc = batch[0][1][0]
                if previous_batch_dc and (current_batch_dc[:2] == previous_batch_dc[:2]):
                    await asyncio.sleep(3)
                else:
                    await asyncio.sleep(0.5)

                previous_batch_dc = current_batch_dc
            
            else:
                await asyncio.sleep(1)

            await asyncio.gather(
                *[_run_routine(row_index, row, version) for row_index, row, version in batch]
            )
            print(f"-> Batch {batch_index}/{num_batches} has been completed!")

    # Close the session when all batches are done
    await teststat.session.close()

    stats["failure"] = filter_repeating_stats(stats["failure"], test_run)
    stats["time_out"] = filter_repeating_stats(stats["time_out"], test_run)
    stats["failure"].sort(key=lambda tuple: tuple.test_case)
    stats["time_out"].sort(key=lambda tuple: tuple.test_case)

    num_failure = len(stats["failure"])
    num_time_out = len(stats["time_out"])

    # TODO: The following block may fail for nested parameters!
    if stats["failure"]:

        print("\n\nFAILED TEST CASES:")

        for tuple in stats["failure"]:
            print(
                f"\nTest Case: {tuple.test_case} | Data Call: {tuple.data_call} | URL: {tuple.url}"
            )

            for param, expected_value in tuple.expected_output.items():
                print(
                    f"--> Parameter '{param}'"
                    f"  ||  Expected: {expected_value} | Actual: {tuple.actual_output[param]}"
                )
            if "error" in tuple.actual_output:
                print("----> Error: ", tuple.actual_output["error"])

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

    print("\n", "#" * 100, "\n")
    if not random:
        print(f"Test Cases:           {total_test_cases:,}")
    else:
        print(f"Test Cases:           {total_test_cases:,} (Random {random} test cases per DC)")
    print(f"Failed Test Cases:    {num_failure:,}")
    print(f"Timed-out Test Cases: {num_time_out:,}\n")

    if not slack_hooks:
        return
    
    current_date = datetime.now().strftime("%d/%m/%y")
    report_label = ":red_circle:" if num_failure or num_time_out else ":large_green_circle:"

    header_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{report_label} TESTstat Regression Report - {current_date}"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Host: * <https://{host}|{host}>"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Total Test Cases: * {total_test_cases:,}" if not random \
                        else f"*Total Test Cases: * {total_test_cases:,}\nRandom {random} tests per DC"
                }
            ]
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Failures: * {num_failure:,}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Time-outs: * {num_time_out:,}"
                }
            ]
        },
        {"type": "divider"},
        {"type": "divider"}
    ]

    if num_failure + num_time_out == total_test_cases:
        del header_blocks[2:]
        header_blocks[1]["fields"][1]["text"] = f"\n\n\n*An error occurred during the connection!*"
        post_slack_message({"blocks": header_blocks})
        return

    message_blocks = []

    if num_failure or num_time_out:

        processed_stats = process_stats(stats)

        for data_call, data_call_stats in processed_stats.items():
            
            num_test = test_counts_per_dc[data_call]
            data_call = data_call.replace('-', ' ').replace('_', " v").title()
            num_failure = len(data_call_stats["failed_queries"])
            num_time_out = len(data_call_stats["timed_out_queries"])

            block = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Data Call: * {data_call}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*# Tests | Failures | Time-outs: * {num_test} *|* {num_failure} *|* {num_time_out}"
                    }
                ]
            }

            for block_label, key, url_label in zip(
                ["Failures", "Time-outs"],
                ["failed_queries", "timed_out_queries"],
                ["Failed Request", "Timed-out Request"]
            ):
                text = f"*{block_label}:*\n"
                for idx, url in enumerate(data_call_stats[key], 1):
                    text += f"<{url}|{url_label} {idx}>\n"

                block["fields"].append({
                    "type": "mrkdwn",
                    "text": text
                })

            message_blocks.append(block)
            message_blocks.append({"type": "divider"})


    post_slack_message({"blocks": header_blocks + message_blocks})
