# Flags

ALL = "All following are True"
ANY = "At least one of following is True"

INCLUDE = "assert expected_output[param] in test_output['data'][param]"
MATCH = "assert expected_output[param] == test_output['data'][param]"
GTE = "assert test_output['data'][param] >= expected_output[param]"
TRIM_AS = (
    "if expected_output[param].startswith('as'):"
        "expected_output[param] = expected_output[param][2:]"
)
NOT_EMPTY = (
    "if expected_output[param] == 'not empty':"
        "assert test_output['data'][param]"
)
QUANTITATIVE = (
    "a"
)


# VERBOSE_PARAMS keeps the parameters that contain list of parameters

VERBOSE_PARAMS = [
    "exact",
    "more_specific",
    "less_specific",
    "stats"
]


# Data Call Mapping

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
    "avg": [ANY, NOT_EMPTY, MATCH, QUANTITATIVE],
    "max": [ANY, NOT_EMPTY, MATCH, QUANTITATIVE],
    "min": [ANY, NOT_EMPTY, MATCH, QUANTITATIVE],
    "sum": [ANY, NOT_EMPTY, MATCH, QUANTITATIVE]
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
            }
        }
    },

    "address-space-hierarchy": {
        "data_call_name": "Address Space Hierarchy",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "query_time": [ANY, NOT_EMPTY, MATCH],
            "rir": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH],
            "parameters": {
                "resource": [ANY, NOT_EMPTY, MATCH]
            },
            "exact": WHOIS_PARAMS,
            "more_specific": WHOIS_PARAMS,
            "less_specific": WHOIS_PARAMS    
        }
    },

    "as-path-length": {
        "data_call_name": "AS Path Length",
        "required_params": ["resource"],
        "optional_params": ["sort_by"],
        "output_params": {
            "query_time": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH],
            "sort_by": [ANY, NOT_EMPTY, MATCH],
            "stats": {
                "count": [ANY, NOT_EMPTY, MATCH, QUANTITATIVE],
                "location": [ANY, NOT_EMPTY, MATCH],
                "stripped": AS_PATH_STATS,
                "unstripped": AS_PATH_STATS
            }
        }
    },

    "blocklist": {
        "data_call_name": "Blocklist",
        "required_params": ["resource", "starttime"],
        "optional_params": ["endtime"],
        "output_params": {
            "source": None,
            "prefix": None,
            "details": None,
            "timelines": None,
            "query_starttime": None,
            "query_endtime": None,
            "resource": None
        }
    },

    "dns-chain": {
        "data_call_name": "Dns Chain",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "forward_nodes": None,
            "reverse_nodes": None,
            "nameservers": None,
            "authoritative_nameservers": None,
            "query_time": None,
            "resource": None
        }
    }
}