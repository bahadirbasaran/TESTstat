# This file contains values for the required and optional parameters

import datetime as dt
from sys import maxsize

DATE_BEFORE_TODAY = str(dt.datetime.now() - dt.timedelta(weeks=4))[:10] + "T12:00:00"
DATE_BEFORE_TODAY_2 = str(dt.datetime.now() - dt.timedelta(weeks=4))[:10] + "T11:00:00"
DATE_AFTER_TODAY = str(dt.datetime.now() + dt.timedelta(days=1))[:10] + "T12:00:00"
VALID_BOOLS = ["True", "0"]
VALID_NUMBERS = ["0", "1000"]
INVALID_NUMBERS = [str(maxsize * 2), "-1", "1.2", "loremipsum"]

# Required parameters
resource_asn_200 = ["3333", "3333&3303"]
resource_asn_400 = ["loremipsum", "loremipsum&3333", ""]

resource_prefix_200 = ["193.0.0.0/21", "193/21&191/21"]
resource_prefix_400 = ["loremipsum", "loremipsum&193/21", ""]

resource_ip_200 = ["193.0.0.0", "193.0.0.0&191.0.0.0", "::5f3b:aa35"]
resource_ip_400 = ["loremipsum", "loremipsum&193.0.0.0", ""]

resource_hostname_200 = ["www.ripe.net", "www.ripe.net&www.google.com"]
resource_hostname_400 = ["loremipsum", "loremipsum&www.google.com", ""]

resource_geo_200 = ["nl", "nl&at"]
resource_geo_400 = ["loremipsum", "loremipsum&at", ""]

resource_200 = ["3333", "3333&3303"]
resource_400 = ["loremipsum", "loremipsum&3333", ""]
prefix_200 = ["193.0.0.0/21", "193/21&191/21"]
prefix_400 = ["loremipsum", "loremipsum&193/21", ""]

resource_empty = [""]
resource_req_400 = [
    "loremipsum",
    "3333&loremipsum"
]
# resource_groups = [
#     resource_asn_200,
#     resource_prefix_200,
#     resource_ip_200,
#     resource_hostname_200,
#     resource_geo_200,
#     resource_empty,
#     resource_req_400,
# ]
resource_groups = [
    resource_asn_200,
    resource_asn_400,
    resource_prefix_200,
    resource_prefix_400,
    resource_ip_200,
    resource_ip_400,
    resource_hostname_200,
    resource_hostname_400,
    resource_geo_200,
    resource_geo_400
]

# Optional parameters
starttime_200 = [DATE_BEFORE_TODAY, DATE_BEFORE_TODAY_2]
starttime_400 = [DATE_AFTER_TODAY, "loremipsum", ""]

endtime_200 = [DATE_BEFORE_TODAY, DATE_BEFORE_TODAY_2, DATE_AFTER_TODAY]
endtime_400 = ["loremipsum", ""]

time_200 = [DATE_BEFORE_TODAY]
time_400 = [DATE_AFTER_TODAY, "loremipsum", ""]

query_time_200 = [DATE_BEFORE_TODAY]
query_time_400 = [DATE_AFTER_TODAY, "loremipsum", ""]

timestamp_200 = [DATE_BEFORE_TODAY]
timestamp_400 = [DATE_AFTER_TODAY, "loremipsum", ""]

# limit_200 = ["0"]
# limit_400 = ["-1", "0&7"]
limit_200 = VALID_NUMBERS
limit_400 = INVALID_NUMBERS

# max_rows_200 = ["10", "5"]
# max_rows_400 = ["-1", "0", "loremipsum"]
max_rows_200 = VALID_NUMBERS
max_rows_400 = INVALID_NUMBERS

# num_hours_200 = [20]
# num_hours_400 = ["-1", "loremipsum"]
num_hours_200 = VALID_NUMBERS
num_hours_400 = INVALID_NUMBERS

# min_peers_200 = ["5"]
# min_peers_400 = ["-1", "0&7"]
min_peers_200 = VALID_NUMBERS
min_peers_400 = INVALID_NUMBERS

# max_samples_200 = [20]
# max_samples_400 = ["-1", "loremipsum"]
max_samples_200 = VALID_NUMBERS
max_samples_400 = INVALID_NUMBERS

# max_related_200 = ["10", "5"]
# max_related_400 = ["-1", "0", "loremipsum"]
max_related_200 = VALID_NUMBERS
max_related_400 = INVALID_NUMBERS

# look_back_limit_200 = [85000]
# look_back_limit_400 = ["-85000"]
look_back_limit_200 = VALID_NUMBERS
look_back_limit_400 = INVALID_NUMBERS

# min_peers_seeing_200 = [20]
# min_peers_seeing_400 = ["-1", "20&10"]
min_peers_seeing_200 = VALID_NUMBERS
min_peers_seeing_400 = INVALID_NUMBERS

# min_sampling_period_200 = ["4"]
# min_sampling_period_400 = ["-1", "4&6", "loremipsum"]
min_sampling_period_200 = VALID_NUMBERS
min_sampling_period_400 = INVALID_NUMBERS

# v4_full_prefix_threshold_200 = [20]
# v4_full_prefix_threshold_400 = ["-1", "loremipsum"]
v4_full_prefix_threshold_200 = VALID_NUMBERS
v4_full_prefix_threshold_400 = INVALID_NUMBERS

# v6_full_prefix_threshold_200 = ["5"]
# v6_full_prefix_threshold_400 = ["-1", "0&7"]
v6_full_prefix_threshold_200 = VALID_NUMBERS
v6_full_prefix_threshold_400 = INVALID_NUMBERS

# ipv4_200 = ["true", "false", "0"]
# ipv4_400 = ["loremipsum", "5"]
ipv4_200 = VALID_BOOLS
ipv4_400 = ["loremipsum"]

# ipv6_200 = ["true", "false", "0"]
# ipv6_400 = ["loremipsum", "5"]
ipv6_200 = VALID_BOOLS
ipv6_400 = ["loremipsum"]

# list_asns_200 = ["true", "false"]
# list_asns_400 = ["loremipsum"]
list_asns_200 = VALID_BOOLS
list_asns_400 = ["loremipsum"]

# delegated_200 = ["true", "false"]
# delegated_400 = ["loremipsum", "5"]
delegated_200 = VALID_BOOLS
delegated_400 = ["loremipsum"]

# hide_empty_samples_200 = ["true", "false"]
# hide_empty_samples_400 = ["loremipsum", "5"]
hide_empty_samples_200 = VALID_BOOLS
hide_empty_samples_400 = ["loremipsum"]

# list_prefixes_200 = ["true", "false"]
# list_prefixes_400 = ["loremipsum", "5"]
list_prefixes_200 = VALID_BOOLS
list_prefixes_400 = ["loremipsum"]

# compare_with_live_200 = ["true", "false"]
# compare_with_live_400 = ["loremipsum"]
compare_with_live_200 = VALID_BOOLS
compare_with_live_400 = ["loremipsum"]

# all_level_more_specifics_200 = ["True", "False"]
# all_level_more_specifics_400 = ["loremipsum", "5"]
all_level_more_specifics_200 = VALID_BOOLS
all_level_more_specifics_400 = ["loremipsum"]

# unix_timestamps_200 = ["True", "False"]
# unix_timestamps_400 = ["loremipsum", "5"]
unix_timestamps_200 = VALID_BOOLS
unix_timestamps_400 = ["loremipsum"]

# best_match_only_200 = ["true", "false"]
# best_match_only_400 = ["loremipsum", "5"]
best_match_only_200 = VALID_BOOLS
best_match_only_400 = ["loremipsum"]

# normalise_visibility_200 = ["true", "false"]
# normalise_visibility_400 = ["loremipsum"]
normalise_visibility_200 = VALID_BOOLS
normalise_visibility_400 = ["loremipsum"]

# include_first_hop_200 = ["true", "false"]
# include_first_hop_400 = ["loremipsum", "5"]
include_first_hop_200 = VALID_BOOLS
include_first_hop_400 = ["loremipsum"]

lod_200 = ["0", "1", "2"]
# lod_400 = ["loremipsum"]
lod_400 = INVALID_NUMBERS

# family_200 = ["4", "6", "6&4"]
# family_400 = ["-1", "3", "loremipsum"]
family_200 = ["4", "6", "6&4"]
family_400 = INVALID_NUMBERS

# version_200 = ["4"]
# version_400 = ["-1", "4&2", "loremipsum"]
version_200 = ["4", DATE_BEFORE_TODAY]
version_400 = INVALID_NUMBERS

noise_200 = ["keep", "filter"]
noise_400 = ["loremipsum"]

include_200 = ["more_specific", "low_visibility_flag"]
include_400 = ["loremipsum"]

types_200 = ["o", "t", "o&t"]
types_400 = ["loremipsum"]

asn_types_200 = ["o", "t", "o&t"]
asn_types_400 = ["loremipsum"]

sort_by_200 = ["geo", "count", "location"]
sort_by_400 = ["geo&location", "loremipsum"]

v4_format_200 = ["prefix", ""]
v4_format_400 = ["loremipsum"]

af_200 = ["v4", "v6", "v4&v6"]
af_400 = ["loremipsum"]

resolution_200 = ["1d"]
resolution_400 = ["1", "2a", "loremipsum"]

method_200 = ["overview", "test", "details", "progress"]
method_400 = ["loremipsum"]

# rrcs_200 = ["0"]
# rrcs_400 = ["-1", "0&7"]
rrcs_200 = ["0", "4&12"]
rrcs_400 = ["4&2a", "12&-1", "loremipsum"]

object_200 = [*resource_asn_200, *resource_prefix_200]
object_400 = [*resource_asn_400, *resource_prefix_400]
type_200 = ["aut-num", "inetnum", "person"]
type_400 = ["loremipsum", ""]
source_200 = ["RIPE", "APNIC"]
source_400 = ["loremipsum", ""]


resource_optional_200 = [
    res_ind
    for res in [resource_asn_200, resource_prefix_200, resource_ip_200]
    for res_ind in res
]
resource_optional_400 = [
    res_ind for res in [resource_geo_200, resource_req_400] for res_ind in res
]
