# -*- coding: utf-8 -*-
import argparse
import json
import sys
from typing import Any
from typing import List

from mantis_scenario_model.signature_model import Signature
from pydantic.json import pydantic_encoder

from mantis_api_client import scenario_api
from mantis_api_client.utils import colored


#
# 'signature_list_handler' handler
#
def signature_list_handler(args: Any) -> None:
    try:
        signatures = scenario_api.fetch_signatures()
    except Exception as e:
        print(colored(f"Error when fetching signatures: '{e}'", "red"))
        sys.exit(1)

    if args.json:
        print(json.dumps(signatures, default=pydantic_encoder))
        return
    for key, signature in sorted(
        signatures.items(), key=lambda kv: kv[1].attack_reference_id  # (clé, Signature)
    ):
        print(f"[+] \033[1m{signature.attack_reference_id}\033[0m")
        print(f"  [+] id: {key}")
        implems = ", ".join(
            imp.implementation_type.value for imp in signature.implementations
        )
        print(f"  [+] available implementations: {implems}")


def add_signature_parser(
    root_parser: argparse.ArgumentParser,
    subparsers: Any,
) -> None:
    # -------------------
    # --- Scenario API options (signatures)
    # -------------------

    parser_signature = subparsers.add_parser(
        "signature",
        help="Scenario API related commands (signature)",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_signature = parser_signature.add_subparsers()

    # 'signature_list' command
    parser_signature_list = subparsers_signature.add_parser(
        "list",
        help="List all available signatures",
        formatter_class=root_parser.formatter_class,
    )
    parser_signature_list.set_defaults(func=signature_list_handler)
    parser_signature_list.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    parser_signature_info = subparsers_signature.add_parser(
        "info",
        help="Get information about a signature",
        formatter_class=root_parser.formatter_class,
    )
    parser_signature_info.set_defaults(func=signature_info_handler)
    parser_signature_info.add_argument(
        "signature_id", type=str, help="The signature id"
    )
    parser_signature_info.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    group = parser_signature_info.add_mutually_exclusive_group()

    # Ajoutez les arguments au groupe
    group.add_argument(
        "--attack",
        help="The signature_id is a reference to an attack name. Cannot be used with --scenario.",
        action="store_true",
    )
    group.add_argument(
        "--scenario",
        help="The signature_id is a reference to a scenario name. Cannot be used with --attack.",
        action="store_true",
    )

    parser_signature.set_defaults(func=lambda _: parser_signature.print_help())


def print_signatures_of_scenario(signatures: List[Signature]) -> None:
    for sig in signatures:
        print_signature(sig)


def print_signature(signature) -> None:

    print(f"[+] \033[1m{signature.attack_reference_id}\033[0m")
    print("  [+] available implementations:")
    for i in signature.implementations:
        print(f"  [>] {i.implementation_type.value}")
        for k in i.signatures:
            print(f"    [+] Format \033[1m{k.signature_type.value}\033[0m")
            print(f"    {k.signature}")


def signature_info_handler(args: Any) -> None:
    # Parameters
    signature_id = args.signature_id
    signatures = []
    signature = None

    try:
        if args.attack is True:
            # It's an attack ID
            signature = scenario_api.fetch_signature_by_attack_id(signature_id)
        elif args.scenario is True:
            # It's a scenario ID
            signatures = scenario_api.fetch_signatures_by_scenario_id(signature_id)
        else:
            # It's a signature ID
            signature = scenario_api.fetch_signature_by_signature_id(signature_id)
    except Exception as e:
        print(colored(f"Error when fetching signature {signature_id}: '{e}'", "red"))
        sys.exit(1)

    if args.json and args.scenario is False and signature is not None:
        print(signature.json())
        return
    elif args.json and args.scenario is True and signatures is not None:
        json_data = [sig.json() for sig in signatures]

        # Now json_data is a list of JSON strings, but if you want it in the final JSON format, use json.dumps
        json_str = json.dumps(json_data)

        # Print the final JSON string
        print(json_str)
        return

    if args.scenario is True:
        print_signatures_of_scenario(signatures)
    else:
        print_signature(signature)
