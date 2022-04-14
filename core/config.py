# NESTED_PARAMS keeps the parameters that contain list of parameters
NESTED_PARAMS = [
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
    # "prefixes->timelines',
    "stats",
    "imports",
    "exports",
    "neighbours",
    # "neighbours->timelines',
]


# Conditional Flags
ALL = "All following are True"
ANY = "At least one of following is True"

INCLUDE = "assert all([p in test_output['data'][param] for p in expected_output[param].split(',')])"
INCLUDE_KEYS = "assert all([p in test_output['data'][param].keys() for p in expected_output[param].split(',')])"
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

    AS_PEER_PARAMS = {
        "in_bgp": [ANY, NOT_EMPTY, MATCH],
        "in_whois": [ANY, NOT_EMPTY, MATCH],
        "peer": [ANY, NOT_EMPTY, MATCH, COMPARE]
    }

    TIMELINES = {
        "starttime": [ANY, NOT_EMPTY, MATCH],
        "endtime": [ANY, NOT_EMPTY, MATCH]
    }

    PREFIX_CHANGES_PER_TIMESTAMP = {
        "prefixes": [],
        "timestamp": [],
        "address-space": []
    }

    PREFIX_SIZE = {
        "size": [],
        "count": []
    }


##############################################################################
# The GUI populates the test case creation panel based on this map

##### When tests run, for each test case:
# App compares each output param's expected value with the real output based on the flags of that param in this map:
#   if the first flag is ANY -> if any of the following flags matches, the test passes for that param
#   if the first flag is ALL -> if all of the following flags matches, the test passes for that param
#   flags that come before ANY/ALL is applied first to filter corresponding param's expected value typed by user

##### FLAGS:
# NOT_EMPTY: This flag is just to check if a parameter of the response is not empty, without dealing with the value.
#            If user types "not empty" for any slot, or checks "Not Empty" checkbox for any nested parameter group,
#            and if corresponding parameter includes this flag, test passes if the response's param is not empty.
# MATCH:     Test passes should an expected value of a param typed by user matches with the real value.
# INCLUDE:   Test passes if value of a param in response includes all values in expected param.
# INCLUDE_KEYS: If param in response includes key-value pairs in that slot, test passes if its keys include all values in expected param.
# COMPARE:   Quantative comparisons: <[=] >[=]

##### If a param is covered by NESTED_PARAMS, test control logic behaves slightly different:
# e.g. https://stat.ripe.net/data/address-space-hierarchy/data.json?resource=110/4
# Those params can include same set of keys multiple times with different values.
# In such case, test passes if app can find an element that matches all the expected output values typed by user with one of the nested items in e.g. "exact" param of response.
# Otherwise, it returns an error "<param>: No item matching all the expected inputs found!"

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
                # "timelines": CommonParamsEnum.TIMELINES
            },
            "ripencc": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "status": [ANY, NOT_EMPTY, MATCH],
                # "timelines": CommonParamsEnum.TIMELINES
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
                # "timelines": CommonParamsEnum.TIMELINES,
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

    "as-routing-consistency": {
        "data_call_name": "AS Routing Consistency",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "prefixes": {
                "in_bgp": [ANY, NOT_EMPTY, MATCH],
                "in_whois": [ANY, NOT_EMPTY, MATCH],
                "irr_sources": [ANY, NOT_EMPTY, INCLUDE],
                "prefix": [ANY, NOT_EMPTY, MATCH]
            },
            "imports": CommonParamsEnum.AS_PEER_PARAMS,
            "exports": CommonParamsEnum.AS_PEER_PARAMS,
            "authority": [ANY, NOT_EMPTY, MATCH],
            "query_starttime": [ANY, NOT_EMPTY, MATCH],
            "query_endtime": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH]
        }
    },
    
    "asn-neighbours": {
        "data_call_name": "ASN Neighbours",
        "required_params": ["resource"],
        "optional_params": ["query_time"],
        "output_params": {
            "neighbour_counts": {
                "left": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "right": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "unique": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "uncertain": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "neighbours": {
                "asn": [ANY, NOT_EMPTY, MATCH],
                "type": [ANY, NOT_EMPTY, MATCH],
                "power": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "v4_peers": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "v6_peers": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "earliest_time": [ANY, NOT_EMPTY, MATCH],
            "latest_time": [ANY, NOT_EMPTY, MATCH],
            "query_starttime": [ANY, NOT_EMPTY, MATCH],
            "query_endtime": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH]
        }
    },

    "asn-neighbours-history": {
        "data_call_name": "ASN Neighbours History",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "max_rows"],
        "output_params": {
            "neighbours": {
                "neighbour": [ANY, NOT_EMPTY, MATCH, COMPARE],
                # "timelines": CommonParamsEnum.TIMELINES
            },
            "earliest_time": [ANY, NOT_EMPTY, MATCH],
            "latest_time": [ANY, NOT_EMPTY, MATCH],
            "query_starttime": [ANY, NOT_EMPTY, MATCH],
            "query_endtime": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH]
        }
    },

    "dns-chain": {
        "data_call_name": "DNS Chain",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "forward_nodes": [ANY, NOT_EMPTY, INCLUDE_KEYS],
            "reverse_nodes": [ANY, NOT_EMPTY, INCLUDE_KEYS],
            "nameservers": [ANY, NOT_EMPTY, INCLUDE],
            "authoritative_nameservers": [ANY, NOT_EMPTY, INCLUDE],
            "query_time": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH]
        }
    },

    # Under construction !!!

    "atlas-probe-deployment": {
        "data_call_name": "Atlas Probe Deployment",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "deployments": {
                "resource": [],
                "deployment": {
                    "date": [],
                    "statuses": {
                        "neverseen": [],
                        "connected": [],
                        "disconnected": [],
                        "abandoned": []
                    }
                }
            },
            "query_date": [],
            "starttime": [],
            "endtime": [],
            "resource": []
        }
    },

    "atlas-probes": {
        "data_call_name": "Atlas Probes",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "probes": {
                "prefix_v4": [],
                "status": [],
                "status_name": [],
                "prefix_v6": [],
                "is_anchor": [],
                "last_connected": [],
                "tags": [],
                "type": [],
                "address_v6": [],
                "latitude": [],
                "longitude": [],
                "id": [],
                "address_v4": [],
                "country_code": [],
                "is_public": [],
                "asn_v4": [],
                "asn_v6": [],
                "status_since": [],
                "first_connected": [],
                "total_uptime": []
            },
            "stats": {
                "total": []
            },
            "resource": []
        }
    },

    "atlas-targets": {
        "data_call_name": "Atlas Targets",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "measurements": {
                "af": [],
                "msm_id": [],
                "stop_time": [],
                "start_time": [],
                "dst_name": [],
                "dst_addr": [],
                "dst_asn": [],
                "status": {
                    "name": [],
                    "id": [],
                    "when": []
                },
                "type": {
                    "name": []
                },
                "creation_time": [],
                "description": [],
                "result": [],
                "size": [],
                "is_public": [],
                "participant_count": []
            },
            "stats": {
                "total": []
            },
            "authenticated": [],
            "resource": []
        }
    },

    "bgp-state": {
        "data_call_name": "BGP State",
        "required_params": ["resource"],
        "optional_params": ["timestamp", "rrcs", "unix_timestamps"],
        "output_params": {
            "bgp_state": {
                "target_prefix": [],
                "source_id": [],
                "path": [],
                "community": []
            },
            "nr_routes": [],
            "query_time": [],
            "resource": []
        }
    },

    "bgp-update-activity": {
        "data_call_name": "BGP Update Activity",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "max_samples", "min_sampling_period", "num_hours", "hide_empty_samples"],
        "output_params": {
            "updates": {
                "announcements": [],
                "withdrawals": [],
                "starttime": []
            },
            "sampling_period": [],
            "sampling_period_human": [],
            "max_samples": [],
            "related_prefixes": [],
            "query_starttime": [],
            "query_endtime": [],
            "resource": [],
            "resource_type": []
        }
    },

    "bgp-updates": {
        "data_call_name": "BGP Updates",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "rrcs", "unix_timestamps"],
        "output_params": {
            "updates": {
                "seq": [],
                "timestamp": [],
                "type": [],
                "attrs": {
                    "source_id": [],
                    "target_prefix": [],
                    "path": [],
                    "community": []
                }
            },
            "nr_updates": [],
            "query_starttime": [],
            "query_endtime": [],
            "resource": []
        }
    },

    "bgplay": {
        "data_call_name": "BGPlay",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "rrcs", "unix_timestamps"],
        "output_params": {
            "initial_state": {
                "target_prefix": [],
                "source_id": [],
                "path": [],
                "community": []
            },
            "events": {
                "seq": [],
                "timestamp": [],
                "type": [],
                "attrs": {
                    "source_id": [],
                    "target_prefix": [],
                    "path": [],
                    "community": []
                }
            },
            "nodes": {
                "as_number": [],
                "owner": []
            },
            "targets": {
                "prefix": []
            },
            "sources": {
                "id": [],
                "as_number": [],
                "ip": [],
                "rrc": []
            },
            "query_starttime": [],
            "query_endtime": [],
            "resource": []
        }
    },

    "blocklist": {
        "data_call_name": "Blocklist",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "sources": {
                "uceprotect-level1": {
                    "prefix": [],
                    "details": [],
                    "timelines": {
                        "starttime": [],
                        "endtime": []
                    }
                }
            },
            "query_starttime": [],
            "query_endtime": [],
            "resource": []
        }
    },

    "country-asns": {
        "data_call_name": "Country ASNs",
        "required_params": ["resource"],
        "optional_params": ["query_time", "lod"],
        "output_params": {
            "countries": {
                "stats": {
                    "registered": [],
                    "routed": [],
                },
                "resource": []
            },
            "lod": [],
            "latest_time": [],
            "query_time": [],
            "resource": []  #BEWARE! This is different than other resource params.
        }
    },

    "country-resource-list": {
        "data_call_name": "Country Resource List",
        "required_params": ["resource"],
        "optional_params": ["time", "v4_format"],
        "output_params": {
            "resources": {
                "asn": [],
                "ipv4": [],
                "ipv6": []
            },
            "query_time": []
        }
    },

    "example-resources": {
        "data_call_name": "Example Resources",
        "required_params": [],
        "optional_params": [],
        "output_params": {
            "ipv4": [],
            "range4": [],
            "ipv6": [],
            "asn": []
        }
    },

    "historical-whois": {
        "data_call_name": "Historical Whois",
        "required_params": ["resource"],
        "optional_params": ["version"],
        "output_params": {
            "terms_and_conditions": [],
            "num_versions": [],
            "versions": {
                "from_time": [],
                "to_time": [],
                "version": []
            },
            "database": [],
            "type": [],
            "objects": {
                "type": "aut-num",
                "key": "AS3333",
                "attributes": {
                    "attribute": "aut-num",
                    "value": "AS3333"
                }
            },
            "referencing": [],  # Beware, different implementation. https://stat.ripe.net/data/historical-whois/data.json?resource=3333
            "referenced_by": [], # probably nested. Couldn't find an example.
            "access": [],
            "suggestions": {
                "type": [],
                "key": [],
                "attributes": {
                    "attribute": [],
                    "value": []
                },
                "from_time": [],
                "version": [],
                "latest": [],
                "deleted": []
            },
            "version": [],
            "latest_time": [],
            "resource": [],
        }
    },

    "iana-registry-info": {
        "data_call_name": "IANA Registry Info",
        "required_params": [],
        "optional_params": ["resource", "best_match_only"],
        "output_params": {
            "resources": {
                "resource": [],
                "type_properties": [],
                "description": [],
                "details": {
                    "Designation": [],
                    "Date": [],
                    "WHOIS": [],
                    "RDAP": [],
                    "Status [1]": [],
                    "Note": []
                },
                "source": [],
                "source_url": []
            },
            "load_time": [],
            "returned": [],
            "resource": []
        }
    },

    "looking-glass": {
        "data_call_name": "Looking Glass",
        "required_params": ["resource"],
        "optional_params": ["look_back_limit"],
        "output_params": {
            "rrcs": {
                "rrc": [],
                "location": [],
                "peers": {
                    "asn_origin": [],
                    "as_path": [],
                    "community": [],
                    "last_updated": [],
                    "prefix": [],
                    "peer": [],
                    "origin": [],
                    "next_hop": [],
                    "latest_time": []
                }
            },
            "query_time": [],
            "latest_time": [],
            "parameters": {
                "resource": [],
                "look_back_limit": []
            }
        }
    },

    "maxmind-geo-lite": {
        "data_call_name": "Maxmind Geo Lite",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "located_resources": {
                "resource": [],
                "locations": {
                    "country": [],
                    "city": [],
                    "resources": [],
                    "latitude": [],
                    "longitude": [],
                    "covered_percentage": []
                },
                "unknown_percentage": []
            },
            "unknown_percentage": {
                "v4": [],
                "v6": []
            },
            "result_time": [],
            "earliest_time": [],
            "latest_time": [],
            "parameters": {
                "resource": [],
                "resolution": []
            }
        }
    },

    "maxmind-geo-lite-announced-by-as": {
        "data_call_name": "Maxmind Geo Lite Announced By AS",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "located_resources": {
                "resource": [],
                "locations": {
                    "country": [],
                    "city": [],
                    "resources": [],
                    "latitude": [],
                    "longitude": [],
                    "covered_percentage": []
                },
                "unknown_percentage": []
            },
            "unknown_percentage": {
                "v4": [],
                "v6": []
            },
            "result_time": [],
            "earliest_time": [],
            "latest_time": [],
            "parameters": {
                "resource": [],
                "resolution": []
            }
        }
    },

    "meternet-bandwidth-measurements": {
        "data_call_name": "Meter.net Bandwidth Measurements",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "measurements": {
                "prefix": [],
                "date": [],
                "down": [],
                "up": []
            },
            "statistics": {
                "measurements": []
            },
            "earliest_time": [],
            "latest_time": [],
            "starttime": [],
            "endtime": [],
            "resource": []
        }
    },

    "mlab-activity-count": {
        "data_call_name": "M-lab Activity Count",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "nr_ips": [],
            "perc_coverage": [],
            "query_starttime": [],
            "query_endtime": [],
            "resource": []
        }
    },

    "mlab-bandwidth": {
        "data_call_name": "Mlab Bandwidth",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "bandwidths": [],
            "query_starttime": [],
            "query_endtime": [],
            "resource": []
        }
    },

    "mlab-clients": {
        "data_call_name": "Mlab Clients",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "clients": {
                "num_tests": [],
                "country": [],
                "city": [],
                "latitude": [],
                "longitude": []
            },
            "nr_clients": [],
            "perc_coverage": [],
            "query_starttime": [],
            "query_endtime": [],
            "resource": []
        }
    },

    "network-info": {
        "data_call_name": "Network Info",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "asns": [],
            "prefix": []
        }
    },

    "prefix-count": {
        "data_call_name": "Prefix Count",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "min_peers_seeing", "resolution"],
        "output_params": {
            "ipv4": CommonParamsEnum.PREFIX_CHANGES_PER_TIMESTAMP,
            "ipv6": CommonParamsEnum.PREFIX_CHANGES_PER_TIMESTAMP,
            "resolution": [],
            "query_starttime": [],
            "query_endtime": [],
            "resource": []
        }
    },

    "prefix-overview": {
        "data_call_name": "Prefix Overview",
        "required_params": ["resource"],
        "optional_params": ["min_peers_seeing", "max_related", "query_time"],
        "output_params": {
            "asns": {
                "asn": [],
                "holder": []
            },
            "is_less_specific": [],
            "announced": [],
            "related_prefixes": [],
            "resource": [],
            "type": [],
            "block": {
                "resource": [],
                "desc": [],
                "name": []
            },
            "actual_num_related": [],
            "query_time": [],
            "num_filtered_out": [],
            "resource": []
        }
    },

    "prefix-routing-consistency": {
        "data_call_name": "Prefix Routing Consistency",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "routes": {
                "in_bgp": [],
                "in_whois": [],
                "prefix": [],
                "origin": [],
                "irr_sources": [],
                "asn_name": []
            },
            "query_starttime": [],
            "query_endtime": [],
            "resource": []
        }
    },

    "prefix-size-distribution": {
        "data_call_name": "Prefix Size Distribution",
        "required_params": ["resource"],
        "optional_params": ["timestamp", "min_peers_seeing"],
        "output_params": {
            "ipv4": CommonParamsEnum.PREFIX_SIZE,
            "ipv6": CommonParamsEnum.PREFIX_SIZE,
            "query_time": [],
            "resource": []
        }
    },

    "related-prefixes": {
        "data_call_name": "Related Prefixes",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "prefixes": {
                "prefix": [],
                "origin_asn": [],
                "asn_name": [],
                "relationship": []
            },
            "query_time": [],
            "resource": []
        }
    },

    "reverse-dns": {
        "data_call_name": "Reverse DNS",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "delegations": {
                "key": [],
                "value": []
            },
            "query_time": [],
            "resource": []
        }
    },

    "reverse-dns-consistency": {
        "data_call_name": "Reverse DNS Consistency",
        "required_params": ["resource"],
        "optional_params": ["ipv4", "ipv6"],
        "output_params": {
            "prefixes": {
                "ipv4": [],
                "ipv6": []
            },
            "source": [],
            "ipv4": [],
            "ipv6": [],
            "query_time": [],
            "resource": []
        }
    },

    "reverse-dns-ip": {
        "data_call_name": "Reverse DNS IP",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "result": [],
            "error": [],
            "query_time": [],
            "resource": []
        }
    },

    "rir": {
        "data_call_name": "RIR",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "lod"],
        "output_params": {
            "rirs": {
                "rir": [],
                "first_time": [],
                "last_time": []
            },
            "lod": [],
            "latest": [],
            "query_starttime": [],
            "query_endtime": [],
            "resource": []
        }
    },
    
    "rir-geo": {
        "data_call_name": "RIR Geo",
        "required_params": ["resource"],
        "optional_params": ["query_time"],
        "output_params": {
            "located_resources": {
                "resource": [],
                "location": []
            },
            "parameters": {
                "resource": [],
                "query_time": []
            },
            "result_time": [],
            "earliest_time": [],
            "latest_time": []
        }
    },

    "rir-prefix-size-distribution": {
        "data_call_name": "RIR Prefix Size Distribution",
        "required_params": ["resource"],
        "optional_params": ["query_time"],
        "output_params": {
            "rirs": {
                "rir": [],
                "distribution": {
                    "prefix_size": [],
                    "count": []
                }
            },
            "query_starttime": [],
            "query_endtime": [],
            "resource": []
        }
    },

    "rir-stats-country": {
        "data_call_name": "RIR Stats Country",
        "required_params": ["resource"],
        "optional_params": ["query_time"],
        "output_params": {
            "located_resources": {
                "resource": [],
                "location": []
            },
            "result_time": [],
            "earliest_time": [],
            "latest_time": [],
            "parameters": {
                "resource": [],
                "query_time": []
            }
        }
    },

    # Beware! Output structure changes based on inputs for list_asns and asn_types
    "ris-asns": {
        "data_call_name": "RIS ASNs",
        "required_params": [],
        "optional_params": ["list_asns", "asn_types", "query_time"],
        "output_params": {
            "asns": [],
            "counts": [],
            "earliest_time": [],
            "latest_time": [],
            "query_time": []
        }
    },

    "ris-first-last-seen": {
        "data_call_name": "RIS First-Last-Seen",
        "required_params": ["resource"],
        "optional_params": ["include"],
        "output_params": {}
    },

    "ris-full-table-threshold": {
        "data_call_name": "RIS Full-Table Threshold",
        "required_params": [],
        "optional_params": ["query_time"],
        "output_params": {
            "v4": [],
            "v6": [],
            "result_time": [],
            "earliest_time": [],
            "latest_time": [],
            "parameters": {
                "query_time": []
            }
        }
    },

    "ris-peer-count": {
        "data_call_name": "RIS Peer Count",
        "required_params": [],
        "optional_params": ["starttime", "endtime", "v4_full_prefix_threshold", "v6_full_prefix_threshold"],
        "output_params": {
            "peer_count": {
                "v4": {
                    "total": {
                        "timestamp": [],
                        "count": []
                    },
                    "full_feed": {
                        "timestamp": [],
                        "count": []
                    }
                },
                "v6": {
                    "total": {
                        "timestamp": [],
                        "count": []
                    },
                    "full_feed": {
                        "timestamp": [],
                        "count": []
                    }
                }
            },
            "v4_full_prefix_threshold": [],
            "v6_full_prefix_threshold": [],
            "starttime": [],
            "endtime": []
        }
    },

    "ris-peerings": {
        "data_call_name": "RIS Peerings",
        "required_params": ["resource"],
        "optional_params": ["query_time"],
        "output_params": {
            "peerings": {
                "probe": {
                    "city": [],
                    "country": [],
                    "longitude": [],
                    "latitude": [],
                    "name": [],
                    "ipv4_peer_count": [],
                    "ipv6_peer_count": [],
                    "ixp": []
                },
                "peers": {
                    "asn": [],
                    "ip": [],
                    "ip_version": [],
                    "table_version": [],
                    "prefix_count": [],
                    "routes": {
                        "as_path": []
                    }
                }
            }
        },
        "query_starttime": [],
        "query_endtime": [],
        "resource": []
    },

    "ris-peers": {
        "data_call_name": "RIS Peers",
        "required_params": [],
        "optional_params": ["query_time"],
        "output_params": {
            "peers": [],    #INCLUDE_KEYS
            "earliest_time": [],
            "latest_time": [],
            "parameters": {
                "query_time": []
            }
        }
    },

    # Beware! Output structure changes based on inputs for params
    "ris-prefixes": {
        "data_call_name": "RIS Peers",
        "required_params": ["resource"],
        "optional_params": ["query_time", "list_prefixes", "types", "af", "noise"],
        "output_params": {
            "counts": {
                "v4": [],
                "v6": []
            },
            "list_prefixes": [],
            "af": [],
            "types": [],
            "noise": [],
            "earliest_time": [],
            "latest_time": [],
            "query_time": [],
            "resource": [],
        }
    },

    "routing-history": {
        "data_call_name": "Routing History",
        "required_params": ["resource"],
        "optional_params": ["max_rows", "include_first_hop", "normalise_visibility", "min_peers", "starttime", "endtime"],
        "output_params": {
            "by_origin": {
                "origin": [],
                "prefixes": {
                    "prefix": [],
                    "timelines": {
                        "starttime": [],
                        "endtime": [],
                        "full_peers_seeing": []
                    }
                }
            },
            "latest_max_ff_peers": {
                "v4": [],
                "v6": []
            },
            "time_granularity": [],
            "query_starttime": [],
            "query_endtime": [],
            "resource": [],
        }
    },

    "routing-status": {
        "data_call_name": "Routing Status",
        "required_params": ["resource"],
        "optional_params": ["timestamp", "min_peers_seeing"],
        "output_params": {
            "first_seen": {
                "prefix": [],
                "origin": [],
                "time": []
            },
            "last_seen": {
                "prefix": [],
                "origin": [],
                "time": []
            },
            "visibility": {
                "v4": {
                    "ris_peers_seeing": [],
                    "total_ris_peers": []
                },
                "v6": {
                    "ris_peers_seeing": [],
                    "total_ris_peers": []
                }
            },
            "announced_space": {
                "v4": {
                    "prefixes": [],
                    "ips": []
                },
                "v6": {
                    "prefixes": [],
                    "48s": []
                }
            },
            "observed_neighbours": [],
            "resource": [],
            "query_time": []
        }
    },

    # Beware! Output structure changes based on inputs for params
    "rpki-history": {
        "data_call_name": "RPKI History",
        "required_params": ["resource"],
        "optional_params": ["family", "resolution", "delegated"],
        "output_params": {
            "timeseries": {
                "cc": [],
                "time": [],
                "family": [],
                "rpki": {
                    "vrp_count": []
                }
            },
            "resource": []
        }
    },

    "rpki-validation": {
        "data_call_name": "RPKI Validation Status",
        "required_params": ["resource", "prefix"],
        "optional_params": [],
        "output_params": {
            "validating_roas": {
                "origin": [],
                "prefix": [],
                "max_length": [],
                "validity": []
            },
            "status": [],
            "validator": [],
            "prefix": [],
            "resource": []
        }
    },

    "rrc-info": {
        "data_call_name": "RRC Info",
        "required_params": [],
        "optional_params": [],
        "output_params": {
            "rrcs": {
                "id": [],
                "name": [],
                "geographical_location": [],
                "topological_location": [],
                "multihop": [],
                "activated_on": [],
                "deactivated_on": [],
                "peers": {
                    "asn": [],
                    "ip": [],
                    "v4_prefix_count": [],
                    "is_full_feed_v4": [],
                    "v6_prefix_count": [],
                    "is_full_feed_v6": []
                }
            },
            "parameters": []
        }
    },

    "searchcomplete": {
        "data_call_name": "Searchcomplete",
        "required_params": ["resource"],
        "optional_params": ["limit"],
        "output_params": {
            "categories": {
                "category": [],
                "suggestions": {
                    "label": [],
                    "value": [],
                    "description": []
                }
            },
            "query_term": [],
            "limit": [],
            "query_time": []
        }
    },

    "speedchecker-bandwidth-measurements": {
        "data_call_name": "Speedchecker Bandwidth Measurements",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "measurements": {
                "prefix": [],
                "date": [],
                "down": [],
                "up": []
            },
            "statistics": {
                "measurements": []
            },
            "earliest_time": [],
            "latest_time": [],
            "starttime": [],
            "endtime": [],
            "resource": []
        }
    },

    "visibility": {
        "data_call_name": "Visibility",
        "required_params": ["resource"],
        "optional_params": ["query_time", "include"],
        "output_params": {
            "visibilities": {
                "probe": {
                    "city": [],
                    "country": [],
                    "longitude": [],
                    "latitude": [],
                    "name": [],
                    "ipv4_peer_count": [],
                    "ipv6_peer_count": [],
                    "ixp": []
                },
                "ipv4_full_table_peers_not_seeing": [],
                "ipv6_full_table_peers_not_seeing": [],
                "ipv4_full_table_peer_count": [],
                "ipv6_full_table_peer_count": []
            },
            "related_prefixes": [],
            "include": [],
            "query_time": [],
            "latest_time": [],
            "resource": []
        }
    },

    "whats-my-ip": {
        "data_call_name": "Whats My IP",
        "required_params": [],
        "optional_params": [],
        "output_params": {
            "ip": []
        }
    },

    "whois": {
        "data_call_name": "Whois",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "records": [],
            "irr_records": [],
            "authorities": [],
            "query_time": [],
            "resource": [],
        }
    },

    "whois-object-last-updated": {
        "data_call_name": "Whois Object Last Updated",
        "required_params": ["object", "type", "source"],
        "optional_params": ["timestamp", "compare_with_live"],
        "output_params": {
            "object": [],
            "last_updated": [],
            "query_time": [],
            "same_as_live": [],
        }
    },

    "zonemaster": {
        "data_call_name": "Zonemaster",
        "required_params": ["resource"],
        "optional_params": ["method"],
        "output_params": {
            "params": {
                "domain": [],
                "user_ip": [],
                "client_id": [],
                "client_version": []
            },
            "hash_id": [],
            "id": [],
            "results": {
                "level": [],
                "module": [],
                "message": []
            },
            "creation_time": [],
            "parameters": {
                "resource": [],
                "method": []
            }
        }
    },

}

#as overview testleri eksik, country-resource-stats komple eksik