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
# 'basebox_list_handler' handler
def basebox_list_handler(args: Any) -> None:
    try:
        baseboxes = sorted(scenario_api.fetch_baseboxes(), key=lambda x: x.id)
    except Exception as e:
        print(colored(f"Error when fetching baseboxes: '{e}'", "red"))
        sys.exit(1)

    if args.json:
        print(json.dumps(baseboxes, default=pydantic_encoder))
        return

    print("[+] Available baseboxes:")
    for basebox in baseboxes:
        print(f"  [+] {basebox.id}")


#
# 'basebox_info_handler' handler
#
def basebox_info_handler(args: Any) -> None:
    # Parameters
    basebox_id = args.basebox_id

    try:
        basebox = scenario_api.fetch_basebox_by_id(basebox_id)
    except Exception as e:
        print(colored(f"Error when fetching basebox {basebox_id}: '{e}'", "red"))
        sys.exit(1)

    if args.json:
        print(basebox.json())
        return

    print("[+] Basebox information:")
    print(f"  [+] \033[1mId\033[0m: {basebox.id}")
    print(f"  [+] \033[1mDescription\033[0m: {basebox.description}")
    print(f"  [+] \033[1mOS\033[0m: {basebox.operating_system} ({basebox.system_type})")
    print(f"  [+] \033[1mLanguage\033[0m: {basebox.language}")
    print(f"  [+] \033[1mInstallation date\033[0m: {basebox.installation_date}")
    print("  [+] \033[1mCredentials\033[0m:")
    if basebox.username != "" and basebox.username:
        print(f"       [+] User: {basebox.username}:{basebox.password}")
    if basebox.admin_username != "" and basebox.admin_username:
        print(
            f"       [+] Administrator: {basebox.admin_username}:{basebox.admin_password}"
        )
    print("  [+] \033[1mCPE\033[0m:")
    for cpe in basebox.cpes:
        print(f"        [+] {cpe}")
    if basebox.changelog:
        print("  [+] \033[1mChangelog\033[0m:")
        for changelog in basebox.changelog:
            if changelog.get("date", "") != "":
                print(f"""        [+] {changelog.get("date")}:""")
                for info in changelog.get("info", "").splitlines():
                    print(f"""              {info}""")


def _basebox_create_or_run_lab(args: Any, do_run: bool = True):
    # Parameters
    basebox_id = args.basebox_id
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

    # Launch basebox
    try:
        print(f"[+] Going to execute basebox: {basebox_id}")

        if do_run:
            lab_id = scenario_api.run_lab_basebox(
                basebox_id, lab_config, group_name, group_id
            )
        else:
            lab_id = scenario_api.create_lab_basebox(
                basebox_id, lab_config, group_name, group_id
            )

        print(f"[+] Basebox lab ID: {lab_id}")

        if do_run:
            wait_lab(lab_id)
            print("[+] Basebox lab started")

    except Exception as e:
        print(colored(f"Error when running basebox {basebox_id}: '{e}'", "red"))
        sys.exit(1)
    finally:
        if do_run and args.destroy_after_scenario:
            print("[+] Stopping lab...")
            scenario_api.stop_lab(lab_id)


#
# 'basebox_create_lab_handler' handler
#
def basebox_create_lab_handler(args: Any) -> None:
    _basebox_create_or_run_lab(args, do_run=False)


#
# 'basebox_run_lab_handler' handler
#
def basebox_run_lab_handler(args: Any) -> None:
    _basebox_create_or_run_lab(args, do_run=True)


def add_basebox_parser(
    root_parser: argparse.ArgumentParser,
    subparsers: Any,
) -> None:
    # -------------------
    # --- Scenario API options (baseboxes)
    # -------------------

    parser_basebox = subparsers.add_parser(
        "basebox",
        help="Scenario API related commands (basebox)",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_basebox = parser_basebox.add_subparsers()

    # 'basebox_list' command
    parser_basebox_list = subparsers_basebox.add_parser(
        "list",
        help="List all available baseboxes",
        formatter_class=root_parser.formatter_class,
    )
    parser_basebox_list.set_defaults(func=basebox_list_handler)
    parser_basebox_list.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'basebox_info' command
    parser_basebox_info = subparsers_basebox.add_parser(
        "info",
        help="Get information about a basebox",
        formatter_class=root_parser.formatter_class,
    )
    parser_basebox_info.set_defaults(func=basebox_info_handler)
    parser_basebox_info.add_argument("basebox_id", type=str, help="The basebox ID")
    parser_basebox_info.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'basebox_create_lab' command
    parser_basebox_create_lab = subparsers_basebox.add_parser(
        "create",
        help="Create a lab with a specific basebox",
        formatter_class=root_parser.formatter_class,
    )
    parser_basebox_create_lab.set_defaults(func=basebox_create_lab_handler)
    parser_basebox_create_lab.add_argument(
        "basebox_id", type=str, help="The basebox ID"
    )
    parser_basebox_create_lab.add_argument(
        "--destroy",
        action="store_true",
        dest="destroy_after_scenario",
        help="Do not keep the lab up after basebox execution (False by default)",
    )
    parser_basebox_create_lab.add_argument(
        "--group_name",
        dest="group_name",
        help="The group ID that have ownership on lab",
    )
    parser_basebox_create_lab.add_argument(
        "--lab_config",
        action="store",
        required=False,
        dest="lab_config_path",
        help="Input path of a YAML configuration for the scenario to run",
    )

    # 'basebox_run_lab' command
    parser_basebox_run_lab = subparsers_basebox.add_parser(
        "run",
        help="Create and run a lab with a specific basebox",
        formatter_class=root_parser.formatter_class,
    )
    parser_basebox_run_lab.set_defaults(func=basebox_run_lab_handler)
    parser_basebox_run_lab.add_argument("basebox_id", type=str, help="The basebox ID")
    parser_basebox_run_lab.add_argument(
        "--destroy",
        action="store_true",
        dest="destroy_after_scenario",
        help="Do not keep the lab up after basebox execution (False by default)",
    )
    parser_basebox_run_lab.add_argument(
        "--group_name",
        dest="group_name",
        help="The group ID that have ownership on lab",
    )
    parser_basebox_run_lab.add_argument(
        "--lab_config",
        "-lc",
        action="store",
        required=False,
        dest="lab_config_path",
        help="Input path of a YAML configuration for the scenario run",
    )

    parser_basebox.set_defaults(func=lambda _: parser_basebox.print_help())
