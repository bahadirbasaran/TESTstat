import requests
from datetime import datetime

from core.socket import INRDBSocket
from core.utils import post_slack_message


def run_rrc_check(host, slack_hooks):

    missing_rrcs = []

    ncc_prefixes = [
        "193.0.0.0/21",
        "2001:67c:2e8::/48"
    ]
    str_ncc_prefixes = "\n".join(ncc_prefixes)

    # Static list of RRCs
    rrc_map = {
        "0": "RIPE-NCC Multihop, Amsterdam, Netherlands",
        "1": "LINX / LONAP, London, United Kingdom",
        "2": "SFINX, Paris, France",
        "3": "AMS-IX / NL-IX, Amsterdam, Netherlands",
        "4": "CIXP, Geneva, Switzerland",
        "5": "VIX, Vienna, Austria",
        "6": "DIX-IE / JPIX, Tokyo, Japan",
        "7": "Netnod, Stockholm, Sweden",
        "8": "MAE-WEST, San Jose, California, US",
        "9": "TIX, Zurich, Switzerland",
        "10": "MIX, Milan, Italy",
        "11": "NYIIX, New York City, New York, US",
        "12": "DE-CIX, Frankfurt, Germany",
        "13": "MSK-IX, Moscow, Russian Federation",
        "14": "PAIX, Palo Alto, California, US",
        "15": "PTTMetro, Sao Paulo, Brazil",
        "16": "NOTA, Miami, Florida, US",
        "18": "Catnix, Barcelona, Spain",
        "19": "NAP Africa JB, Johannesburg, South Africa",
        "20": "SwissIX, Zurich, Switzerland",
        "21": "France-IX, Paris, France",
        "22": "InterLAN, Bucharest, Romania",
        "23": "Equinix SG, Singapore, Singapore",
        "24": "LACNIC Multihop, Montevideo, Uruguay",
        "25": "RIPE-NCC Multihop, Amsterdam, Netherlands",
        "26": "UAE-IX, Dubai, UAE"
    }

    current_date = datetime.now().strftime("%d/%m/%y")

    message_payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f":red_circle: TESTstat RRC Report - {current_date}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Resources used: *\n{str_ncc_prefixes}"
                    }
                ]
            }
        ]
    }

    response_rrc_locations = requests.get(f"https://{host}/data/rrc-locations/data.json?cache=ignore")
    if response_rrc_locations.status_code == 200:
        rrc_map = response_rrc_locations.json()["data"]["locations"]

    # Pad single digits for compliance with response data
    rrc_map = {f"RRC{int(rrc):02}": location for rrc, location in rrc_map.items()}

    try:
        whois_socket = INRDBSocket("riswhois.ripe.net", 43)
    except Exception as exception:
        error_message = "An error occurred during the connection to riswhois.ripe.net!"
        message_payload["blocks"][1]["fields"][0]["text"] = error_message

        print(exception)
        if slack_hooks:
            post_slack_message(message_payload)
        exit(1)

    for resource in ncc_prefixes:

        # Get RIPEstat ris-peerings response
        stat_response = requests.get(
            f"https://{host}/data/ris-peerings/data.json?resource={resource}&cache=ignore"
        )
        if stat_response.status_code != 200:
            error_message = "An error occurred during the connection to RIS Peerings!"
            message_payload["blocks"][1]["fields"][0]["text"] = error_message
            
            print(error_message)
            if slack_hooks:
                post_slack_message(message_payload)
            exit(1)

        rrcs_in_peerings = [
            peering["probe"]["name"] for peering in stat_response.json()["data"]["peerings"]
        ]

        # Get RIS Whois response
        whois_response = ''
        socket_finished = False
        current_line = last_line = "waiting"
        
        whois_socket.send_line(f" -x {resource}")
        while not socket_finished:
            last_line = current_line
            try:
                current_line = whois_socket.receive_line()
            except Exception as exception:
                error_message = "An error occurred during the connection to riswhois.ripe.net!"
                message_payload["blocks"][1]["fields"][0]["text"] = error_message

                print(exception)
                if slack_hooks:
                    post_slack_message(message_payload)

                whois_socket.close_socket()
                exit(1)

            if not (last_line or current_line):
                socket_finished = True
            else:
                whois_response += current_line + '\n'
    
        whois_response = whois_response[whois_response.find("seen-at:      ") + len("seen-at:      "):whois_response.rfind("num-rispeers")]
        whois_response = whois_response.rstrip()
        rrcs_in_ris_whois = [rrc.upper() for rrc in whois_response.split(',')]

        missing_rrcs.extend([rrc for rrc in rrcs_in_ris_whois if rrc not in rrcs_in_peerings])
    
    whois_socket.close_socket()

    if missing_rrcs:

        unique_missing_rrcs = list(set(missing_rrcs))
        unique_missing_rrcs.sort()
        str_unique_missing_rrcs = "\n".join(unique_missing_rrcs)
        str_rrc_locations = "\n".join([rrc_map[rrc] for rrc in unique_missing_rrcs])

        if slack_hooks:
            message_block = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*RRC:*\n{str_unique_missing_rrcs}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Location:*\n{str_rrc_locations}"
                    }
                ]
            }
            message_payload["blocks"].append(message_block)
            post_slack_message(message_payload)
            
        print("Missing RRCs:\n")
        print("|RRC|      Location      |")
        for rrc in unique_missing_rrcs:
            print(f"| {rrc} | {rrc_map[rrc]} |")
