import os
import csv
import asyncio
from math import ceil
from collections import Counter
from datetime import datetime
from matplotlib.scale import FuncScale
import matplotlib.pyplot as plt

from google.cloud import storage

from core.teststat import TestStat
from core.utils import MessageEnum, MATTERMOST_OKR_TABLE_FRAME, PLOT_COLORS, \
    get_batch, parse_csv, parse_row, post_mattermost_message, scale_plot, scale_plot_inverse


okr_data_calls = [
    "abuse-contact-finder",
    "address-space-hierarchy",
    "announced-prefixes",
    "as-path-length",
    "atlas-targets",
    "country-resource-stats",
    "looking-glass",
    "network-info",
    "prefix-overview",
    "reverse-dns-ip",
    "rir",
    "rir-geo",
    "routing-status",
    "rpki-validation",
    "whois"
]


def post_data_to_GCS(file_path):
    """
    Upload given file to the public TESTstat bucket in Google Cloude Storage.
    Beware, this cloud bucket was created to store only insensitive data!
    It does not contain anything related RIPEstat codebase.
    """

    file_name = file_path[:-4].split('/')[-1]
    bucket_name = "stat_bucket"
    bucket_url = "https://storage.googleapis.com/stat_bucket/"

    client = storage.Client.from_service_account_json(json_credentials_path="") # TODO: credentials are required to be hidden.
    bucket = storage.Bucket(client, bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_path)

    return bucket_url + file_name


async def run_okr_tests(host, batch_size):
    """Run the OKR test cases in data/okr_tests/okr_tests.csv for given host"""

    async def _run_routine(row):
        
        data_call, test_input, expected_output = parse_row(row)

        test_output, url = await teststat.run_test(data_call, test_input, expected_output)

        if test_output == MessageEnum.TIMEOUT:
            return

        if (expected_output["status_code"] != "500" and test_output) or \
                ("status_code" in test_output and
                    (expected_output["status_code"] == str(test_output["status_code"]) == "500")):
            failures.append((data_call, url))

    teststat = TestStat(host)

    current_date = datetime.now().strftime("%d/%m/%y")

    stat_source = "data/okr_tests/" + host.split('.')[0] + "_okr_stats.csv"
    test_source = "data/okr_tests/okr_tests.csv"
    image_path = stat_source[:-4] + ".png"
    msg_table = MATTERMOST_OKR_TABLE_FRAME

    failures = []
    date_stats = {"dates": []}
    test_cases = parse_csv(test_source, [], []) # Yes I know this smells, but this is intended to be a quick patch.
    tests_per_dc = Counter(test[0] for _, test, _ in test_cases)
    total_test_cases = len(test_cases)
    num_batches = ceil(total_test_cases / batch_size)

    # Create an event loop for a batch of coroutines, and proceed to the next when it's done
    for batch_index, batch in enumerate(get_batch(test_cases, batch_size), 1):
        await asyncio.gather(*[_run_routine(row) for _, row, _ in batch])
        print(f"-> Batch {batch_index}/{num_batches} has been completed!")

    # Close the session when all batches are done
    await teststat.session.close()

    num_failure = len(failures)
    failures_per_dc = {}
    for dc_failure_tuple in failures:
        if dc_failure_tuple[0] not in failures_per_dc:
            failures_per_dc[dc_failure_tuple[0]] = [dc_failure_tuple[1]]
        else:
            failures_per_dc[dc_failure_tuple[0]].append(dc_failure_tuple[1])
    for okr_dc in okr_data_calls:
        if okr_dc not in failures_per_dc:
            failures_per_dc[okr_dc] = []

    if not os.path.isfile(stat_source):
        with open(stat_source, 'w') as csv_file:
            csv_file.write("date,data_call,num_tests,num_failures\n")
    
    with open(stat_source, 'a') as csv_file:
        for data_call, failures in failures_per_dc.items():
            csv_file.write(f"{current_date},{data_call},{tests_per_dc[data_call]},{len(failures)}\n")

    msg_table += f"|Total|{total_test_cases:,}|{num_failure:,}||\n"
    for data_call, failures in failures_per_dc.items():
        if failures:
            msg_table += f"|{data_call}|{tests_per_dc[data_call]:,}|{len(failures):,}|{failures[0]}|\n"
        else:
            msg_table += f"|{data_call}|{tests_per_dc[data_call]:,}|0||\n"

    with open(stat_source, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)

        for index, row in enumerate(csv_reader):
            if index == 0 or row[0] != date_stats["dates"][-1]:
                date_stats["dates"].append(row[0])

            if row[1] not in date_stats:
                date_stats[row[1]] = [int(row[3])]
            else:
                date_stats[row[1]].append(int(row[3]))

    x_axis = [datetime.strptime(date, "%d/%m/%y").date() for date in date_stats.pop("dates")]
    y_total = []
    for index in range(len(x_axis)):
        y_total.append(sum(map(lambda failures: int(failures[index]), date_stats.values())))
    
    with plt.style.context("seaborn"):

        _, ax = plt.subplots()

        plt.plot(x_axis, y_total, label="Total", color="red")
        for data_call, failures in date_stats.items():
            plt.plot(x_axis, failures, label=data_call, color=PLOT_COLORS.pop())

        scale = FuncScale(ax, functions=(scale_plot, scale_plot_inverse))
        ax.set_yscale(scale)

        y_ticks = [0, 5, 10, 15, 20, 40, 60, 80, 100, 200, 300, 400, 500, 1000, 2000, 3000, 4000]
        plt.yticks(y_ticks, y_ticks)

        plt.gcf().autofmt_xdate()
        plt.xticks(x_axis)
        
        plt.legend(loc='center left', bbox_to_anchor=[1, 0.5], title='Data Calls')
        plt.title("Number of Failures")
        plt.tight_layout()
        
        plt.savefig(stat_source[:-4])

    message_payload = f"**Host:** {host}   |   **Test Source:** {test_source}\n\n"
    message_payload += msg_table

    # Update the image in the TESTstat Google Cloud Storage bucket
    image_url = post_data_to_GCS(image_path)

    post_mattermost_message(
        "TESTstat Weekly OKR Report",
        message_payload,
        "teststat",
        image_url
    )