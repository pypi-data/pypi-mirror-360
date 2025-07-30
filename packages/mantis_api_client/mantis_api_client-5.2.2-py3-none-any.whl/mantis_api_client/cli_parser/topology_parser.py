# -*- coding: utf-8 -*-
import argparse
import json
import sys
from typing import Any

from mantis_scenario_model.lab_config_model import LabConfig
from mantis_scenario_model.node import VirtualMachine
from pydantic.json import pydantic_encoder
from ruamel.yaml import YAML

from mantis_api_client import scenario_api
from mantis_api_client import user_api
from mantis_api_client.oidc import get_oidc_client
from mantis_api_client.utils import colored
from mantis_api_client.utils import wait_lab


#
# 'topology_list_handler' handler
#
def topology_list_handler(args: Any) -> None:
    try:
        topologies = sorted(scenario_api.fetch_topologies(), key=lambda x: x.name)
    except Exception as e:
        print(colored(f"Error when fetching topologies: '{e}'", "red"))
        sys.exit(1)

    if args.json:
        print(json.dumps(topologies, default=pydantic_encoder))
        return

    print("[+] Available topologies:")
    for topology in topologies:
        print(f"  [+] {topology.name}")


#
# 'topology_info_handler' handler
#
def topology_info_handler(args: Any) -> None:
    # Parameters
    topology_name = args.topology_name

    try:
        topology = scenario_api.fetch_topology_by_name(topology_name)
    except Exception as e:
        print(colored(f"Error when fetching topology {topology_name}: '{e}'", "red"))
        sys.exit(1)

    if args.json:
        print(topology.json())
        return

    print("[+] Topology information:")
    print(f"  [+] \033[1mName\033[0m: {topology.name}")
    print("  [+] \033[1mNodes\033[0m:")
    for node in topology.nodes:
        if type(node) is VirtualMachine:
            print(f"       [+] {node.type}: {node.name} ({node.basebox_id})")
        else:
            print(f"       [+] {node.type}: {node.name}")
    print("  [+] \033[1mLinks\033[0m:")
    for link in topology.links:
        print(
            f"        [+] {link.switch.name}({link.switch.type}) -- {link.params.ip} -- {link.node.name}({link.node.type})"
        )


def _topology_create_or_run_lab(args: Any, do_run: bool = True):
    # Parameters
    topology_name = args.topology_name
    lab_config_path = args.lab_config_path

    if not args.group_name:
        try:
            group_name = get_oidc_client().get_default_group(raise_exc=True)
        except Exception as e:
            print(colored(f"Error when fetching attacks: '{e}'", "red"))
            sys.exit(1)
    else:
        group_name = args.group_name

    # Retrieve associated group id
    if group_name is None:
        print(colored("Your subscription level does not permit to launch labs", "red"))
        sys.exit(1)
    group_id = user_api.get_organization_id_from_group_name(group_name)

    # Manage lab configuration
    if lab_config_path is None:
        lab_config_dict = {}
    else:
        with open(lab_config_path, "r") as fd:
            yaml_content = fd.read()
        loader = YAML(typ="rt")
        lab_config_dict = loader.load(yaml_content)
    lab_config = LabConfig(**lab_config_dict)

    # Launch topology
    try:
        topology = scenario_api.fetch_topology_by_name(topology_name)
        print(f"[+] Going to execute topology: {topology.name}")

        if do_run:
            lab_id = scenario_api.run_lab_topology(
                topology, lab_config, group_name, group_id
            )
        else:
            lab_id = scenario_api.create_lab_topology(
                topology, lab_config, group_name, group_id
            )

        print(f"[+] Topology lab ID: {lab_id}")

        if do_run:
            wait_lab(lab_id)
            print("[+] Topology started")

    except Exception as e:
        print(colored(f"Error when running topology {topology_name}: '{e}'", "red"))
        sys.exit(1)
    finally:
        if do_run and args.destroy_after_scenario:
            print("[+] Stopping lab...")
            scenario_api.stop_lab(lab_id)


#
# 'topology_create_lab_handler' handler
#
def topology_create_lab_handler(args: Any) -> None:
    _topology_create_or_run_lab(args, do_run=False)


#
# 'topology_run_lab_handler' handler
#
def topology_run_lab_handler(args: Any) -> None:
    _topology_create_or_run_lab(args, do_run=True)


def add_topology_parser(
    root_parser: argparse.ArgumentParser,
    subparsers: Any,
) -> None:
    # -------------------
    # --- Scenario API options (topologies)
    # -------------------

    parser_topology = subparsers.add_parser(
        "topology",
        help="Scenario API related commands (topology)",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_topology = parser_topology.add_subparsers()

    # 'topology_list' command
    parser_topology_list = subparsers_topology.add_parser(
        "list",
        help="List all available topologies",
        formatter_class=root_parser.formatter_class,
    )
    parser_topology_list.set_defaults(func=topology_list_handler)
    parser_topology_list.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'topology_info' command
    parser_topology_info = subparsers_topology.add_parser(
        "info",
        help="Get information about a topology",
        formatter_class=root_parser.formatter_class,
    )
    parser_topology_info.set_defaults(func=topology_info_handler)
    parser_topology_info.add_argument(
        "topology_name", type=str, help="The topology name"
    )
    parser_topology_info.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'topology_create_lab' command
    parser_topology_create_lab = subparsers_topology.add_parser(
        "create",
        help="Create a lab with a specific topology",
        formatter_class=root_parser.formatter_class,
    )
    parser_topology_create_lab.set_defaults(func=topology_create_lab_handler)
    parser_topology_create_lab.add_argument(
        "topology_name", type=str, help="The topology name"
    )
    parser_topology_create_lab.add_argument(
        "--destroy",
        action="store_true",
        dest="destroy_after_scenario",
        help="Do not keep the lab up after topology execution (False by default)",
    )
    parser_topology_create_lab.add_argument(
        "--group_name",
        dest="group_name",
        help="The group ID that have ownership on lab",
    )
    parser_topology_create_lab.add_argument(
        "--lab_config",
        action="store",
        required=False,
        dest="lab_config_path",
        help="Input path of a YAML configuration for the scenario to run",
    )

    # 'topology_run_lab' command
    parser_topology_run_lab = subparsers_topology.add_parser(
        "run",
        help="Create and run a lab with a specific topology",
        formatter_class=root_parser.formatter_class,
    )
    parser_topology_run_lab.set_defaults(func=topology_run_lab_handler)
    parser_topology_run_lab.add_argument(
        "topology_name", type=str, help="The topology name"
    )
    parser_topology_run_lab.add_argument(
        "--destroy",
        action="store_true",
        dest="destroy_after_scenario",
        help="Do not keep the lab up after topology execution (False by default)",
    )
    parser_topology_run_lab.add_argument(
        "--group_name",
        dest="group_name",
        help="The group ID that have ownership on lab",
    )
    parser_topology_run_lab.add_argument(
        "--lab_config",
        "-lc",
        action="store",
        required=False,
        dest="lab_config_path",
        help="Input path of a YAML configuration for the scenario run",
    )

    parser_topology.set_defaults(func=lambda _: parser_topology.print_help())
