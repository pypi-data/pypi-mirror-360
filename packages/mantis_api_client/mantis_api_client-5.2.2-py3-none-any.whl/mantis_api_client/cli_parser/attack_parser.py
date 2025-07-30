# -*- coding: utf-8 -*-
import argparse
import json
import sys
import traceback
from typing import Any

from mantis_scenario_model.common import Empty
from mantis_scenario_model.lab_config_model import LabConfig
from pydantic.json import pydantic_encoder
from ruamel.yaml import YAML

from mantis_api_client import scenario_api
from mantis_api_client import user_api
from mantis_api_client.oidc import get_oidc_client
from mantis_api_client.utils import colored
from mantis_api_client.utils import wait_lab


#
# 'attack_list_handler' handler
#
def attack_list_handler(args: Any) -> None:
    try:
        attacks = sorted(scenario_api.fetch_attacks(), key=lambda x: x.name)
    except Exception as e:
        print(colored(f"Error when fetching attacks: '{e}'", "red"))
        sys.exit(1)

    if args.json:
        print(json.dumps(attacks, default=pydantic_encoder))
        return

    width = 35
    print(f"[+] Available attacks ({len(attacks)}):")
    name = "NAME"
    print(f"  [+] \033[1m{name: <{width}}- DESCRIPTION\033[0m")

    for attack in attacks:
        if not isinstance(attack.mitre_data.subtechnique, Empty):
            mitre_print = attack.mitre_data.subtechnique.id
        else:
            mitre_print = attack.mitre_data.technique.id

        print("  [+] ", end="")
        print(f"{attack.name: <{width}}", end="")
        print(f"- {attack.title} ({mitre_print})")


#
# 'attack_info_handler' handler
#
def attack_info_handler(args: Any) -> None:
    # Parameters
    attack_name = args.attack_name

    try:
        attack = scenario_api.fetch_attack_by_name(attack_name)
    except Exception as e:
        print(
            colored(
                f"Error when fetching attack {attack_name}: '{e}'", "red", "on_white"
            )
        )
        sys.exit(1)

    if args.json:
        print(attack.json())
        return

    print("[+] Attack information:")
    print(f"  [+] \033[1mID\033[0m: {attack.worker_id}")
    print(f"  [+] \033[1mName\033[0m: {attack.name}")
    print(f"  [+] \033[1mDescription\033[0m: {attack.description}")
    print("  [+] \033[1mAvailable scenario profiles\033[0m:")
    for scenario_profile in attack.scenario_profiles:
        print(
            f"    [+] {scenario_profile.name} (Topology: {scenario_profile.topology_name})"
        )


def _attack_create_or_run_lab(args: Any, do_run: bool = True):
    # Parameters
    attack_name = args.attack_name
    scenario_profile = args.scenario_profile
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

    # Safety checks
    try:
        attack = scenario_api.fetch_attack_by_name(attack_name)
    except Exception as e:
        print(colored(f"{e}", "red", "on_white"))
        sys.exit(1)
    print(f"[+] Going to create lab for: {attack.name}")

    # Safety checks
    if len(attack.scenario_profiles) == 0:
        print(
            f"Cannot run attack '{attack_name}', because it does not have any unit scenario"
        )
        sys.exit(-1)

    if scenario_profile is None:
        print(
            "Needed argument --scenario_profile in order to choose the unit scenario to run"
        )
        print("Available unit scenarios:")
        for available_scenario_profile in attack.scenario_profiles:
            print(f"  [+] {available_scenario_profile.name}")
        sys.exit(-1)

    for available_scenario_profile in attack.scenario_profiles:
        if available_scenario_profile.name == scenario_profile:
            break
    else:
        print(f"Select scenario config '{scenario_profile}' is not available")
        print("Available unit scenarios:")
        for available_scenario_profile in attack.scenario_profiles:
            print(f"  [+] {available_scenario_profile.name}")
        sys.exit(-1)

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
        if do_run:
            lab_id = scenario_api.run_lab_attack(
                attack,
                scenario_profile,
                lab_config,
                group_name,
                group_id,
            )
        else:
            lab_id = scenario_api.create_lab_attack(
                attack,
                scenario_profile,
                lab_config,
                group_name,
                group_id,
            )

        print(f"[+] Scenario lab ID: {lab_id}")

        if do_run:
            wait_lab(lab_id)
            print("[+] Scenario ended")

    except Exception as e:
        print(colored(f"Error when running attack {attack_name}: '{e}'", "red"))
        print(traceback.format_exc())
        sys.exit(1)
    finally:
        if do_run and args.destroy_after_scenario:
            print("[+] Stopping lab...")
            scenario_api.stop_lab(lab_id)


#
# 'attack_create_lab_handler' handler
#
def attack_create_lab_handler(args: Any) -> None:
    _attack_create_or_run_lab(args, do_run=False)


#
# 'attack_run_lab_handler' handler
#
def attack_run_lab_handler(args: Any) -> None:
    _attack_create_or_run_lab(args, do_run=True)


def add_attack_parser(root_parser: argparse.ArgumentParser, subparsers: Any) -> None:
    # --------------------
    # --- Scenario API options (attack)
    # --------------------

    parser_attack = subparsers.add_parser(
        "attack",
        help="Scenario API related commands (attacks)",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_attack = parser_attack.add_subparsers()

    # 'attack_list' command
    parser_attack_list = subparsers_attack.add_parser(
        "list",
        help="List all available attacks",
        formatter_class=root_parser.formatter_class,
    )
    parser_attack_list.set_defaults(func=attack_list_handler)
    parser_attack_list.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'attack_info' command
    parser_attack_info = subparsers_attack.add_parser(
        "info",
        help="Get information about an attack",
        formatter_class=root_parser.formatter_class,
    )
    parser_attack_info.set_defaults(func=attack_info_handler)
    parser_attack_info.add_argument("attack_name", type=str, help="The attack name")
    parser_attack_info.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'attack_create_lab' command
    parser_attack_create_lab = subparsers_attack.add_parser(
        "create",
        help="Create a lab with a specific attack",
        formatter_class=root_parser.formatter_class,
    )
    parser_attack_create_lab.set_defaults(func=attack_create_lab_handler)
    parser_attack_create_lab.add_argument(
        "attack_name", type=str, help="The attack name"
    )
    parser_attack_create_lab.add_argument(
        "--destroy",
        action="store_true",
        dest="destroy_after_scenario",
        help="Do not keep the lab up after scenario execution (False by default)",
    )
    parser_attack_create_lab.add_argument(
        "--scenario_profile",
        "-sp",
        dest="scenario_profile",
        help="Allows to define the unit scenario to create_lab for a unit attack",
    )
    parser_attack_create_lab.add_argument(
        "--group_name",
        dest="group_name",
        help="The group name that have ownership on lab",
    )
    parser_attack_create_lab.add_argument(
        "--lab_config",
        "-lc",
        action="store",
        required=False,
        dest="lab_config_path",
        help="Input path of a YAML configuration for the scenario to run",
    )

    # 'attack_run_lab' command
    parser_attack_run_lab = subparsers_attack.add_parser(
        "run",
        help="Create and run a lab with a specific attack",
        formatter_class=root_parser.formatter_class,
    )
    parser_attack_run_lab.set_defaults(func=attack_run_lab_handler)
    parser_attack_run_lab.add_argument("attack_name", type=str, help="The attack name")
    parser_attack_run_lab.add_argument(
        "--destroy",
        action="store_true",
        dest="destroy_after_scenario",
        help="Do not keep the lab up after scenario execution (False by default)",
    )
    parser_attack_run_lab.add_argument(
        "--scenario_profile",
        "-sp",
        dest="scenario_profile",
        help="Allows to define the unit scenario to run for a unit attack",
    )
    parser_attack_run_lab.add_argument(
        "--group_name",
        dest="group_name",
        help="The group name that have ownership on lab",
    )
    parser_attack_run_lab.add_argument(
        "--lab_config",
        "-lc",
        action="store",
        required=False,
        dest="lab_config_path",
        help="Input path of a YAML configuration for the scenario run",
    )

    parser_attack.set_defaults(func=lambda _: parser_attack.print_help())
