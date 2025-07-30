# -*- coding: utf-8 -*-
import argparse
import json
import sys
import time
import zipfile
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from uuid import UUID

from mantis_dataset_model.dataset_model import PartialManifest
from pydantic.json import pydantic_encoder

from mantis_api_client import dataset_api
from mantis_api_client.exceptions import ConfigException
from mantis_api_client.oidc import get_oidc_client
from mantis_api_client.utils import colored


#
# 'datasets_list_handler' handler
#
def datasets_list_handler(args: Any) -> None:
    try:
        datasets: Dict[str, List[Dict[UUID, PartialManifest]]] = (
            dataset_api.fetch_datasets()
        )
    except ConfigException as e:
        print("{} You should run `mantis init` again to login to M&ntis SSO.", e)
        exit(1)
    except Exception as e:
        print(colored(f"Error when listing datasets: '{e}'", "red"))
        sys.exit(1)

    if args.json:
        print(json.dumps(datasets, default=pydantic_encoder))
        return

    print("[+] Available datasets:")
    for dataset in datasets:
        if len(datasets[dataset]) > 0:
            print(f"  [+] Datasets of '{dataset}': ")
            for d in datasets[dataset]:
                for id in d:
                    print(
                        f"""    [+] {id} - {d[id]['name']} ({d[id]["date_dataset_created"]})"""
                    )


#
# 'datasets_info_handler' handler
#
def datasets_info_handler(args: Any) -> None:
    # Parameters
    dataset_id = args.dataset_id

    try:
        dataset = dataset_api.fetch_dataset_by_uuid(dataset_id)
    except Exception as e:
        print(colored(f"Error when fetching dataset: '{e}'", "red"))
        sys.exit(1)

    if args.json:
        print(dataset.json())
        return

    print("[+] Dataset information: ")
    print(f"  [+] \033[1mName\033[0m: {dataset.name}")
    print(f"  [+] \033[1mDescription\033[0m: {dataset.description}")
    print(f"  [+] \033[1mCreation date\033[0m: {dataset.date_dataset_created}")
    if dataset.scenario:  # scenario is optional
        if (
            "timestamps" in dataset.scenario
            and "duration" in dataset.scenario["timestamps"]
        ):
            print(f"  [+] Duration: {dataset.scenario['timestamps']['duration']}")


#
# 'datasets_push_handler' handler
#
def datasets_push_handler(args: Any) -> None:
    """
    Handler to upload dataset to remote

    An attempt is performed to send the dataset and make it available to group users of each GROUP_ID (--groups).
    """
    # Parameters
    dataset_path: Path = args.dataset_path
    groups = args.groups
    uploaded: bool = False
    error_msg: str = ""
    public = args.public

    if public is False and groups == []:
        groups.append(get_oidc_client().get_default_group())
    if public is True:
        groups = []

    if dataset_path.exists() is False:
        print(f"The dataset path '{dataset_path}' does not exist.")
        sys.exit(1)

    try:
        zipfile.ZipFile(dataset_path, "r")
    except Exception:
        print(f"Could not open zip file '{dataset_path}'")
        sys.exit(1)

    if groups == []:
        print("[+] Uploading dataset accessible to anyone")
    else:
        print(f"[+] Uploading dataset accessible to groups: {', '.join(groups)}")

    # Uploading the dataset
    dataset_id = dataset_api.upload_dataset(dataset_path, groups)
    print(f"  [+] Dataset id: {dataset_id}")

    # Checking the status of the task
    timeout = 300  # seconds
    start = time.time()
    finished = False
    while time.time() - start < timeout and finished is False:
        res = dataset_api.upload_dataset_status(dataset_id)
        state = res["status"]
        error_msg = res["message"]
        if state in ["FINISHED", "FINISHED_ERROR"]:
            finished = True
            uploaded = state == "FINISHED"
        else:
            print("  [+] Dataset verification in progress")
            time.sleep(1)

    if uploaded is False:
        print(colored(f"  [-] The dataset could not be uploaded: {error_msg}.", "red"))
    else:
        print("  [+] Successfully uploaded the dataset.")


def add_dataset_parser(root_parser: argparse.ArgumentParser, subparsers: Any) -> None:

    # -------------------
    # --- Dataset API options
    # -------------------

    parser_dataset = subparsers.add_parser(
        "dataset",
        help="Dataset API related commands",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_dataset = parser_dataset.add_subparsers()

    # 'datasets_list' command
    parser_dataset_list = subparsers_dataset.add_parser(
        "list",
        help="List all available datasets",
        formatter_class=root_parser.formatter_class,
    )
    parser_dataset_list.set_defaults(func=datasets_list_handler)
    parser_dataset_list.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    # 'datasets_info' command
    parser_datasets_info = subparsers_dataset.add_parser(
        "info",
        help="Get information about a dataset",
        formatter_class=root_parser.formatter_class,
    )
    parser_datasets_info.set_defaults(func=datasets_info_handler)
    parser_datasets_info.add_argument("dataset_id", type=str, help="The dataset id")
    parser_datasets_info.add_argument(
        "--json", help="Return JSON result.", action="store_true"
    )

    parser_datasets_push = subparsers_dataset.add_parser(
        "push",
        help="Upload a local dataset .zip file to the remote",
        formatter_class=root_parser.formatter_class,
    )
    parser_datasets_push.set_defaults(func=datasets_push_handler)
    grps = parser_datasets_push.add_mutually_exclusive_group(required=True)
    grps.add_argument("--groups", action="extend", nargs="+", default=[])
    grps.add_argument("--public", action="store_true")
    parser_datasets_push.add_argument(
        "dataset_path", type=Path, help="The path to the dataset .zip file to upload"
    )
    parser_dataset.set_defaults(func=lambda _: parser_dataset.print_help())
