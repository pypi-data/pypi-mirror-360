# -*- coding: utf-8 -*-
import argparse
import json
import sys
from typing import Any

from pydantic.json import pydantic_encoder

from mantis_api_client import scenario_api
from mantis_api_client.utils import colored


#
# 'log_collector_list_handler' handler
#
def log_collector_list_handler(args: Any) -> None:
    try:

        log_collectors = scenario_api.get_log_collectors()
        log_collectors = sorted(log_collectors, key=lambda k: (k["collector_name"]))

        if args.json:
            print(json.dumps(log_collectors, default=pydantic_encoder))
            return

        print("[+] Available Logs collectors:")
        for lg in log_collectors:
            print(f"       [+] \033[1mName\033[0m: {lg['collector_name']}")
            print(f"       [+] \033[1mType\033[0m: {lg['collector_type']}")
            print(f"       [+] \033[1mDescription\033[0m: {lg['description']}")
            cpes = lg["cpe_os_constraints"]
            if len(cpes) > 0:
                print("       [+] \033[1mCPE OS constraints\033[0m:")
                for cpe in cpes:
                    print(f"           [+] {cpe}")
            print()

    except Exception as e:
        print(
            colored(
                f"Error when fetching log collectors data: '{e}'", "red", "on_white"
            )
        )
        sys.exit(1)


def add_log_collector_parser(root_parser: argparse.ArgumentParser, subparsers: Any):

    # --------------------
    # --- Scenario API options (log_collector)
    # --------------------

    parser_log_collector = subparsers.add_parser(
        "log_collector",
        help="Scenario API related commands (log_collector)",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_log_collector = parser_log_collector.add_subparsers()

    # 'log_collector_list' command
    parser_log_collector_list = subparsers_log_collector.add_parser(
        "list",
        help="List log collectors configuration information",
        formatter_class=root_parser.formatter_class,
    )
    parser_log_collector_list.set_defaults(func=log_collector_list_handler)
    parser_log_collector_list.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    parser_log_collector.set_defaults(func=lambda _: parser_log_collector.print_help())
