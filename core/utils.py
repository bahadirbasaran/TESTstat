import csv
import json
import random as rand
from datetime import datetime
from collections import defaultdict

import requests

from core.config import MATTERMOST_CHANNEL, MATTERMOST_URL


MATTERMOST_NEWLINE = "` `  "
MATTERMOST_TABLE_FRAME = (
    "| Data Call | Tests | Failures | Timeouts | Failed & Timed-out URLs |\n"
    "|:----------|:-----:|:--------:|:--------:|:------------------------|\n"
)


class MessageEnum():

    NO = 65536
    YES = 16384
    TIMEOUT = 408
    CONNECTION_ERROR = 500
    BAD_GATEWAY = 502
    CRITICAL = 1
    WARNING = 2


def get_innermost_value(param, param_set):
    """Return innermost value of nested parameters"""

    if "->" in param:
        for index, inner_param in enumerate(param.split("->")):

            if index == 0:
                inner_param_value = param_set[inner_param]
            else:
                if isinstance(inner_param_value, list):
                    inner_param_value = inner_param_value[0]

                inner_param_value = inner_param_value[inner_param]
    else:
        inner_param_value = param_set[param]

    return inner_param_value


def filter_param_set(param_set, filtered_param_set={}, current_level=None):
    """
    Make all parameter-value pairs of param_set lower case, trims whitespaces,
    convert bools&numbers into string representations.
    """

    def _f(input):
        return input.lower().replace(' ', '')

    for param, value in param_set.items():

        if isinstance(value, str):
            if current_level:
                filtered_param_set[current_level][_f(param)] = _f(value)
            else:
                filtered_param_set[_f(param)] = _f(value)

        # Bools should be checked first, since Boolean is a subclass of int,
        # any bool variable matches with the following isinstance too.
        elif isinstance(value, bool):
            if current_level:
                filtered_param_set[current_level][_f(param)] = "true" if value else "false"
            else:
                filtered_param_set[_f(param)] = "true" if value else "false"

        elif isinstance(value, (int, float)):
            if current_level:
                filtered_param_set[current_level][_f(param)] = str(value)
            else:
                filtered_param_set[_f(param)] = str(value)

        elif value is None:
            if current_level:
                filtered_param_set[current_level][_f(param)] = "none"
            else:
                filtered_param_set[_f(param)] = "none"

        elif isinstance(value, list):
            new_value = []

            for list_item in value:

                if isinstance(list_item, str):
                    new_value.append(_f(list_item))

                elif isinstance(list_item, bool) and list_item:
                    new_value.append("true")

                elif isinstance(list_item, bool):
                    new_value.append("false")

                elif isinstance(list_item, (int, float)):
                    new_value.append(str(list_item))

                elif list_item is None:
                    new_value.append("none")

                elif isinstance(list_item, list):
                    new_list_item = []

                    for inner_item in list_item:
                        new_list_item.append(filter_param_set(inner_item, {}))

                    new_value.append(new_list_item)

                else:
                    new_value.append(filter_param_set(list_item, {}))

            if current_level:
                filtered_param_set[current_level][_f(param)] = new_value
            else:
                filtered_param_set[_f(param)] = new_value

        else:
            filtered_param_set[param] = {}
            filtered_param_set = filter_param_set(value, filtered_param_set, param)

    return filtered_param_set


def reshape_param_set(param_set):
    """
    param_set:
            param = 'exact->inetnum'          value = 'a'
            param = 'exact->netname'          value = 'b'
            param = 'more_specific'           value = 'notempty'
            param = 'stats->stripped->avg'    value = 'c'
            param = 'stats->stripped->min'    value = 'd'
            param = 'stats->unstripped->avg'  value = 'e'
    =>> reshaped_param_set = {
            'exact': {
                'inetnum': 'a',
                'netname': 'b'
            },

            'more_specific': "notempty",

            'stats': {
                'stripped': {
                    'avg': 'c',
                    'min': 'd'
                },
                'unstripped': {
                    'avg': 'e'
                }
            }
        }
    """

    reshaped_param_set = {}

    for key, value in param_set.items():

        current_dict = reshaped_param_set
        *parts, last = key.split('->')

        if len(parts) > 0 and parts[0] in current_dict and current_dict[parts[0]] == "notempty":
            continue
        else:
            for part in parts:

                if part not in current_dict:
                    current_dict[part] = {}

                if isinstance(current_dict[part], dict):
                    current_dict = current_dict[part]

        current_dict[last] = value

    return reshaped_param_set


def compare_output_equality(comparison_fields, *outputs):
    """
    Compare test outputs and return True if all have the same status code and data.
    If comparison_fields is given, compare only those fields in the response data block.
    """

    # If any of the queries return time-out/exception etc.
    for output in outputs:
        if isinstance(output, int):
            return output

    if not all(str(output["status_code"]) == str(outputs[0]["status_code"]) for output in outputs):
        return False

    # Sort lists to comply with json.dumps (different order produces different results)
    for output in outputs:
        for key, value in output["data"].items():
            if isinstance(value, list):
                output["data"][key] = sorted(value)

    if comparison_fields:

        if not all(
            json.dumps(
                {fld: val for fld, val in output["data"].items() if fld in comparison_fields}
            ).encode('utf-8') ==
            json.dumps(
                {fld: val for fld, val in outputs[0]["data"].items() if fld in comparison_fields}
            ).encode('utf-8')
            for output in outputs
        ):
            return False
        return True

    if not all(
        json.dumps(
            output["data"]).encode('utf-8') == json.dumps(outputs[0]["data"]).encode('utf-8')
        for output in outputs
    ):
        return False
    return True


def post_message(message, url=MATTERMOST_URL, channel=MATTERMOST_CHANNEL):
    """Post given message to the Mattermost channel hooked with the given URL"""

    current_date = datetime.now().strftime("%d/%m/%y")
    frame = f"### TESTstat Report - {current_date}\n"
    payload = {
        "channel": channel,
        "text": frame + message
    }
    requests.post(url, data=json.dumps(payload))


def process_stats(stats, sort_by="count"):
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

    if sort_by == "count":
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
    else:
        data_calls_in_order = list(sorted(processed_stats))

    return {data_call: processed_stats[data_call] for data_call in data_calls_in_order}


def get_batch(iterable, batch_size):
    """Slice iterable and return batches of batch_size each time"""

    total_length = len(iterable)

    for index in range(0, total_length, batch_size):
        yield iterable[index:min(index + batch_size, total_length)]


def get_dc_version_map(preferred_data_calls):
    """Create a data call-version mapping"""

    dc_version_map = {}

    for dc_and_versions in preferred_data_calls.split():
        data_call = dc_and_versions.split('_')[0]
        versions = dc_and_versions.split('_')[1:]
        dc_version_map[data_call] = versions

    return dc_version_map


def parse_csv(csv_path, preferred_data_calls=None, random=None):
    """
    Parse given CSV file and return test cases for all/requested data calls
    If random is given, sample a specific number of test cases per data call
    (implemented only for full run without any data call preference)
    """

    with open(csv_path) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')

        # Skip the header
        next(csv_reader)

        # Filter data calls (with preferred versions) if specified.
        # e.g. preferred_data_calls = ['bgplay', 'abuse-contact-finder_2.0_2.1']
        if preferred_data_calls:
            dc_version_map = get_dc_version_map(preferred_data_calls)

            csv_reader = filter(lambda row: row[0] in dc_version_map, list(csv_reader))

            test_cases = []

            for row_index, row in enumerate(csv_reader, 1):

                # If there is no specific version requested
                if not dc_version_map[row[0]]:
                    test_cases.append((row_index, row, None))
                else:
                    for version in dc_version_map[row[0]]:
                        test_cases.append((row_index, row, version))
        else:
            if not random:
                test_cases = [(row[0], row[1], None) for row in list(enumerate(csv_reader, 1))]
            else:
                test_cases = []
                test_cases_per_dc = defaultdict(list)

                for row in list(csv_reader):
                    test_cases_per_dc[row[0]].append(row)

                for tests in test_cases_per_dc.values():
                    if len(tests) <= random:
                        for test in tests:
                            test_cases.append((len(test_cases) + 1, test, None))
                    else:
                        random_tests = rand.sample(tests, random)
                        for test in random_tests:
                            test_cases.append((len(test_cases) + 1, test, None))

    return test_cases
