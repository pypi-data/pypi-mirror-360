# -*- coding: utf-8 -*-
import argparse
import json
import sys
from typing import Any

from mantis_scenario_model.lab_config_model import LabConfig
from pydantic.json import pydantic_encoder
from ruamel.yaml import YAML

from mantis_api_client import scenario_api
from mantis_api_client import user_api
from mantis_api_client.oidc import get_oidc_client
from mantis_api_client.utils import colored
from mantis_api_client.utils import wait_lab


#
# 'scenario_list_handler' handler
#
def scenario_list_handler(args: Any) -> None:
    try:
        scenarios = sorted(scenario_api.fetch_scenarios(), key=lambda x: x.name)
    except Exception as e:
        print(colored(f"Error when fetching scenarios: '{e}'", "red"))
        sys.exit(1)

    if args.json:
        print(json.dumps(scenarios, default=pydantic_encoder))
        return

    print(f"[+] Available scenarios ({len(scenarios)}):")
    for scenario in scenarios:
        print(f"  [+] \033[1m{scenario.name}\033[0m")
        print(f"         {scenario.description}")


#
# 'scenario_info_handler' handler
#
def scenario_info_handler(args: Any) -> None:
    # Parameters
    scenario_name = args.scenario_name

    try:
        scenario = scenario_api.fetch_scenario_by_name(scenario_name)
    except Exception as e:
        print(
            colored(
                f"Error when fetching scenario {scenario_name}: '{e}'",
                "red",
                "on_white",
            )
        )
        sys.exit(1)

    if args.json:
        print(scenario.json())
        return

    print("[+] Scenario information:")
    print(f"  [+] \033[1mName\033[0m: {scenario.name}")
    print("  [+] \033[1mKeywords\033[0m: ", end="")
    print(", ".join(scenario.keywords))
    print(f"  [+] \033[1mDescription\033[0m: {scenario.description}")
    if len(scenario.long_description) > 0:
        print("  [+] \033[1mLong description\033[0m:")
        for ld in scenario.long_description:
            print(f"        - {ld}")
    print(f"  [+] \033[1mLearning context\033[0m: {scenario.learning_context}")
    print("  [+] \033[1mAvailable scenario profiles\033[0m:")
    for scenario_profile in scenario.scenario_profiles:
        target = f", target: {scenario_profile.compromission.target_name}"
        print(
            f"""       [+] {scenario_profile.name} (Topology: {scenario_profile.topology_name}){target}"""
        )
    print("  [+] \033[1mUnit attacks available\033[0m:")
    for attack in scenario.attacks:
        print(f"       - {attack}")


def _scenario_create_or_run_lab(args: Any, do_run: bool = True):
    # Parameters
    scenario_name = args.scenario_name
    lab_config_path = args.lab_config_path
    scenario_profile = args.scenario_profile

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

    # Launch scenario
    try:
        scenario = scenario_api.fetch_scenario_by_name(scenario_name)
        print(f"[+] Going to execute scenario: {scenario.name}")

        if scenario_profile is None:
            print(
                "Needed argument --scenario_profile in order to choose the unit scenario to run"
            )
            print("Available unit scenarios:")
            for available_scenario_profile in scenario.scenario_profiles:
                print(f"  [+] {available_scenario_profile.name}")
            sys.exit(-1)

        if not any(scenario_profile == c.name for c in scenario.scenario_profiles):
            print(
                colored(
                    f"Error '{scenario_profile}' not supported for this scenario.",
                    "red",
                    "on_white",
                )
            )
            sys.exit(-1)

        if do_run:
            lab_id = scenario_api.run_lab_scenario(
                scenario=scenario,
                scenario_profile=scenario_profile,
                lab_config=lab_config,
                group_name=group_name,
                group_id=group_id,
            )
        else:
            lab_id = scenario_api.create_lab_scenario(
                scenario=scenario,
                scenario_profile=scenario_profile,
                lab_config=lab_config,
                group_name=group_name,
                group_id=group_id,
            )

        print(f"[+] Scenario lab ID: {lab_id}")

        if do_run:
            wait_lab(lab_id)
            print("[+] Scenario ended")

    except Exception as e:
        print(colored(f"Error when running scenario {scenario_name}: '{e}'", "red"))
        sys.exit(1)
    finally:
        if do_run and args.destroy_after_scenario:
            print("[+] Stopping lab...")
            scenario_api.stop_lab(lab_id)


#
# 'scenario_create_lab_handler' handler
#
def scenario_create_lab_handler(args: Any) -> None:
    _scenario_create_or_run_lab(args, do_run=False)


#
# 'scenario_run_lab_handler' handler
#
def scenario_run_lab_handler(args: Any) -> None:
    _scenario_create_or_run_lab(args, do_run=True)


def add_scenario_parser(
    root_parser: argparse.ArgumentParser,
    subparsers: Any,
) -> None:
    # --------------------
    # --- Scenario API options (scenario)
    # --------------------

    parser_scenario = subparsers.add_parser(
        "scenario",
        help="Scenario API related commands (scenario)",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_scenario = parser_scenario.add_subparsers()

    # 'scenario_list' command
    parser_scenario_list = subparsers_scenario.add_parser(
        "list",
        help="List all available scenarios",
        formatter_class=root_parser.formatter_class,
    )
    parser_scenario_list.set_defaults(func=scenario_list_handler)
    parser_scenario_list.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'scenario_info' command
    parser_scenario_info = subparsers_scenario.add_parser(
        "info",
        help="Get information about a scenario",
        formatter_class=root_parser.formatter_class,
    )
    parser_scenario_info.set_defaults(func=scenario_info_handler)
    parser_scenario_info.add_argument(
        "scenario_name", type=str, help="The scenario name"
    )
    parser_scenario_info.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'scenario_create_lab' command
    parser_scenario_create_lab = subparsers_scenario.add_parser(
        "create",
        help="Create a lab with a specific scenario",
        formatter_class=root_parser.formatter_class,
    )
    parser_scenario_create_lab.set_defaults(func=scenario_create_lab_handler)
    parser_scenario_create_lab.add_argument(
        "scenario_name", type=str, help="The scenario name"
    )
    parser_scenario_create_lab.add_argument(
        "--group_name",
        dest="group_name",
        help="The group ID that have ownership on lab",
    )
    parser_scenario_create_lab.add_argument(
        "--destroy",
        action="store_true",
        dest="destroy_after_scenario",
        help="Do not keep the lab up after scenario execution (False by default)",
    )
    parser_scenario_create_lab.add_argument(
        "--lab_config",
        "-lc",
        action="store",
        required=False,
        dest="lab_config_path",
        help="Input path of a YAML configuration for the scenario to run",
    )
    parser_scenario_create_lab.add_argument(
        "--scenario_profile",
        "-sp",
        required=False,
        dest="scenario_profile",
        help="Allows to define the scenario config to run",
    )

    # 'scenario_run_lab' command
    parser_scenario_run_lab = subparsers_scenario.add_parser(
        "run",
        help="Create and run a lab with a specific scenario",
        formatter_class=root_parser.formatter_class,
    )
    parser_scenario_run_lab.set_defaults(func=scenario_run_lab_handler)
    parser_scenario_run_lab.add_argument(
        "scenario_name", type=str, help="The scenario name"
    )
    parser_scenario_run_lab.add_argument(
        "--group_name",
        dest="group_name",
        help="The group ID that have ownership on lab",
    )
    parser_scenario_run_lab.add_argument(
        "--topology",
        action="store",
        required=False,
        dest="topology_file",
        help="Input path of a YAML topology file to override the default one",
    )
    parser_scenario_run_lab.add_argument(
        "--destroy",
        action="store_true",
        dest="destroy_after_scenario",
        help="Do not keep the lab up after scenario execution (False by default)",
    )
    parser_scenario_run_lab.add_argument(
        "--lab_config",
        "-lc",
        action="store",
        required=False,
        dest="lab_config_path",
        help="Input path of a YAML configuration for the scenario run",
    )
    parser_scenario_run_lab.add_argument(
        "--scenario_profile",
        "-sp",
        required=False,
        dest="scenario_profile",
        help="Allows to define the scenario config to run",
    )

    parser_scenario.set_defaults(func=lambda _: parser_scenario.print_help())
