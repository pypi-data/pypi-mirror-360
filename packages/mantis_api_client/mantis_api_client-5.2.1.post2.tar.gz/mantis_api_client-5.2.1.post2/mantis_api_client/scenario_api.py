#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from typing import Any
from typing import Dict
from typing import List

import requests
from mantis_common_model.pagination import Pagination
from mantis_scenario_model.api_scenario_model import LabListReply
from mantis_scenario_model.api_scenario_model import PausedStatus
from mantis_scenario_model.api_scenario_model import RemoteAccess
from mantis_scenario_model.basebox_model import Basebox
from mantis_scenario_model.lab_config_model import ContentType
from mantis_scenario_model.lab_config_model import LabConfig
from mantis_scenario_model.log_collector_model import LogCollector
from mantis_scenario_model.scenario_model import Scenario
from mantis_scenario_model.signature_model import Signature
from mantis_scenario_model.topology_model import Topology
from mantis_scenario_model.unit_attack_model import UnitAttack
from pydantic import parse_obj_as

from mantis_api_client.config import mantis_api_client_config
from mantis_api_client.oidc import authorize

# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: Any) -> requests.Response:
    return requests.get(
        f"{mantis_api_client_config.scenario_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _post(route: str, **kwargs: Any) -> requests.Response:
    return requests.post(
        f"{mantis_api_client_config.scenario_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _put(route: str, **kwargs: Any) -> requests.Response:
    return requests.put(
        f"{mantis_api_client_config.scenario_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _delete(route: str, **kwargs: Any) -> requests.Response:
    return requests.delete(
        f"{mantis_api_client_config.scenario_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _handle_error(
    result: requests.Response, context_error_msg: str
) -> requests.Response:
    error_msg = ""
    if result.headers.get("content-type") == "application/json":
        error_data = result.json()
        for k in ("message", "detail"):
            if k in error_data:
                error_msg = error_data[k]
                break
    if not error_msg:
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
    Return publish API version.

    :return: The version number is a string
    """
    result = authorize(_get)("/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve scenario API version")

    return result.json()


# -------------------------------------------------------------------------- #
# Scenario API
# -------------------------------------------------------------------------- #


def fetch_attacks() -> Any:
    """
    List all available unit attacks

    :return: the list of unit attacks
    """
    result = authorize(_get)("/unit_attack")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve unit attacks from scenario API")
    else:
        attacks_data = result.json()
        attacks = parse_obj_as(List[UnitAttack], attacks_data)

    return attacks


def fetch_attack_by_name(attack_name: str) -> Any:
    """
    Get the full JSON manifest of a specific unit attack

    :param attack_name: the name of the unit attack to fetch

    :return: the JSON of unit attacks
    """
    result = authorize(_get)(f"/unit_attack/{attack_name}")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot retrieve unit attack '{attack_name}' from frontend publish API",
        )
    else:
        attack_data = result.json()
        attack = UnitAttack(**attack_data)

    return attack


def fetch_scenarios() -> List[Scenario]:
    """
    List all available scenarios

    :return: the list of scenarios
    """
    result = authorize(_get)("/scenario")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve scenarios from scenario API")
    else:
        scenarios_data = result.json()
        scenarios = parse_obj_as(List[Scenario], scenarios_data)

    return scenarios


def fetch_scenario_by_name(scenario_id: str) -> Scenario:
    """
    Get the full JSON manifest of a specific scenario.

    :param scenario_id: id of the scenario to fetch

    :return: the JSON of the scenario
    """
    result = authorize(_get)(f"/scenario/{scenario_id}")

    if result.status_code != 200:
        _handle_error(
            result, f"Cannot retrieve scenario '{scenario_id}' from scenario API"
        )
    else:
        scenario_data = result.json()
        scenario = Scenario(**scenario_data)

    return scenario


def fetch_topologies() -> List[Topology]:
    """
    List all available topologies

    :return: the list of topologies
    """
    result = authorize(_get)("/topology")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve topologies from scenario API")
    else:
        topologies_data = result.json()
        topologies = parse_obj_as(List[Topology], topologies_data)

    return topologies


def fetch_topology_by_name(topology_name: str) -> Topology:
    """
    Get the topology object given its name.

    :param topology_name: name of the topology

    :return: the topology object
    """
    params = {"topology_name": topology_name}
    result = authorize(_get)("/topology/info", params=params)

    if result.status_code != 200:
        _handle_error(
            result, f"Cannot retrieve topology '{topology_name}' from scenario API"
        )
    else:
        topology_data = result.json()
        topology = Topology(**topology_data)

    return topology


def fetch_baseboxes() -> List[Basebox]:
    """
    List all available baseboxes

    :return: the list of baseboxes
    """
    result = authorize(_get)("/basebox")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve baseboxes from scenario API")
    else:
        baseboxes_data = result.json()
        baseboxes = parse_obj_as(List[Basebox], baseboxes_data)

    return baseboxes


def fetch_basebox_by_id(basebox_id: str) -> Basebox:
    """
    Get the basebox object given its ID.

    :param basebox_id: name of the basebox

    :return: the basebox object
    """
    result = authorize(_get)(f"/basebox/{basebox_id}")

    if result.status_code != 200:
        _handle_error(
            result, f"Cannot retrieve basebox '{basebox_id}' from scenario API"
        )
    else:
        basebox_data = result.json()
        basebox = Basebox(**basebox_data)

    return basebox


def get_log_collectors() -> List[LogCollector]:
    """
    Retrieve log collectors configuration information.
    """

    result = authorize(_get)("/log_collector")

    if result.status_code != 200:
        _handle_error(
            result,
            "Cannot get log collectors data from scenario API",
        )

    return result.json()


def create_lab_topology(
    topology: Topology,
    lab_config: LabConfig,
    group_name: str,
    group_id: str,
) -> str:
    """
    Create a lab with the given topology.

    :param topology: the topology to run

    :return: a lab uuid
    """

    # Inject content information into lab_config
    lab_config.content_type = ContentType.TOPOLOGY
    lab_config.content_name = topology.name

    # Convert model into dict
    lab_config_dict = json.loads(lab_config.json())

    # API call
    result = authorize(_post)(
        "/topology/create_lab",
        params={"group_name": group_name, "group_id": group_id},
        json={"lab_config": lab_config_dict},
    )

    if result.status_code != 200:
        _handle_error(
            result, f"Cannot run topology '{topology.name}' from scenario API"
        )

    return result.json()


def run_lab_topology(
    topology: Topology,
    lab_config: LabConfig,
    group_name: str,
    group_id: str,
) -> str:
    """
    Run the given topology.

    :param topology: the topology to run

    :return: a lab id
    """

    # Inject content information into lab_config
    lab_config.content_type = ContentType.TOPOLOGY
    lab_config.content_name = topology.name

    # Convert model into dict
    lab_config_dict = json.loads(lab_config.json())

    # API call
    result = authorize(_post)(
        "/topology/run_lab",
        params={"group_name": group_name, "group_id": group_id},
        json={"lab_config": lab_config_dict},
    )

    if result.status_code != 200:
        _handle_error(
            result, f"Cannot run topology '{topology.name}' from scenario API"
        )

    return result.json()


def create_lab_basebox(
    basebox_id: str,
    lab_config: LabConfig,
    group_name: str,
    group_id: str,
) -> str:
    """
    Create a lab with the given basebox.

    :param basebox_id: the basebox to run

    :return: a lab uuid
    """

    # Inject content information into lab_config
    lab_config.content_type = ContentType.BASEBOX
    lab_config.content_name = basebox_id

    # Convert model into dict
    lab_config_dict = json.loads(lab_config.json())

    # API call
    result = authorize(_post)(
        "/basebox/create_lab",
        params={"group_name": group_name, "group_id": group_id},
        json={"lab_config": lab_config_dict},
    )

    if result.status_code != 200:
        _handle_error(result, f"Cannot run basebox '{basebox_id}' from scenario API")

    return result.json()


def run_lab_basebox(
    basebox_id: str,
    lab_config: LabConfig,
    group_name: str,
    group_id: str,
) -> str:
    """
    Run the given basebox.

    :param basebox_id: the basebox to run

    :return: a lab id
    """

    # Inject content information into lab_config
    lab_config.content_type = ContentType.BASEBOX
    lab_config.content_name = basebox_id

    # Convert model into dict
    lab_config_dict = json.loads(lab_config.json())

    # API call
    result = authorize(_post)(
        "/basebox/run_lab",
        params={"group_name": group_name, "group_id": group_id},
        json={"lab_config": lab_config_dict},
    )

    if result.status_code != 200:
        _handle_error(result, f"Cannot run basebox '{basebox_id}' from scenario API")

    return result.json()


def create_lab_scenario(
    scenario: Scenario,
    scenario_profile: str,
    lab_config: LabConfig,
    group_name: str,
    group_id: str,
) -> str:
    """
    Create a lab with the given scenario.

    :param scenario: the scenario to run

    :return: a lab uuid
    """

    # Inject content information into lab_config
    lab_config.content_type = ContentType.KILLCHAIN
    lab_config.content_name = scenario.name
    lab_config.scenario_profile = scenario_profile

    # Convert model into dict
    lab_config_dict = json.loads(lab_config.json())

    # API call
    result = authorize(_post)(
        "/scenario/create_lab",
        params={"group_name": group_name, "group_id": group_id},
        json={
            "lab_config": lab_config_dict,
        },
    )

    if result.status_code != 200:
        _handle_error(
            result, f"Cannot run scenario '{scenario.name}' from scenario API"
        )

    return result.json()


def run_lab_scenario(
    scenario: Scenario,
    scenario_profile: str,
    lab_config: LabConfig,
    group_name: str,
    group_id: str,
) -> str:
    """
    Run the given scenario.

    :param scenario: the scenario to run

    :return: a lab id
    """

    # Inject content information into lab_config
    lab_config.content_type = ContentType.KILLCHAIN
    lab_config.content_name = scenario.name
    lab_config.scenario_profile = scenario_profile

    # Convert model into dict
    lab_config_dict = json.loads(lab_config.json())

    # API call
    result = authorize(_post)(
        "/scenario/run_lab",
        params={"group_name": group_name, "group_id": group_id},
        json={
            "lab_config": lab_config_dict,
        },
    )

    if result.status_code != 200:
        _handle_error(
            result, f"Cannot run scenario '{scenario.name}' from scenario API"
        )

    return result.json()


def create_lab_attack(
    attack: UnitAttack,
    scenario_profile: str,
    lab_config: LabConfig,
    group_name: str,
    group_id: str,
) -> str:
    """
    Create a lab with the given attack.

    :param attack: the attack to run
    :param scenario_profile: the unit scenario to run for the current attack

    :return: a lab uuid
    """

    # Inject content information into lab_config
    lab_config.content_type = ContentType.ATTACK
    lab_config.content_name = attack.name
    lab_config.scenario_profile = scenario_profile

    # Convert model into dict
    lab_config_dict = json.loads(lab_config.json())

    # API call
    result = authorize(_post)(
        "/unit_attack/create_lab",
        params={"group_name": group_name, "group_id": group_id},
        json={
            "lab_config": lab_config_dict,
        },
    )

    if result.status_code != 200:
        _handle_error(result, f"Cannot run attack '{attack.name}' from scenario API")

    return result.json()


def run_lab_attack(
    attack: UnitAttack,
    scenario_profile: str,
    lab_config: LabConfig,
    group_name: str,
    group_id: str,
) -> str:
    """
    Run the given attack.

    :param attack: the attack to run
    :param scenario_profile: the unit scenario to run for the current attack

    :return: a lab id
    """

    # Inject content information into lab_config
    lab_config.content_type = ContentType.ATTACK
    lab_config.content_name = attack.name
    lab_config.scenario_profile = scenario_profile

    # Convert model into dict
    lab_config_dict = json.loads(lab_config.json())

    # API call
    result = authorize(_post)(
        "/unit_attack/run_lab",
        params={"group_name": group_name, "group_id": group_id},
        json={
            "lab_config": lab_config_dict,
        },
    )

    if result.status_code != 200:
        _handle_error(result, f"Cannot run attack '{attack.name}' from scenario API")

    return result.json()


def fetch_labs(
    all_labs: bool = False, pagination: Pagination = Pagination()
) -> LabListReply:
    """
    Get list of current labs.
    If all_labs is True, retrieve also stopped labs.

    :return: a list containg the current labs.
    """
    params = {"all_labs": all_labs, "limit": pagination.limit, "page": pagination.page}
    result = authorize(_get)("/runner", params=params)

    if result.status_code != 200:
        _handle_error(result, "Cannot get lab list from scenario API")

    return result.json()


def fetch_lab(lab_id: str) -> Dict:
    """
    Get status of a lab.

    :param lab_id: the lab id

    :return: a dict containg the lab status and potential results
    """
    result = authorize(_get)(f"/runner/{lab_id}")

    if result.status_code != 200:
        _handle_error(
            result, f"Cannot get lab status from id '{lab_id}' from scenario API"
        )

    return result.json()


def run_lab(lab_id: str) -> None:
    """
    Run a lab.

    :param lab_id: the lab id
    """
    result = authorize(_get)(f"/runner/{lab_id}/run")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot run lab of id '{lab_id}' from scenario API",
        )


def stop_lab(lab_id: str) -> None:
    """
    Stop lab execution.

    :param lab_id: the lab id

    :return: a dict containg the lab status and potential results
    """
    result = authorize(_get)(f"/runner/{lab_id}/stop")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot stop lab execution of id '{lab_id}' from scenario API",
        )


def resume_lab(lab_id: str) -> None:
    """
    Resume lab execution.

    :param lab_id: the lab id

    :return: a dict containg the lab status and potential results
    """
    result = authorize(_get)(f"/runner/{lab_id}/resume")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot resume lab execution of id '{lab_id}' from scenario API",
        )


def fetch_lab_paused_status(lab_id: str) -> PausedStatus:
    """
    Fetch lab status during pause.

    :param lab_id: the lab id

    :return: a dict containg the lab paused status
    """
    result = authorize(_get)(f"/runner/{lab_id}/paused_status")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot resume lab execution of id '{lab_id}' from scenario API",
        )
    else:
        paused_status_data = result.json()
        paused_status = PausedStatus(**paused_status_data)

    return paused_status


def fetch_lab_topology(lab_id: str) -> Topology:
    """
    Get scenario topology of a current lab.

    :param lab_id: the lab id

    :return: a dict containg the topology
    """
    result = authorize(_get)(f"/runner/{lab_id}/topology")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot get scenario topology from id '{lab_id}' from scenario API",
        )
    else:
        topology_data = result.json()
        topology = Topology(**topology_data)

    return topology


def fetch_lab_nodes(lab_id: str) -> List:
    """
    Get scenario nodes of a current lab.

    :param lab_id: the lab id

    :return: the current nodes
    """
    result = authorize(_get)(f"/runner/{lab_id}/nodes")

    if result.status_code != 200:
        _handle_error(
            result, f"Cannot get scenario nodes from id '{lab_id}' from scenario API"
        )

    return result.json()


def fetch_lab_assets(lab_id: str) -> List:
    """
    Get scenario assets of a current lab.

    :param lab_id: the lab id

    :return: the current assets
    """
    result = authorize(_get)(f"/runner/{lab_id}/assets")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot get scenario assets from id '{lab_id}' from scenario API",
        )

    return result.json()


def fetch_lab_attack_report(lab_id: str) -> List:
    """
    Get scenario attack report of a current lab.

    :param lab_id: the lab id

    :return: the current attack report
    """
    result = authorize(_get)(f"/runner/{lab_id}/attack_report")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot get scenario attack report from id '{lab_id}' from scenario API",
        )

    return result.json()


def fetch_lab_attack_infras(lab_id: str) -> List:
    """
    Get scenario attack infrastructures of a current lab.

    :param lab_id: the lab id

    :return: the current attack infrastructures
    """
    result = authorize(_get)(f"/runner/{lab_id}/attack_infras")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot get scenario attack infras from id '{lab_id}' from scenario API",
        )

    return result.json()


def fetch_lab_attack_sessions(lab_id: str) -> List:
    """
    Get scenario attack sessions of a current lab.

    :param lab_id: the lab id

    :return: the current attack sessions
    """
    result = authorize(_get)(f"/runner/{lab_id}/attack_sessions")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot get scenario attack sessions from id '{lab_id}' from scenario API",
        )

    return result.json()


def fetch_lab_attack_knowledge(lab_id: str) -> Dict:
    """
    Get scenario attack knowledge of a current lab.

    :param lab_id: the lab id

    :return: the attack knowledge
    """
    result = authorize(_get)(f"/runner/{lab_id}/attack_knowledge")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot get scenario attack knowledge from id '{lab_id}' from scenario API",
        )

    return result.json()


def fetch_lab_notifications(lab_id: str) -> List:
    """
    Get scenario notifications of a current lab.

    :param lab_id: the lab id

    :return: the notifications as a list of strings
    """
    result = authorize(_get)(f"/runner/{lab_id}/notifications")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot get scenario notifications from id '{lab_id}' from scenario API",
        )

    return result.json()


def delete_lab(lab_id: str) -> None:
    """
    Delete a lab from its ID.

    :param lab_id: the lab id
    """
    result = authorize(_delete)(f"/runner/{lab_id}")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot delete lab from id '{lab_id}' from scenario API",
        )


def fetch_lab_config(lab_id: str) -> LabConfig:
    """
    Get lab config of a current lab.

    :param lab_id: the lab id

    :return: the lab config
    """
    result = authorize(_get)(f"/runner/{lab_id}/lab_config")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot get lab config from id '{lab_id}' from scenario API",
        )
    else:
        lab_config_data = result.json()
        lab_config = LabConfig(**lab_config_data)

    return lab_config


def fetch_lab_remote_access(lab_id: str) -> RemoteAccess:
    """
    Get info to remotly access lab VMs.

    :param lab_id: the lab id

    :return: the remote lab VMs info
    """
    result = authorize(_get)(f"/runner/{lab_id}/remote_access")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot get lab config from id '{lab_id}' from scenario API",
        )
    else:
        remote_access_data = result.json()
        remote_access = RemoteAccess(**remote_access_data)

    return remote_access


def fetch_signatures() -> Dict[str, Signature]:
    """
    List all available signatures

    :return: the list of signature
    """
    result = authorize(_get)("/signature")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve signatures from scenario API")
    else:
        signatures_data = result.json()
        signatures = parse_obj_as(Dict[str, Signature], signatures_data)

    return signatures


def raise_for_errors(result):
    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve signatures from scenario API")


def parse_dict_to_signature(signature_data) -> Signature:
    signature = None

    signature = Signature(**signature_data)

    return signature


def fetch_signatures_by_scenario_id(scenario_id: str) -> List[Signature]:
    sig_list: List[Signature] = []
    params = {"scenario_id": scenario_id}
    result = authorize(_get)("/signature/scenario/info", params=params)
    raise_for_errors(result)
    signatures = result.json()
    for sig in signatures:
        signature = parse_dict_to_signature(sig)
        sig_list.append(signature)

    return sig_list


def fetch_signature_by_attack_id(signature_id: str) -> Signature:
    """
    Get the signature object given its attack reference id.

    :param signature_id: name of the signature

    :return: the signature object
    """
    params = {"signature_id": signature_id}
    result = authorize(_get)("/signature/attack/info", params=params)
    raise_for_errors(result)
    signature = parse_dict_to_signature(result.json())

    return signature


def fetch_signature_by_signature_id(signature_id: str) -> Signature:
    """
    Get the signature object given its id.

    :param signature_id: id of the signature

    :return: the signature object
    """
    params = {"signature_id": signature_id}
    result = authorize(_get)("/signature/info", params=params)
    raise_for_errors(result)
    signature = parse_dict_to_signature(result.json())

    return signature
