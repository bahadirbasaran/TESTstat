# The GUI populates the test case creation panel based on DATA_CALL_MAP below

# When tests run, for each test case:
# TESTstat compares each output param's expected value with the real output
# based on the flags of that param in this map:
#   if the first flag is ANY -> if any of the following flags matches,
#       the test passes for that param
#   if the first flag is ALL -> if all of the following flags matches,
#       the test passes for that param
#   flags that come before ANY/ALL is applied first to filter corresponding
#       param's expected value typed by user

# If a parameter is covered by NESTED_PARAMS, test logic behaves differently:
# Those params can include same set of keys multiple times with different
# values. In such case, a test passes if TESTstat can find an element that
# matches all the expected output values typed by user with one of the nested
# items in e.g. "exact" param of response. Otherwise, it returns an error
# "<param>: No item matching all the expected inputs found!".
#   https://stat.ripe.net/data/address-space-hierarchy/data.json?resource=110/4


# Application-wide definitions
BATCH_SIZE = 100

MATTERMOST_URL = "https://mattermost.ripe.net/hooks/6xp8tt93i3fwde5d43jegsxi8a"
MATTERMOST_CHANNEL = "ripestat-teststat"

ALL = "All following are True"
ANY = "At least one of following is True"
COMPARE = "Compare quantitatively (<[=] >[=])"
INCLUDE = (
    "Check if a parameter of the response is not empty, without dealing with"
    "the value. If a user types 'not empty' for any slot, or checks Not Empty"
    "checkbox for any nested parameter group, and if corresponding parameter"
    "includes this flag, test passes if the response's param is not empty."
)
INCLUDE_KEYS = (
    "If a parameter in response includes key-value pairs in that slot, test"
    "passes if its keys include all values in expected param."
)
MATCH = (
    "Check any given data field in response if it matches with the expected"
    "output for that field"
)
NOT_EMPTY = "Check any given data field in response is empty or not"
TRIM_AS = "If resource starts with 'as', trim it"


class ParamsCommons():
    """Contains parameters' commons shared across different data calls/fields"""

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
        "iana->timelines",
        "ripencc->timelines",
        "prefixes",
        "prefixes->timelines",
        "stats",
        "imports",
        "exports",
        "neighbours",
        "neighbours->timelines",
        "probes"
    ]

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


DATA_CALL_MAP = {

    "abuse-contact-finder": {
        "data_call_name": "Abuse Contact Finder",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "abuse_contacts": [ANY, NOT_EMPTY, INCLUDE],
            "authoritative_rir": [ANY, NOT_EMPTY, MATCH]
        }
    },

    "address-space-hierarchy": {
        "data_call_name": "Address Space Hierarchy",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "exact": ParamsCommons.WHOIS_PARAMS,
            "more_specific": ParamsCommons.WHOIS_PARAMS,
            "less_specific": ParamsCommons.WHOIS_PARAMS,
            "rir": [ANY, NOT_EMPTY, MATCH],
            "resource": [ANY, NOT_EMPTY, MATCH]
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
            }
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
                "timelines": ParamsCommons.TIMELINES
            },
            "ripencc": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "status": [ANY, NOT_EMPTY, MATCH],
                "timelines": ParamsCommons.TIMELINES
            }
        }
    },

    "announced-prefixes": {
        "data_call_name": "Announced Prefixes",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "min_peers_seeing"],
        "output_params": {
            "prefixes": {
                "prefix": [ANY, NOT_EMPTY, MATCH],
                "timelines": ParamsCommons.TIMELINES,
            }
        }
    },

    # Test cases are missing
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
            "announced": [ANY, NOT_EMPTY, MATCH]
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
                "stripped": ParamsCommons.AS_PATH_STATS,
                "unstripped": ParamsCommons.AS_PATH_STATS
            },
            "sort_by": [ANY, NOT_EMPTY, MATCH]
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
            "imports": ParamsCommons.AS_PEER_PARAMS,
            "exports": ParamsCommons.AS_PEER_PARAMS,
            "authority": [ANY, NOT_EMPTY, MATCH]
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
            }
        }
    },

    "asn-neighbours-history": {
        "data_call_name": "ASN Neighbours History",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "max_rows"],
        "output_params": {
            "neighbours": {
                "neighbour": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "timelines": ParamsCommons.TIMELINES
            }
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
            "authoritative_nameservers": [ANY, NOT_EMPTY, INCLUDE]
        }
    },

    "atlas-probe-deployment": {
        "data_call_name": "Atlas Probe Deployment",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "deployments": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "deployment": {
                    "date": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "statuses": {
                        "neverseen": [ANY, NOT_EMPTY, MATCH, COMPARE],
                        "connected": [ANY, NOT_EMPTY, MATCH, COMPARE],
                        "disconnected": [ANY, NOT_EMPTY, MATCH, COMPARE],
                        "abandoned": [ANY, NOT_EMPTY, MATCH, COMPARE]
                    }
                }
            }
        }
    },

    "atlas-probes": {
        "data_call_name": "Atlas Probes",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "probes": {
                "prefix_v4": [ANY, NOT_EMPTY, MATCH],
                "status": [ANY, NOT_EMPTY, MATCH],
                "status_name": [ANY, NOT_EMPTY, MATCH],
                "prefix_v6": [ANY, NOT_EMPTY, MATCH],
                "is_anchor": [ANY, NOT_EMPTY, MATCH],  # bool
                "last_connected": [ANY, NOT_EMPTY, MATCH],
                "tags": [ANY, NOT_EMPTY, INCLUDE],
                "type": [ANY, NOT_EMPTY, MATCH],
                "address_v6": [ANY, NOT_EMPTY, MATCH],
                "latitude": [ANY, NOT_EMPTY, MATCH],
                "longitude": [ANY, NOT_EMPTY, MATCH],
                "id": [ANY, NOT_EMPTY, MATCH],
                "address_v4": [ANY, NOT_EMPTY, MATCH],
                "country_code": [ANY, NOT_EMPTY, MATCH],
                "is_public": [ANY, NOT_EMPTY, MATCH],  # bool
                "asn_v4": [ANY, NOT_EMPTY, MATCH],
                "asn_v6": [ANY, NOT_EMPTY, MATCH],
                "status_since": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "first_connected": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "total_uptime": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "stats": {
                "total": [ANY, NOT_EMPTY, MATCH, COMPARE]
            }
        }
    },

    "atlas-targets": {
        "data_call_name": "Atlas Targets",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "measurements": {
                "af": [ANY, NOT_EMPTY, MATCH],  # address family, 4 or 6 -- always not empty
                "msm_id": [ANY, NOT_EMPTY, MATCH],
                "stop_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "start_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "dst_name": [ANY, NOT_EMPTY, MATCH],
                "dst_addr": [ANY, NOT_EMPTY, MATCH],
                "dst_asn": [ANY, NOT_EMPTY, MATCH],
                "status": {
                    "name": [ANY, NOT_EMPTY, MATCH],
                    "id": [ANY, NOT_EMPTY, MATCH],
                    "when": [ANY, NOT_EMPTY, MATCH]
                },
                "type": {
                    "name": [ANY, NOT_EMPTY, MATCH]
                },
                "creation_time": [ANY, NOT_EMPTY, MATCH],
                "description": [ANY, NOT_EMPTY, MATCH],
                "result": [ANY, NOT_EMPTY, MATCH],
                "size": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "is_public": [ANY, NOT_EMPTY, MATCH],  # bool
                "participant_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "stats": {
                "total": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "authenticated": [ANY, NOT_EMPTY, MATCH],  # bool
        }
    },

    "bgp-state": {
        "data_call_name": "BGP State",
        "required_params": ["resource"],
        "optional_params": ["timestamp", "rrcs", "unix_timestamps"],
        "output_params": {
            "bgp_state": {
                "target_prefix": [ANY, NOT_EMPTY, MATCH],
                "source_id": [ANY, NOT_EMPTY, MATCH],
                "path": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                "community": [ANY, NOT_EMPTY, MATCH, INCLUDE]
            },
            "nr_routes": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "bgp-update-activity": {
        "data_call_name": "BGP Update Activity",
        "required_params": ["resource"],
        "optional_params": [
            "starttime",
            "endtime",
            "max_samples",
            "min_sampling_period",
            "num_hours",
            "hide_empty_samples"
        ],
        "output_params": {
            "updates": {
                "announcements": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "withdrawals": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "starttime": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "sampling_period": [ANY, NOT_EMPTY, MATCH, COMPARE],
            "sampling_period_human": [ANY, NOT_EMPTY, MATCH],
            "max_samples": [ANY, NOT_EMPTY, MATCH, COMPARE],
            "related_prefixes": [ANY, NOT_EMPTY, MATCH, INCLUDE],
            "resource_type": [ANY, NOT_EMPTY, MATCH]
        }
    },

    "bgp-updates": {
        "data_call_name": "BGP Updates",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "rrcs", "unix_timestamps"],
        "output_params": {
            "updates": {
                "seq": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "timestamp": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "type": [ANY, NOT_EMPTY, MATCH],
                "attrs": {
                    "source_id": [ANY, NOT_EMPTY, MATCH],
                    "target_prefix": [ANY, NOT_EMPTY, MATCH],
                    "path": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                    "community": [ANY, NOT_EMPTY, MATCH, INCLUDE]
                }
            },
            "nr_updates": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "bgplay": {
        "data_call_name": "BGPlay",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "rrcs", "unix_timestamps"],
        "output_params": {
            "initial_state": {
                "target_prefix": [ANY, NOT_EMPTY, MATCH],
                "source_id": [ANY, NOT_EMPTY, MATCH],
                "path": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                "community": [ANY, NOT_EMPTY, MATCH, INCLUDE]
            },
            "events": {
                "seq": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "timestamp": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "type": [ANY, NOT_EMPTY, MATCH],
                "attrs": {
                    "source_id": [ANY, NOT_EMPTY, MATCH],
                    "target_prefix": [ANY, NOT_EMPTY, MATCH],
                    "path": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                    "community": [ANY, NOT_EMPTY, MATCH, INCLUDE]
                }
            },
            "nodes": {
                "as_number": [ANY, NOT_EMPTY, MATCH],
                "owner": [ANY, NOT_EMPTY, MATCH]
            },
            "targets": {
                "prefix": [ANY, NOT_EMPTY, MATCH]
            },
            "sources": {
                "id": [ANY, NOT_EMPTY, MATCH],
                "as_number": [ANY, NOT_EMPTY, MATCH],
                "ip": [ANY, NOT_EMPTY, MATCH],
                "rrc": [ANY, NOT_EMPTY, MATCH]
            }
        }
    },

    "blocklist": {
        "data_call_name": "Blocklist",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "sources": {
                "uceprotect-level1": {
                    "prefix": [ANY, NOT_EMPTY, MATCH],
                    "details": [ANY, NOT_EMPTY, MATCH],
                    "timelines": {
                        "starttime": [ANY, NOT_EMPTY, MATCH, COMPARE],
                        "endtime": [ANY, NOT_EMPTY, MATCH, COMPARE]
                    }
                }
            }
        }
    },

    "country-asns": {
        "data_call_name": "Country ASNs",
        "required_params": ["resource"],
        "optional_params": ["query_time", "lod"],
        "output_params": {
            "countries": {
                "stats": {
                    "registered": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "routed": [ANY, NOT_EMPTY, MATCH, COMPARE],
                },
                "resource": [ANY, NOT_EMPTY, MATCH]
            },
            "lod": [ANY, NOT_EMPTY, MATCH],
            "latest_time": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "country-resource-list": {
        "data_call_name": "Country Resource List",
        "required_params": ["resource"],
        "optional_params": ["time", "v4_format"],
        "output_params": {
            "resources": {
                "asn": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                "ipv4": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                "ipv6": [ANY, NOT_EMPTY, MATCH, INCLUDE]
            }
        }
    },

    "country-resource-stats": {
        "data_call_name": "Country Resource Stats",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "resolution"],
        "output_params": {
            "stats": {
                "timeline": {
                    "starttime": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "endtime": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "v4_prefixes_ris": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "v6_prefixes_ris": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "asns_ris": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "v4_prefixes_stats": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "v6_prefixes_stats": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "asns_stats": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "stats_date": [ANY, NOT_EMPTY, MATCH, COMPARE]

            },
            "latest_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
            "earliest_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
            "hd_latest_time": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "example-resources": {
        "data_call_name": "Example Resources",
        "required_params": [],
        "optional_params": [],
        "output_params": {
            "ipv4": [ANY, NOT_EMPTY],
            "range4": [ANY, NOT_EMPTY],
            "ipv6": [ANY, NOT_EMPTY],
            "asn": [ANY, NOT_EMPTY]
        }
    },

    # Output structure changes based on inputs for params
    # might require change
    "historical-whois": {
        "data_call_name": "Historical Whois",
        "required_params": ["resource"],
        "optional_params": ["version"],
        "output_params": {
            "terms_and_conditions": [ANY, NOT_EMPTY, MATCH],
            "num_versions": [ANY, NOT_EMPTY, MATCH, COMPARE],
            "versions": {
                "from_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "to_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "version": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "database": [ANY, NOT_EMPTY, MATCH],
            "type": [ANY, NOT_EMPTY, MATCH],
            "objects": {
                "type": [ANY, NOT_EMPTY, MATCH],
                "key": [ANY, NOT_EMPTY, MATCH],
                "attributes": {
                    "attribute": [ANY, NOT_EMPTY, MATCH],
                    "value": [ANY, NOT_EMPTY, MATCH]
                }
            },
            # Beware, different implementation (e.g. resource=3333)
            "referencing": {
                "type": [ANY, NOT_EMPTY, MATCH],
                "key": [ANY, NOT_EMPTY, MATCH],
                "from_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "to_time": [ANY, NOT_EMPTY, MATCH, COMPARE],  # could be missing
                "version": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "latest": [ANY, NOT_EMPTY, MATCH]  # bool

            },
            "referenced_by": {
                "type": [ANY, NOT_EMPTY, MATCH],
                "key": [ANY, NOT_EMPTY, MATCH],
                "from_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "to_time": [ANY, NOT_EMPTY, MATCH, COMPARE],  # could be missing
                "version": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "latest": [ANY, NOT_EMPTY, MATCH]  # bool
            },
            "access": [ANY, NOT_EMPTY, MATCH],
            "suggestions": {
                "type": [ANY, NOT_EMPTY, MATCH],
                "key": [ANY, NOT_EMPTY, MATCH],
                "attributes": {
                    "attribute": [ANY, NOT_EMPTY, MATCH],
                    "value": [ANY, NOT_EMPTY, MATCH]
                },
                "from_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "version": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "latest": [ANY, NOT_EMPTY, MATCH],
                "deleted": [ANY, NOT_EMPTY, MATCH]  # bool
            }
        }
    },

    "iana-registry-info": {
        "data_call_name": "IANA Registry Info",
        "required_params": [],
        "optional_params": ["resource", "best_match_only"],
        "output_params": {
            "resources": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "type_properties": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                "description": [ANY, NOT_EMPTY, MATCH],
                "details": {
                    "Designation": [ANY, NOT_EMPTY, MATCH],
                    "Date": [ANY, NOT_EMPTY, MATCH],
                    "WHOIS": [ANY, NOT_EMPTY, MATCH],
                    "RDAP": [ANY, NOT_EMPTY, MATCH],
                    "Status [1]": [ANY, NOT_EMPTY, MATCH],
                    "Note": [ANY, NOT_EMPTY, MATCH]
                },
                "source": [ANY, NOT_EMPTY, MATCH],
                "source_url": [ANY, NOT_EMPTY, MATCH]
            },
            "load_time": [ANY, NOT_EMPTY, MATCH],
            "returned": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "looking-glass": {
        "data_call_name": "Looking Glass",
        "required_params": ["resource"],
        "optional_params": ["look_back_limit"],
        "output_params": {
            "rrcs": {
                "rrc": [ANY, NOT_EMPTY, MATCH],
                "location": [ANY, NOT_EMPTY, MATCH],
                "peers": {
                    "asn_origin": [ANY, NOT_EMPTY, MATCH],
                    "as_path": [ANY, NOT_EMPTY, MATCH],
                    "community": [ANY, NOT_EMPTY, MATCH],
                    "last_updated": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "prefix": [ANY, NOT_EMPTY, MATCH],
                    "peer": [ANY, NOT_EMPTY, MATCH],
                    "origin": [ANY, NOT_EMPTY, MATCH],
                    "next_hop": [ANY, NOT_EMPTY, MATCH],
                    "latest_time": [ANY, NOT_EMPTY, MATCH]
                }
            },
            "latest_time": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "maxmind-geo-lite": {
        "data_call_name": "Maxmind Geo Lite",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "located_resources": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "locations": {
                    "country": [ANY, NOT_EMPTY, MATCH],
                    "city": [ANY, NOT_EMPTY, MATCH],
                    "resources": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                    "latitude": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "longitude": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "covered_percentage": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "unknown_percentage": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "unknown_percentage": {
                "v4": [ANY, NOT_EMPTY, MATCH, COMPARE]
            }
        }
    },

    "maxmind-geo-lite-announced-by-as": {
        "data_call_name": "Maxmind Geo Lite Announced By AS",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "located_resources": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "locations": {
                    "country": [ANY, NOT_EMPTY, MATCH],
                    "city": [ANY, NOT_EMPTY, MATCH],
                    "resources": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                    "latitude": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "longitude": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "covered_percentage": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "unknown_percentage": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "unknown_percentage": {
                "v4": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "v6": [ANY, NOT_EMPTY, MATCH, COMPARE]
            }
        }
    },

    # cannot obtain measurements
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
                "measurements": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "earliest_time": [],
            "latest_time": [],
            "starttime": [],
            "endtime": [],
            "resource": []
        }
    },
    # in maintenance
    "mlab-activity-count": {
        "data_call_name": "Mlab Activity Count",
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
    # in maintenance
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
    # in maintenance
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
            "asns": [ANY, NOT_EMPTY, MATCH, INCLUDE],
            "prefix": [ANY, NOT_EMPTY, MATCH]
        }
    },

    "prefix-count": {
        "data_call_name": "Prefix Count",
        "required_params": ["resource"],
        "optional_params": [
            "starttime",
            "endtime",
            "min_peers_seeing",
            "resolution"
        ],
        "output_params": {
            "ipv4": ParamsCommons.PREFIX_CHANGES_PER_TIMESTAMP,
            "ipv6": ParamsCommons.PREFIX_CHANGES_PER_TIMESTAMP,
            "resolution": [ANY, NOT_EMPTY, MATCH]
        }
    },

    "prefix-overview": {
        "data_call_name": "Prefix Overview",
        "required_params": ["resource"],
        "optional_params": ["min_peers_seeing", "max_related", "query_time"],
        "output_params": {
            "asns": {
                "asn": [ANY, NOT_EMPTY, MATCH],
                "holder": [ANY, NOT_EMPTY, MATCH]
            },
            "is_less_specific": [ANY, NOT_EMPTY, MATCH],  # bool
            "announced": [ANY, NOT_EMPTY, MATCH],  # bool
            "related_prefixes": [ANY, NOT_EMPTY, MATCH, INCLUDE],
            "type": [ANY, NOT_EMPTY, MATCH],
            "block": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "desc": [ANY, NOT_EMPTY, MATCH],
                "name": [ANY, NOT_EMPTY, MATCH]
            },
            "actual_num_related": [ANY, NOT_EMPTY, MATCH, COMPARE],
            "num_filtered_out": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "prefix-routing-consistency": {
        "data_call_name": "Prefix Routing Consistency",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "routes": {
                "in_bgp": [ANY, NOT_EMPTY, MATCH],   # bool
                "in_whois": [ANY, NOT_EMPTY, MATCH],   # bool
                "prefix": [ANY, NOT_EMPTY, MATCH],
                "origin": [ANY, NOT_EMPTY, MATCH],
                "irr_sources": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                "asn_name": [ANY, NOT_EMPTY, MATCH]
            }
        }
    },

    "prefix-size-distribution": {
        "data_call_name": "Prefix Size Distribution",
        "required_params": ["resource"],
        "optional_params": ["timestamp", "min_peers_seeing"],
        "output_params": {
            "ipv4": ParamsCommons.PREFIX_SIZE,
            "ipv6": ParamsCommons.PREFIX_SIZE
        }
    },

    "related-prefixes": {
        "data_call_name": "Related Prefixes",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "prefixes": {
                "prefix": [ANY, NOT_EMPTY, MATCH],
                "origin_asn": [ANY, NOT_EMPTY, MATCH],
                "asn_name": [ANY, NOT_EMPTY, MATCH],
                "relationship": [ANY, NOT_EMPTY, MATCH]
            },
        }
    },

    "reverse-dns": {
        "data_call_name": "Reverse DNS",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "delegations": {
                "key": [ANY, NOT_EMPTY, MATCH],
                "value": [ANY, NOT_EMPTY, MATCH]
            }
        }
    },

    # not straightforward -- to discuss, there are changing prefixes
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
            "result": [ANY, NOT_EMPTY, MATCH, INCLUDE],
            "error": [ANY, NOT_EMPTY, MATCH]
        }
    },

    "rir": {
        "data_call_name": "RIR",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime", "lod"],
        "output_params": {
            "rirs": {
                "rir": [ANY, NOT_EMPTY, MATCH],
                "first_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "last_time": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "lod": [ANY, NOT_EMPTY, MATCH],
            "latest": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "rir-geo": {
        "data_call_name": "RIR Geo",
        "required_params": ["resource"],
        "optional_params": ["query_time"],
        "output_params": {
            "located_resources": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "location": [ANY, NOT_EMPTY, MATCH]
            }
        }
    },

    "rir-prefix-size-distribution": {
        "data_call_name": "RIR Prefix Size Distribution",
        "required_params": ["resource"],
        "optional_params": ["query_time"],
        "output_params": {
            "rirs": {
                "rir": [ANY, NOT_EMPTY, MATCH],
                "distribution": {
                    "prefix_size": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                }
            }
        }
    },

    "rir-stats-country": {
        "data_call_name": "RIR Stats Country",
        "required_params": ["resource"],
        "optional_params": ["query_time"],
        "output_params": {
            "located_resources": {
                "resource": [ANY, NOT_EMPTY, MATCH],
                "location": [ANY, NOT_EMPTY, MATCH]
            }
        }
    },

    # Output structure changes based on inputs for list_asns and asn_types
    # requires the change
    "ris-asns": {
        "data_call_name": "RIS ASNs",
        "required_params": [],
        "optional_params": ["list_asns", "asn_types", "query_time"],
        "output_params": {
            # "asns": [ANY, NOT_EMPTY, MATCH, INCLUDE],
            "asns": {
                "originating": [ANY, NOT_EMPTY, MATCH, INCLUDE],
                "transiting": [ANY, NOT_EMPTY, MATCH, INCLUDE]
            },
            "counts": {
                "total": [ANY, NOT_EMPTY, MATCH, COMPARE]
            }
        }
    },

    "ris-first-last-seen": {
        "data_call_name": "RIS First-Last-Seen",
        "required_params": ["resource"],
        "optional_params": ["include"],
        "output_params": {
            "measurements": [ANY, NOT_EMPTY, MATCH, INCLUDE],
            "statistics": {
                "measurements": [ANY, NOT_EMPTY, MATCH, COMPARE]
            }
        }
    },

    "ris-full-table-threshold": {
        "data_call_name": "RIS Full-Table Threshold",
        "required_params": [],
        "optional_params": ["query_time"],
        "output_params": {
            "v4": [ANY, NOT_EMPTY, MATCH, COMPARE],
            "v6": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "ris-peer-count": {
        "data_call_name": "RIS Peer Count",
        "required_params": [],
        "optional_params": [
            "starttime",
            "endtime",
            "v4_full_prefix_threshold",
            "v6_full_prefix_threshold"
        ],
        "output_params": {
            "peer_count": {
                "v4": {
                    "total": {
                        "timestamp": [ANY, NOT_EMPTY, MATCH, COMPARE],
                        "count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                    },
                    "full_feed": {
                        "timestamp": [ANY, NOT_EMPTY, MATCH, COMPARE],
                        "count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                    }
                },
                "v6": {
                    "total": {
                        "timestamp": [ANY, NOT_EMPTY, MATCH, COMPARE],
                        "count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                    },
                    "full_feed": {
                        "timestamp": [ANY, NOT_EMPTY, MATCH, COMPARE],
                        "count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                    }
                }
            },
            "v4_full_prefix_threshold": [ANY, NOT_EMPTY, MATCH, COMPARE],
            "v6_full_prefix_threshold": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "ris-peerings": {
        "data_call_name": "RIS Peerings",
        "required_params": ["resource"],
        "optional_params": ["query_time"],
        "output_params": {
            "peerings": {
                "probe": {
                    "city": [ANY, NOT_EMPTY, MATCH],
                    "country": [ANY, NOT_EMPTY, MATCH],
                    "longitude": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "latitude": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "name": [ANY, NOT_EMPTY, MATCH],
                    "ipv4_peer_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "ipv6_peer_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "ixp": [ANY, NOT_EMPTY, MATCH]
                },
                "peers": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "ip_version": [ANY, NOT_EMPTY, MATCH],
                    "table_version": [ANY, NOT_EMPTY, MATCH],
                    "prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "routes": {
                        "as_path": [ANY, NOT_EMPTY, MATCH, INCLUDE]
                    }
                }
            }
        }
    },
    # how to optimize the keys here?
    "ris-peers": {
        "data_call_name": "RIS Peers",
        "required_params": [],
        "optional_params": ["query_time"],
        "output_params": {
            # INCLUDE_KEYS
            "peers": {
                "rrc00": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc01": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc02": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc03": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc04": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc05": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc06": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc07": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc08": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc09": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc10": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc11": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc12": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc13": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc14": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc15": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc16": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc17": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc18": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc19": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc20": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc21": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc22": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc23": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc24": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc25": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "rrc26": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },

            },
        }
    },

    "ris-prefixes": {
        "data_call_name": "RIS Peers",
        "required_params": ["resource"],
        "optional_params": [
            "query_time",
            "list_prefixes",
            "types",
            "af",
            "noise"
        ],
        "output_params": {
            "counts": {
                "v4": {
                    "originating": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "transiting": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "v6": {
                    "originating": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "transiting": [ANY, NOT_EMPTY, MATCH, COMPARE]
                }
            }
        }
    },

    "routing-history": {
        "data_call_name": "Routing History",
        "required_params": ["resource"],
        "optional_params": [
            "max_rows",
            "include_first_hop",
            "normalise_visibility",
            "min_peers",
            "starttime",
            "endtime"
        ],
        "output_params": {
            "by_origin": {
                "origin": [ANY, NOT_EMPTY, MATCH],
                "prefixes": {
                    "prefix": [ANY, NOT_EMPTY, MATCH],
                    "timelines": {
                        "starttime": [ANY, NOT_EMPTY, MATCH, COMPARE],
                        "endtime": [ANY, NOT_EMPTY, MATCH, COMPARE],
                        "full_peers_seeing": [ANY, NOT_EMPTY, MATCH, COMPARE]
                    }
                }
            },
            "latest_max_ff_peers": {
                "v4": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "v6": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "time_granularity": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "routing-status": {
        "data_call_name": "Routing Status",
        "required_params": ["resource"],
        "optional_params": ["timestamp", "min_peers_seeing"],
        "output_params": {
            "first_seen": {
                "prefix": [ANY, NOT_EMPTY, MATCH],
                "origin": [ANY, NOT_EMPTY, MATCH],
                "time": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "last_seen": {
                "prefix": [ANY, NOT_EMPTY, MATCH],
                "origin": [ANY, NOT_EMPTY, MATCH],
                "time": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "visibility": {
                "v4": {
                    "ris_peers_seeing": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "total_ris_peers": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "v6": {
                    "ris_peers_seeing": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "total_ris_peers": [ANY, NOT_EMPTY, MATCH, COMPARE]
                }
            },
            "announced_space": {
                "v4": {
                    "prefixes": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "ips": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "v6": {
                    "prefixes": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "48s": [ANY, NOT_EMPTY, MATCH, COMPARE]
                }
            },
            "observed_neighbours": [ANY, NOT_EMPTY, MATCH, COMPARE]
        }
    },

    "rpki-history": {
        "data_call_name": "RPKI History",
        "required_params": ["resource"],
        "optional_params": ["family", "resolution", "delegated"],
        "output_params": {
            "timeseries": {
                "asn": [ANY, NOT_EMPTY, MATCH],
                "time": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "family": [ANY, NOT_EMPTY, MATCH],
                "rpki": {
                    "vrp_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                }
            }
        }
    },

    "rpki-validation": {
        "data_call_name": "RPKI Validation Status",
        "required_params": ["resource", "prefix"],
        "optional_params": [],
        "output_params": {
            "validating_roas": {
                "origin": [ANY, NOT_EMPTY, MATCH],
                "prefix": [ANY, NOT_EMPTY, MATCH],
                "max_length": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "validity": [ANY, NOT_EMPTY, MATCH]
            },
            "status": [ANY, NOT_EMPTY, MATCH],
            "validator": [ANY, NOT_EMPTY, MATCH],
        }
    },

    "rrc-info": {
        "data_call_name": "RRC Info",
        "required_params": [],
        "optional_params": [],
        "output_params": {
            "rrcs": {
                "id": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "name": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "geographical_location": [ANY, NOT_EMPTY, MATCH],
                "topological_location": [ANY, NOT_EMPTY, MATCH],
                "multihop": [ANY, NOT_EMPTY, MATCH],  # bool
                "activated_on": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "deactivated_on": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "peers": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "v4_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "is_full_feed_v4": [ANY, NOT_EMPTY, MATCH],  # bool
                    "v6_prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "is_full_feed_v6": [ANY, NOT_EMPTY, MATCH]  # bool
                }
            }
        }
    },

    "searchcomplete": {
        "data_call_name": "Searchcomplete",
        "required_params": ["resource"],
        "optional_params": ["limit"],
        "output_params": {
            "categories": {
                "category": [ANY, NOT_EMPTY, MATCH],
                "suggestions": {
                    "label": [ANY, NOT_EMPTY, MATCH],
                    "value": [ANY, NOT_EMPTY, MATCH],
                    "description": [ANY, NOT_EMPTY, MATCH]
                }
            }
        }
    },

    "speedchecker-bandwidth-measurements": {
        "data_call_name": "Speedchecker Bandwidth Measurements",
        "required_params": ["resource"],
        "optional_params": ["starttime", "endtime"],
        "output_params": {
            "measurements": {
                "prefix": [ANY, NOT_EMPTY, MATCH],
                "date": [ANY, NOT_EMPTY, MATCH],
                "down": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "up": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "statistics": {
                "measurements": [ANY, NOT_EMPTY, MATCH, COMPARE]
            }
        }
    },

    "visibility": {
        "data_call_name": "Visibility",
        "required_params": ["resource"],
        "optional_params": ["query_time", "include"],
        "output_params": {
            "visibilities": {
                "probe": {
                    "city": [ANY, NOT_EMPTY, MATCH],
                    "country": [ANY, NOT_EMPTY, MATCH],
                    "longitude": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "latitude": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "name": [ANY, NOT_EMPTY, MATCH],
                    "ipv4_peer_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "ipv6_peer_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                    "ixp": [ANY, NOT_EMPTY, MATCH]
                },
                "ipv4_full_table_peers_not_seeing": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "ipv6_full_table_peers_not_seeing": {
                    "asn": [ANY, NOT_EMPTY, MATCH],
                    "ip": [ANY, NOT_EMPTY, MATCH],
                    "prefix_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
                },
                "ipv4_full_table_peer_count": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "ipv6_full_table_peer_count": [ANY, NOT_EMPTY, MATCH, COMPARE]
            },
            "related_prefixes": [ANY, NOT_EMPTY, MATCH, INCLUDE]
        }
    },

    "whats-my-ip": {
        "data_call_name": "Whats My IP",
        "required_params": [],
        "optional_params": [],
        "output_params": {
            "ip": [ANY, NOT_EMPTY, MATCH]
        }
    },

    "whois": {
        "data_call_name": "Whois",
        "required_params": ["resource"],
        "optional_params": [],
        "output_params": {
            "records": {
                "key": [ANY, NOT_EMPTY, MATCH],
                "value": [ANY, NOT_EMPTY, MATCH],
                "details_link": [ANY, NOT_EMPTY, MATCH]
            },
            "irr_records": {
                "key": [ANY, NOT_EMPTY, MATCH],
                "value": [ANY, NOT_EMPTY, MATCH],
                "details_link": [ANY, NOT_EMPTY, MATCH]
            },
            "authorities": [ANY, NOT_EMPTY, MATCH, INCLUDE]
        }
    },

    "whois-object-last-updated": {
        "data_call_name": "Whois Object Last Updated",
        "required_params": ["object", "type", "source"],
        "optional_params": ["timestamp", "compare_with_live"],
        "output_params": {
            "last_updated": [ANY, NOT_EMPTY, MATCH, COMPARE],
            "same_as_live": [ANY, NOT_EMPTY, MATCH],
        }
    },

    "zonemaster": {
        "data_call_name": "Zonemaster",
        "required_params": ["resource"],
        "optional_params": ["method"],
        "output_params": {
            "id": [],
            "result": {
                "created_at": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "undelegated": [ANY, NOT_EMPTY, MATCH],
                "id": [ANY, NOT_EMPTY, MATCH],
                "creation_time": [ANY, NOT_EMPTY, MATCH, COMPARE],
                "overall_result": [ANY, NOT_EMPTY, MATCH]
            }
        }
    }
}
