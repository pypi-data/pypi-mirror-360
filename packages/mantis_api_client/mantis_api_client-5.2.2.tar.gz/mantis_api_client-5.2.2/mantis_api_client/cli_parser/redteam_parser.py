# -*- coding: utf-8 -*-
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from colorama import Fore
from colorama import Style

from cr_api_client import redteam_api  # type: ignore[attr-defined]


def select_attack_session() -> Dict:

    attack_sessions = redteam_api.attack_sessions()
    print("Choose one attack session in list:")

    list_sessions(attack_sessions)

    id_session = input("Select attack session index: ")
    try:
        attack_session = attack_sessions[int(id_session)]
    except Exception as e:
        print(f"Error when fetching command: '{e}'")
        sys.exit(1)

    return attack_session


def list_sessions(attack_sessions: List[Dict]) -> None:
    i = 0
    for a_s in attack_sessions:

        # Check attack session link
        if a_s.get("is_up", False):
            connected = "UP"
        else:
            connected = "DOWN"

        if a_s["privilege_level"] == 0:
            privilege = "user"
        elif a_s["privilege_level"] == 1:
            privilege = "user UAC"
        else:
            privilege = "administrator"
        print(
            f""" [{connected}] {i} : {a_s["identifier"]}, {a_s["username"]} (privilege {privilege}) on {a_s["target"]["host"]["hostname"]} ({a_s["target"]["ip"]})"""
        )
        i = i + 1


def redteam_session_list_handler(args: Any) -> None:
    sessions = redteam_api.attack_sessions()
    list_sessions(sessions)


def redteam_command_history_handler(args: Any) -> None:

    commands = redteam_api.get_commands()

    for command in commands:
        print(f"""[+] {command["idResultCommand"]} : {command["command"]}""")


def redteam_command_get_handler(args: Any) -> None:

    command_id = args.command_id

    try:
        command = redteam_api.get_command(command_id=command_id)
    except Exception as e:
        print(f"Error when fetching command: '{e}'")
        sys.exit(1)

    print(json.dumps(command))


def redteam_command_execute_handler(args: Any) -> None:

    if args.identifier is None:
        attack_session = select_attack_session()
    else:
        attack_session = {}
        attack_session["identifier"] = args.identifier

    if args.command is None:
        command = input("Command to execute (one line): ")
    else:
        command = args.command

    if args.background is None:
        background_input = (
            input("Command need to be executed in background, y or n ? (n by default) ")
            or "n"
        )
        if background_input not in ["y", "n"]:
            print("You need to answer y or n.")
            sys.exit(1)

        if "y" in background_input:
            background = True
        else:
            background = False
    else:
        if args.background.lower() == "true":
            background = True
        elif args.background.lower() == "false":
            background = False
        else:
            print("Background argument is boolean (true or false)")
            sys.exit(1)

    if args.timeout is None:
        max_time = (
            input("Max waiting time for command result in seconds ? (60 by default) ")
            or 60
        )
        try:
            max_time = int(max_time)
        except ValueError:
            print("Error max waiting time is not an integer.")
            sys.exit(1)
    else:
        try:
            max_time = int(args.timeout)
        except ValueError:
            print("Timeout argument must be an integer.")
            sys.exit(1)

    manage_command(
        command=command,
        attack_session_identifier=attack_session["identifier"],
        background=background,
        max_time=max_time,
    )


def redteam_shell_handler(args: Any) -> None:

    print(f"{Style.BRIGHT}M{Fore.RED}&{Fore.RESET}NTIS SHELL{Style.NORMAL}")

    attack_session = select_attack_session()

    max_time = (
        input("Max waiting time for command result in secondes ? (60 by default)") or 60
    )
    try:
        max_time = int(max_time)
    except ValueError:
        print("Error max waiting time is not an integer.")
        sys.exit(1)

    stop = False

    while not stop:
        command = input("> ")
        if command == "exit":
            stop = True
            break
        manage_command(
            command=command,
            attack_session_identifier=attack_session["identifier"],
            background=False,
            max_time=max_time,
        )


def manage_command(
    command: str, attack_session_identifier: str, background: bool, max_time: int
) -> None:
    result, output = redteam_api.execute_command(
        command, attack_session_identifier, background=background
    )

    id_command = output["idResultCommand"]

    output = None
    i = 0

    while i < max_time:
        result = redteam_api.get_command(id_command)
        if result.get("output", "") != "":
            output = result["output"]
            break
        time.sleep(1)
        i = i + 1

    if not output:
        print(f"""Command timeout (more than {max_time} seconds)""")
    print(output)


def redteam_upload_handler(args: Any) -> None:

    attack_session = select_attack_session()

    path = input("Local path for the file : ")
    filename = Path(path).name

    success = redteam_api.upload_file(
        filepath=path, attack_session_identifier=attack_session["identifier"]
    )

    if success:
        if attack_session["type"] == "powershell":
            upload_path = f"""C:\\Users\\{attack_session["username"]}\\AppData\\Local\\Temp\\{filename}"""
        else:
            upload_path = f"""/tmp/{filename}"""

        print(f"File upload successfully on {upload_path}")
    else:
        print("Upload failed.")


def add_redteam_parser(root_parser: argparse.ArgumentParser, subparsers: Any) -> None:
    # Subparser redteam
    parser_redteam = subparsers.add_parser(
        "redteam",
        help="Redteam actions in running labs",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_redteam = parser_redteam.add_subparsers()
    parser_redteam.set_defaults(func=lambda _: parser_redteam.print_help())

    # Redteam session parser
    parser_redteam_session = subparsers_redteam.add_parser(
        name="session",
        help="Redteam session information",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_session = parser_redteam_session.add_subparsers()
    parser_redteam_session_list = subparsers_session.add_parser(
        "list",
        help="List all redteam sessions.",
        formatter_class=root_parser.formatter_class,
    )
    parser_redteam_session_list.set_defaults(func=redteam_session_list_handler)
    parser_redteam_session.set_defaults(
        func=lambda _: parser_redteam_session.print_help()
    )

    # Redteam command parser
    parser_redteam_command = subparsers_redteam.add_parser(
        name="command",
        help="Custom command execution on redteam session",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_command = parser_redteam_command.add_subparsers()
    parser_redteam_command.set_defaults(
        func=lambda _: parser_redteam_command.print_help()
    )

    parser_redteam_command_history = subparsers_command.add_parser(
        "history",
        help="Custom command execution history",
        formatter_class=root_parser.formatter_class,
    )
    parser_redteam_command_history.set_defaults(func=redteam_command_history_handler)

    parser_redteam_command_get = subparsers_command.add_parser(
        "get",
        help="Get information regarding a specific command",
        formatter_class=root_parser.formatter_class,
    )
    parser_redteam_command_get.set_defaults(func=redteam_command_get_handler)
    parser_redteam_command_get.add_argument(
        "command_id", type=str, help="The command id"
    )

    parser_redteam_command_execute = subparsers_command.add_parser(
        "execute",
        help="Execute command on attack session",
        formatter_class=root_parser.formatter_class,
    )
    parser_redteam_command_execute.add_argument(
        "--background",
        "-b",
        help="Execute command in background or not (Invoke-WmiMethod on Windows and & on Linux.)",
        default=None,
    )
    parser_redteam_command_execute.add_argument(
        "--timeout",
        "-t",
        help="Maximum time (seconds) to wait result command before timeout",
        default=None,
    )
    parser_redteam_command_execute.add_argument(
        "--identifier",
        "-id",
        help="Attack session identifier",
        default=None,
    )
    parser_redteam_command_execute.add_argument(
        "--command",
        "-c",
        help="Command to execute, must be surrounded by quotation marks",
        default=None,
    )
    parser_redteam_command_execute.set_defaults(func=redteam_command_execute_handler)

    parser_redteam_upload = subparsers_redteam.add_parser(
        "upload",
        help="Upload a file on target with attack session",
        formatter_class=root_parser.formatter_class,
    )
    parser_redteam_upload.set_defaults(func=redteam_upload_handler)

    parser_redteam_shell = subparsers_redteam.add_parser(
        "shell",
        help="Redteam shell on attack session",
        formatter_class=root_parser.formatter_class,
    )
    parser_redteam_shell.set_defaults(func=redteam_shell_handler)
