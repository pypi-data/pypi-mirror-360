# -*- coding: utf-8 -*-
import argparse
import datetime
import json
import os
import pprint
import sys
from typing import Any

from mantis_scenario_model.lab_model import Lab

import mantis_api_client.scenario_api as scenario_api
from cr_api_client.cli_parser.provisioning_parser import add_provisioning_parser
from mantis_api_client.cli_parser.redteam_parser import add_redteam_parser
from mantis_api_client.oidc import get_oidc_client


#
# 'lab_info_handler' handler
#
def lab_info_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        ret = scenario_api.fetch_lab(lab_id)
        lab: Lab = Lab(**ret)
    except Exception as e:
        print(f"Error when fetching lab: '{e}'")
        sys.exit(1)

    if args.json:
        print(lab.json())
        return

    print("[+] Lab information:")
    print(f"""  [+] \033[1mId\033[0m: {lab.runner_id}""")
    print(f"""  [+] \033[1mName\033[0m: {lab.name}""")
    print(f"""  [+] \033[1mType\033[0m: {lab.content_type}""")
    print(f"""  [+] \033[1mStatus\033[0m: {lab.status}""")
    print(f"""  [+] \033[1mCreated by\033[0m: {lab.created_by}""")

    print("""  [+] \033[1mTimestamps:""")

    lab_creation_timestamp = (
        datetime.datetime.fromtimestamp(
            lab.lab_creation_timestamp, datetime.timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S")
        + " UTC"
    )

    if lab.lab_start_timestamp is not None:
        lab_start_timestamp = (
            datetime.datetime.fromtimestamp(
                lab.lab_start_timestamp, datetime.timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S")
            + " UTC"
        )
    else:
        lab_start_timestamp = str(lab.lab_start_timestamp)

    if lab.lab_content_end_timestamp is not None:
        lab_content_end_timestamp = (
            datetime.datetime.fromtimestamp(
                lab.lab_content_end_timestamp, datetime.timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S")
            + " UTC"
        )
    else:
        lab_content_end_timestamp = str(lab.lab_content_end_timestamp)

    if lab.lab_end_timestamp is not None:
        lab_end_timestamp = (
            datetime.datetime.fromtimestamp(
                lab.lab_end_timestamp, datetime.timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S")
            + " UTC"
        )
    else:
        lab_end_timestamp = str(lab.lab_end_timestamp)

    print(f"""    [+] \033[1mCreation time\033[0m:    {lab_creation_timestamp}""")
    print(f"""    [+] \033[1mStart time\033[0m:       {lab_start_timestamp}""")
    print(f"""    [+] \033[1mContent end time\033[0m: {lab_content_end_timestamp}""")
    print(f"""    [+] \033[1mLab end time\033[0m:     {lab_end_timestamp}""")


#
# 'lab_api_handler' handler
#
def lab_api_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    active_profile_domain = get_oidc_client().get_active_profile_domain(raise_exc=False)
    if not active_profile_domain:
        print("[+] Not authenticated")
        return

    it_simulation_api_url = (
        f"https://app.{active_profile_domain}/proxy/{lab_id}/api/it_simulation"
    )
    provisioning_api_url = (
        f"https://app.{active_profile_domain}/proxy/{lab_id}/api/provisioning"
    )
    user_activity_api_url = (
        f"https://app.{active_profile_domain}/proxy/{lab_id}/api/user_activity"
    )
    redteam_api_url = f"https://app.{active_profile_domain}/proxy/{lab_id}/api/redteam"

    if args.json:
        print(
            json.dumps(
                {
                    "it_simulation_api_url": it_simulation_api_url,
                    "provisioning_api_url": provisioning_api_url,
                    "user_activity_api_url": user_activity_api_url,
                    "redteam_api_url": redteam_api_url,
                }
            )
        )
        return

    print("[+] Lab APIs:")
    print(f"""  [+] \033[1mIT simulation API URL\033[0m: {it_simulation_api_url}""")
    print(f"""  [+] \033[1mProvisioning API URL\033[0m:  {provisioning_api_url}""")
    print(f"""  [+] \033[1mUser activity API URL\033[0m: {user_activity_api_url}""")
    print(f"""  [+] \033[1mRedteam API URL\033[0m:       {redteam_api_url}""")


#
# 'lab_run_handler' handler
#
def lab_run_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        scenario_api.run_lab(lab_id)
    except Exception as e:
        print(f"Error when running lab: '{e}'")
        sys.exit(1)

    print(f"[+] Lab '{lab_id}' is running")


#
# 'lab_stop_handler' handler
#
def lab_stop_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        scenario_api.stop_lab(lab_id)
    except Exception as e:
        print(f"Error when stopping lab: '{e}'")
        sys.exit(1)

    print(f"[+] Lab '{lab_id}' stopped")


#
# 'lab_delete_lab_handler' handler
#
def lab_delete_lab_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        scenario_api.delete_lab(lab_id)
    except Exception as e:
        print(f"Error when deleting lab ID {lab_id}: '{e}'")
        sys.exit(1)

    print(f"[+] Lab '{lab_id}' deleted")


#
# 'lab_resume_handler' handler
#
def lab_resume_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        scenario_api.resume_lab(lab_id)
    except Exception as e:
        print(f"Error when resume lab: '{e}'")
        sys.exit(1)

    print(f"[+] Lab '{lab_id}' resumed")


#
# 'lab_paused_status' handler
#
def lab_paused_status_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        paused_status = scenario_api.fetch_lab_paused_status(lab_id)
    except Exception as e:
        print(f"Error when fetching lab paused status: '{e}'")
        sys.exit(1)

    if args.json:
        print(paused_status.json())
        return

    if paused_status.is_before_step is None:
        position = None
    elif paused_status.is_before_step is True:
        position = "before"
    else:
        position = "after"

    print(f"[+] Lab '{lab_id}' paused status:")
    print(f"  [+] Step: {paused_status.step}")
    print(f"  [+] Paused: {position}")


#
# 'lab_topology_handler' handler
#
def lab_topology_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        topology = scenario_api.fetch_lab_topology(lab_id)
    except Exception as e:
        print(f"Error when fetching scenario topology: '{e}'")
        sys.exit(1)

    if args.json:
        print(topology.json())
        return

    print("[+] Lab topology")
    print("  [+] Nodes")
    for node in topology.nodes:
        print(f"    [+] {node.name} ({node.type})")
    print("  [+] Links")
    for node in topology.nodes:
        if node.type == "switch":
            print(f"    [+] {node.name}")
            for link in topology.links:
                if link.switch.name == node.name:
                    print(f"      [+] {link.node.name} - {link.params.ip}")


#
# 'lab_nodes_handler' handler
#
def lab_nodes_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        nodes = scenario_api.fetch_lab_nodes(lab_id)
    except Exception as e:
        print(f"Error when fetching scenario nodes: '{e}'")
        sys.exit(1)

    if args.json:
        print(json.dumps(nodes))
        return

    print("[+] Lab nodes")
    for node in nodes:
        if node["type"] == "switch":
            continue
        print(f"  [+] {node['name']} ({node['type']})")
        print("    [+] network interfaces")

        for ni in node["network_interfaces"]:
            if ni["ip_address_runtime"] is not None:
                ip_address = ni["ip_address_runtime"]
            else:
                ip_address = ni["ip_address"]
            print(f"      - {ip_address}")

        if node["type"] == "virtual_machine":
            print("    [+] Credentials")
            print(
                f"      - username: {node['username']} - password: {node['password']}"
            )
            print(
                f"      - admin_username: {node['admin_username']} - admin_password: {node['admin_password']}"
            )


#
# 'lab_assets_handler' handler
#
def lab_assets_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        assets = scenario_api.fetch_lab_assets(lab_id)
    except Exception as e:
        print(f"Error when fetching scenario assets: '{e}'")
        sys.exit(1)

    if args.json:
        print(json.dumps(assets))
        return

    print("[+] Lab assets")
    for asset in assets:
        print(f"  [+] {asset['name']} ({asset['type']})")
        print(f"    [+] roles: {asset['roles']}")
        if asset["type"] == "virtual_machine":
            print(f"    [+] os: {asset['os']} ({asset['os_family']})")
            print("    [+] network interfaces")
            for ni in asset["network_interfaces"]:
                print(f"      - {ni['ipv4']}")
            print("    [+] CPE IDs:")
            for cpe in asset["cpes"]:
                print(f"      - {cpe}")


#
# 'lab_attack_report_handler' handler
#
def lab_attack_report_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        attack_report = scenario_api.fetch_lab_attack_report(lab_id)
    except Exception as e:
        print(f"Error when fetching scenario attack_report: '{e}'")
        sys.exit(1)

    if args.json:
        print(json.dumps(attack_report))
        return

    print("[+] Lab attack report:")
    pp = pprint.PrettyPrinter(width=160)
    pp.pprint(attack_report)


#
# 'lab_attack_infras_handler' handler
#
def lab_attack_infras_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        attack_infras = scenario_api.fetch_lab_attack_infras(lab_id)
    except Exception as e:
        print(f"Error when fetching scenario attack_infras: '{e}'")
        sys.exit(1)

    if args.json:
        print(json.dumps(attack_infras))
        return

    print("[+] Lab attack infrastructures:")
    for infra in attack_infras:
        print(f"  [+] {infra}")


#
# 'lab_attack_sessions_handler' handler
#
def lab_attack_sessions_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        attack_sessions = scenario_api.fetch_lab_attack_sessions(lab_id)
    except Exception as e:
        print(f"Error when fetching scenario attack_sessions: '{e}'")
        sys.exit(1)

    if args.json:
        print(json.dumps(attack_sessions))
        return

    knowledge = scenario_api.fetch_lab_attack_knowledge(lab_id)

    print("[+] Lab attack sessions:")
    for session in attack_sessions:
        compromised_host_ip = None
        if "hosts" in knowledge:
            for host in knowledge["hosts"]:
                for nic in host:
                    if nic is not None:
                        if "ip" in nic and "idHost" in nic:
                            if nic["idHost"] == session["idHost"]:
                                compromised_host_ip = nic["ip"]
        print(
            f"  [+] {session['idAttackSession']} - compromised host: {compromised_host_ip} - type: {session['type']} - direct_access: {session['direct_access']} - privilege_level: {session['privilege_level']} - uuid: {session['identifier']}"
        )


#
# 'lab_attack_knowledge_handler' handler
#
def lab_attack_knowledge_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        attack_knowledge = scenario_api.fetch_lab_attack_knowledge(lab_id)
    except Exception as e:
        print(f"Error when fetching scenario attack_knowledge: '{e}'")
        sys.exit(1)

    if args.json:
        print(json.dumps(attack_knowledge))
        return

    print("[+] Lab attack knowledge:")
    pp = pprint.PrettyPrinter(compact=True, width=160)
    pp.pprint(attack_knowledge)


#
# 'lab_notifications_handler' handler
#
def lab_notifications_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        notifications = scenario_api.fetch_lab_notifications(lab_id)
    except Exception as e:
        print(f"Error when fetching scenario notifications: '{e}'")
        sys.exit(1)

    if args.json:
        print(json.dumps(notifications))
        return

    print("[+] Lab notifications")
    for notification in notifications:
        event = json.loads(notification)
        print(f"⚡ {event['event_datetime']} - {event['event_data']}")


#
# 'lab_config_handler' handler
#
def lab_config_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        lab_config = scenario_api.fetch_lab_config(lab_id)
    except Exception as e:
        print(f"Error when fetching lab config: '{e}'")
        sys.exit(1)

    if args.json:
        print(lab_config.json())
        return

    print("[+] Lab lab_config:")
    pp = pprint.PrettyPrinter(width=160)
    pp.pprint(lab_config.dict())


def lab_set_lab_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    active_profile_domain = get_oidc_client().get_active_profile_domain(raise_exc=False)
    if not active_profile_domain:
        print("[+] Not authenticated")
        return

    os.environ["CORE_API_URL"] = (
        f"https://app.{active_profile_domain}/proxy/{lab_id}/api/it_simulation"
    )
    os.environ["PROVISIONING_API_URL"] = (
        f"https://app.{active_profile_domain}/proxy/{lab_id}/api/provisioning"
    )
    os.environ["USER_ACTIVITY_API_URL"] = (
        f"https://app.{active_profile_domain}/proxy/{lab_id}/api/user_activity"
    )
    os.environ["REDTEAM_API_URL"] = (
        f"https://app.{active_profile_domain}/proxy/{lab_id}/api/redteam"
    )


def lab_unset_lab_handler(args: Any) -> None:
    del os.environ["CORE_API_URL"]
    del os.environ["PROVISIONING_API_URL"]
    del os.environ["USER_ACTIVITY_API_URL"]
    del os.environ["REDTEAM_API_URL"]


#
# 'lab_get_remote_access_handler' handler
#
def lab_get_remote_access_handler(args: Any) -> None:
    # Parameters
    lab_id = args.lab_id

    try:
        remote_access = scenario_api.fetch_lab_remote_access(lab_id)
    except Exception as e:
        print(f"Error when fetching lab config: '{e}'")
        sys.exit(1)

    if args.json:
        print(remote_access.json())
        return

    print("[+] Lab remote access information:")
    print(f"[+] \033[1mLab ID\033[0m: {lab_id}")
    for node in remote_access.nodes:
        print(f"  [+] \033[1mNode name\033[0m: {node.name}")
        print(f"    [+] \033[1mHTTP URL\033[0m: {node.http_url}")

        if len(node.credentials) > 0:
            print("    [+] \033[1mCredentials\033[0m:")
        for credential in node.credentials:
            print("      ----")
            print(f"      [+] \033[1mLogin\033[0m: {credential.login}")
            print(f"      [+] \033[1mPassword\033[0m: {credential.password}")
            print(f"      [+] \033[1mPrivilege\033[0m: {credential.privilege}")


def add_lab_parser(root_parser: argparse.ArgumentParser, subparsers: Any) -> None:
    # Subparser lab
    parser_lab = subparsers.add_parser(
        "lab",
        help="Scenario API related commands (lab)",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab.set_defaults(set_lab=lab_set_lab_handler)
    parser_lab.set_defaults(unset_lab=lab_unset_lab_handler)
    parser_lab.add_argument("lab_id", type=str, help="The lab id")
    subparsers_lab = parser_lab.add_subparsers()

    # 'lab_info' command
    parser_lab_info = subparsers_lab.add_parser(
        "info",
        help="Get information about a lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_info.set_defaults(func=lab_info_handler)
    parser_lab_info.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_api' command
    parser_lab_api = subparsers_lab.add_parser(
        "api",
        help="Get API URLs to directly access the lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_api.set_defaults(func=lab_api_handler)
    parser_lab_api.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_run' command
    parser_lab_run = subparsers_lab.add_parser(
        "run", help="Run a specific lab", formatter_class=root_parser.formatter_class
    )
    parser_lab_run.set_defaults(func=lab_run_handler)

    # 'lab_stop' command
    parser_lab_stop = subparsers_lab.add_parser(
        "stop", help="Stop a specific lab", formatter_class=root_parser.formatter_class
    )
    parser_lab_stop.set_defaults(func=lab_stop_handler)

    # 'lab_delete_lab' command
    parser_lab_delete_lab = subparsers_lab.add_parser(
        "delete",
        help="Delete lab from its lab id",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_delete_lab.set_defaults(func=lab_delete_lab_handler)

    # 'lab_resume' command
    parser_lab_resume = subparsers_lab.add_parser(
        "resume",
        help="Resume a specific lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_resume.set_defaults(func=lab_resume_handler)

    # 'lab_paused_status' command
    parser_lab_paused_status = subparsers_lab.add_parser(
        "paused-status",
        help="Show current lab paused status",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_paused_status.set_defaults(func=lab_paused_status_handler)
    parser_lab_paused_status.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_topology' command
    parser_lab_topology = subparsers_lab.add_parser(
        "topology",
        help="Get scenario topology on current lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_topology.set_defaults(func=lab_topology_handler)
    parser_lab_topology.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_nodes' command
    parser_lab_nodes = subparsers_lab.add_parser(
        "nodes",
        help="Get scenario nodes on current lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_nodes.set_defaults(func=lab_nodes_handler)
    parser_lab_nodes.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_assets' command
    parser_lab_assets = subparsers_lab.add_parser(
        "assets",
        help="Get scenario assets on current lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_assets.set_defaults(func=lab_assets_handler)
    parser_lab_assets.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_attack_report' command
    parser_lab_attack_report = subparsers_lab.add_parser(
        "attack-report",
        help="Get scenario attack report on current lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_attack_report.set_defaults(func=lab_attack_report_handler)
    parser_lab_attack_report.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_attack_infras' command
    parser_lab_attack_infras = subparsers_lab.add_parser(
        "attack-infras",
        help="Get scenario attack infras on current lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_attack_infras.set_defaults(func=lab_attack_infras_handler)
    parser_lab_attack_infras.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_attack_sessions' command
    parser_lab_attack_sessions = subparsers_lab.add_parser(
        "attack-sessions",
        help="Get scenario attack sessions on current lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_attack_sessions.set_defaults(func=lab_attack_sessions_handler)
    parser_lab_attack_sessions.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_attack_knowledge' command
    parser_lab_attack_knowledge = subparsers_lab.add_parser(
        "attack-knowledge",
        help="Get scenario attack knowledge on current lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_attack_knowledge.set_defaults(func=lab_attack_knowledge_handler)
    parser_lab_attack_knowledge.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_notifications' command
    parser_lab_notifications = subparsers_lab.add_parser(
        "notifications",
        help="Get scenario notifications on current lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_notifications.set_defaults(func=lab_notifications_handler)
    parser_lab_notifications.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_config' command
    parser_lab_config = subparsers_lab.add_parser(
        "lab-config",
        help="Get lab config on current lab",
        formatter_class=root_parser.formatter_class,
    )
    parser_lab_config.set_defaults(func=lab_config_handler)
    parser_lab_config.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'lab_get_remote_access' command
    parser_lab_get_remote_access = subparsers_lab.add_parser(
        "remote-access",
        help="Get info for remote access to lab VMs",
    )
    parser_lab_get_remote_access.set_defaults(func=lab_get_remote_access_handler)
    parser_lab_get_remote_access.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    parser_lab.set_defaults(func=lambda _: parser_lab.print_help())

    # -------------------
    # --- Redteam actions on labs
    # -------------------

    add_redteam_parser(root_parser=root_parser, subparsers=subparsers_lab)

    # -------------------
    # --- Provisioning actions on labs
    # -------------------

    add_provisioning_parser(root_parser=root_parser, subparsers=subparsers_lab)
