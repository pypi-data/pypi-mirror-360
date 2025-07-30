# -*- coding: utf-8 -*-
import argparse
import getpass
import os
import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from pathlib import Path
from threading import Thread
from typing import Any
from typing import List
from urllib.parse import parse_qs
from urllib.parse import urlparse

import requests
from mantis_authz import jwt
from rich.console import Console
from rich.prompt import Prompt

import mantis_api_client.dataset_api as dataset_api
import mantis_api_client.oidc
import mantis_api_client.scenario_api as scenario_api
from mantis_api_client.config import mantis_api_client_config
from mantis_api_client.oidc import get_oidc_client
from mantis_api_client.utils import colored


class Version:
    def __init__(self, str_vers: str) -> None:
        try:
            self.major, self.minor, self.patch = str_vers.split(".")
        except Exception as e:
            raise Exception(
                "Bad version format for '{}': 'X.Y.Z' expected. Error: {}".format(
                    str_vers, e
                )
            )


#
# 'status' related functions
#
def status_handler(args: Any) -> None:  # noqa: C901
    """Get platform status."""

    exit_code = 0

    client_version = mantis_api_client.__version__
    client_vers = Version(str_vers=client_version)
    client_fullversion = mantis_api_client.__fullversion__
    print(
        f"[+] mantis_api_client version: {client_version} ({client_fullversion})".format(
            client_version
        )
    )

    active_profile_domain = get_oidc_client().get_active_profile_domain(raise_exc=False)
    if active_profile_domain:
        print(f"[+] Authenticated to {active_profile_domain}")
    else:
        print(
            colored(
                "[+] Not authenticated, you need to execute 'mantis account login'",
                "red",
            )
        )
        sys.exit(1)
    print("[+] APIs status")

    # Dataset API
    print("  [+] Dataset API")
    print("    [+] address: {}".format(mantis_api_client_config.dataset_api_url))
    try:
        dataset_api_version = dataset_api.get_version()
        dataset_vers = Version(str_vers=dataset_api_version)
    except requests.exceptions.ConnectionError:
        exit_code = 1
        print("    [-] API status: " + colored("not running !", "white", "on_red"))
    else:
        print("    [+] API status: " + colored("OK", "grey", "on_green"))
        print("    [+] version: {}".format(dataset_api_version))
        if dataset_vers.major != client_vers.major:
            exit_code = 1
            print(
                "    [-] "
                + colored(
                    "Error: Dataset API major version ({}) mismatchs with mantis_api_client major version ({})".format(
                        dataset_vers.major, client_vers.major
                    ),
                    "white",
                    "on_red",
                )
            )

    # Scenario API
    print("  [+] Scenario API")
    print("    [+] address: {}".format(mantis_api_client_config.scenario_api_url))
    try:
        scenario_api_version = scenario_api.get_version()
        scenario_vers = Version(str_vers=scenario_api_version)
    except requests.exceptions.ConnectionError:
        exit_code = 1
        print("    [-] API status: " + colored("not running !", "white", "on_red"))
    else:
        print("    [+] API status: " + colored("OK", "grey", "on_green"))
        print("    [+] version: {}".format(scenario_api_version))
        if scenario_vers.major != client_vers.major:
            exit_code = 1
            print(
                "    [-] "
                + colored(
                    "Error: Scenario API major version ({}) mismatchs with mantis_api_client major version ({})".format(
                        scenario_vers.major, client_vers.major
                    ),
                    "white",
                    "on_red",
                )
            )

    if exit_code != 0:
        sys.exit(exit_code)


#
# 'info' related functions
#
def info_handler(args: Any) -> None:  # noqa: C901
    """Get personal info."""

    active_profile_domain = get_oidc_client().get_active_profile_domain(raise_exc=False)
    if not active_profile_domain:
        print("[+] Not authenticated")
        return

    console = Console(highlight=False)
    rprint = console.print
    active_tokens = get_oidc_client().get_active_tokens()
    access_token = jwt.get_unverified_claims(active_tokens["access_token"])
    id_token = jwt.get_unverified_claims(active_tokens["id_token"])

    user_groups = id_token.get("groups")

    # Handle case where the user pertains to an organization
    if user_groups is not None:
        default_group = get_oidc_client().get_default_group()
        groups_comma_sep = ", ".join(user_groups)
        if default_group:
            # mark default group bold
            groups_comma_sep = groups_comma_sep.replace(
                default_group, f"[bold]{default_group}[/bold]"
            )

    sorted_scopes = ", ".join(sorted(access_token["scope"].split()))

    print(f"[+] Connected to {active_profile_domain}")
    print(f"  [+] Username: {id_token['preferred_username']}")
    print(f"  [+] Email: {id_token.get('email', 'N/A')}")
    if user_groups is not None:
        rprint(rf"  \[+] Group membership: {groups_comma_sep}")
    print(f"  [+] Scopes: {sorted_scopes}")


#
# 'login_handler' handler
#
def login_handler(args: Any) -> None:
    # Parameters
    oidc_domain = args.domain
    username = args.username
    if args.password_stdin:
        password = sys.stdin.read().rstrip()
    elif args.password_fd:
        with os.fdopen(args.password_fd) as f:
            password = f.read().rstrip()
    elif args.password_file:
        password = args.password_file.read_text().rstrip()
    elif args.username:
        password = getpass.getpass()
    else:
        password = None

    scope = " ".join(
        [
            "openid",
            "offline_access",
            "groups",
            "profile",
            "email",
            "dataset:read",
            "scenario:run",
        ]
    )
    redirect_uri = mantis_api_client_config.oidc.redirect_uri
    redirect_auto = redirect_uri.startswith("http")
    code_placeholder: List[str] = []
    if redirect_auto:
        thread = _init_create_callback_request_handler_thread(code_placeholder)
        thread.start()
    if username and password:
        token = get_oidc_client().token(
            oidc_domain, username, password, redirect_uri=redirect_uri, scope=scope
        )
    else:
        auth_url = get_oidc_client().auth_url(
            oidc_domain,
            redirect_uri=redirect_uri,
            scope=scope,
        )
        if shutil.which("xdg-open") is not None:
            subprocess.run(["xdg-open", auth_url])
            print(f"A web browser should have been opened for {oidc_domain!r}")
        else:
            print(
                f"Open this URL in a web browser in order to create an access token for M&NTIS:\n\n{auth_url}\n"
            )

        if redirect_auto:
            timeout = mantis_api_client_config.oidc.redirect_url_timeout
            print(f"Waiting callback for {timeout}s")
            thread.join(timeout)
            if thread.is_alive():
                print("Timeout exceeded, exiting")
                print("Access NOT granted")
                exit(1)
            code = code_placeholder[0]
        else:
            code = input("Paste the code displayed in the webpage: ")
        token = get_oidc_client().token(
            oidc_domain,
            grant_type="authorization_code",
            code=code,
            redirect_uri=redirect_uri,
        )
    print("Access granted")

    claims = jwt.get_unverified_claims(token["access_token"])
    selected_group = args.group
    claimed_groups = claims.get("groups")

    # Handle case where the user does not pertain to an organization
    if claimed_groups is None:
        selected_group = None
    else:
        # Handle case where the user pertains to only one organization
        if claimed_groups and len(claimed_groups) == 1 and selected_group is None:
            selected_group = claimed_groups[0]

        if selected_group not in claimed_groups:
            if selected_group:
                print(f"You are not member of group '{selected_group}'")
            selected_group = Prompt.ask(
                "Select a group to activate", choices=claimed_groups
            )
        print(f"Group `{selected_group}` activated")

    get_oidc_client().configure_profile(
        oidc_domain, token["refresh_token"], selected_group
    )


#
# 'logout_handler' handler
#
def logout_handler(args: Any) -> None:
    get_oidc_client().configure_profile(None)


def _init_create_callback_request_handler_thread(code_placeholder: list) -> Thread:
    class CallbackHTTPRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            query = urlparse(self.path).query
            if "error" in query:
                self.send_response(404)
            else:
                code = parse_qs(query)["code"][0]
                code_placeholder.append(code)
                self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                "<script>window.close()</script> Authorization {}. You may close this window.\r\n".format(
                    "failed" if "error" in query else "succeeded"
                ).encode()
            )

        def log_request(*args, **kwargs):
            # do nothing
            pass

    def serve_one_redirect_callback() -> None:
        with HTTPServer(
            (
                mantis_api_client_config.oidc.redirect_url.host,
                mantis_api_client_config.oidc.redirect_url.port,
            ),
            CallbackHTTPRequestHandler,
        ) as server:
            server.handle_request()

    return Thread(target=serve_one_redirect_callback, daemon=True)


def add_account_parser(root_parser: argparse.ArgumentParser, subparsers: Any) -> None:
    # -------------------
    # --- login options
    # -------------------

    parser_account = subparsers.add_parser(
        "account",
        help="Authentication actions for M&NTIS CLI.",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_account = parser_account.add_subparsers()

    # 'status' command
    parser_status = subparsers_account.add_parser(
        "status",
        help="Get platform status",
        formatter_class=root_parser.formatter_class,
    )
    parser_status.set_defaults(func=status_handler)

    # 'info' command
    parser_info = subparsers_account.add_parser(
        "info", help="Get personal info", formatter_class=root_parser.formatter_class
    )
    parser_info.set_defaults(func=info_handler)

    parser_login = subparsers_account.add_parser(
        "login",
        help="Log into a M&ntis account",
        formatter_class=root_parser.formatter_class,
    )
    parser_login.add_argument(
        "--domain",
        help="The M&ntis cluster SSO domain (default: %(default)s)",
        default="mantis-platform.io",
    )
    parser_login.add_argument(
        "--username",
        "-u",
        help="Your M&ntis cluster SSO username",
    )
    parser_login_mex_group = parser_login.add_mutually_exclusive_group()
    parser_login_mex_group.add_argument(
        "--password-stdin",
        action="store_true",
        help="Read your M&ntis cluster SSO password from stdin",
    )
    parser_login_mex_group.add_argument(
        "--password-fd",
        type=int,
        help="Read your M&ntis cluster SSO password from a descriptor",
    )
    parser_login_mex_group.add_argument(
        "--password-file",
        type=Path,
        help="Read your M&ntis cluster SSO password from a file",
    )
    parser_login.add_argument(
        "-g",
        "--group",
        help="Select the group name that will be used for contextual commands like `mantis scenario run`",
    )
    parser_login.set_defaults(func=login_handler)

    # -------------------
    # --- logout options
    # -------------------

    parser_logout = subparsers_account.add_parser(
        "logout",
        help="Log out from your M&ntis account",
        formatter_class=root_parser.formatter_class,
    )
    parser_logout.set_defaults(func=logout_handler)

    parser_account.set_defaults(func=lambda _: parser_account.print_help())
