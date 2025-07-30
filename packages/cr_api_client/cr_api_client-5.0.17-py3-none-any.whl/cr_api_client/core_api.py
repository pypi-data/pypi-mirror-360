#! /usr/bin/env python
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
import json
import os
import random
import shutil
import string
import time
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

import requests
from mantis_catalog.path import copytree_path
from mantis_dataset_model.dataset_analysis_model import DatasetAnalysisResult
from mantis_scenario_model.lab_model import ScenarioExecutionStopped
from mantis_scenario_model.topology_model import Topology
from ruamel.yaml import YAML

from cr_api_client import shutil_make_archive_lock
from cr_api_client.config import cr_api_client_config
from cr_api_client.logger import logger


# from humanize import naturalsize

# Module variables
cbk_check_stopped = None
cbk_create_simulation_before = None
cbk_create_simulation_after = None
cbk_start_simulation_before = None
cbk_start_simulation_after = None

# Simulation status mapping
map_status = {
    "CREATED": 1,
    "PREPARING": 2,
    "READY": 3,
    "STARTING": 4,
    "PROVISIONING": 5,
    "RUNNING": 6,
    "USER_ACTIVITY_PLAYING": 7,
    "STOPPING": 8,
    "DESTROYED": 9,
    "CLONING": 10,
    "PAUSING": 11,
    "UNPAUSING": 12,
    "PAUSED": 13,
    "ERROR": 14,
}


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: Any) -> requests.Response:
    return requests.get(
        f"{cr_api_client_config.core_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        **kwargs,
    )


def _post(route: str, **kwargs: Any) -> requests.Response:
    return requests.post(
        f"{cr_api_client_config.core_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _put(route: str, **kwargs: Any) -> requests.Response:
    return requests.put(
        f"{cr_api_client_config.core_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _delete(route: str, **kwargs: Any) -> requests.Response:
    return requests.delete(
        f"{cr_api_client_config.core_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _handle_error(result: requests.Response, context_error_msg: str) -> None:
    error_msg: Optional[str] = None

    if result.headers.get("content-type") == "application/json":
        result_json = result.json()
        if "message" in result_json:
            error_msg = result_json["message"]
        elif "detail" in result_json:
            error_msg = result_json["detail"]

    if error_msg is None:
        error_msg = result.text

    raise Exception(
        f"{context_error_msg}. "
        f"Status code: '{result.status_code}'. "
        f"Error message: '{error_msg}'."
    )


# Generate a unique ascii name
def _get_random_string(length: int) -> str:
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


def _simulation_execute_operation(
    method: str,
    operation: str,
    id_simulation: int,
    expected_current_simulation_status: str,
    optional_param1: Optional[Any] = None,
    optional_param2: Optional[Any] = None,
    post_data: Optional[Any] = None,
) -> int:
    """
    Generic method to launch IT Simulation API operation on a target simulation.

    This function SHOULD be used to call all "asynchronous" operations exposed by the
    IT Simulation API. That is, for all API endpoints that launch an "asynchronous task",
    and which have an associated "/get_status" endpoint.

    This function MUST NOT be used for synchronous endpoints.
    """

    logger.info(
        "[+] Going to execute operation '{}' on simulation ID '{}'".format(
            operation, id_simulation
        )
    )

    # Build URI
    uri = f"/simulation/{id_simulation}/{operation}"
    if optional_param1 is not None:
        uri = f"{uri}/{str(optional_param1)}"
    if optional_param2 is not None:
        uri = f"{uri}/{str(optional_param2)}"

    # Start the operation
    result, task_identifier = _simulation_start_operation(
        method, operation, uri, post_data
    )

    # Build URI to get the status of the task
    uri_get_status = (
        f"/simulation/{id_simulation}/{operation}/get_status/{task_identifier}"
    )

    # Handle cloning case where a new id_simulation or new dataset_id is returned
    if operation == "clone":
        id_simulation = result.json()["id"]

    # Wait for the operation to be completed in backend
    current_operation_status: Dict[str, Any] = {}
    display_idx = 0
    while True:

        if cbk_check_stopped is not None:
            if cbk_check_stopped() is True:
                logger.info("   [+]    Current process was asked to stop")
                raise ScenarioExecutionStopped

        # Sleep before next iteration
        time.sleep(0.3)

        # Do not display debug info at each loop iteraion
        if display_idx % 10 == 0:
            logger.info(
                "  [+] Currently executing operation '{}' on "
                "simulation ID '{}', with task id {}...".format(
                    operation, id_simulation, task_identifier
                )
            )
        display_idx += 1

        result = _get(uri_get_status)
        if result.status_code != 200:
            _handle_error(
                result,
                f"Error while getting the status of the operation '{operation}' (task id {task_identifier})",
            )

        current_operation_status = result.json()
        if not all(
            k in current_operation_status for k in ["state", "error_msg", "result"]
        ):
            raise Exception(
                f"Error while getting the status of the ongoing '{operation}' operation (task id {task_identifier}): returned information from API is not well formed"
            )

        if current_operation_status["state"] == "FINISHED":
            break

    # The operation is completed
    simulation_dict = _simulation_conclude_operation(
        id_simulation, operation, current_operation_status
    )

    if simulation_dict["error_msg"] and simulation_dict["error_msg"] != "None":
        potential_error_msg = " (with error '{}')".format(simulation_dict["error_msg"])
    else:
        potential_error_msg = ""
    logger.info(
        "[+] Current simulation status: '{}'{}".format(
            simulation_dict["status"], potential_error_msg
        )
    )

    return id_simulation


def _simulation_start_operation(
    method: str,
    operation: str,
    # id_simulation: int,
    uri: str,
    # uri_get_status_base: str,
    post_data: Optional[Any] = None,
) -> Tuple[requests.Response, str]:
    if method == "get":
        result = _get(uri)
    else:
        data = json.dumps(post_data)
        result = _post(uri, data=data, headers={"Content-Type": "application/json"})

    # if result.status_code != 200:
    #     # Special case: this operations is already running in the IT Simulation API backend
    #     # but is actually finished. In this case, get its status (this will delete the task
    #     # the IT Simulation API backend), and try again.
    #     # TODO: this is not perfect, in the sense that it is not a great UX.
    #     try:
    #         result_get_status = _get(uri_get_status)
    #         if result_get_status.status_code == 200:
    #             result_get_status_json = result_get_status.json()
    #             if (
    #                 all(
    #                     k in result_get_status_json
    #                     for k in ["state", "result", "error_msg"]
    #                 )
    #                 and result_get_status_json["state"] == "FINISHED"
    #             ):
    #                 logger.warning(
    #                     "  [+] A previous '{}' operation was running for simulation ID {} and terminated, but its result was not fetched (result was {}, error was {}). Attempting the operation again.".format(
    #                         operation,
    #                         id_simulation,
    #                         result_get_status_json["result"],
    #                         result_get_status_json["error_msg"],
    #                     )
    #                 )
    #                 if method == "get":
    #                     result = _get(uri)
    #                 else:
    #                     result = _post(uri)
    #     except Exception:
    #         pass

    if result.status_code != 200:
        _handle_error(result, f"Cannot execute operation '{operation}'")

    # Get back the task name
    try:
        task_identifier: str = result.json()["task_name"]
    except Exception:
        raise Exception(
            f"Cannot execute operation '{operation}': IT Simulation API did not send back the task name properly. Aborting."
        )

    return result, task_identifier


def _simulation_conclude_operation(
    id_simulation: int, operation: str, final_operation_status: Dict[str, Any]
) -> Dict[str, Any]:
    simulation_dict = fetch_simulation(id_simulation)
    if (
        final_operation_status["state"] != "FINISHED"
        or final_operation_status["error_msg"] is not None
    ):
        # Something went wrong
        # Raise an exception, but also ensure that the simulation status is ERROR
        if final_operation_status["state"] != "FINISHED":
            # Should never happen, normally
            error_msg = "Error during simulation operation '{}' on simulation ID '{}' (task id {}): operation ended unexpectedly. The operation status is '{}' and the given error is '{}'".format(
                operation,
                id_simulation,
                final_operation_status["task_name"],
                final_operation_status["state"],
                final_operation_status["error_msg"],
            )
        else:
            # Error during the operation
            error_msg = "Error during simulation operation '{}' on simulation ID '{}' (task id {} ): returned error message is '{}'".format(
                operation,
                id_simulation,
                final_operation_status["task_name"],
                final_operation_status["error_msg"],
            )

        # Update simulation status if necessary
        if simulation_dict["status"] != "ERROR":
            simulation_dict["status"] = "ERROR"
            data = {"status": "ERROR"}
            if (
                simulation_dict["error_msg"] is not None
                and len(simulation_dict["error_msg"]) > 0
                and simulation_dict["error_msg"] != "None"
            ):
                data["error_msg"] = simulation_dict[
                    "error_msg"
                ] + ". Another error occured: {}".format(error_msg)
            else:
                data["error_msg"] = error_msg
            update_simulation(id_simulation, data)

        raise Exception(error_msg)
    else:
        # All went well

        # Delete the error message in db, if necessary
        if (
            simulation_dict["status"] != "ERROR"
            and simulation_dict["error_msg"] is not None
            and len(simulation_dict["error_msg"]) > 0
            and simulation_dict["error_msg"] != "None"
        ):
            simulation_dict["error_msg"] = "None"
            data = {"error_msg": simulation_dict["error_msg"]}
            update_simulation(id_simulation, data)

        if final_operation_status["result"]:
            result_operation = " Result is:\n{}".format(
                final_operation_status["result"]
            )
        else:
            result_operation = ""
        logger.info(
            "[+] Operation '{}' on simulation ID '{}' (task id {}) was correctly executed.{}".format(
                operation,
                id_simulation,
                final_operation_status["task_name"],
                result_operation,
            )
        )
    return simulation_dict


def _validate_yaml_topology_file(yaml_configuration_file: Path) -> None:
    if yaml_configuration_file.exists() is not True:
        raise Exception(
            "The provided YAML configuration path does not exist: '{}'".format(
                yaml_configuration_file
            )
        )

    if yaml_configuration_file.is_file() is not True:
        raise Exception(
            "The provided YAML configuration path is not a file: '{}'".format(
                yaml_configuration_file
            )
        )


def _validate_topology_requirements(topology: Dict, resources: Optional[List]) -> None:
    """
    Checks that resources are provided for topology that expects resources

    Return True if resources are provided, or if no resources are provided and the topology does not
    expect any resource.
    """
    if resources:
        return

    for node in topology.get("nodes", ()):
        for volume in node.get("volumes", ()):
            if "host_path" in volume:
                raise Exception("The provided topology expects resources")


def _read_yaml_topology_file(yaml_configuration_file: Path) -> str:
    with yaml_configuration_file.open() as fd:
        yaml_content = fd.read()
        return yaml_content


def _zip_resources(resources_path: Path, temp_dir: Path) -> str:
    """
    Zip a folder in an archive
    """
    dir_name: str = os.path.basename(os.path.normpath(resources_path))
    zip_base_name: str = os.path.join(temp_dir, dir_name)
    zip_format: str = "zip"
    with shutil_make_archive_lock:
        shutil.make_archive(
            base_name=zip_base_name, format=zip_format, root_dir=resources_path
        )
    return "{}.zip".format(zip_base_name)


# Modify the topology to add parameters that can be deduced by
# reading the topology
def _simu_create_add_implicit_topo_parameters(topology: Any) -> None:
    # Add a "dns" parameter to docker nodes by deducing it from
    # reading the "dhcp_nameserver" of router nodes
    _simu_create_add_implicit_dns_parameter(topology)


def _simu_create_add_implicit_dns_parameter(topology: Any) -> None:
    # List the DNS servers and their switches
    switch_name_to_dns_ip: Dict[str, List[str]] = dict()
    for link in topology["links"]:
        if "type" not in link["node"]:
            continue
        if link["node"]["type"] == "router":
            params = link["params"]
            if "dhcp_nameserver" not in params:
                continue
            dns_server_ip = params["dhcp_nameserver"]
            if "name" not in link["switch"]:
                continue
            sw_name = link["switch"]["name"]
            if sw_name not in switch_name_to_dns_ip:
                switch_name_to_dns_ip[sw_name] = []
            switch_name_to_dns_ip[sw_name].append(dns_server_ip)

    # Add the switches IPs to the docker nodes
    for link in topology["links"]:
        node = link["node"]
        if "type" not in node:
            continue
        if node["type"] == "docker":
            sw = link["switch"]["name"]
            if sw not in list(switch_name_to_dns_ip.keys()):
                continue
            dns_list = switch_name_to_dns_ip[sw]
            if "dns" not in node:
                node["dns"] = []
            for dns in dns_list:
                node["dns"].append(dns)
            # add a default dns server
            node["dns"].append("1.1.1.1")
            # Ensure unicity and ordering, from python 3.7+, because dict is ordered:
            node["dns"] = list(dict.fromkeys(node["dns"]))


def _validate_resources_path(
    resources_path: Path, raise_exception: bool = True
) -> bool:
    # Exists ?
    if not resources_path.exists():
        if raise_exception:
            raise FileNotFoundError(
                f'The provided resources path does not exist: "{resources_path}"'
            )
        return False
    # Directory ?
    if not resources_path.is_dir():
        if raise_exception:
            raise NotADirectoryError(
                f'The provided resources path is not a directory: "{resources_path}"'
            )
        return False
    # Empty ?
    files = list(resources_path.iterdir())
    if len(files) == 0:
        if raise_exception:
            raise OSError(
                f'The provided resources path is an empty directory: "{resources_path}"'
            )
        return False
    return True


def _normalize_simulation_resource_paths(
    topology_resources_paths: Optional[List[Path]] = None,
) -> List[Path]:
    """Normalize simulation resource paths..

    :return: The normalized paths.
    :rtype: :class:`List[Path]`

    :param topology_resources_paths: The path to resources that will be pushed into compatible nodes.
    :type topology_resources_paths: :class:`list`, optional

    """
    if topology_resources_paths is None:
        topology_resources_paths = []

    normalized_paths = []
    for resource in topology_resources_paths:
        normalized_resource: Path = resource.resolve()
        normalized_paths.append(normalized_resource)
    topology_resources_paths = normalized_paths

    return topology_resources_paths


def _normalize_simulation_resources(
    topology_content: Dict[str, Any],
    topology_resources_paths: Optional[List[Path]] = None,
) -> Dict[str, Any]:
    """Create a new simulation model in database based on the provided topology, along with optional resource files.

    :return: A tuple containing the ID of the created simulation, and the new nodes of the simulation.

    :param topology_content: A dict containing the nodes and network topology to create.
    :param topology_resources_paths: The path to resources that will be pushed into compatible node
    """

    if "name" not in topology_content:
        name = "Unnamed topology"
    else:
        name = topology_content["name"]

    if "description" not in topology_content:
        description = "No description"
    else:
        description = topology_content["description"]

    if "nodes" not in topology_content:
        raise Exception(
            "There should be a 'nodes' structure in the YAML configuration file"
        )

    if "links" not in topology_content:
        raise Exception(
            "There should be a 'links' structure in the YAML configuration file"
        )

    required = ["switch", "node", "params"]
    for link in topology_content["links"]:
        for req in required:
            if req not in link:
                raise Exception(
                    f"There should be a '{req}' parameter for every item of 'links' in the YAML configuration file"
                )

    _simu_create_add_implicit_topo_parameters(topology_content)

    simulation_dict = {
        "name": name,
        "description": description,
        "network": topology_content,
    }

    # Normalize the resources paths
    topology_resources_paths = _normalize_simulation_resource_paths(
        topology_resources_paths
    )

    # Verify that we do not have the same resources path in the list
    if len(set(topology_resources_paths)) != len(topology_resources_paths):
        raise Exception("Identical resources paths have been given")

    for resource in topology_resources_paths:
        # Validate resources path
        _validate_resources_path(resource)  # raise an exception if invalid

    simulation_dict["resources_paths"] = topology_resources_paths  # type: ignore

    return simulation_dict


# -------------------------------------------------------------------------- #
# API helpers
# -------------------------------------------------------------------------- #


###
# Simulation helpers
###


def create_simulation(
    topology_content: Dict[str, Any],
    topology_resources_paths: Optional[List[Path]] = None,
    allocation_strategy: Optional[str] = None,
) -> Tuple[int, List[str]]:
    """Create a new simulation model in database based on the provided topology, along with optional resource files.

    :return: A tuple containing the ID of the created simulation, and the new nodes of the simulation.

    :param topology_content: A dict containing the nodes and network topology to create.
    :param topology_resources_paths: The path to resources that will be pushed into compatible nodes.
    :param allocation_strategy: Name of the allocation strategy to use to allocate nodes to compute servers.

    """

    # Callback on input
    if cbk_create_simulation_before:
        (
            topology_content,
            topology_resources_paths,
            allocation_strategy,
        ) = cbk_create_simulation_before(
            topology_content, topology_resources_paths, allocation_strategy
        )

    simulation_dict = _normalize_simulation_resources(
        topology_content=topology_content,
        topology_resources_paths=topology_resources_paths,
    )

    id_simulation, new_nodes = _create_or_extend_simulation(
        simulation_dict=simulation_dict, allocation_strategy=allocation_strategy
    )

    # Callback on output
    if cbk_create_simulation_after:
        id_simulation, new_nodes = cbk_create_simulation_after(id_simulation, new_nodes)

    return id_simulation, new_nodes


def extend_simulation(
    id_simulation: int,
    topology_content: Dict[str, Any],
    topology_resources_paths: Optional[List[Path]] = None,
    allocation_strategy: Optional[str] = None,
) -> Tuple[int, List[str]]:
    """Extend an existing simulation model in database based on the provided topology, along with optional resource files.

    :return: A tuple containing the ID of the updated simulation, and the new node names of the simulation.

    :param id_simulation: The simulation ID, when extending an existing simulation with new nodes and links.
    :param topology_content: A dict containing the nodes and network topology to create.
    :param topology_resources_paths: The path to resources that will be pushed into compatible nodes.
    :param allocation_strategy: Name of the allocation strategy to use to allocate nodes to compute servers.


    """

    simulation_dict = _normalize_simulation_resources(
        topology_content=topology_content,
        topology_resources_paths=topology_resources_paths,
    )

    return _create_or_extend_simulation(
        simulation_dict=simulation_dict,
        id_simulation=id_simulation,
        allocation_strategy=allocation_strategy,
    )


def create_simulation_from_topology(
    topology_file: Path,
    topology_resources_paths: Optional[List[Path]] = None,
    allocation_strategy: Optional[str] = None,
) -> Tuple[int, List[str]]:
    """Create a new simulation model in database based on the provided topology file, along with optional resource files.

    :return: A tuple containing the ID of the created simulation, and the new nodes of the simulation.

    :param topology_file: The path to a topology file containing the nodes and network topology to create.
    :param topology_resources_paths: The path to resources that will be pushed into compatible nodes.
    :param allocation_strategy: Name of the allocation strategy to use to allocate nodes to compute servers.

    >>> from cr_api_client import core_api
    >>> core_api.reset()
    'Compute infrastructure successfully reset'
    >>> core_api.create_simulation_from_topology("data/topologies/topology-1-client.yaml")
    (1, ['CLIENT1', 'Router1', 'Switch1'])

    """

    if topology_resources_paths is None:
        topology_resources_paths = []

    # Create a new simulation model in database based on the provided topology file path."""
    if topology_file is None:
        raise Exception("An topology file is required")

    # Validate YAML configuration file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML configuration file
    yaml_content = _read_yaml_topology_file(topology_file)

    # Parse YAML configuration
    # We use ruamel.yaml because it keeps anchors and
    # aliases in memory. It is very convenient when the simulation
    # is stored/fetched (references are kept!)
    loader = YAML(typ="rt")
    topology_content = loader.load(yaml_content)

    _validate_topology_requirements(topology_content, topology_resources_paths)

    # Add a default resources directory if it exists.
    # If the topology is "path/to/topo.yaml", the default resources directory is "path/to/resources".
    topology_resources_paths = _normalize_simulation_resource_paths(
        topology_resources_paths
    )
    default_resources_path = os.path.join(topology_file.parent, "resources")
    default_resources_path = os.path.normpath(default_resources_path)
    if _validate_resources_path(Path(default_resources_path), False):
        if default_resources_path not in topology_resources_paths:
            topology_resources_paths.append(Path(default_resources_path))

    return create_simulation(
        topology_content=topology_content,
        topology_resources_paths=topology_resources_paths,
        allocation_strategy=allocation_strategy,
    )


def extend_simulation_from_topology(
    id_simulation: int,
    topology_file: Path,
    topology_resources_paths: Optional[List[Path]] = None,
    allocation_strategy: Optional[str] = None,
) -> Tuple[int, List[str]]:
    """Extend an existing simulation model in database based on the provided topology file, along with optional resource files.

    :return: A tuple containing the ID of the created simulation, and the new nodes of the simulation.

    :param id_simulation: The simulation ID, when extending an existing simulation with new nodes and links.
    :param topology_file: The path to a topology file containing the nodes and network topology to add.
    :param topology_resources_paths: The path to resources that will be pushed into compatible nodes.
    :param allocation_strategy: Name of the allocation strategy to use to allocate nodes to compute servers.

    """
    if topology_resources_paths is None:
        topology_resources_paths = []

    # Create a new simulation model in database based on the provided topology file path."""
    if topology_file is None:
        raise Exception("An topology file is required")

    # Validate YAML configuration file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML configuration file
    yaml_content = _read_yaml_topology_file(topology_file)

    # Parse YAML configuration
    # We use ruamel.yaml because it keeps anchors and
    # aliases in memory. It is very convenient when the simulation
    # is stored/fetched (references are kept!)
    loader = YAML(typ="rt")
    topology_content = loader.load(yaml_content)

    # Add a default resources directory if it exists.
    # If the topology is "path/to/topo.yaml", the default resources directory is "path/to/resources".
    default_resources_path = os.path.join(topology_file.parent, "resources")
    default_resources_path = os.path.normpath(default_resources_path)
    if _validate_resources_path(Path(default_resources_path), False):
        if default_resources_path not in topology_resources_paths:
            topology_resources_paths.append(Path(default_resources_path))

    return extend_simulation(
        topology_content=topology_content,
        topology_resources_paths=topology_resources_paths,
        allocation_strategy=allocation_strategy,
        id_simulation=id_simulation,
    )


def create_simulation_from_basebox(
    basebox_id: str,
    add_internet: bool = False,
    add_host: bool = False,
    allocation_strategy: Optional[str] = None,
) -> Tuple[int, List[str]]:
    """Create a new simulation model in database based on the provided basebox id, with
    optional internet and/or host connectivity.

    :return: A tuple containing the ID of the created simulation, and the new nodes of the simulation.

    :param basebox_id: The basebox ID to add to the simulation.
    :param add_internet: Add connectivity to internet (not active by default).
    :param add_host: Add connectivity to host system (not active by default).
    :param allocation_strategy: Name of the allocation strategy to use to allocate nodes to compute servers.

    """

    if basebox_id is None:
        raise Exception("A basebox ID is required")

    # Create an topology with the provided basebox ID
    try:
        basebox = fetch_basebox(basebox_id)
    except Exception:
        raise Exception(
            f"Cannot find basebox in database from basebox ID '{basebox_id}'"
        )

    node_name = "basebox"
    role = basebox["role"]
    nb_proc = basebox["nb_proc"]
    memory_size = basebox["memory_size"]

    yaml_content = f"""---
name: "{basebox_id}"
nodes:

  - &switch
    type: switch
    name: "switch"

  - &router
    type: router
    name: "router"

  - &client
    type: virtual_machine
    name: "{node_name}"
    basebox_id: "{basebox_id}"
    nb_proc: {nb_proc}
    memory_size: {memory_size}
    roles: ["{role}"]
"""

    if add_host:
        yaml_content += """
  - &host_machine
    type: host_machine
    name: "host"
"""

    if add_internet:
        # add default route to gateway, a gateway and a switch to plug the gateway and the router
        yaml_content += """
  - &SwitchMonitoring
    type: switch
    name: "SwitchMonitoring"

  - &SwitchGateway
    type: switch
    name: "SwitchGateway"

  # Public IP addresses will be routed through the physical gateway, if activated.
  # It is expected that the physical gateway will have the IP address 192.168.251.2
  # All private IP addresses will be routed trough the internal router.
  - &RouterGateway
    type: router
    name: "RouterGateway"
    routes:
    - "0.0.0.0/0 -> 192.168.251.2"
    - "192.168.0.0/16 -> 192.168.250.254"
    - "172.16.0.0/12 -> 192.168.250.254"
    - "10.0.0.0/8 -> 192.168.250.254"
"""

    yaml_content += """
links:

  - switch: *switch
    node: *router
    params:
      ip: "192.168.2.1/24"
      dhcp_nameserver: "8.8.8.8"

  - switch: *switch
    node: *client
    params:
      ip: "192.168.2.2/24"
"""

    if add_host:
        yaml_content += """
  - switch: *switch
    node: *host_machine
    params:
      ip: "192.168.2.3/24"
"""

    if add_internet:
        yaml_content += """
  - switch: *SwitchMonitoring
    node: *router
    params:
      ip: "192.168.250.254/24"
      dhcp_router: "192.168.250.253"
      dhcp_nameserver: "8.8.8.8"

  - switch: *SwitchMonitoring
    node: *RouterGateway
    params:
      ip: "192.168.250.253/24"
      dhcp: false
      dhcp_nameserver: "8.8.8.8"

  - switch: *SwitchGateway
    node: *RouterGateway
    params:
      ip: "192.168.251.1/24"
"""

    loader = YAML(typ="rt")
    topology_content = loader.load(yaml_content)

    return create_simulation(
        topology_content=topology_content,
        allocation_strategy=allocation_strategy,
    )


def extend_simulation_from_basebox(
    id_simulation: int,
    basebox_id: str,
    switch_name: str,
    allocation_strategy: Optional[str] = None,
) -> Tuple[int, List[str]]:
    """Extend an existing simulation model in database based on the
    provided basebox id, and plug the new node of the specifed switch.

    :return: A tuple containing the ID of the updated simulation, and the new nodes of the simulation.

    :param id_simulation: The simulation ID, when extending an existing simulation with new nodes and links.
    :param basebox_id: The basebox ID to add to the simulation.
    :param switch_name: The switch name on which to connect the new basebox.
    :param allocation_strategy: Name of the allocation strategy to use to allocate nodes to compute servers.

    """

    if basebox_id is None:
        raise Exception("A basebox ID is required")

    # Create an topology with the provided basebox ID
    try:
        basebox = fetch_basebox(basebox_id)
    except Exception:
        raise Exception(
            f"Cannot find basebox in database from basebox ID '{basebox_id}'"
        )

    node_name = _get_random_string(10)
    role = basebox["role"]
    nb_proc = basebox["nb_proc"]
    memory_size = basebox["memory_size"]

    topology_content = {
        "nodes": [
            {
                "type": "virtual_machine",
                "name": node_name,
                "basebox_id": basebox_id,
                "nb_proc": nb_proc,
                "memory_size": memory_size,
                "roles": [role],
            }
        ],
        "links": [
            {
                "switch": {"type": "switch", "name": switch_name},
                "node": {
                    "type": "virtual_machine",
                    "name": node_name,
                },
                "params": {},  # Dynamic IP address
            }
        ],
    }

    return extend_simulation(
        topology_content=topology_content,
        allocation_strategy=allocation_strategy,
        id_simulation=id_simulation,
    )


###
# Topology helpers
###


def topology_file_add_websites(
    topology_file: Path, websites: List[str], switch_name: str
) -> str:
    """Add docker websites node to a given topology, and return the updated topology.

    :return: The updated topology content as a string.

    :param topology_file: The path to a topology file.
    :param websites: The website names to add to the topology.
    :param switch_name: The switch on which to connect the docker website nodes.

    """

    # Validate YAML topology file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML topology file
    topology_yaml = _read_yaml_topology_file(topology_file)

    # Update topology with the API
    topology_yaml = topology_add_websites(topology_yaml, websites, switch_name)

    return topology_yaml


def topology_file_add_dga(
    topology_file: Path,
    algorithm: str,
    switch_name: str,
    number: int,
    resources_dir: str,
) -> Tuple[str, List[str]]:
    """Add docker empty websites node with DGA domains to a given topology, and return the updated topology.

    :return: A new topology content, along with the list of added domains.

    :param topology_file: The path to a topology file.
    :param algorithm: The algorithm used to generate the new DGA domains.
    :param switch_name: The switch on which to connect the docker website nodes.
    :param number: The number of DGA domains to add.
    :param resources_dir: The path to resources that will be pushed into the new docker nodes.

    """

    # Validate

    # Validate YAML topology file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML topology file
    topology_yaml = _read_yaml_topology_file(topology_file)

    # Update topology with the API
    (topology_yaml, domains) = topology_add_dga(
        topology_yaml, algorithm, switch_name, number, resources_dir
    )

    return topology_yaml, domains


def topology_file_add_dns_server(
    topology_file: Path,
    switch_name: str,
    resources_dir: str,
) -> Tuple[str, str]:
    """Add a DNS server to a YAML topology.

    :return: The updated topology content and the content of the DNS configuration file.

    :param topology_file: The path to a topology file.
    :param switch_name: The switch on which to connect the docker DNS server node.
    :param resources_dir: The path to resources that will be pushed into the new docker node.

    """

    # Validate

    # Validate YAML topology file
    _validate_yaml_topology_file(topology_file)

    # Open and read YAML topology file
    topology_yaml = _read_yaml_topology_file(topology_file)

    # Update topology with the API
    (topology_yaml, dns_conf_content) = topology_add_dns_server(
        topology_yaml, switch_name, resources_dir
    )

    return topology_yaml, dns_conf_content


###
# Basebox helpers
###


def _baseboxes_task_raise_error_msg(result: dict) -> None:
    """
    Raise an error message if a task (eg the basebox verification) failed

    :param result: the result of the task

    """
    if "error_msg" in result:
        error_msg = result["error_msg"]
        raise Exception(error_msg)
    else:
        raise Exception(f"No 'error_msg' key in result: {result}")


def _baseboxes_verification_wait_until_complete(
    task_id: str, log_suffix: Optional[str] = None, timeout: float = 3600.0
) -> dict:
    """
    Wait until the verification task representing by its id is completed

    :param task_id: the task id
    :param log_suffix: what to insert into the log
    :param timeout: the timeout to stop the task
    :return: the result of the basebox verification

    """

    start_time = time.time()

    finished = False
    while not (finished or (time.time() - start_time) > timeout):

        if cbk_check_stopped is not None:
            if cbk_check_stopped() is True:
                logger.info("   [+]    Current process was asked to stop")
                raise ScenarioExecutionStopped

        time.sleep(2)

        current_time = time.time()
        elapsed = int(current_time - start_time)
        if log_suffix is not None:
            logger.info(
                f"   [+] Currently verifying {log_suffix} for {elapsed} seconds (timeout at {timeout} seconds)"
            )
        else:
            logger.info(
                f"   [+] Currently running the verification for {elapsed} seconds"
            )

        result = _post("/basebox/status_verify", data={"task_id": task_id})
        result.raise_for_status()
        result_json = result.json()

        if "status" not in result_json:
            verify_basebox_stop(task_id)
            raise Exception(
                "Error during verification operation: unexpected response format from IT Simulation API on /baseboxes/status_verify"
            )

        if result_json["status"] == "FINISHED":
            finished = True

    if not finished:
        error_msg = f"[-] Unable to terminate operation before timeout of {timeout} seconds. Stopping operation."
        result = verify_basebox_stop(task_id)
        stopped = result_json["status"] == "STOPPED"
        if stopped:
            result_json["result"] = dict()
            result_json["success"] = False
            result_json["error_msg"] = error_msg
            return result_json
        else:
            raise Exception("Unable to stop verification task after timeout")

    result = _post("/basebox/result_verify", data={"task_id": task_id})
    result.raise_for_status()
    result_json = result.json()

    success = result_json["status"] == "FINISHED" and result_json["success"] is True

    if not success:
        error_msg = result_json["error_msg"]
        logger.error(
            f"[-] The basebox verification was executed with error(s): {error_msg}"
        )

    return result_json


def _wait_for_the_operation_to_start(task_id: str) -> bool:
    """
    Wait for a task to start
    :param task_id: the task id
    :return: Is the task running
    """

    running = False
    timeout = 10
    start_time = time.time()
    while not (running or (time.time() - start_time) > timeout):

        if cbk_check_stopped is not None:
            if cbk_check_stopped() is True:
                logger.info("   [+]    Current process was asked to stop")
                raise ScenarioExecutionStopped

        result = _post("/basebox/status_verify", data={"task_id": task_id})
        result.raise_for_status()
        result_json = result.json()
        running = result_json["status"] == "RUNNING"
        time.sleep(1)

    if not running:
        logger.error(
            f"[-] Unable to start operation before timeout of {timeout} seconds"
        )

    return running


def _handle_wait_basebox_verify(
    wait: bool, task_id: str, log_suffix: str, timeout: int = 3600
) -> Any:
    """

    :param wait: Wait for the operation to be completed in backend
    :param task_id: the task id
    :param log_suffix: the string to be inserted in the log
    :param timeout: the time limit before stopping the task
    :return: the result of the verification
    """
    success = True

    if wait:
        # Wait for the operation to be completed in backend

        result = _baseboxes_verification_wait_until_complete(
            task_id=task_id, log_suffix=log_suffix, timeout=timeout
        )

        finished = "status" in result and result["status"] == "FINISHED"
        success = finished

        if success:
            if "result" in result:
                return result

        if not success:
            _baseboxes_task_raise_error_msg(result)

    else:
        # wait for the operation to start
        running = _wait_for_the_operation_to_start(task_id)

        if not running:
            success = False

    return success


# -------------------------------------------------------------------------- #
# Core API
# -------------------------------------------------------------------------- #


def get_version() -> str:
    """Return IT Simulation API version.

    :return: Return version.

    """
    result = _get("/simulation/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve Core API version")

    return result.json()


def reset(delete_compute_servers: bool = False, keep_db: bool = False) -> Any:
    """
    Reset the IT Simulation infrastructure

    This has the following effect:
    - clean the database and re-populate it with static info (baseboxes, roles...)
    - by defaut, the table of compute servers is kept, but `delete_compute_servers=True` changes that behavior
    - reset the simulation manager
    - reset the compute servers (stop VMs and dockers, reset networks, ...)

    :return: A message telling how the operation executed.

    :param delete_compute_servers: A boolean telling if we need to delete known compute servers.

    """
    params = {"keep_db": keep_db}
    if delete_compute_servers:
        params.update({"delete_compute_servers_from_db": delete_compute_servers})

    result = _delete("/simulation/compute_infrastructure_reset", params=params)

    if result.status_code != 200:
        _handle_error(result, "Cannot reset simulation infrastructure")

    return result.json()


def _create_or_extend_simulation(
    simulation_dict: dict,
    id_simulation: Optional[int] = None,
    allocation_strategy: Optional[str] = None,
) -> Tuple[int, List[str]]:
    """Create a simulation, or extend an existing simulation with new
    nodes and links, and return a simulation ID."""

    # Get the paths if some have been provided
    resources_paths = simulation_dict.pop("resources_paths", [])

    data = json.dumps(simulation_dict)

    # Creation of a folder containing all the resources, this folder will then be zipped
    with TemporaryDirectory(prefix="cyber_range_cr_core_resources") as main_resources:
        # copy all resources in the main temporary folder
        for resource in resources_paths:
            if resource.is_dir():
                copytree_path(resource, Path(main_resources) / resource.name)
            elif resource.is_file():
                with resource.open("rb") as src_file:
                    with (Path(main_resources) / resource.name).open("wb") as dst_file:
                        dst_file.write(src_file.read())
            else:
                raise Exception(f"Cannot copy {resource}")

        # We have to create a new temporary folder to host the archive
        with TemporaryDirectory(prefix="cyber_range_cr_core_archive") as temp_dir:
            if resources_paths:
                zip_file_name = _zip_resources(Path(main_resources), Path(temp_dir))
                resources_file = open(zip_file_name, "rb")
                files = {"resources_file": resources_file, "data": data}
            else:
                resources_file = None
                files = {"data": data}

            try:
                if id_simulation is None:
                    # Create new simulation
                    result = _post(
                        "/simulation/",
                        files=files,
                    )
                else:
                    # Extend an existing simulation
                    result = _post(
                        f"/simulation/{id_simulation}/extend",
                        files=files,
                    )
            finally:
                if resources_file:
                    resources_file.close()

    if not main_resources:
        if id_simulation is None:
            # Create new simulation
            result = _post(
                "/simulation/",
                data=data,
                headers={"Content-Type": "application/json"},
            )
        else:
            # Extend an existing simulation
            result = _post(
                f"/simulation/{id_simulation}/extend",
                data=data,
                headers={"Content-Type": "application/json"},
            )

    if result.status_code != 200:
        _handle_error(result, "Cannot post simulation information to core API")

    new_id_simulation = result.json()["id"]
    new_nodes = result.json()["new_nodes"]
    logger.info(f"[+] New nodes for simulation id '{new_id_simulation}': '{new_nodes}'")

    # Prepare disk resources
    post_data = {"nodes": new_nodes}
    _simulation_execute_operation(
        method="post",
        operation="prepare",
        id_simulation=new_id_simulation,
        expected_current_simulation_status="PREPARING",
        optional_param1=allocation_strategy,
        post_data=post_data,
    )

    # TODO: Check that the docker volumes that will be mounted by simu_run are present on the filesystem
    # for ...: _simu_create_validate_resources_exists()

    return (new_id_simulation, new_nodes)


def simulation_status(id_simulation: int) -> str:
    """Retrieve the simulation status.

    :return: The status of the simulation.

    :param id_simulation: The simulation ID.

    """
    result = _get(f"/simulation/{id_simulation}/status")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from IT Simulation API")

    return result.json()


def fetch_simulation(id_simulation: int) -> dict:
    """Retrieve a specific simulation given a simulation id.

    :return: A dict containing data related to the targeted simulation.

    :param id_simulation: The simulation ID.

    """
    result = _get(f"/simulation/{id_simulation}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from IT Simulation API")

    simulation_dict = result.json()

    return simulation_dict


def fetch_simulations() -> List[Any]:
    """Get the list of simulations, including the currently running simualtion, along with
    information on nodes.

    :return: The list of simulations.

    """
    result = _get("/simulation/")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation info from IT Simulation API")

    simulation_list = result.json()
    return simulation_list


def delete_simulation(id_simulation: int) -> Any:
    """Delete a simulation in database.

    :return: A message telling how the operation executed.

    :param id_simulation: The simulation ID.

    """

    # Destroy simulation if it is running
    if simulation_status(id_simulation) == "RUNNING":
        nodes: List[str] = []
        post_data = {"nodes": nodes}

        _simulation_execute_operation(
            "post", "destroy", id_simulation, "STOPPING", post_data=post_data
        )

    _simulation_execute_operation("get", "delete_snapshots", id_simulation, "STOPPING")

    # Delete simulation nodes
    delete_nodes(id_simulation)

    # Delete simulation
    result = _delete(f"/simulation/{id_simulation}")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete simulation from IT Simulation API")

    return result.json()


def node_status(id_node: int) -> str:
    """Retrieve node status.

    :return: The status of the node.

    :param id_node: The node ID.

    """

    result = _get(f"/node/{id_node}/status")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node info from IT Simulation API")

    return result.json()


def stop_node_by_name(id_simulation: int, node_name: str) -> None:
    """Stop a node if it is running.

    :param id_simulation: The simulation ID.
    :param node_name: The node name to stop.

    """

    # Retrieve id_node
    node = fetch_node_by_name(id_simulation, node_name)
    id_node = node["id"]

    # Delete node
    stop_node(id_simulation, id_node)


def stop_node(id_simulation: int, id_node: int) -> None:
    """Stop a node if it is running.

    :param id_simulation: The simulation ID.
    :param id_node: The node ID.

    """

    # Retrieve node according to its name
    node = fetch_node(id_node)

    # Set node names to delete
    nodes_to_delete = [node["name"]]
    post_data = {"nodes": nodes_to_delete}

    # Stop node if it is running
    if node_status(id_node) == "RUNNING":
        _simulation_execute_operation(
            "post",
            "halt",
            id_simulation,
            "STOPPING",
            post_data=post_data,
        )


def update_simulation(id_simulation: int, simulation_dict: dict) -> Any:
    """Update simulation information information given a simulation id
    and a dict containing simulation info.

    :return: A message telling how the operation executed.

    :param id_simulation: The simulation ID.
    :param simulation_dict: The dict containing the entries to update.

    """
    data = json.dumps(simulation_dict)
    result = _put(
        f"/simulation/{id_simulation}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot update simulation information")

    return result.json()


def fetch_simulation_topology_graph(id_simulation: int) -> Any:
    """Return the topology graph of a simulation. This graph can be
    used for rendering with viz.js.

    :return: The simulation topology graph.

    :param id_simulation: The simulation ID.

    """
    result = _get(f"/simulation/{id_simulation}/topology_graph")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation topology info")

    return result.json()


def fetch_simulation_topology_yaml(id_simulation: int) -> Any:
    """Return the YAML topology content of a simulation.

    :return: The YAML simulation topology.

    :param id_simulation: The simulation ID.

    """
    result = _get(f"/simulation/{id_simulation}/topology_yaml")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation topology info")

    return result.json()


def fetch_simulation_topology(id_simulation: int) -> Any:
    """Return the topology typed object of a simulation.

    :return: The typed topology.

    :param id_simulation: The simulation ID.

    """
    result = _get(f"/simulation/{id_simulation}/topology")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation topology info")
    else:
        topology_data = result.json()
        topology = Topology(**topology_data)

    return topology


def fetch_assets(id_simulation: int) -> Any:
    """Return the list of the assets of a given simulation. It corresponds
    to the list of the nodes with some additional information.

    :return: The simulation assets.

    :param id_simulation: The simulation ID.

    """
    result = _get(f"/simulation/{id_simulation}/assets")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve assets from core API")

    return result.json()


def fetch_switch_by_network_id(id_simulation: int, network_id: str) -> Any:
    """Return a switch given its network_id.

    :return: The switch dict.

    :param id_simulation: The simulation ID.
    :param network_id: The network ID.

    """

    result = _get(f"/simulation/{id_simulation}/switch/{network_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation switch from core API")

    return result.json()


def fetch_node(node_id: int) -> Any:
    """Return a node given its ID.

    :return: The node dict.

    :param node_id: The node ID.

    """
    result = _get(f"/node/{node_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node from IT Simulation API")

    return result.json()


def fetch_node_by_name(id_simulation: int, node_name: str) -> Any:
    """Return a node given its name.

    :return: The node dict.

    :param id_simulation: The simulation ID.
    :param node_name: The node name to fetch.

    """

    result = _get(f"/simulation/{id_simulation}/node/{node_name}")

    if result.status_code != 200:
        _handle_error(
            result, "Cannot retrieve node based on its name from IT Simulation API"
        )

    return result.json()


def fetch_nodes_by_roles(id_simulation: int) -> Any:
    """Retrieve nodes content by roles.

    :return: Return a dict wkere keys are roles (such as 'ad', 'file_server', 'client', ...) and values are nodes.

    :param id_simulation: The simulation ID.

    """
    result = _get(f"/simulation/{id_simulation}/nodes_by_roles")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve nodes")

    roles_dict = result.json()
    return roles_dict


def delete_node_by_name(id_simulation: int, node_name: str) -> None:
    """

    :param id_simulation: The simulation ID.
    :param node_name: The node name to delete.

    """
    # Retrieve id_node
    node = fetch_node_by_name(id_simulation, node_name)
    id_node = node["id"]

    # Delete node
    delete_node(id_node)


def delete_node(id_node: int) -> Any:
    """Delete node from database given its ID.

    :return: A message telling how the operation executed.

    :param id_node: The node ID.

    """

    # Fetch virtual node network interfaces
    network_interfaces = fetch_node_network_interfaces(id_node)

    # Delete each network interfaces
    for network_interface in network_interfaces:
        delete_network_interface(network_interface["id"])

    # Delete node
    result = _delete(f"/node/{id_node}")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete node")

    return result.json()


def fetch_nodes(id_simulation: int) -> Any:
    """Return simulation nodes dict given
    a simulation ID, where keys are node names.

    :return: The node list.

    :param id_simulation: The simulation ID.

    """
    result = _get(f"/simulation/{id_simulation}/node")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve nodes from IT Simulation API")

    return result.json()


def fetch_virtual_machines(id_simulation: int) -> List[dict]:
    """Return simulation virtual machines dict given a simulation ID,
    where keys are virtual machine names.

    :return: The list of virtual machines.

    :param id_simulation: The simulation ID.

    """
    results = fetch_nodes(id_simulation)

    vm_only = filter(lambda m: m["type"] == "virtual_machine", results)
    return list(vm_only)


def delete_nodes(id_simulation: int) -> str:
    """Delete simulation nodes given a simulation ID.

    :return: A message telling how the operation executed.

    :param id_simulation: The simulation ID.

    """

    # Fetch simulation nodes
    result = _get(f"/simulation/{id_simulation}/node")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete simulation nodes")

    nodes_list = result.json()

    # Delete each node
    for node in nodes_list:
        delete_node(node["id"])

    result_json = "{}"
    return result_json


def update_node(node_id: int, node_dict: dict) -> Any:
    """Update node information given a node id and a dict containing
    node data.

    :return: A message telling how the operation executed.

    :param node_id: The node ID.
    :param node_dict: The dict containing the entries to update.

    """
    data = json.dumps(node_dict)
    result = _put(
        f"/node/{node_id}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot update node information with core API")

    return result.json()


def get_node_default_gateway(id_node: int) -> Optional[str]:
    """Retrieve node default gateway, which can either be an IP address
    of the form xx.xx.xx.xx or None if no gateway is set.

    :return: The node default gateway.

    :param id_node: The node ID.

    """

    result = _get(f"/node/{id_node}/default_gateway")

    if result.status_code != 200:
        _handle_error(
            result, "Cannot retrieve node default gateway from IT Simulation API"
        )

    default_gateway = result.json()

    return default_gateway


def get_node_statistics_by_id(id_node: int) -> Any:
    """
    Return aggregated statistics from CPU, memory, block devices and network interfaces.
    Note: you can get the node IDs using the simu_status command (or the fetch_simulations() function).

    :return: The node statistics.

    :param id_node: The node ID.

    """
    result = _get(f"/node/{id_node}/stats")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node statistics")

    return result.json()


def node_logs(id_node: int) -> Any:
    """
    Retrieve logs from specified node (only work for Docker node).

    :return: The logs as a string.

    :param id_node: The node ID.

    """

    # Check that the target node is a docker node (node_exec only
    # works for Docker node for now)
    node = fetch_node(id_node)
    if node["type"] != "docker":
        raise Exception("Cannot execute command for nodes different from docker nodes")

    result = _get(f"/node/{id_node}/logs")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve logs from IT Simulation API")

    logs = result.json()

    return logs


def node_exec(id_node: int, command: str, wait: bool = True) -> Any:
    """
    Execute a command on specified node (only work for Docker node).

    :return: Return either a tuple (exit_code: int, stdout: str, stderr: str) of the executed command, or None if wait is false

    :param id_node: The node ID.
    :param command: The command to execute on the node.
    :param wait:  Wait until the command finishes, or return directly

    """

    # Check that the target node is a docker node (node_exec only
    # works for Docker node for now)
    node = fetch_node(id_node)
    if node["type"] != "docker":
        raise Exception("Cannot execute command for nodes different from docker nodes")

    status_key = "status"
    exit_code = "exit_code"
    stdout = "stdout"
    stderr = "stderr"

    post_data = {"command": command}
    data = json.dumps(post_data)
    result = _post(
        f"/node/{id_node}/exec", data=data, headers={"Content-Type": "application/json"}
    )

    if (
        result.status_code != 200
        or status_key not in result.json()
        or result.json()[status_key] != "STARTED"
    ):
        _handle_error(result, "Cannot initiate exec command from IT Simulation API")

    logger.info(f"[+] Executing command '{command}' for node '{id_node}'...")

    if not wait:
        return
    else:
        # Wait for the operation to be completed in backend
        # Note : loop inspired from _simulation_execute_operation
        while True:

            if cbk_check_stopped is not None:
                if cbk_check_stopped() is True:
                    logger.info("   [+]    Current process was asked to stop")
                    raise ScenarioExecutionStopped

            # Sleep before next iteration
            time.sleep(2)

            # Fetch the current status of the memdump
            result = _get(f"/node/{id_node}/exec_status")

            if result.status_code != 200:
                _handle_error(
                    result, "Cannot get status of exec command from IT Simulation API"
                )

            result_json = result.json()
            if not (
                all(k in result_json for k in (exit_code, stdout, stderr, status_key))
            ):
                raise Exception(
                    f"Contents of exec command status update is not in the expected format (attributes '{exit_code}', '{stdout}', '{stderr}' and '{status_key}' expected)"
                )

            # Log info on progression
            if result_json[status_key] == "STARTED":
                logger.info(
                    f"  [+] Currently waiting for exec command for node '{id_node}') to start..."
                )
            elif result_json[status_key] == "PROGRESS":
                logger.info(
                    f"  [+] Currently performing exec command for node '{id_node}')..."
                )
            elif result_json[status_key] == "SUCCESS":
                break
            else:
                raise Exception(
                    "Error during exec command for node {} operation: '{}'".format(
                        id_node, result_json[status_key]
                    )
                )

        logger.info("[+] Node exec command finished")

        return (result_json[exit_code], result_json[stdout], result_json[stderr])


def node_exec_status(id_node: int) -> Any:
    """
    Get the status of a command in the process of being executed on a node (only work for Docker node).

    :return: Return a tuple (status: str, exit_code: int, stdout: str, stderr: str) of the executed command, with status being one of "STARTED", "PROGRESS" or "SUCCESS", and the exit_code having value *1 while status is "RUNNING"

    :param id_node: The node ID.
    """

    # Check that the target node is a docker node (node_exec only
    # works for Docker node for now)
    node = fetch_node(id_node)
    if node["type"] != "docker":
        raise Exception("Cannot execute command for nodes different from docker nodes")

    status_key = "status"
    exit_code = "exit_code"
    stdout = "stdout"
    stderr = "stderr"

    # Fetch the current status of the memdump
    result = _get(f"/node/{id_node}/exec_status")

    if result.status_code != 200:
        _handle_error(
            result, "Cannot get status of exec command from IT Simulation API"
        )

    result_json = result.json()
    if not (all(k in result_json for k in (exit_code, stdout, stderr, status_key))):
        raise Exception(
            f"Contents of exec command status update is not in the expected format (attributes '{exit_code}', '{stdout}', '{stderr}' and '{status_key}' expected)"
        )

    if result_json[status_key] not in ["STARTED", "PROGRESS", "SUCCESS"]:
        raise Exception(
            "Error during exec command for node {} operation: '{}'".format(
                id_node, result_json[status_key]
            )
        )

    return (
        result_json[status_key],
        result_json[exit_code],
        result_json[stdout],
        result_json[stderr],
    )


def node_memorydump(id_node: int) -> Any:
    """
    Return RAM dump of a node in a running simulation
    Note: you can get the node IDs using the simu_status command (or the fetch_simulations() function).

    :return: A message telling how the operation executed.

    :param id_node: The node ID.

    """

    ## TODO: implement this operation in API backend
    raise NotImplementedError()

    # file_path_key = "file_path"
    # file_size_key = "file_size"
    # status_key = "status"

    # result = _get(f"/node/{id_node}/memorydump")

    # if (
    #     result.status_code != 200
    #     or status_key not in result.json()
    #     or result.json()[status_key] != "STARTED"
    # ):
    #     _handle_error(result, "Cannot initiate node memory dump from core API")

    # logger.info("[+] Initialized memory dump of node '{}'...".format(id_node))

    # # Wait for the operation to be completed in backend
    # # Note : loop inspired from _simulation_execute_operation
    # while True:
    #     # Sleep before next iteration
    #     time.sleep(2)

    #     # Fetch the current status of the memdump
    #     result = _get(f"/node/{id_node}/memorydump_status")

    #     if result.status_code != 200:
    #         _handle_error(result, "Cannot get status of node memory dump from core API")

    #     result_json = result.json()
    #     print(result_json)
    #     if not (
    #         all(k in result_json for k in (file_path_key, file_size_key, status_key))
    #     ):
    #         raise Exception(
    #             f"Contents of memory dump status update is not in the expected format (attributes '{file_path_key}', '{file_size_key}' and '{status_key}' expected)"
    #         )

    #     # Log info on progression
    #     if result_json[status_key] == "STARTED":
    #         pass
    #     elif result_json[status_key] == "PROGRESS":
    #         logger.info(
    #             "  [+] Currently performing memory dump of node '{}' (current dump file size is {})...".format(
    #                 id_node, naturalsize(result_json[file_size_key], binary=True)
    #             )
    #         )
    #     elif result_json[status_key] == "SUCCESS":
    #         break
    #     else:
    #         raise Exception(
    #             "Error during memory dump of node {} operation: '{}'".format(
    #                 id_node, result_json[status_key]
    #             )
    #         )

    # logger.info(
    #     "[+] Node memory dump (raw dump with libvirt) obtained, and placed in file {} ({}) on the server.".format(
    #         result_json[file_path_key],
    #         naturalsize(result_json[file_size_key], binary=True),
    #     )
    # )

    # return result_json[file_path_key], result_json[file_size_key]


def node_create_dnat_rule(node_id: int, exposed_port: int) -> int:
    """
    Create DNAT iptables rule to redirect exposed port from compute server instance to the node IP:port.

    Params:
    - **node_id** (int): id of the node
    - **exposed_port** (int): exposed port from the targeted node

    Returns the redirection port (i.e. the port that will be open on the compute server host, in order to redirect to the node).

    """

    # Check that the target node is a docker or virtual_machine node
    node = fetch_node(node_id)
    if node["type"] not in ["docker", "virtual_machine"]:
        raise Exception(
            "Cannot create DNAT rule for nodes different from docker or virtual_machine nodes"
        )

    result = _get(f"/node/{node_id}/create_dnat_rule/{exposed_port}")

    if result.status_code != 200:
        _handle_error(result, "Cannot create DNAT rule from IT Simulation API")

    redirection_port = result.json()

    return redirection_port


def fetch_node_network_interfaces(id_node: int) -> Any:
    """Return network interfaces list given a node ID.

    :return: The list of network interfaces.

    :param id_node: The node ID.

    """
    result = _get(f"/node/{id_node}/network_interface")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node network interfaces")

    return result.json()


def fetch_simulation_network_interfaces(id_simulation: int) -> Any:
    """Return network interfaces list given a simulation ID.

    :return: The list of network interfaces.

    :param id_simulation: The simulation ID.

    """
    result = _get(f"/simulation/{id_simulation}/network_interface")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation network interfaces")

    return result.json()


def fetch_network_interface_by_mac(id_simulation: int, mac_address: str) -> Any:
    """Return network interface list given a mac address.

    :return: The network interface.

    :param id_simulation: The simulation ID.
    :param mac_address: The mac_address to look for.

    """
    # Fetch node network interfaces
    result = _get(f"/simulation/{id_simulation}/network_interface")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve network interfaces")

    network_interfaces = result.json()

    for network_interface in network_interfaces:
        if network_interface["mac_address"] == mac_address:
            return network_interface
    else:
        return None


def delete_network_interface(id_network_interface: int) -> Any:
    """Delete network interface given an id.

    :return: A message telling how the operation executed.

    :param id_network_interface: The network interface ID.

    """
    result = _delete(f"/network_interface/{id_network_interface}")

    if result.status_code != 200:
        _handle_error(
            result, "Cannot retrieve node network interfaces from IT Simulation API"
        )

    return result.json()


def update_network_interface(
    id_network_interface: int, network_interface_dict: dict
) -> Any:
    """Update network interface information information given a network interface id and a
    dict containing network info.

    :return: A message telling how the operation executed.

    :param id_network_interface: The network interface ID.
    :param network_interface_dict: The dict containing the entries to update.

    """
    data = json.dumps(network_interface_dict)
    result = _put(
        f"/network_interface/{id_network_interface}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot update network interface information")

    return result.json()


def fetch_probe(probe_id: int) -> Any:
    """Return a probe given its ID.

    :return: The probe dict.

    :param probe_id: The probe ID.

    """
    result = _get(f"/probe/{probe_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve probe from core API")

    return result.json()


def fetch_probes(id_simulation: int) -> Any:
    """Return simulation probes dict given
    a simulation ID, where keys are probes ids.

    :return: The list of probe dicts.

    :param id_simulation: The simulation ID.

    """

    result = _get(f"/simulation/{id_simulation}/probe")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve simulation probes from core API")

    return result.json()


def create_probe(
    id_simulation: int,
    network_interfaces: List[int],
    iface: Optional[str] = None,
    pcap: Optional[bool] = False,
    filter: Optional[str] = "",
    direction: Optional[str] = "both",
) -> int:
    """Create a new probe for the simulation given a dict containing probe data.

    :return: The new probe ID.

    :param id_simulation: The simulation ID.
    :param network_interfaces: The list of network interfaces to capture traffic from.
    :param iface: Interface where the traffic is mirrored to. Ex: 'dummy0'.
    :param pcap: A boolean indicating if the capture should be saved on disk in a pcap file (to be included in dataset)
    :param filter: String filtering tcpdump capture. Ex: 'tcp port 80'.
    :param direction: Select which traffic to monitor on the mirrored interface(s): either 'ingress', 'egress' or 'both'.

    """

    data_dict = {
        "iface": iface,
        "pcap": pcap,
        "filter": filter,
        "network_interfaces": network_interfaces,
        "direction": direction,
    }

    data = json.dumps(data_dict)
    result = _post(
        f"/simulation/{id_simulation}/probe",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot create probe with core API")

    probe_id = result.json()["id"]

    return probe_id


def update_probe(probe_id: int, probe_dict: dict) -> Any:
    """Update probe information given a probe id and a dict containing
    probe data.

    :return: A message telling how the operation executed.

    :param probe_id: The probe ID.
    :param probe_dict: The dict containing the entries to update.

    """

    data = json.dumps(probe_dict)
    result = _put(
        f"/probe/{probe_id}",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot update probe information with core API")

    return result.json()


def delete_probe(probe_id: int) -> Any:
    """Delete simulation probe given its ID.

    :return: A message telling how the operation executed.

    :param probe_id: The probe ID.

    """

    # Delete probe
    result = _delete(f"/probe/{probe_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete probe")

    return result.json()


def fetch_baseboxes() -> Any:
    """Return baseboxes list.

    :return: The list of baseboxes dict.

    """
    result = _get("/basebox")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve baseboxes list from IT Simulation API")

    baseboxes = result.json()
    return baseboxes


def fetch_basebox(id_basebox: str) -> Any:
    """Return basebox given a basebox ID.

    :return: The basebox dict.

    :param id_basebox: The basebox ID.

    """
    result = _get(f"/basebox/id/{id_basebox}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from IT Simulation API")

    basebox = result.json()
    return basebox


def reload_baseboxes() -> Any:
    """
    Call the cyber range API to reload the list of available baseboxes.

    :return: A message telling how the operation executed.

    """
    result = _get("/basebox/reload")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from IT Simulation API")

    return result.json()


def verify_basebox_result(task_id: str) -> Any:
    """Call the API to get the result the current verification.

    :param task_id: The task ID.

    :return: The result of the verification.

    """

    data = {"task_id": task_id}

    try:
        result = _post(
            "/basebox/result_verify",
            data=data,
        )

        if result.status_code != 200:
            _handle_error(result, "Cannot get verification result")

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting verification result: '{}'".format(e))


def verify_basebox_stop(task_id: str) -> Any:
    """Call the API to stop the current verification.

    :return: A message telling how the operation executed.

    :param task_id: The task ID.

    """
    data = {"task_id": task_id}

    result = _post("/basebox/stop_verify", data=data)

    if result.status_code != 200:
        _handle_error(result, "Cannot stop verification task")

    return result.json()


def verify_basebox_status(task_id: str) -> Any:
    """
    Call the API to get the status of current verification

    :return: A message telling how the operation executed.

    :param task_id: The task ID.

    """
    data = {"task_id": task_id}

    try:
        result = _post("/basebox/status_verify", data=data)

        if result.status_code != 200:
            _handle_error(result, "Cannot get verify status")

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting verify status: '{}'".format(e))


def verify_basebox(basebox_id: str) -> Dict:
    """Call the API to verify the integrity of the given basebox based on its ID.

    :param basebox_id: The basebox ID.

    :return: A dict containing verification results.

    """
    result = _get(f"/basebox/verify/{basebox_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from IT Simulation API")

    result_json = result.json()
    task_id = result_json["task_id"]
    success = result_json["result"] == "STARTED"

    if not success:
        _baseboxes_task_raise_error_msg(result_json)

    logger.info(f"[+] Verification task ID: {task_id}")

    verify_result = _handle_wait_basebox_verify(
        wait=True, task_id=task_id, log_suffix=str(basebox_id), timeout=3600
    )

    return {
        "success": verify_result["success"],
        "task_id": task_id,
        "result": verify_result["result"],
    }


def verify_baseboxes() -> Dict:
    """Call the API to verify the checksum of all baseboxes.

    :return: A dict containing verification results.
    """
    result = _get("/basebox/verify/")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from IT Simulation API")

    result_json = result.json()
    task_id = result_json["task_id"]
    success = result_json["result"] == "STARTED"

    if not success:
        _baseboxes_task_raise_error_msg(result_json)

    logger.info(f"[+] Verification task ID: {task_id}")

    new_result = _handle_wait_basebox_verify(
        wait=True, task_id=task_id, log_suffix="all baseboxes", timeout=3600
    )

    return {
        "success": new_result["success"],
        "task_id": task_id,
        "result": new_result["result"],
    }


def fetch_domains() -> Dict[str, str]:
    """Returns the mapping domain->IP.

    :return: The list of domain dicts.

    """

    # FIXME(multi-tenant): we should retrieve domains according to a simulation id
    result = _get("/network_interface/domains")

    if result.status_code != 200:
        _handle_error(result, "Error while fetching domains")

    return result.json()


def fetch_websites() -> Any:
    """Return the websites list.

    :return: The list of website dicts.

    """
    result = _get("/website")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve websites list from IT Simulation API")

    websites = result.json()
    return websites


def topology_add_websites(
    topology_yaml: str, websites: List[str], switch_name: str
) -> str:
    """Add docker websites node to a given topology.

    :return: The updated topology content.

    :param topology_yaml: The input topology content as a string.
    :param websites: The list of websites to add.
    :param switch_name: The switch on which to connect the docker website nodes.

    """

    data_dict = {
        "topology_yaml": topology_yaml,
        "websites": websites,
        "switch_name": switch_name,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/topology/add_websites",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding websites to a topology")

    topology_yaml = result.json()["topology_yaml"]

    return topology_yaml


def topology_add_dga(
    topology_yaml: str,
    algorithm: str,
    switch_name: str,
    number: int,
    resources_dir: str,
) -> Tuple[str, List[str]]:
    """Add docker empty websites with DGA node to a given topology.

    :return: The tuple containeing the updated topology associated with the domains.

    :param topology_yaml: The input topology content as a string.
    :param algorithm: The algorithm used to generate the new DGA domains.
    :param switch_name: The switch on which to connect the docker website nodes.
    :param number: The number of DGA domains to add.
    :param resources_dir: The path to resources that will be pushed into the new docker nodes.

    """

    data_dict = {
        "topology_yaml": topology_yaml,
        "algorithm": algorithm,
        "switch_name": switch_name,
        "number": number,
        "resources_dir": resources_dir,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/topology/add_dga",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding websites to a topology")

    topology_yaml = result.json()["topology_yaml"]
    domains = result.json()["domains"]

    return topology_yaml, domains


def topology_add_dns_server(
    topology_yaml: str,
    switch_name: str,
    resources_dir: str,
) -> Tuple[str, str]:
    """

    :return: The tuple containing the updated topology associated with the DNS configuration generated.

    :param topology_yaml: The input topology content as a string.
    :param switch_name: The switch on which to connect the docker DNS server node.
    :param resources_dir: The path to resources that will be pushed into the new docker node.

    """
    data_dict = {
        "topology_yaml": topology_yaml,
        "switch_name": switch_name,
        "resources_dir": resources_dir,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/topology/add_dns_server",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding a DNS server to a topology")

    topology_yaml = result.json()["topology_yaml"]
    dns_conf = result.json()["dns_conf"]

    return topology_yaml, dns_conf


def tools_generate_domains(
    algorithm: str,
    number: int,
) -> List[str]:
    """Generate domain names according to the given algorithm.

    :return: A list of domains.

    :param algorithm: The algorithm used to generate the new domains.
    :param number: Number of domains to generate.

    """
    data_dict = {
        "algorithm": algorithm,
        "number": number,
    }
    data = json.dumps(data_dict)
    result = _post(
        "/domain/generate_domains",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while generating domains")

    domains = result.json()["domains"]

    return domains


def fetch_topologies() -> Any:
    """Return topologies list.

    :return: The list of available topologies.

    """
    result = _get("/topology")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve topologies list from IT Simulation API")

    topologies = result.json()
    return topologies


###
# Simulation commands
###


def start_simulation(
    id_simulation: int,
    use_install_time: bool = False,
    timeout: int = 300,
    nodes: Optional[List[str]] = None,
) -> None:
    """Start the simulation, with current time (by default) or time where
    the VM was created (use_install_time=True). It is possible to
    specify the nodes to start. By default, all nodes are started.

    :param id_simulation: The simulation ID.
    :param use_install_time: Tell to start the virtual machines with the current time or to use the installation time of the associated baseboxes. By default (True), the current host system time is used for the current time.
    :param timeout: By default, a 300 seconds timeout is used to limit the amount of time we wait for the nodes to finish to start. This delay can be changed.
    :param nodes: The nodes to start (all nodes by default).

    """

    # Callback on input
    if cbk_start_simulation_before:
        id_simulation, use_install_time, timeout, nodes = cbk_start_simulation_before(
            id_simulation, use_install_time, timeout, nodes
        )

    # Check that no other simulation is running
    simulation_list = fetch_simulations()
    for simulation in simulation_list:
        if simulation["id"] != id_simulation and simulation["status"] == "RUNNING":
            raise Exception(
                "Cannot start a new simulation, as the simulation '{}' is "
                "already running".format(simulation["id"])
            )

    # Initiate the simulation
    if nodes is None:
        nodes = []
    post_data = {"nodes": nodes}

    _simulation_execute_operation(
        "post",
        "start",
        id_simulation,
        "STARTING",
        optional_param1=use_install_time,
        optional_param2=timeout,
        post_data=post_data,
    )

    # Callback on output
    if cbk_start_simulation_after:
        cbk_start_simulation_after()


def pause_simulation(id_simulation: int) -> None:
    """Pause a simulation (calls libvirt suspend API).

    :param id_simulation: The simulation ID.

    """
    _simulation_execute_operation("get", "pause", id_simulation, "PAUSING")


def unpause_simulation(id_simulation: int) -> None:
    """Unpause a simulation (calls libvirt resume API).

    :param id_simulation: The simulation ID.

    """
    _simulation_execute_operation("get", "unpause", id_simulation, "UNPAUSING")


def create_backup_simulation(
    id_simulation: int,
    nodes: Optional[List[str]] = None,
) -> None:
    """Create backup of a simulation. It is possible to specify the nodes
    to backup. By default, all nodes are backed up.

    :param id_simulation: The simulation ID.
    :param nodes: The nodes for which to create backup (all nodes by default).

    """

    if nodes is None:
        nodes = []
    post_data = {"nodes": nodes}

    _simulation_execute_operation(
        "post", "create_backup", id_simulation, "PREPARING", post_data=post_data
    )


def restore_backup_simulation(
    id_simulation: int,
    nodes: Optional[List[str]] = None,
) -> None:
    """Restore backup of a simulation. It is possible to specify the nodes
    to restore. By default, all nodes are restored.

    :param id_simulation: The simulation ID.
    :param nodes: The nodes for which to restore backup (all nodes by default).

    """

    if nodes is None:
        nodes = []
    post_data = {"nodes": nodes}

    _simulation_execute_operation(
        "post", "restore_backup", id_simulation, "PREPARING", post_data=post_data
    )


def halt_simulation(id_simulation: int, nodes: Optional[List[str]] = None) -> None:
    """Properly stop a simulation, by sending a shutdown signal to the
    operating systems. It is possible to specify the nodes to
    start. By default, all nodes are started.

    :param id_simulation: The simulation ID.
    :param nodes: The nodes to halt (all nodes by default).

    """
    if nodes is None:
        nodes = []
    post_data = {"nodes": nodes}

    _simulation_execute_operation(
        "post",
        "stop",
        id_simulation,
        "STOPPING",
        post_data=post_data,
    )


def destroy_simulation(id_simulation: int, nodes: Optional[List[str]] = None) -> None:
    """Stop a simulation through a hard reset.

    :param id_simulation: The simulation ID.
    :param nodes: The nodes to destroy (all nodes by default).

    """

    if nodes is None:
        nodes = []
    post_data = {"nodes": nodes}

    _simulation_execute_operation(
        "post", "destroy", id_simulation, "STOPPING", post_data=post_data
    )


def clone_simulation(id_simulation: int) -> int:
    """Clone a simulation and create a new simulation, and return the new ID.

    :return: The ID of the cloned simulation.

    :param id_simulation: The simulation ID.

    """
    id_new_simulation = _simulation_execute_operation(
        "get", "clone", id_simulation, "CLONING"
    )
    return id_new_simulation


def net_create_probe(  # noqa: C901
    id_simulation: int,
    simu_nodes: Dict,
    iface: Optional[str] = None,
    pcap: Optional[bool] = False,
    filter: Optional[str] = "",
    direction: Optional[str] = "both",
) -> int:
    """Create a new probe and configure his network collections points.

    :param id_simulation: The simulation ID.
    :param simu_nodes: A dictionary storing the collection points to capture. Ex: {'switchs': [['switch1', 'client1']], 'nodes': ['client2']}.
    :param iface: Interface where the traffic is mirrored to. Ex: 'dummy0'.
    :param pcap: A boolean indicating if the capture should be saved on disk in a pcap file (to be included in dataset)
    :param filter: String filtering tcpdump capture. Ex: 'tcp port 80'.
    :param direction: Select which traffic to monitor on the mirrored interface(s): either 'ingress', 'egress' or 'both'.

    """

    network_interfaces = []

    if simu_nodes["switchs"] is None and simu_nodes["nodes"] is None:
        # Consider all node of the simulation (except routers that are
        # OVN abstract objects on which it is not possible to capture
        # traffic)
        for node in fetch_nodes(id_simulation):
            if node["type"] != "router":
                for network_interface in node["network_interfaces"]:
                    network_interfaces.append(network_interface["mac_address"])
    else:
        if simu_nodes["switchs"] is not None:
            # Mirror traffic from node interfaces connected to the specified switchs
            for switch_nodes in simu_nodes["switchs"]:
                switch = fetch_node_by_name(id_simulation, switch_nodes[0])

                # Check if specific nodes are defined, for this switch
                if switch_nodes[1:]:
                    for node_name in switch_nodes[1:]:
                        node = fetch_node_by_name(id_simulation, node_name)

                        for network_interface in node["network_interfaces"]:
                            if network_interface["switch_name"] == switch["name"]:
                                network_interfaces.append(
                                    network_interface["mac_address"]
                                )
                                break
                        else:
                            raise Exception(
                                "The node '{}' isn't linked with the switch '{}'".format(
                                    node_name, switch["name"]
                                )
                            )
                # Else, consider all nodes connected to the switch
                else:
                    for node in fetch_nodes(id_simulation):
                        if node["type"] != "router":
                            for network_interface in node["network_interfaces"]:
                                if network_interface["switch_name"] == switch["name"]:
                                    network_interfaces.append(
                                        network_interface["mac_address"]
                                    )

        if simu_nodes["nodes"] is not None:
            # Mirror traffic on all interfaces from the specified nodes
            for node_name in simu_nodes["nodes"]:
                for network_interface in fetch_node_by_name(id_simulation, node_name)[
                    "network_interfaces"
                ]:
                    network_interfaces.append(network_interface["mac_address"])

    probe_id = create_probe(
        id_simulation, network_interfaces, iface, pcap, filter, direction
    )

    return probe_id


def net_start_probe(id_simulation: int, probe_id: int) -> None:
    """Redirect network traffic to the probe interface.

    :param id_simulation: The simulation ID.
    :param probe_id: The probe ID.

    """

    result = _get(f"/simulation/{id_simulation}/probe/{probe_id}")

    if result.status_code != 200:
        _handle_error(
            result, "Cannot activate network traffic redirection from IT Simulation API"
        )


def net_stop_probe(id_simulation: int, probe_id: int) -> None:
    """Stop redirection of network traffic to the probe interface.

    :param id_simulation: The simulation ID.
    :param probe_id: The probe ID.

    """

    result = _get(f"/simulation/{id_simulation}/stop_probe/{probe_id}")

    if result.status_code != 200:
        _handle_error(
            result, "Cannot stop network traffic redirection from IT Simulation API"
        )


def fetch_list_probes(id_simulation: int) -> Dict:
    """Return the list of probes with their data

    :param id_simulation: The simulation ID.

    :return: A list of probes with their data.
    """

    result = {}

    probes = fetch_probes(id_simulation)
    for probe in probes:
        result[probe["id"]] = {
            "collecting_points": fetch_probe_collecting_points(id_simulation, probe),
            "iface": probe["iface"],
            "pcap": probe["pcap"],
            "filter": probe["filter"],
            "capture_in_progress": probe["capture_in_progress"],
            "direction": probe["direction"],
        }

    return result


def fetch_probe_collecting_points(id_simulation: int, probe: Dict) -> Any:
    """Return the list of collecting points used to capture the network traffic to a given probe of a simulation.

    :param id_simulation: The simulation ID.
    :param probe: The given probe of the simulation.

    :type probe: :class:`class`:`Dict`, ex : {'iface': 'dummy0', 'id': 1, 'pcap': True, 'capture_in_progress': False, 'filter': 'tcp port 80', 'simulation_id': 1, 'network_interfaces': ['00:21:a1:07:7d:be'], 'direction': 'ingress'}

    """

    collecting_points: Dict[Any, Any] = {"switchs": {}, "nodes": []}

    network_interfaces = [
        fetch_network_interface_by_mac(id_simulation, n)
        for n in probe["network_interfaces"]
    ]

    nodes_to_capture = []
    for network_interface in network_interfaces:
        node = fetch_node(network_interface["node_id"])
        if node not in nodes_to_capture:
            nodes_to_capture.append(node)

    # Return None if there is nothing to capture
    if nodes_to_capture == []:
        return None

    # Return {} if every node must be captured
    if len(network_interfaces) == len(
        fetch_simulation_network_interfaces(id_simulation)
    ):
        return {}

    for node in nodes_to_capture:
        # If every network_interface from a node is captured, it goes to the "nodes" dict
        capture_all_network_interfaces = True
        for node_network_interface in node["network_interfaces"]:
            capture_all_network_interfaces = capture_all_network_interfaces and (
                node_network_interface in network_interfaces
            )

        if capture_all_network_interfaces:
            collecting_points["nodes"].append(node["name"])
        else:
            # Else, it goes to the "switchs" dict
            for node_network_interface in node["network_interfaces"]:
                if node_network_interface in network_interfaces:
                    switch = {"name": node_network_interface["switch_name"]}

                    if switch["name"] not in collecting_points["switchs"].keys():
                        collecting_points["switchs"][switch["name"]] = []
                    collecting_points["switchs"][switch["name"]].append(node["name"])

    return collecting_points


def snapshot_simulation(id_simulation: int) -> str:
    """Create a snapshot of a simulation.

    All the files will be stored to
    /cyber-range-catalog/simulations/<hash campaign>/<timestamp>/

    :return: The path where the topology file will be stored.

    :param id_simulation: The simulation ID.

    """

    # simu_snap can only be done on a RUNNING simulation
    if simulation_status(id_simulation) != "RUNNING":
        raise Exception(
            "Cannot create a snapshot of the simulation, as the simulation '{}' is "
            "not running".format(id_simulation)
        )

    # Call snapshot API
    result = _post(f"/simulation/{id_simulation}/snapshot")
    if result.status_code != 200:
        _handle_error(result, "Error while creating snapshot")

    yaml: str = result.json()

    logger.info(f"[+] Starting the snapshot of simulation {id_simulation}...")
    while simulation_status(id_simulation) != "SNAPSHOT":

        if cbk_check_stopped is not None:
            if cbk_check_stopped() is True:
                logger.info("   [+]    Current process was asked to stop")
                raise ScenarioExecutionStopped

        time.sleep(1)

        simulation_dict = fetch_simulation(id_simulation)
        current_status = simulation_dict["status"]
        if current_status == "ERROR":
            error_message = simulation_dict["error_msg"]
            raise Exception(
                "Error during simulation snapshot: '{}'".format(error_message)
            )

    logger.info("[+] Snapshot process has started")

    while simulation_status(id_simulation) != "READY":

        if cbk_check_stopped is not None:
            if cbk_check_stopped() is True:
                logger.info("   [+]    Current process was asked to stop")
                raise ScenarioExecutionStopped

        logger.info("  [+] Snapshot in progress...")
        time.sleep(1)

        simulation_dict = fetch_simulation(id_simulation)
        current_status = simulation_dict["status"]
        if current_status == "ERROR":
            error_message = simulation_dict["error_msg"]
            raise Exception(
                "Error during simulation snapshot: '{}'".format(error_message)
            )

    return yaml


def compute_infrastructure_status() -> Any:
    """Get compte server services status.

    :return: The compute server services status.

    """
    result = _get("/simulation/compute_infrastructure_status")

    if result.status_code != 200:
        _handle_error(result, "Cannot get compute infrastructure status")

    simulation_dict = result.json()["result"]
    return simulation_dict


def add_dns_entries(id_simulation: int, dns_entries: Dict[str, str]) -> None:
    """Add volatile DNS entries to the current simulation. Volatile means that it is not
    stored in database.

    :param id_simulation: The simulation ID.
    :param dns_entries: The DNS entries (a dict with domains as keys and IP addresses as values).

    """

    data = json.dumps(dns_entries)
    result = _post(
        f"/simulation/{id_simulation}/add_dns_entries",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding DNS entries")


def connect_host(id_simulation: int) -> None:
    """Connect the host interface to the current simulation.

    :param id_simulation: The simulation ID.

    """

    result = _get(f"/simulation/{id_simulation}/connect_host")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot execute operation 'connect_host' on simulation '{id_simulation}'.",
        )


def disconnect_host(id_simulation: int) -> None:
    """Disconnect the host interface to the current simulation.

    :param id_simulation: The simulation ID.

    """

    result = _get(f"/simulation/{id_simulation}/disconnect_host")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot execute operation 'disconnect_host' on simulation '{id_simulation}'.",
        )


def generate_malicious_domains(
    algorithm: Optional[str] = None, number: int = 1
) -> List[str]:
    """Generate and return a list of malicious domains.

    :return: The list of generated domains.

    :param algorithm: The algorithm used to generate the new domains.
    :param number: Number of domains to generate.

    """

    data_dict = {
        "algorithm": algorithm,
        "number": number,
    }
    data = json.dumps(data_dict)

    result = _post(
        "/topology/generate_malicious_domains",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Error while adding DNS entries")

    domains = result.json()
    return domains["domains"]


def verify_dataset_all() -> Dict[str, DatasetAnalysisResult]:
    logger.info("[+] Going to verify all datasets")
    result = _get("/verify/all")
    if result.status_code != 200:
        err = f"Dataset verification launch failed with code {result.status_code}."
        raise Exception(err)
    for _ in range(0, 600):
        time.sleep(5)
        result = _get("/verify/all/status")
        if result.status_code != 200:
            err = f"Dataset verification status failed with code {result.status_code}."
            raise Exception(err)
        result_json = result.json()
        if "status" in result_json:
            if result_json["status"] == "FINISHED_ERROR":
                err = f"Dataset verification status failed {result_json['message']}."
                raise Exception(err)
            elif result_json["status"] == "FINISHED":
                logger.info("All Dataset verification done")
                for k, v in result_json["result"].items():
                    logger.info(f"[+] Verification for dataset UUID {k}")
                    res: DatasetAnalysisResult = DatasetAnalysisResult(**v)
                    res.display(logger)
                    logger.info("")
                break
            elif result_json["status"] == "RUNNING":
                logger.info(result_json["status"] + ": " + result_json["message"])
    else:
        err = "Timeout during the verification of all datasets."
        logger.error(err)
        raise Exception(err)

    return result_json


def verify_dataset(dataset_id: uuid.UUID) -> DatasetAnalysisResult:
    logger.info("[+] Going to verify dataset '{}'".format(dataset_id))
    result = _get(f"/verify/{dataset_id}", timeout=500)
    if result.status_code != 200:
        err = f"Dataset verification failed with code {result.status_code}."
        raise Exception(err)

    return DatasetAnalysisResult(**result.json())


def create_dataset(
    id_simulation: int,
    dont_check_logs_path: bool = False,
    scenario: Optional[Dict] = None,
    scenario_profile: Optional[str] = "",
) -> Optional[uuid.UUID]:
    """Handles the creation of the dataset after the end of a simulation

    Must be called after a STOP operation, and once all compute
    servers have fully stopped.

    Basically, this function communicates with the core API, which itself
    communicates with the publish server's "backend" API.

    :return: The new dataset UUID.

    :param id_simulation: The simulation ID.
    :param dont_check_logs_path: Tell to not emit a warning if logs paths are incorrect (warning are emitted by default).

    """

    logger.info(
        "[+] Going to create dataset based on data produced by simulation ID '{}'".format(
            id_simulation
        )
    )

    # if dont_check_logs_path is False:
    #     _check_logs_path(id_simulation)

    # Ask the core API to contact the /backend/ publish server API
    # in order to start the dataset creation process
    result = _post(
        f"/create_dataset/{id_simulation}",
        json={"scenario": scenario, "scenario_profile": scenario_profile},
    )
    if result.status_code != 200:
        _handle_error(result, "Cannot initiate the creation of the dataset")

    dataset_id = result.json()["dataset_id"]

    logger.info(f"  [+] Dataset pre-created with dataset id {dataset_id}")

    # Start an active waiting loop until the dataset creation if fully complete
    # Indeed, dataset creation involves the download of potentially large
    # files overs the network, which can take some time!
    max_retries = 5
    retries = max_retries
    while True:

        if cbk_check_stopped is not None:
            if cbk_check_stopped() is True:
                logger.info("   [+]    Current process was asked to stop")
                raise ScenarioExecutionStopped

        time.sleep(2)
        # Might requires longer timeout since foresinc output preparation is time consuming
        result = _get(f"/create_dataset/status/{dataset_id}", timeout=300)
        if result.status_code != 200:
            if (
                result.headers.get("content-type") == "application/json"
                and "message" in result.json()
            ):
                error_msg = result.json()["message"]
            else:
                error_msg = result.text

            # Retry to get the status a couple of times before qsending back an error
            if retries == 0:
                raise Exception(
                    "Error during creation of dataset {}: could not get status of the dataset creation after {} tries. Core API HTTP status: {}. Response: {} ".format(
                        dataset_id, max_retries, result.status_code, error_msg
                    )
                )
            else:
                logger.warning(
                    "  [+] Could not get status of dataset creation (Retries left: {}. Core API HTTP status: {}. Response: {})".format(
                        retries, result.status_code, error_msg
                    )
                )
                retries -= 1
        else:
            # Reset the number of retries
            retries = max_retries

            # Get the status and message
            dataset_creation_status = result.json()["status"]
            dataset_creation_message = result.json()["message"]

            logger.info(
                "  [+] Dataset creation in progress (Status: {})".format(
                    dataset_creation_status
                )
            )

            if dataset_creation_status == "FINISHED":
                # All went well
                break
            elif dataset_creation_status == "FINISHED_ERROR":
                # The dataset creation encountered errors
                raise Exception(
                    "Error during creation of dataset {}: dataset creation ended with errors ('{}').".format(
                        dataset_id, dataset_creation_message
                    )
                )
            # Otherwise, dataset creation is not finished, just loop

    logger.info("[+] Dataset creation was correctly executed")

    # Set the simulation status to READY
    update_simulation(id_simulation, {"status": "READY"})

    simulation = fetch_simulation(id_simulation)
    logger.info("[+] Current simulation status: '{}'".format(simulation["status"]))

    return uuid.UUID(dataset_id)


def _check_logs_path(id_simulation: int) -> None:
    """Produces error message if a bad path was set for the log_collector's log
    volume.

    Do a small check for the sake of helping the user and giving better
    user experience: check if the log_collector docker (which collects logs)
    is inside the topology, and if so, check the "host_path" for logs
    (a specific path is expected, and is hardcoded in it_simulation)

    """
    # TODO(CRD): this check will always fail when cr_api_client, the
    # it_simulation docker, and the rsyslog docker are not on the same machine

    topology = YAML().load(fetch_simulation_topology_yaml(id_simulation))

    # The path of the logs, on the compute server file system should ALWAYS be as follows
    log_collector_docker_present: bool = False
    potential_logs_absolute_path: List[Path] = []
    for node in topology["nodes"]:
        if (
            node["type"] == "docker"
            and "log_collector" in node["roles"]
            and "volumes" in node
        ):
            log_collector_docker_present = True
            for volume in node["volumes"]:
                if (
                    "host_path" in volume
                    and "writable" in volume
                    and volume["writable"]
                ):
                    potential_logs_absolute_path.append(Path(volume["host_path"]))

    # If no log_collector docker is present, jsut issue a non-blocking warning
    if log_collector_docker_present is False:
        logger.warning(
            "  [+] The collection of logs was not activated for the simulation (A log_collector docker is not present in the topology). No log will be included in the dataset."
        )
    else:
        wrong_host_path = True
        for p in potential_logs_absolute_path:
            if not p.is_absolute() and p == Path("shared_resources/log_collector/ecs"):
                wrong_host_path = False
                break
            elif p.is_absolute() and Path(str(p)[1:]) == Path(
                "shared_resources/log_collector/ecs"
            ):
                wrong_host_path = False
                break
            elif p.is_absolute() and p == Path(
                "/cyber-range-catalog/simulations_resources/1/shared_resources/log_collector/ecs"
            ):
                wrong_host_path = False
                break

        if wrong_host_path is True:
            logger.error(
                "  [+] It seems that the simulation includes a 'log_collector' docker that collects the logs, but does not specify the appropriate host_path for the logs. It is expected that the log_collector docker node specifies a (writable) volume with a host_path equal to '/shared_resources/log_collector/ecs'. Candidates are '{}' instead.".format(
                    [str(p) for p in potential_logs_absolute_path],
                )
            )
            logger.error(
                " [+] Dataset creation aborted. You may wish to move the log files to the appropriate folder on the compute server(s), and then retry. Alternatively, you can bypass this check with the dont_check_log_path option."
            )


def stop_dataset_creation(dataset_id: uuid.UUID) -> Any:
    """
    Stops/aborts the creation of a dataset that is in the process of being created.

    This function should be used, for instance, if a dataset creation has been
    automatically started although the user does not want a dataset, and the dataset
    creation process is taking too much time.

    WARNING: after stopping the dataset creation, it is advised to delete or at least
    repair the dataset.

    :param dataset_id: The dataset ID which is in the process of being created and that must be aborted.
    :return: Return the json body of the core API response.

    """
    # Simply calls the core API which itself asks the publish
    # server (backend) to stop of the dataset creation process.

    result = _put("/create_dataset/stop/{}".format(str(dataset_id)))

    if result.status_code != 200:
        _handle_error(result, "Cannot stop dataset creation through core API")

    return result.json()


def fetch_compute_server(compute_server_id: int) -> Any:
    """Return a compute server given its ID.

    :return: The compute server dict.

    :param compute_server_id: The compute server ID.

    """
    result = _get(f"/compute_servers/{compute_server_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node from IT Simulation API")

    return result.json()


def fetch_compute_server_by_node_id(node_id: int) -> Any:
    """Return a compute server where a node ID is running.

    :return: The compute server dict.

    :param node_id: The node ID to look for.

    """
    result = _get(f"/compute_servers/node/{node_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve node from IT Simulation API")

    return result.json()


def fetch_compute_servers() -> List[Dict[str, Any]]:
    """
    Return the list of compute servers as known in database.

    :return: The list of compute server dicts.

    """
    result = _get("/compute_servers/")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve compute servers from IT Simulation API")

    return result.json()


def delete_compute_server(compute_server_id: int) -> None:
    """
    Deletes a compute server in database using its id.

    Compute servers ids can be obtained through `cyber_range status` or :func:`fetch_compute_server`.

    :param compute_server_id: The compute server ID.

    """
    result = _delete(f"/compute_servers/{compute_server_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot delete compute server in core API")

    return result.json()


def provisioning_deploy_playbook_on_agent_compute_server(
    id_simulation: int,
    provisioning_agent_node_name: str,
    playbook_folder: Path,
    playbook_name: str,
) -> None:
    """
    "Backend" type of API endpoint, for Provisioning API to deploy a playbook on the compute server of a running provisioning agent

    Ultimately, this allows to deploy the playbook and its resources in /cyber-range-catalog/provisioning_playbooks/.

    :param id_simulation: ID of the simulation of the target running provisioning agent
    :param provisioning_agent_node_name: the name of the provisioning agent node, currently running in the simulation
    :param playbook_folder: local path of the playbook to deploy. The contents of this folder will be zipped and sent to the compute server.
    :param playbook_name: Determines the name of the folder (subfolder of /cyber-range-catalog/provisioning_playbooks/) in which the playbook resources will be unzipped on the compute server
    """

    # Make the zip and send it to it_simulation
    with TemporaryDirectory(prefix="cyber_range_provisioning_playbook_tmp") as tmp_dir:
        try:
            zip_file_name = _zip_resources(playbook_folder, Path(tmp_dir))
        except Exception as e:
            raise Exception(
                f"The local playbook folder {playbook_folder} could not be zipped: {e.__class__.__name__}({str(e)})"
            )

        with open(zip_file_name, "rb") as zipped_playbook_file:
            files = {"playbook_resources": (playbook_name, zipped_playbook_file)}
            data = {"provisioning_agent_node_name": provisioning_agent_node_name}

            try:
                result = _post(
                    f"/simulation/{id_simulation}/deploy_provisioning_playbook",
                    data=data,
                    files=files,
                )
            except Exception as e:
                logger.error(
                    "Error during the upload of the playbook to IT Simulation API"
                )
                logger.exception(e)
                raise Exception(
                    f"Error during the upload of the playbook to IT Simulation API : {e.__class__.__name__}({str(e)})"
                )

            if result.status_code != 200:
                _handle_error(
                    result,
                    "Error during the upload of the playbook to IT Simulation API",
                )


def download_baseboxes_by_id(baseboxes: List[str]) -> Dict[str, Any]:
    """
    Fetch baseboxes on compute servers from a list

    :param baseboxes: List of basebox id (e.g. "REFERENCE/linux/debian")
    """
    result = _post(
        "/basebox/download",
        json=baseboxes,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve basebox info from IT Simulation API")

    result_json = result.json()
    task_id = result_json["task_id"]
    success = result_json["result"] == "STARTED"

    if not success:
        _baseboxes_task_raise_error_msg(result_json)

    logger.info(f"[+] Download task ID: {task_id}")

    download_result = _handle_wait_basebox_download_task(
        wait=True, task_id=task_id, log_suffix="baseboxes", timeout=3600
    )

    return {
        "success": download_result["success"],
        "task_id": task_id,
        "result": download_result["result"],
    }


def download_baseboxes_by_topology(topology_file: Path) -> Dict[str, Any]:
    """
    Fetch baseboxes on compute servers for a given topology

    :param topology_file: The path of the topology file
    """
    baseboxes: Set[str] = set()

    _validate_yaml_topology_file(topology_file)
    yaml_content = _read_yaml_topology_file(topology_file)
    loader = YAML(typ="rt")
    topology_content = loader.load(yaml_content)

    for node in topology_content["nodes"]:
        if "basebox_id" in node and node.get("active", True):
            baseboxes.add(node["basebox_id"])

    return download_baseboxes_by_id(list(baseboxes))


def download_basebox_stop(task_id: str) -> Any:
    """Call the API to stop the current verification.

    :return: A message telling how the operation executed.

    :param task_id: The task ID.

    """
    data = {"task_id": task_id}

    result = _post("/basebox/stop_download", data=data)

    if result.status_code != 200:
        _handle_error(result, "Cannot stop download task")

    return result.json()


def _baseboxes_download_wait_until_complete(
    task_id: str, log_suffix: Optional[str] = None, timeout: int = 3600
) -> dict:
    """
    Wait until the download task represented by its id is completed

    :param task_id: the task id
    :param log_suffix: what to insert into the log
    :param timeout: the timeout to stop the task
    :return: the result of the basebox download
    """

    start_time = time.time()

    finished = False
    while not (finished or (time.time() - start_time) > timeout):

        if cbk_check_stopped is not None:
            if cbk_check_stopped() is True:
                logger.info("   [+]    Current process was asked to stop")
                raise ScenarioExecutionStopped

        time.sleep(5)
        current_time = time.time()
        elapsed = int(current_time - start_time)
        if log_suffix is not None:
            logger.info(
                f"   [+] Currently downloading {log_suffix} for {elapsed} seconds (timeout at {timeout} seconds)"
            )
        else:
            logger.info(f"   [+] Currently running the download for {elapsed} seconds")

        result = _post("/basebox/status_download", data={"task_id": task_id})
        result.raise_for_status()
        result_json = result.json()

        if "status" not in result_json:
            download_basebox_stop(task_id)
            raise Exception(
                "Error during download operation: unexpected response format from IT Simulation API on /baseboxes/status_download"
            )

        if result_json["status"] == "FINISHED":
            finished = True

    if not finished:
        error_msg = f"[-] Unable to terminate operation before timeout of {timeout} seconds. Stopping operation."
        stop_result = download_basebox_stop(task_id)
        stopped = stop_result["status"] == "STOPPED"
        if stopped:
            stop_result["result"] = dict()
            stop_result["success"] = False
            stop_result["error_msg"] = error_msg
            return stop_result
        else:
            raise Exception("Unable to stop download task after timeout")

    result = _post("/basebox/result_download", data={"task_id": task_id})
    result.raise_for_status()
    result_json = result.json()

    if result_json["status"] == "FINISHED" and result_json["success"] is True:
        logger.info("[+] The basebox download was executed successfully")
    else:
        error_msg = result_json["error_msg"]
        logger.error(
            f"[-] The basebox download was executed with error(s): {error_msg}"
        )
        for cs_id, cs_result in result_json["result"].items():
            for bb_id, bb_result in cs_result.items():
                if not bb_result["downloaded"]:
                    logger.error(f"  [-] {bb_result['error_msg']}")

    return result_json


def _handle_wait_basebox_download_task(
    wait: bool, task_id: str, log_suffix: str, timeout: int = 3600
) -> Any:
    """

    :param wait: Wait for the operation to be completed in backend
    :param task_id: the task id
    :param log_suffix: the string to be inserted in the log
    :param timeout: the time limit before stopping the task
    :return: the result of the verification
    """
    success = True

    if wait:
        # Wait for the operation to be completed in backend

        result = _baseboxes_download_wait_until_complete(
            task_id=task_id, log_suffix=log_suffix, timeout=timeout
        )

        finished = result.get("status", "unknown") == "FINISHED"
        success = finished and result.get("success", False)

        if success:
            if "result" in result:
                return result

        if not success:
            _baseboxes_task_raise_error_msg(result)

    else:
        # wait for the operation to start
        running = _wait_for_download_to_start(task_id)

        if not running:
            success = False

    return success


def _wait_for_download_to_start(task_id: str) -> bool:
    """
    Wait for a task to start
    :param task_id: the task id
    :return: Is the task running
    """

    running = False
    timeout = 10
    start_time = time.time()
    while not (running or (time.time() - start_time) > timeout):

        if cbk_check_stopped is not None:
            if cbk_check_stopped() is True:
                logger.info("   [+]    Current process was asked to stop")
                raise ScenarioExecutionStopped

        result = _post("/basebox/status_download", data={"task_id": task_id})
        result.raise_for_status()
        result_json = result.json()
        running = result_json["status"] == "RUNNING"
        time.sleep(1)

    if not running:
        logger.error(
            f"[-] Unable to start operation before timeout of {timeout} seconds"
        )

    return running
