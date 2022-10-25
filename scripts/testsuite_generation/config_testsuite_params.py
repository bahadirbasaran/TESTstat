# This file contains configuration for the automated test suite generation
# This file holds information about the required and optional parameters for the datacalls
# If there is only one required parameter with more values types (asn and ip address, for example)
# they should be passed in *args format
# In case there are more required parameters, they should be added as separate lists containing
# parameter name. Check, that group parameter_name_200
# and parameter_name_200 exists in the file config_autogeneration_param_values. As an example,
# see datacall "rpki-validation"
# For the optional parameters, the list of strings (parameters names) is expected

import config_testsuite_param_values as ctpv

# Data calls' required parameters
resource_params = {
    "rpki-validation": [["resource"], ["prefix"]],
    "abuse-contact-finder": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_hostname_200,
    ],
    "address-space-hierarchy": [
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_hostname_200,
    ],
    "address-space-usage": [
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_hostname_200,
    ],
    "allocation-history": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_hostname_200,
    ],
    "announced-prefixes": [*ctpv.resource_asn_200],
    "as-overview": [*ctpv.resource_asn_200],
    "as-path-length": [*ctpv.resource_asn_200],
    "as-routing-consistency": [*ctpv.resource_asn_200],
    "asn-neighbours": [*ctpv.resource_asn_200],
    "asn-neighbours-history": [*ctpv.resource_asn_200],
    "atlas-probe-deployment": [*ctpv.resource_asn_200, *ctpv.resource_geo_200],
    "atlas-probes": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_geo_200,
    ],
    "atlas-targets": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "bgp-state": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "bgp-update-activity": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "bgp-updates": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "bgplay": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "blocklist": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "country-asns": [*ctpv.resource_geo_200],
    "country-resource-list": [*ctpv.resource_geo_200],
    "country-resource-stats": [*ctpv.resource_geo_200],
    "dns-chain": [*ctpv.resource_ip_200, *ctpv.resource_hostname_200],
    "historical-whois": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "iana-registry-info": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "looking-glass": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "maxmind-geo-lite": [*ctpv.resource_prefix_200, *ctpv.resource_ip_200],
    "maxmind-geo-lite-announced-by-as": [*ctpv.resource_asn_200],
    "network-info": [*ctpv.resource_prefix_200, *ctpv.resource_ip_200],
    "prefix-count": [*ctpv.resource_asn_200],
    "prefix-overview": [*ctpv.resource_prefix_200, *ctpv.resource_ip_200],
    "prefix-routing-consistency": [*ctpv.resource_prefix_200, *ctpv.resource_ip_200],
    "prefix-size-distribution": [*ctpv.resource_asn_200],
    "related-prefixes": [*ctpv.resource_prefix_200],
    "reverse-dns": [*ctpv.resource_prefix_200, *ctpv.resource_ip_200],
    "reverse-dns-consistency": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_geo_200,
        *ctpv.resource_hostname_200,
    ],
    "reverse-dns-ip": [*ctpv.resource_ip_200],
    "rir": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_geo_200,
        *ctpv.resource_hostname_200,
    ],
    "rir-geo": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_geo_200,
        *ctpv.resource_hostname_200,
    ],
    "rir-prefix-size-distribution": [*ctpv.resource_prefix_200, *ctpv.resource_ip_200],
    "rir-stats-country": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_geo_200,
    ],
    "ris-asns": [*ctpv.resource_empty],
    "ris-first-last-seen": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_geo_200,
    ],
    "ris-full-table-threshold": [*ctpv.resource_empty],
    "ris-peer-count": [*ctpv.resource_empty],
    "ris-peerings": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "ris-peers": [*ctpv.resource_empty],
    "ris-prefixes": [*ctpv.resource_asn_200],
    "routing-history": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "routing-status": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "rpki-history": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_geo_200,
    ],
    "searchcomplete": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_geo_200,
    ],
    "speedchecker-bandwidth-measurements": [
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "visibility": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
    ],
    "whats-my-ip": [*ctpv.resource_empty],
    "whois": [
        *ctpv.resource_asn_200,
        *ctpv.resource_prefix_200,
        *ctpv.resource_ip_200,
        *ctpv.resource_geo_200,
    ],
    "zonemaster": [*ctpv.resource_hostname_200],
    # "whois-object-last-updated": []# in maintanence currently
}

# Data calls' optional parameters
optional_params = {
    "address-space-usage": ["all_level_more_specifics"],
    "allocation-history": ["starttime", "endtime"],
    "announced-prefixes": ["starttime", "endtime", "min_peers_seeing"],
    "as-path-length": ["sort_by"],
    "asn-neighbours": ["query_time"],
    "asn-neighbours-history": ["starttime", "endtime", "max_rows"],
    "atlas-probe-deployment": ["starttime", "endtime"],
    "bgp-state": ["timestamp", "rrcs", "unix_timestamps"],
    "bgp-update-activity": [
        "starttime",
        "endtime",
        "max_samples",
        "min_sampling_period",
        "num_hours",
        "hide_empty_samples",
    ],
    "bgp-updates": ["starttime", "endtime", "rrcs", "unix_timestamps"],
    "bgplay": ["starttime", "endtime", "rrcs", "unix_timestamps"],
    "blocklist": ["starttime", "endtime"],
    "country-asns": ["query_time", "lod"],
    "country-resource-list": ["time", "v4_format"],
    "country-resource-stats": ["starttime", "endtime", "resolution"],
    "historical-whois": ["version"],
    "iana-registry-info": ["resource_optional", "best_match_only"],
    "looking-glass": ["look_back_limit"],
    "prefix-count": ["starttime", "endtime", "resolution", "min_peers_seeing"],
    "prefix-overview": ["min_peers_seeing", "query_time", "max_related"],
    "prefix-size-distribution": ["timestamp", "min_peers_seeing"],
    "reverse-dns-consistency": ["ipv4", "ipv6"],
    "rir": ["starttime", "endtime", "lod"],
    "rir-geo": ["query_time"],
    "rir-prefix-size-distribution": ["query_time"],
    "rir-stats-country": ["query_time"],
    "ris-asns": ["list_asns", "asn_types", "query_time"],
    "ris-first-last-seen": ["include"],
    "ris-full-table-threshold": ["query_time"],
    "ris-peer-count": [
        "starttime",
        "endtime",
        "v4_full_prefix_threshold",
        "v6_full_prefix_threshold",
    ],
    "ris-peerings": ["query_time"],
    "ris-peers": ["query_time"],
    "ris-prefixes": ["query_time", "list_prefixes", "types", "af", "noise"],
    "routing-history": [
        "max_rows",
        "include_first_hop",
        "normalise_visibility",
        "min_peers",
        "starttime",
        "endtime",
    ],
    "routing-status": ["min_peers_seeing", "timestamp"],
    "rpki-history": ["family", "resolution", "delegated"],
    "searchcomplete": ["limit"],
    "speedchecker-bandwidth-measurements": ["starttime", "endtime"],
    "visibility": ["query_time", "include"],
    "zonemaster": ["method"],
}
