# This file contains values for the required and Optional parameters
# Required parameters
resource_asn_200 = ["3333", "as3333", "3333&3303"]
resource_asn_400 = ["loremipsum", "loremipsum&3333", ""]

resource_prefix_200 = ["193/21", "193/21&191/21"]
resource_prefix_400 = ["loremipsum", "loremipsum&193/21", ""]

resource_ip_200 = ["193.0.0.0", "193.0.0.0&191.0.0.0"]
resource_hostname_200 = ["www.ripe.net", "www.ripe.net&www.google.com"]
resource_geo_200 = ["nl", "nl&at"]

resource_ip_400 = ["loremipsum", "loremipsum&193.0.0.0", ""]
resource_hostname_400 = ["loremipsum", "loremipsum&www.google.com", ""]
resource_geo_400 = ["loremipsum", "loremipsum&at", ""]

resource_empty = [""]
resource_req_400 = [
    "loremipsum",
    "loremipsum&nl",
    "loremipsum&3333",
    "loremipsum&193/21",
    "loremipsum&193.0.0.0",
]

resource_200 = ["3333", "as3333", "3333&3303"]
resource_400 = ["loremipsum", "loremipsum&3333", ""]
prefix_200 = ["193/21", "193/21&191/21"]
prefix_400 = ["loremipsum", "loremipsum&193/21", ""]

resource_groups = [
    resource_asn_200,
    resource_prefix_200,
    resource_ip_200,
    resource_hostname_200,
    resource_geo_200,
    resource_empty,
    resource_req_400,
]

# Optional params
starttime_200 = ["2020-12-12T12:00"]
starttime_400 = ["2023-12-12T12:00"]

min_peers_seeing_200 = [20]
min_peers_seeing_400 = ["-1", "20&10"]

v4_full_prefix_threshold_200 = [20]
v4_full_prefix_threshold_400 = ["-1", "loremipsum"]

num_hours_200 = [20]
num_hours_400 = ["-1", "loremipsum"]

max_samples_200 = [20]
max_samples_400 = ["-1", "loremipsum"]

look_back_limit_200 = [85000]
look_back_limit_400 = ["-85000"]


ipv4_200 = ["true", "false", "0"]
ipv4_400 = ["loremipsum", "5"]

compare_with_live_200 = ["true", "false"]
compare_with_live_400 = ["loremipsum"]

ipv6_200 = ["true", "false", "0"]
ipv6_400 = ["loremipsum", "5"]

sort_by_200 = ["geo", "count", "location"]
sort_by_400 = ["geo&location", "count&location", "geo&count", "loremipsum"]

query_time_200 = ["2020-12-12T12:00"]
query_time_400 = ["2023-12-12T12:00"]

time_200 = ["2020-12-12T12:00"]
time_400 = ["2023-12-12T12:00"]

all_level_more_specifics_200 = ["True", "False"]
all_level_more_specifics_400 = ["loremipsum", "5"]

version_200 = ["4"]
version_400 = ["-1", "4&2", "loremipsum"]

max_related_200 = ["10", "5"]
max_related_400 = ["-1", "0", "loremipsum"]

v4_format_200 = ["prefix"]
v4_format_400 = ["loremipsum"]

lod_200 = ["0", "1", "2"]
lod_400 = ["loremipsum"]

unix_timestamps_200 = ["True", "False"]
unix_timestamps_400 = ["loremipsum", "5"]

resolution_200 = ["1d", "2m"]
resolution_400 = ["2a", "loremipsum"]

timestamp_200 = ["2020-12-12T12:00"]
timestamp_400 = ["2023-12-12T12:00"]

best_match_only_200 = ["true", "false"]
best_match_only_400 = ["loremipsum", "5"]

rrcs_200 = ["0"]
rrcs_400 = ["-1", "0&7"]

endtime_200 = ["2021-12-12T12:00"]
endtime_400 = ["2023-12-12T12:00"]

asn_types_200 = ["o", "t", "o&t"]
asn_types_400 = ["loremipsum", "m"]

types_200 = ["o", "t", "o&t"]
types_400 = ["loremipsum", "m"]

list_asns_200 = ["true", "false"]
list_asns_400 = ["loremipsum"]

max_rows_200 = ["10", "5"]
max_rows_400 = ["-1", "0", "loremipsum"]

delegated_200 = ["true", "false"]
delegated_400 = ["loremipsum", "5"]

limit_200 = ["0"]
limit_400 = ["-1", "0&7"]

family_200 = ["4", "6", "6&4"]
family_400 = ["-1", "3", "loremipsum"]

method_200 = ["details"]
method_400 = ["loremipsum"]

resource_optional_200 = [
    l1 for res in [resource_asn_200, resource_prefix_200, resource_ip_200] for l1 in res
]
resource_optional_400 = [
    l1 for res in [resource_geo_200, resource_req_400] for l1 in res
]

normalise_visibility_200 = ["true", "false"]
normalise_visibility_400 = ["loremipsum"]

noise_200 = ["keep", "filter"]
noise_400 = ["loremipsum"]

include_200 = ["more_specific", "low_visibility_flag"]
include_400 = ["loremipsum"]

min_sampling_period_200 = ["4"]
min_sampling_period_400 = ["-1", "4&6", "loremipsum"]

hide_empty_samples_200 = ["true", "false"]
hide_empty_samples_400 = ["loremipsum", "5"]

v6_full_prefix_threshold_200 = ["5"]
v6_full_prefix_threshold_400 = ["-1", "0&7"]

list_prefixes_200 = ["true", "false"]
list_prefixes_400 = ["loremipsum", "5"]

af_200 = ["v4", "v6", "v4&v6"]
af_400 = ["loremipsum", "5"]

include_first_hop_200 = ["true", "false"]
include_first_hop_400 = ["loremipsum", "5"]

min_peers_200 = ["5"]
min_peers_400 = ["-1", "0&7"]
