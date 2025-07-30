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
import json
import os
import shutil
import time
from tempfile import TemporaryDirectory
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import requests
from mantis_scenario_model.notification_model import Notification
from mantis_scenario_model.notification_model import NotificationStage
from mantis_scenario_model.lab_model import ScenarioExecutionStopped

import cr_api_client.core_api as core_api
from cr_api_client import shutil_make_archive_lock
from cr_api_client.config import cr_api_client_config
from cr_api_client.logger import logger


# Module variables
cbk_check_stopped = None
cbk_event = None

# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: Any) -> Any:
    return requests.get(
        f"{cr_api_client_config.provisioning_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _post(route: str, **kwargs: Any) -> Any:
    return requests.post(
        f"{cr_api_client_config.provisioning_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=60,  # Set 60s to allow transfer of large zip files
        **kwargs,
    )


def _put(route: str, **kwargs: Any) -> Any:
    return requests.put(
        f"{cr_api_client_config.provisioning_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _delete(route: str, **kwargs: Any) -> Any:
    return requests.delete(
        f"{cr_api_client_config.provisioning_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _handle_error(result: requests.Response, context_error_msg: str) -> None:
    if result.headers.get("content-type") == "application/json":
        error_msg = result.json()["message"]
    else:
        error_msg = result.text

    raise Exception(
        f"{context_error_msg}. "
        f"Status code: '{result.status_code}'.\n"
        f"Error message: '{error_msg}'."
    )


def _validate_yaml_file(input_file: str) -> None:
    if os.path.exists(input_file) is not True:
        raise Exception("The provided path does not exist: '{}'".format(input_file))

    if os.path.isfile(input_file) is not True:
        raise Exception("The provided path is not a file: '{}'".format(input_file))

    if os.access(input_file, os.R_OK) is not True:
        raise Exception("The provided file is not readable: '{}'".format(input_file))


def _read_yaml_file(yaml_configuration_file: str) -> str:
    with open(yaml_configuration_file, "r") as fd:
        yaml_content = fd.read()
        return yaml_content


def _zip_resources(resources_path: str, temp_dir: str) -> str:
    """Private function to zip resources path content"""
    zip_file_name = os.path.join(temp_dir, "resources")

    with shutil_make_archive_lock:
        shutil.make_archive(zip_file_name, "zip", resources_path)

    return "{}.zip".format(zip_file_name)


def _raise_error_msg(result: dict) -> None:
    error_msg = "No error message returned"
    if "result" in result:
        if "error_msg" in result["result"]:
            error_msg = result["result"]["error_msg"]
            raise Exception(error_msg)
        else:
            raise Exception("Failed, but no error message was provided")
    else:
        raise Exception(f"No 'result' key in result: {result}")


# -------------------------------------------------------------------------- #
# Provisioning API
# -------------------------------------------------------------------------- #


def get_version() -> str:
    """Return Provisioning API version."""
    result = _get("/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve Provisioning API version")

    return result.json()


def provisioning_execute(
    id_simulation: Optional[int] = None,
    machines_file: Optional[str] = None,
    provisioning_file: Optional[str] = None,
    debug: bool = False,
    ansible_verbosity: int = 0,
    wait: bool = True,
    timeout: int = 10800,
    stream_ansible: bool = False,
    reload_provisioning_agent: bool = False,
) -> Tuple[bool, str]:
    """Apply provisioning configuration defined in YAML file on simulation defined in
    argument ID OR on machines defined in file. The ``wait`` parameter defines if the
    function wait for task to complete or not.

    """

    if provisioning_file is None:
        raise Exception("provisioning_file parameter cannot be None")

    if (id_simulation is None and machines_file is None) or (
        id_simulation is not None and machines_file is not None
    ):
        # By default, use id_simulation = 1
        id_simulation = 1

    if id_simulation is not None:
        log_suffix = f"on simulation ID '{id_simulation}'"
    else:
        log_suffix = f"on machines '{machines_file}'"

    if id_simulation is not None:
        logger.info(f"[+] Starting provisioning {log_suffix}")

        # Check simulation is running
        simulation_dict = core_api.fetch_simulation(id_simulation)
        simulation_status = simulation_dict["status"]
        if simulation_status != "RUNNING":
            raise Exception(
                "The simulation {id_simulation} should have is status RUNNING "
                "(current status is {current_status}) in order to generate provisioning "
                "chronology. Try the command 'cyber_range simu_run {id_simulation}' "
                "to start the simulation.".format(
                    id_simulation=id_simulation, current_status=simulation_status
                )
            )
        machines_yaml = None
    else:
        if machines_file is not None:
            the_file: str = machines_file

            # Validate input file
            _validate_yaml_file(the_file)

            # Open and read YAML input files
            machines_yaml = _read_yaml_file(the_file)

    # Validate input file
    _validate_yaml_file(provisioning_file)

    # Open and read YAML input files
    provisioning_yaml = _read_yaml_file(provisioning_file)

    data = json.dumps(
        {
            "id_simulation": id_simulation,
            "machines_yaml": machines_yaml,
            "provisioning_yaml": provisioning_yaml,
            "debug": debug,
            "ansible_verbosity": ansible_verbosity,
            "stream_ansible": stream_ansible,
            "reload_provisioning_agent": reload_provisioning_agent,
        }
    )

    result = _post(
        "/start_provisioning",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot apply provisioning execute")

    result = result.json()
    task_id = result["task_id"]
    success = result["result"] == "STARTED"

    if not success:
        _raise_error_msg(result)

    logger.info(f"[+] Provisioning task ID: {task_id}")

    result = _provisioning_handle_wait(
        wait, task_id, log_suffix, timeout=timeout, stream_ansible=stream_ansible
    )

    if wait:
        # Only check the result when the user asked to wait
        success = False
        finished = "status" in result and result["status"] == "FINISHED"

        if finished:
            if "result" in result:
                if "success" in result["result"]:
                    success = result["result"]["success"] is True

        if not success:
            if debug:
                # If an error occured, print all Ansible logs
                logger.debug("Ansible log: ")
                logger.debug(result["logs"])

            _raise_error_msg(result)
        else:
            if debug:
                # If no error occured, removing noise debug and print just the recap
                index = result["logs"].find("PLAY RECAP ********")
                if index != -1:
                    debug_str = result["logs"][index:]
                    logger.debug(debug_str)

    return result


def provisioning_ansible(  # noqa: C901
    id_simulation: Optional[int] = None,
    machines_file: Optional[str] = None,
    playbook_path: Optional[str] = None,
    target_roles: Optional[List[str]] = None,
    target_system_types: Optional[List[str]] = None,
    target_operating_systems: Optional[List[str]] = None,
    target_names: Optional[List[str]] = None,
    host_vars: Optional[List[str]] = None,
    extra_vars: Optional[Any] = None,
    gather_facts_override: Optional[bool] = None,
    debug: bool = False,
    ansible_verbosity: int = 0,
    wait: bool = True,
    timeout: int = 3600,
    stream_ansible: bool = False,
    reload_provisioning_agent: bool = False,
    delete: bool = False,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """Apply ansible playbooks on specified target(s). The ``wait`` parameter defines if
    the function wait for task to complete or not.

    """

    if target_roles is None:
        target_roles = []
    if target_system_types is None:
        target_system_types = []
    if target_operating_systems is None:
        target_operating_systems = []
    if target_names is None:
        target_names = []
    if host_vars is None:
        host_vars = []
    extra_vars_str = str(extra_vars)
    extra_vars_str = extra_vars_str.replace("\\\\", "\\")

    if playbook_path is None:
        raise Exception("provisioning_file parameter cannot be None")

    if (id_simulation is None and machines_file is None) or (
        id_simulation is not None and machines_file is not None
    ):
        # By default, use id_simulation = 1
        id_simulation = 1

    if id_simulation is not None:
        log_suffix = f"on simulation ID '{id_simulation}'"
    else:
        log_suffix = f"on machines '{machines_file}'"

    logger.info(
        f"[+] Starting provisioning ansible playbook(s) {playbook_path} {log_suffix}"
    )
    if cbk_event is not None and callable(cbk_event) is True:
        playbook_name = os.path.basename(os.path.normpath(playbook_path))
        event_data = f"Deploying '{playbook_name}' playbook"
        cbk_event(
            Notification(event_data=event_data, stage=NotificationStage.provisioning)
        )

    if id_simulation:
        # Check simulation is running
        simulation_dict = core_api.fetch_simulation(id_simulation)
        simulation_status = simulation_dict["status"]
        if simulation_status != "RUNNING":
            raise Exception(
                "The simulation {id_simulation} should have is status RUNNING "
                "(current status is {current_status}) in order to generate provisioning "
                "chronology. Try the command 'cyber_range simu_run {id_simulation}' "
                "to start the simulation.".format(
                    id_simulation=id_simulation, current_status=simulation_status
                )
            )

        # Remove non-active nodes from target_names, as they are not running on the simulation
        if len(target_names) > 0:
            new_target_names = []
            simulation_nodes = core_api.fetch_nodes(id_simulation)
            for node in simulation_nodes:
                if node["name"] in target_names and node["active"] is True:
                    new_target_names.append(node["name"])

            logger.info(f"[+] Initial target names: {target_names}")
            target_names = new_target_names
            logger.info(
                f"[+] Updated target names according to active nodes on the simulation: {target_names}"
            )

        machines_yaml = None
    else:
        if machines_file is not None:
            the_file: str = machines_file

            # Validate input file
            _validate_yaml_file(the_file)

            # Open and read YAML input files
            machines_yaml = _read_yaml_file(the_file)

    # Use the playbook folder as playbook name
    playbook_name = os.path.basename(playbook_path)

    # Double check if targets are not empty
    if (
        len(target_roles) == 0
        and len(target_system_types) == 0
        and len(target_operating_systems) == 0
        and len(target_names) == 0
    ):
        logger.warning("Target lists are empty. No provisioning will be done.")
        return (False, None, None)

    data = {
        "id_simulation": id_simulation,
        "playbook_name": playbook_name,
        "machines_yaml": machines_yaml,
        "extra_vars": extra_vars_str,
        "target_roles": target_roles,
        "target_system_types": target_system_types,
        "target_operating_systems": target_operating_systems,
        "target_names": target_names,
        "host_vars": host_vars,
        "gather_facts_override": gather_facts_override,
        "debug": debug,
        "ansible_verbosity": ansible_verbosity,
        "stream_ansible": stream_ansible,
        "reload_provisioning_agent": reload_provisioning_agent,
        "delete": delete,
    }

    with TemporaryDirectory(prefix="cyber_range_cr_provisioning_archive") as temp_dir:
        # Zipping resource files
        zip_file_name = _zip_resources(playbook_path, temp_dir)
        resources_file = open(zip_file_name, "rb")
        files = {"resources_file": resources_file}
        try:
            result = _post(
                "/start_ansible",
                data=data,
                files=files,
            )
        finally:
            resources_file.close()

    if result.status_code != 200:
        _handle_error(result, "Cannot apply provisioning ansible")

    result = result.json()
    task_id = result["task_id"]
    success = result["result"] == "STARTED"

    if not success:
        _raise_error_msg(result)

    logger.info(f"[+] Provisioning task ID: {task_id}")

    result = _provisioning_handle_wait(
        wait, task_id, log_suffix, timeout=timeout, stream_ansible=stream_ansible
    )

    if wait:
        # Only check the result when the user asked to wait
        success = False
        finished = "status" in result and result["status"] == "FINISHED"

        if finished:
            if "result" in result:
                if "success" in result["result"]:
                    success = result["result"]["success"] is True

        if not success:
            if debug and not stream_ansible:
                # If an error occured, print all Ansible logs
                logger.debug("Ansible log: ")
                logger.debug(result["logs"])

            _raise_error_msg(result)
        else:
            if debug and not stream_ansible:
                # If no error occured, remove noise debug and print just the recap
                index = result["logs"].find("PLAY RECAP ********")
                if index != -1:
                    debug_str = result["logs"][index:]
                    logger.debug(debug_str)

    return (result["status"], task_id, result["logs"])


def provisioning_inventory(
    id_simulation: Optional[int] = None,
    machines_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    debug: bool = False,
) -> None:
    """Generate ansible inventory files from targets information."""

    if (id_simulation is None and machines_file is None) or (
        id_simulation is not None and machines_file is not None
    ):
        # By default, use id_simulation = 1
        id_simulation = 1

    if id_simulation:
        # Check simulation is running
        simulation_dict = core_api.fetch_simulation(id_simulation)
        simulation_status = simulation_dict["status"]
        if simulation_status != "RUNNING":
            raise Exception(
                "The simulation {id_simulation} should have is status RUNNING "
                "(current status is {current_status}) in order to generate provisioning "
                "chronology. Try the command 'cyber_range simu_run {id_simulation}' "
                "to start the simulation.".format(
                    id_simulation=id_simulation, current_status=simulation_status
                )
            )
        machines_yaml = None
    else:
        if machines_file is not None:
            the_file: str = machines_file

            # Validate input file
            _validate_yaml_file(the_file)

            # Open and read YAML input files
            machines_yaml = _read_yaml_file(the_file)

    data = {
        "id_simulation": id_simulation,
        "machines_yaml": machines_yaml,
        "debug": debug,
    }

    result = _post(
        "/generate_inventory",
        data=data,
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot generate ansible inventory")

    try:
        # Create output dir
        if output_dir is not None:
            the_dir: str = output_dir
            if os.path.exists(the_dir):
                raise Exception(f"Output dir already exists: '{the_dir}'")
            os.mkdir(the_dir)

            # Write zip content in a temp file
            zip_content = result.content
            output_zip_file = os.path.join(the_dir, "inventory.zip")
            with open(output_zip_file, "wb") as fd:
                fd.write(zip_content)
                fd.close()

            # Extract zip content
            shutil.unpack_archive(output_zip_file, the_dir, "zip")

            # Remove temp zip file
            os.unlink(output_zip_file)

            logger.info(f"[+] Inventory written in directory '{the_dir}'")
    except Exception as e:
        raise Exception(f"Cannot retrieve inventory: '{e}'")


def provisioning_status(task_id: str) -> dict:
    """Get provisioning status on targeted simulation."""

    data = {"task_id": task_id}

    try:
        result = _post("/status_provisioning", data=data)

        if result.status_code != 200:
            _handle_error(result, "Cannot get provisioning status")

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting provisioning status: '{}'".format(e))


def provisioning_result(task_id: str) -> str:
    """Get provisioning result on targeted simulation."""

    data = {"task_id": task_id}

    try:
        result = _post(
            "/result_provisioning",
            data=data,
        )

        if result.status_code != 200:
            _handle_error(result, "Cannot get provisioning result")

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting provisioning result: '{}'".format(e))


def provisioning_stop(task_id: str) -> dict:
    """Stop provisioning task representing by its id."""

    data = {"task_id": task_id}

    result = _post("/stop_provisioning", data=data)

    if result.status_code != 200:
        _handle_error(result, "Cannot stop provisioning task")

    return result.json()


def _provisioning_wait_until_complete(  # noqa: C901
    task_id: str,
    log_suffix: Optional[str] = None,
    timeout: int = 3600,
    stream_output: bool = False,
) -> dict:
    """Wait until provisioning task representing by its id is completed."""

    start_time = time.time()

    current_status = ""
    provisioning_output = ""

    starting = True
    finishing = False
    finished = False
    display_idx = 0
    while not (finished or (time.time() - start_time) > timeout):
        time.sleep(1)

        if cbk_check_stopped is not None:
            if cbk_check_stopped() is True:
                logger.info("   [+]    Current process was asked to stop")
                raise ScenarioExecutionStopped

        current_time = time.time()
        elapsed = int(current_time - start_time)

        result = _post("/status_provisioning", data={"task_id": task_id})
        result.raise_for_status()
        result = result.json()

        if "status" in result:
            current_status = result["status"]

            if current_status == "ERROR":
                error_message = result["error_msg"]
                finished = True
                raise Exception(
                    f"Error during provisioning operation: '{error_message}'"
                )
            elif current_status == "FINISHED":
                finished = True

        # Two ways to display output
        if stream_output:
            # Stream the output of the provisioning task as it comes
            if "logs" not in result:
                logger.warning(
                    "   [+] Can not stream the output of ansible, reverting back to standard output"
                )
                stream_output = False
                display_idx = 0
            else:

                # Only print what is new in the output
                new_output = result["logs"][len(provisioning_output) :]
                for line in new_output.splitlines():
                    if line == "ANSIBLE OUTPUT END":
                        finishing = True
                        continue

                    logger.info(f"   [+]    {line}")

                # Record the full output so far
                provisioning_output = result["logs"]

                if provisioning_output != "" or result["logs"] != "":
                    starting = False

                if starting:
                    # At the begining, reassure the user with messages signaling it is going to start
                    if display_idx % 3 == 0:
                        logger.info("   [+] Provisioning task starting...")
                    display_idx += 1
                elif finishing:
                    # At the end reassure the user with messages signaling it is going to stop
                    if display_idx % 3 == 0:
                        logger.info("   [+] Provisioning task stopping...")
                    display_idx += 1

        else:
            # Just display messages showing the user that something is happenning in the background,
            # every 10 seconds or so
            if display_idx % 10 == 0:
                if log_suffix is not None:
                    logger.info(
                        f"   [+] Currently provisioning {log_suffix} for {elapsed} seconds (timeout at {timeout} seconds)"
                    )
                else:
                    logger.info(f"   [+] Currently provisioning for {elapsed} seconds")
            display_idx += 1

    if not finished:
        error_msg = f"[-] Unable to terminate operation before timeout of {timeout} seconds. Stopping operation."
        result = provisioning_stop(task_id)
        stopped = result["status"] == "STOPPED"
        if stopped:
            result["result"] = dict()
            result["result"]["error_msg"] = error_msg
            return result
        else:
            raise Exception("Unable to stop provisioning task")

    # Retrieve task logs, if any
    try:
        logs = provisioning_report(task_id)["logs"]
    except Exception:
        logs = ""

    result = _post("/result_provisioning", data={"task_id": task_id})
    result.raise_for_status()
    result = result.json()

    success = result["status"] == "FINISHED" and result["result"]["success"] is True

    provisioning_duration_seconds = int(time.time() - start_time)

    if success:
        logger.info(
            f"[+] Provisioning was correctly executed in {provisioning_duration_seconds} seconds"
        )
    else:
        error_msg = result["result"]["error_msg"]
        logger.error(
            f"[-] Provisioning was executed in {provisioning_duration_seconds} seconds with error: {error_msg}"
        )
    result["logs"] = logs
    return result


def __wait_for_the_operation_to_start(task_id: str) -> bool:

    running = False
    timeout = 10
    start_time = time.time()
    while not (running or (time.time() - start_time) > timeout):

        if cbk_check_stopped is not None:
            if cbk_check_stopped() is True:
                logger.info("   [+]    Current process was asked to stop")
                raise ScenarioExecutionStopped

        result = _post("/status_provisioning", data={"task_id": task_id})
        result.raise_for_status()
        result = result.json()
        running = result["status"] == "RUNNING"
        time.sleep(1)

    if not running:
        logger.error(
            f"[-] Unable to start operation before timeout of {timeout} seconds"
        )

    return running


def _provisioning_handle_wait(
    wait: bool,
    task_id: str,
    log_suffix: str,
    timeout: int = 3600,
    stream_ansible: bool = False,
) -> Dict:

    result = {}

    if wait:
        # Wait for the operation to be completed in backend

        result = _provisioning_wait_until_complete(
            task_id=task_id,
            log_suffix=log_suffix,
            timeout=timeout,
            stream_output=stream_ansible,
        )
    else:
        result["status"] = "RUNNING"

    return result


def provisioning_report(task_id: str) -> dict:
    """Get ansible report from backend"""

    result = _post("/report_provisioning", data={"task_id": task_id})

    if result.status_code != 200:
        _handle_error(result, "Cannot get report from provisioning task")

    return result.json()
