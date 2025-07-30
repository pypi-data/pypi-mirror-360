#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from pathlib import Path
from typing import Any
from typing import List
from uuid import UUID

import requests
from mantis_dataset_model.dataset_model import Manifest

from mantis_api_client.config import mantis_api_client_config
from mantis_api_client.oidc import authorize

# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


@authorize
def _get(route: str, **kwargs: Any) -> requests.Response:
    return requests.get(
        f"{mantis_api_client_config.dataset_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        timeout=30,
        **kwargs,
    )


@authorize
def _post(route: str, **kwargs: Any) -> requests.Response:
    timeout = kwargs.pop("timeout", 30)
    return requests.post(
        f"{mantis_api_client_config.dataset_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        timeout=timeout,
        **kwargs,
    )


@authorize
def _put(route: str, **kwargs: Any) -> requests.Response:
    return requests.put(
        f"{mantis_api_client_config.dataset_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        timeout=30,
        **kwargs,
    )


@authorize
def _delete(route: str, **kwargs: Any) -> requests.Response:
    return requests.delete(
        f"{mantis_api_client_config.dataset_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _handle_error(
    result: requests.Response, context_error_msg: str
) -> requests.Response:
    if (
        result.headers.get("content-type") == "application/json"
        and "message" in result.json()
    ):
        error_msg = result.json()["message"]
    else:
        error_msg = result.text

    raise Exception(
        f"{context_error_msg}. "
        f"Status code: '{result.status_code}'.\n"
        f"Error message: '{error_msg}'."
    )


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def get_version() -> str:
    """
    Return dataset API version.

    :return: The version inumber n a string
    """
    result = _get("/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve dataset API version")

    return result.json()


# -------------------------------------------------------------------------- #
# Dataset API
# -------------------------------------------------------------------------- #


def fetch_datasets() -> Any:
    """
    List all available datasets

    :return: the list of manifests
    """
    result = _get("/")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve datasets from dataset API")

    return result.json()


def fetch_dataset_by_uuid(partial_dataset_id: str) -> Any:
    """
    Get the full JSON manifest of a specific dataset

    :param partial_dataset_id: UUID of the dataset to fetch, or prefix of it that uniquely identifies the dataset

    If a full UUID is given, returns the identified dataset metadata if it
    exists. If a partial UUID (prefix of an existing UUID) is given, and this
    prefix uniquely identifies one and only one dataset, the latter's metadata
    is returned.
    """
    result = _get(f"/{partial_dataset_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve dataset from dataset API")
    else:
        dataset_data = result.json()
        dataset = Manifest(**dataset_data)

    return dataset


def fetch_dataset_resource(
    partial_dataset_id: str, resource_type_str: str, resource_id: UUID
) -> Any:
    """
    Get the description of a specific resource.

    This function *does not* fetch the file(s) associated with one resource,
    it merely returns the portion of the JSON manifest that describes that
    particular resource. This JSON includes, in particular, the list
    of files included in the resource, and the URLs to download them. It is
    up to the user to manually fetch these URLs.

    :param partial_dataset_id: UUID of the dataset to which the resource belongs, or a prefix of it that uniquely identifies it
    :param resource_type_str: type of the resource to fetch. Must be a string among "log", "pcap", "memory_dump", "redteam_report", "life_report"
    :param resource_id: UUID of the resource
    :return: JSON structure describing the resource
    """
    result = _get(f"/{partial_dataset_id}/{resource_type_str}/{resource_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve dataset from dataset API")

    return result.json()


# def delete_dataset(
#     dataset_id: str, force: bool = False
# ) -> None:
#     """
#     Delete a specific dataset

#     :param dataset_id: the full UUID of the dataset to delete
#     :param force: (optional, default False) if True, forces the deletion of the dataset, even if there are validation errors in the manifest, or in the dataset contents. If the manifest is corrupted, remotely stored resources may not be deleted even though delete_remote_data was set to True.

#     """

#     raise NotImplementedError("This API method is not currently available")

#     # result = _delete(
#     #     f"/{dataset_id}",
#     #     params={"force": force},
#     # )

#     # if result.status_code != 200:
#     #     _handle_error(result, "Cannot delete dataset from dataset API")

#     # return None


# def delete_all_datasets(force: bool = False) -> Any:
#     """
#     Delete all datasets

#     :param force: (optional, default False) if True, forces the deletion of the datasets, even if there are validation errors in the manifests, or in the datasets contents. If a manifest is corrupted, remotely stored resources for that dataset may not be deleted even though delete_remote_data was set to True.
#     :return: a JSON structure specifying the datasets that were successfully deleted, and the errors encountered

#     """

#     raise NotImplementedError("This API method is not currently available")

#     # result = _delete(
#     #     "/all", params={"force": force}
#     # )

#     # if result.status_code != 200:
#     #     _handle_error(result, "Cannot delete datasets from dataset API")

#     # return result.json()


def get_archive_infos_for_dataset(partial_dataset_id: str) -> Any:
    """
    Retrieve information about a zip archive for a partial_dataset_id.

    :param partial_dataset_id: the partial or complete UUID of the dataset
    :return: a JSON structure containing size, url and if the archive exists.
    """
    result = _get(f"/{partial_dataset_id}/zip")

    if result.status_code != 200:
        _handle_error(
            result,
            "Cannot retrieve dataset archive information from dataset API",
        )

    return result.json()


def upload_dataset(dataset_path: Path, groups: List[str]) -> UUID:
    # Uploading the dataset
    params = {"filename": dataset_path.name, "groups": groups}
    with dataset_path.open("rb") as f:
        result = _post("/upload", params=params, data=f, timeout=600)

    if result.status_code != 200:
        _handle_error(
            result,
            "Cannot retrieve dataset archive information from dataset API",
        )
    dataset_id = UUID(result.json()["dataset_id"])

    return dataset_id


def upload_dataset_status(dataset_id: UUID) -> Any:
    # Getting information about the Dataset
    state = _get(f"/upload/{dataset_id}/status")
    state = state.json()
    return state
