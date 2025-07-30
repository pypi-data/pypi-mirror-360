#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import argparse
import sys
from typing import List

import argcomplete
from omegaconf import OmegaConf
from rich_argparse import RichHelpFormatter

from mantis_api_client.cli_parser.account_parser import add_account_parser
from mantis_api_client.cli_parser.attack_parser import add_attack_parser
from mantis_api_client.cli_parser.basebox_parser import add_basebox_parser
from mantis_api_client.cli_parser.dataset_parser import add_dataset_parser
from mantis_api_client.cli_parser.lab_parser import add_lab_parser
from mantis_api_client.cli_parser.labs_parser import add_labs_parser
from mantis_api_client.cli_parser.log_collector_parser import add_log_collector_parser
from mantis_api_client.cli_parser.scenario_parser import add_scenario_parser
from mantis_api_client.cli_parser.signature_parser import add_signature_parser
from mantis_api_client.cli_parser.topology_parser import add_topology_parser
from mantis_api_client.cli_parser.user_parser import add_user_parser
from mantis_api_client.config import mantis_api_client_config
from mantis_api_client.oidc import initialize_oidc_client
from mantis_api_client.utils import colored


def create_mantis_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(formatter_class=RichHelpFormatter)

    # Config file argument
    parser.add_argument("--config", help="Configuration file")

    # Common debug argument
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug_mode",
        help="Activate debug mode (default: %(default)s)",
    )

    subparsers = parser.add_subparsers()

    # --------------------
    # --- Scenario API options (attack)
    # --------------------

    add_attack_parser(root_parser=parser, subparsers=subparsers)

    # --------------------
    # --- Scenario API options (basebox)
    # --------------------

    add_basebox_parser(root_parser=parser, subparsers=subparsers)

    # --------------------
    # --- Scenario API options (dataset)
    # --------------------

    add_dataset_parser(root_parser=parser, subparsers=subparsers)

    # --------------------
    # --- Scenario API options (scenario)
    # --------------------

    add_scenario_parser(root_parser=parser, subparsers=subparsers)

    # --------------------
    # --- Scenario API options (topology)
    # --------------------

    add_topology_parser(root_parser=parser, subparsers=subparsers)

    # --------------------
    # --- Scenario API options (log_collector)
    # --------------------

    add_log_collector_parser(root_parser=parser, subparsers=subparsers)

    # --------------------
    # --- User API options
    # --------------------

    add_user_parser(root_parser=parser, subparsers=subparsers)

    # -------------------
    # --- Labs subparser
    # -------------------

    add_labs_parser(root_parser=parser, subparsers=subparsers)

    # -------------------
    # --- Lab subparser
    # -------------------

    add_lab_parser(root_parser=parser, subparsers=subparsers)

    # -------------------
    # --- login options
    # -------------------

    add_account_parser(root_parser=parser, subparsers=subparsers)

    # --------------------
    # --- Scenario API options (signature)
    # --------------------

    add_signature_parser(root_parser=parser, subparsers=subparsers)

    return parser


def handle_command_line(command_line_args: List[str]) -> None:
    try:
        initialize_oidc_client()
    except Exception as e:
        print(colored(str(e), "white", "on_red"))
        sys.exit(1)

    parser = create_mantis_cli_parser()

    argcomplete.autocomplete(parser)

    parser_defaults = {
        k: mantis_api_client_config[k]
        for k in mantis_api_client_config
        if not OmegaConf.is_missing(mantis_api_client_config, k)
    }
    parser.set_defaults(
        func=lambda _: parser.print_help(), **parser_defaults
    )  # all arguments must be set at same time

    args, left_argv = parser.parse_known_args(command_line_args)

    # Parse remaining args from command line (overriding potential config file
    # parameters)
    args = parser.parse_args(left_argv, args)

    # If in a 'lab' namespace, we set specific environment variables
    # to allow remote access to the running lab
    if hasattr(args, "set_lab"):
        args.set_lab(args)

    args.func(args)

    if hasattr(args, "set_lab"):
        args.unset_lab(args)

    sys.exit(0)


def main() -> None:
    command_line_args = sys.argv[1:]
    handle_command_line(command_line_args)


if __name__ == "__main__":
    main()
