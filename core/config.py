# VERBOSE_PARAMS keeps the parameters that contain list of parameters

VERBOSE_PARAMS = [
    "exact",
    "more_specific",
    "less_specific",
    "assignments",
    "allocations",
    "ip_stats",
    "iana",
    "ripencc",
    # "iana->timelines",
    # "ripencc->timelines",
    "prefixes",
    "stats",
]


# Conditional Flags
    
ALL = "All following are True"
ANY = "At least one of following is True"

INCLUDE = "assert expected_output[param] in test_output['data'][param]"
MATCH = "assert expected_output[param] == test_output['data'][param]"
COMPARE = "quantative comparisons"
TRIM_AS = (
    "if expected_output[param].startswith('as'):"
        "expected_output[param] = expected_output[param][2:]"
)
NOT_EMPTY = (
    "if expected_output[param] == 'not empty':"
        "assert test_output['data'][param]"
)


# Data Call Mapping

class CommonParamsEnum():

    WHOIS_PARAMS = {
        "inetnum": [ANY, NOT_EMPTY, MATCH],
        "netname": [ANY, NOT_EMPTY, MATCH],
        "descr": [ANY, NOT_EMPTY, MATCH],
        "org": [ANY, NOT_EMPTY, MATCH],
        "remarks": [ANY, NOT_EMPTY, MATCH],
        "country": [ANY, NOT_EMPTY, MATCH],
        "admin-c": [ANY, NOT_EMPTY, MATCH],
        "tech-c": [ANY, NOT_EMPTY, MATCH],
        "status": [ANY, NOT_EMPTY, MATCH],
        "mnt-by": [ANY, NOT_EMPTY, MATCH],
        "mnt-lower": [ANY, NOT_EMPTY, MATCH],
        "mnt-routes": [ANY, NOT_EMPTY, MATCH],
        "created": [ANY, NOT_EMPTY, MATCH],
        "last-modified": [ANY, NOT_EMPTY, MATCH],
        "source": [ANY, NOT_EMPTY, MATCH]
    }

    AS_PATH_STATS = {
        "avg": [ANY, NOT_EMPTY, MATCH, COMPARE],
        "max": [ANY, NOT_EMPTY, MATCH, COMPARE],
        "min": [ANY, NOT_EMPTY, MATCH, COMPARE],
        "sum": [ANY, NOT_EMPTY, MATCH, COMPARE]
    }

    TIMELINES = {
        "starttime": [ANY, NOT_EMPTY, MATCH],
        "endtime": [ANY, NOT_EMPTY, MATCH]
    }

DATA_CALL_MAP = {

    "abuse-contact-finder": {
        "data_call_name": "Abuse Contact Finder",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "abuse_contacts": [ANY, NOT_EMPTY, INCLUDE],
            "authoritative_rir": [ANY, NOT_EMPTY, MATCH],
            "earliest_time": [ANY, NOT_EMPTY, MATCH],
            "latest_time": [ANY, NOT_EMPTY, MATCH],
            "parameters": {
                "resource": [TRIM_AS, ANY, NOT_EMPTY, MATCH]
            },
        }
    },

    "address-space-hierarchy": {
        "data_call_name": "Address Space Hierarchy",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "exact": CommonParamsEnum.WHOIS_PARAMS,
            "more_specific": CommonParamsEnum.WHOIS_PARAMS,
            "less_specific": CommonParamsEnum.WHOIS_PARAMS,
            "rir": [ANY, NOT_EMPTY, MATCH],
            "query_time": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH],
            "parameters": {
                "resource": [ANY, NOT_EMPTY, MATCH]
            }
        }
    },

    "address-space-usage": {
        "data_call_name": "Address Space Usage",
        "required_params": ["resource"],
        "optional_params": ["all_level_more_specifics"],
        "output_params": {
            "assignments": {
                "address_range": [ANY, NOT_EMPTY, MATCH],
                "asn_name": [ANY, NOT_EMPTY, MATCH],
                "status": [ANY, NOT_EMPTY, MATCH],
                "parent_allocation": [ANY, NOT_EMPTY, MATCH]
            },
            "allocations": {
                "allocation": [ANY, NOT_EMPTY, MATCH],
                "asn_name": [ANY, NOT_EMPTY, MATCH],
                "status": [ANY, NOT_EMPTY, MATCH],
                "assignments": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "ip_stats": {
                "status": [ANY, NOT_EMPTY, MATCH],
                "ips": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "query_time": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH]
        }
    },

    "allocation-history": {
        "data_call_name": "Allocation History",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "iana": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "status": [ANY, NOT_EMPTY, MATCH],
                # "timelines": TIMELINES
            },
            "ripencc": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "status": [ANY, NOT_EMPTY, MATCH],
                # "timelines": TIMELINES
            },
            "resource": [ANY, NOT_EMPTY, MATCH],
            "query_starttime": [ANY, NOT_EMPTY, MATCH],
            "query_endtime": [ANY, NOT_EMPTY, MATCH],
        }
    },

    "announced-prefixes": {
        "data_call_name": "Announced Prefixes",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "min_peers_seeing"],
        "output_params": {
            "prefixes": {
                "prefix": [ANY, NOT_EMPTY, MATCH],
                # "timelines": TIMELINES,
            },
            "earliest_time": [ANY, NOT_EMPTY, MATCH],
            "latest_time": [ANY, NOT_EMPTY, MATCH],
            "query_starttime": [ANY, NOT_EMPTY, MATCH],
            "query_endtime": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH]
        }
    },
    "as-overview": {
        "data_call_name": "AS Overview",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "block": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "desc": [ANY, NOT_EMPTY, MATCH],
                "name": [ANY, NOT_EMPTY, MATCH]
            },
            "holder": [ANY, NOT_EMPTY, MATCH],
            "announced": [ANY, NOT_EMPTY, MATCH],
            "query_starttime": [ANY, NOT_EMPTY, MATCH],
            "query_endtime": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH]
        }
    },

    "as-path-length": {
        "data_call_name": "AS Path Length",
        "required_params": ["resource"],
        "optional_params": ["sort_by"],
        "output_params": {
            "stats": {
                "count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "location": [ANY, NOT_EMPTY, MATCH],
                "stripped": CommonParamsEnum.AS_PATH_STATS,
                "unstripped": CommonParamsEnum.AS_PATH_STATS
            },
            "sort_by": [ANY, NOT_EMPTY, MATCH],
            "query_time": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH]
        }
    },

}

# "blocklist": {
#     "data_call_name": "Blocklist",
#     "required_params": ["resource", "starttime"],
#     "optional_params": ["endtime"],
#     "output_params": {
#         "source": None,
#         "prefix": None,
#         "details": None,
#         "timelines": None,
#         "query_starttime": None,
#         "query_endtime": None,
#         "resource": None
#     }
# },

# "dns-chain": {
#     "data_call_name": "Dns Chain",
#     "required_params": ["resource"],
#     "optional_params": [],
#     "output_params": {
#         "forward_nodes": None,
#         "reverse_nodes": None,
#         "nameservers": None,
#         "authoritative_nameservers": None,
#         "query_time": None,
#         "resource": None
#     }
# }