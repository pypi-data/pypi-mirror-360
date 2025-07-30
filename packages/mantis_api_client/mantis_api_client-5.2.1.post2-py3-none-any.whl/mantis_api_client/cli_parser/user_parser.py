# -*- coding: utf-8 -*-
import argparse
import json
import sys
from typing import Any

from pydantic.json import pydantic_encoder

from mantis_api_client import user_api
from mantis_api_client.oidc import get_oidc_client
from mantis_api_client.utils import colored


# #
# # 'user_list_handler' handler
# #
# def user_list_handler(args: Any) -> None:
#     try:
#         users = user_api.fetch_users()
#     except Exception as e:
#         print(colored(f"Error when fetching users: '{e}'", "red"))
#         sys.exit(1)

#     if args.json:
#         print(json.dumps(users, default=pydantic_encoder))
#         return

#     print("[+] Organization users:")
#     for user in users["data"]:
#         print(f"  [+] {user['id']}: {user['given_name']} {user['last_name']}")


#
# 'user_self_handler' handler
#
def user_self_handler(args: Any) -> None:
    try:
        user = user_api.fetch_current_user()
    except Exception as e:
        print(colored(f"Error when fetching current user information: '{e}'", "red"))
        sys.exit(1)

    if args.json:
        print(json.dumps(user, default=pydantic_encoder))
        return

    print("[+] Current user information:")
    print(f"  [+] ID: {user['id']}")
    print(f"  [+] Name: {user['given_name']} {user['last_name']}")
    print(f"  [+] Email: {user['email']}")
    print(f"  [+] Creation date: {user['creation_date']}")


#
# 'user_info_handler' handler
#
def user_info_handler(args: Any) -> None:
    # Parameters
    user_id = args.user_id

    try:
        user = user_api.fetch_user(user_id)
    except Exception as e:
        print(
            colored(
                f"Error when fetching information for user '{user_id}': '{e}'",
                "red",
                "on_white",
            )
        )
        sys.exit(1)

    if args.json:
        print(json.dumps(user, default=pydantic_encoder))
        return

    print("[+] User information:")
    print(f"  [+] ID: {user['id']}")
    print(f"  [+] Name: {user['given_name']} {user['last_name']}")
    print(f"  [+] Email: {user['email']}")
    print(f"  [+] Creation date: {user['creation_date']}")


#
# 'organization_info_handler' handler
#
def organization_info_handler(args: Any) -> None:
    try:
        # Retrieve current organization name
        organization_name = get_oidc_client().get_default_group(raise_exc=True)

        # Retrieve associated organization id
        if organization_name is None:
            print("Current user not linked to an organization")
            sys.exit(0)

        organization_id = user_api.get_organization_id_from_group_name(
            organization_name
        )

        # Retrieve organization info
        organization_info = user_api.fetch_organization(organization_id)

        # Retrieve plan info
        plan_info = user_api.get_plan(organization_info["plan_id"])

        # Retrieve plan limits
        plan_limits = user_api.get_plan_limits(organization_info["plan_id"])

        # Retrieve credits list
        credits_list = user_api.get_credits_list(organization_id)

        # Retrieve consumption history
        consumption_history = user_api.get_consumption_history(organization_id)
    except Exception as e:
        print(
            colored(
                f"Error when fetching information for organization '{organization_name}': '{e}'",
                "red",
                "on_white",
            )
        )
        sys.exit(1)

    if args.json:
        print(json.dumps(organization_info, default=pydantic_encoder))
        print(json.dumps(plan_info, default=pydantic_encoder))
        print(json.dumps(plan_limits, default=pydantic_encoder))
        print(json.dumps(credits_list, default=pydantic_encoder))
        print(json.dumps(consumption_history, default=pydantic_encoder))
        return

    print("[+] Organization information:")
    print(f"  [+] ID: {organization_info['id']}")
    print(f"  [+] Name: {organization_info['name']}")
    print(f"  [+] Subscription start: {organization_info['subscription_start']}")
    print(f"  [+] Subscription end: {organization_info['subscription_end']}")

    print("[+] Plan information:")
    print(f"  [+] ID: {plan_info['id']}")
    print(f"  [+] Name: {plan_info['name']}")
    print(f"  [+] Frequency: {plan_info['frequency']}")

    print("[+] Plan limits:")
    print(f"  [+] Max active labs: {plan_limits['nb_active_labs']}")
    print(f"  [+] Max accounts: {plan_limits['nb_accounts']}")
    print(f"  [+] Max workspaces: {plan_limits['nb_workspaces']}")
    print(f"  [+] Max lab duration: {plan_limits['lab_max_duration']}")

    print("[+] Credits:")
    if "data" in credits_list:
        for credit in credits_list["data"]:
            print(f"  [+] ID: {credit['id']}")
            print(f"    [+] Purpose: {credit['purpose']}")
            print(
                f"    [+] Period: {credit['creation_date']} to {credit['expiration_date']}"
            )
            print(f"    [+] Credit: {credit['remaining']}/{credit['total']}")
    else:
        print("  [+] No credits")


def add_user_parser(
    root_parser: argparse.ArgumentParser,
    subparsers: Any,
) -> None:
    # --------------------
    # --- User API options (users)
    # --------------------

    parser_user = subparsers.add_parser(
        "user",
        help="User API related commands",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_user = parser_user.add_subparsers()

    # # 'user_list' command
    # parser_user_list = subparsers_user.add_parser(
    #     "list",
    #     help="List all organization users",
    #     formatter_class=root_parser.formatter_class,
    # )
    # parser_user_list.set_defaults(func=user_list_handler)
    # parser_user_list.add_argument(
    #     "--json", help="Return JSON result.", action="store_true"
    # )

    # 'user_self' command
    parser_user_self = subparsers_user.add_parser(
        "self",
        help="Retrieve information for current user",
        formatter_class=root_parser.formatter_class,
    )
    parser_user_self.set_defaults(func=user_self_handler)
    parser_user_self.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'user_info' command
    parser_user_info = subparsers_user.add_parser(
        "info",
        help="Retrieve information about a specific user",
        formatter_class=root_parser.formatter_class,
    )
    parser_user_info.set_defaults(func=user_info_handler)
    parser_user_info.add_argument("user_id", type=str, help="The user ID")
    parser_user_info.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'orga_info' command
    parser_user_info = subparsers_user.add_parser(
        "organization",
        help="Retrieve information about current organization",
        formatter_class=root_parser.formatter_class,
    )
    parser_user_info.set_defaults(func=organization_info_handler)
    parser_user_info.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    parser_user.set_defaults(func=lambda _: parser_user.print_help())
