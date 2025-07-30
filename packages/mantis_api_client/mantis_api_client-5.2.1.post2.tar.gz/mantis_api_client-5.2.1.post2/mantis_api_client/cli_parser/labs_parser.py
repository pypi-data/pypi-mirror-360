# -*- coding: utf-8 -*-
import argparse
import datetime
import json
import sys
from typing import Any
from typing import List

from mantis_common_model.pagination import Pagination
from mantis_scenario_model.api_scenario_model import LabListReply
from mantis_scenario_model.lab_model import Lab

import mantis_api_client.scenario_api as scenario_api


#
# 'labs_handler' handler
#
def labs_handler(args: Any) -> None:
    all_labs = args.all_labs
    offset = 100
    labs_to_list: List[Lab] = []
    try:
        page: int = 1
        pagination: Pagination = Pagination(**{"page": page, "limit": offset})
        labs: LabListReply = scenario_api.fetch_labs(
            all_labs=all_labs, pagination=pagination
        )
        labs_to_list = labs_to_list + [Lab(**lab) for lab in labs["data"]]
        while pagination.page * pagination.limit < labs["pagination"]["total_records"]:
            page = page + 1
            pagination = Pagination(**{"page": page, "limit": offset})
            labs = scenario_api.fetch_labs(all_labs=all_labs, pagination=pagination)
            labs_to_list = labs_to_list + [Lab(**lab) for lab in labs["data"]]

    except Exception as e:
        print(f"Error when fetching labs: '{e}'")
        sys.exit(1)

    if args.json:
        print(json.dumps(labs))
        return

    print("[+] Available labs:")
    for lab in labs_to_list:
        lab_creation_timestamp = (
            datetime.datetime.fromtimestamp(
                lab.lab_creation_timestamp, datetime.timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S")
            + " UTC"
        )

        print(f"  [+] \033[1mID\033[0m: {lab.runner_id}")
        print(f"        [+] \033[1mLab start time\033[0m: {lab_creation_timestamp}")
        print(f"        [+] \033[1mStatus\033[0m: {lab.status}")
        print(f"        [+] \033[1mType\033[0m: {lab.content_type}")


def add_labs_parser(root_parser: argparse.ArgumentParser, subparsers: Any) -> None:
    # Subparser labs
    parser_labs = subparsers.add_parser(
        "labs", help="List current labs", formatter_class=root_parser.formatter_class
    )
    parser_labs.set_defaults(func=labs_handler)
    parser_labs.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="all_labs",
        help="Include stopped labs",
    )
    parser_labs.add_argument("--json", help="Return JSON result.", action="store_true")
