import json
from datetime import datetime

import requests


BATCH_SIZE = 100

MATTERMOST_URL = "https://mattermost.ripe.net/hooks/6xp8tt93i3fwde5d43jegsxi8a"
MATTERMOST_CHANNEL = "ripestat-teststat"
MATTERMOST_NEWLINE = "` `  "
MATTERMOST_TABLE_FRAME = (
    "| Data Call | Failures | Timeouts | Failed & Timed-out URLs |\n"
    "|:----------|:--------:|:--------:|:------------------------|\n"
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


def get_batch(iterable, batch_size):
    """Slice iterable and return batches of batch_size each time"""

    total_length = len(iterable)

    for index in range(0, total_length, batch_size):
        yield iterable[index:min(index + batch_size, total_length)]


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

    