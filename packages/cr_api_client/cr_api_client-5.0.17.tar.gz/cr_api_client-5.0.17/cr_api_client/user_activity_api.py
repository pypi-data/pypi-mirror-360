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
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests
from mantis_scenario_model.notification_model import Notification
from mantis_scenario_model.notification_model import NotificationStage
from mantis_scenario_model.lab_model import ScenarioExecutionStopped

from cr_api_client import core_api
from cr_api_client import shutil_make_archive_lock
from cr_api_client.config import cr_api_client_config
from cr_api_client.logger import logger
from mantis_scenario_model.common import RoleEnum
from mantis_scenario_model.node import TypeEnum


# Module variables
cbk_check_stopped = None
cbk_event = None

ActionPackSet = Dict[str, str]
ActionPackCategoryList = List[str]

# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: Any) -> Any:
    return requests.get(
        f"{cr_api_client_config.user_activity_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _post(route: str, **kwargs: Any) -> Any:
    return requests.post(
        f"{cr_api_client_config.user_activity_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _put(route: str, **kwargs: Any) -> Any:
    return requests.put(
        f"{cr_api_client_config.user_activity_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _delete(route: str, **kwargs: Any) -> Any:
    return requests.delete(
        f"{cr_api_client_config.user_activity_api_url}{route}",
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


def _handle_result(result: Dict, context: str) -> None:

    if "status" not in result:
        raise Exception(f"Cannot {context}: no status returned")

    status = result["status"]

    if status == "FAILED":
        if "error_message" not in result:
            raise Exception(f"Cannot {context}: no error_message returned")

        error_message = result["error_message"]

        raise Exception(f"Cannot {context}: {error_message}")

    if "task_id" not in result:
        raise Exception(f"Cannot {context}: no task_id returned")


def _zip_user_activity(user_activity_path: str, temp_dir: str) -> str:
    """Private function to zip a user_activity content"""
    zip_file_name = os.path.join(temp_dir, "user_activity")

    with shutil_make_archive_lock:
        shutil.make_archive(zip_file_name, "zip", user_activity_path)

    return "{}.zip".format(zip_file_name)


def get_version() -> str:
    """Return user_activity API version."""
    result = _get("/user_activity/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve User activity API version")

    return result.json()


# -------------------------------------------------------------------------- #
# User activity API
# -------------------------------------------------------------------------- #


def __get_user_activity_results(
    data: dict,
    task_infos: str,
    user_activity_file_results: Optional[str] = None,
) -> None:

    request = _get("/user_activity/result_user_activity", data=data)
    request.raise_for_status()

    result = request.json()

    user_activity_success = False

    if "result" in result:
        user_activity_results = result["result"]
        if user_activity_results is not None:
            if "success" in user_activity_results:
                user_activity_success = user_activity_results["success"]

                if user_activity_success:
                    logger.info(
                        f"[+] user activity was correctly executed for {task_infos}"
                    )
                else:
                    logger.error(
                        f"[-] user activity was executed with errors for {task_infos}"
                    )

            if user_activity_file_results is not None:
                # create file for json results
                try:
                    with open(user_activity_file_results, "w") as fd:
                        json.dump(user_activity_results, fd, indent=4)

                        logger.info(
                            f"[+] user activity results are available here: {user_activity_file_results}"
                        )

                except Exception as e:
                    logger.error(f"[-] Error while writing user activity results: {e}")

            if not user_activity_success:
                json_results = json.dumps(
                    user_activity_results, indent=4, separators=(",", ": ")
                )
                raise Exception(
                    f"Some action could not be played. See user activity result for more information: {json_results}"
                )


def __handle_wait(
    node_name: str,
    wait: bool,
    id_simulation: int,
    task_id: str,
    extra_infos: str = "",
    user_activity_file_results: Optional[str] = None,
) -> bool:
    current_status = ""
    data = {
        "task_id": task_id,
    }
    if wait:

        done = False
        running = False

        task_infos = f"task ID '{task_id}'"
        if len(extra_infos) > 0:
            task_infos = f"{extra_infos}"

        while not done:

            if cbk_check_stopped is not None:
                if cbk_check_stopped() is True:
                    logger.info("   [+]    Current process was asked to stop")
                    raise ScenarioExecutionStopped

            # Sleep before next iteration
            time.sleep(2)

            action_name = None

            result = _get("/activity_orchestrator/orchestrator_is_running")

            result.raise_for_status()
            result = result.json()
            orchestrator_error = "ERROR" in result
            if orchestrator_error is True:
                logger.error(f"Server error: {result['ERROR']}")
                return False

            orchestrator_running = result["RUNNING"] is True

            data_action = {"node_name": node_name}

            if orchestrator_running is True:
                result = _post(
                    "/activity_orchestrator/orchestrator_current_running_action",
                    data=data_action,
                )

                if result.status_code != 200:
                    _handle_error(
                        result,
                        "Cannot get current background running action from user activity API",
                    )
                result = result.json()
                action_name = result["action_name"]

            result = _get("/user_activity/status_user_activity", data=data)

            result.raise_for_status()

            result = result.json()

            if "status" in result:
                current_status = result["status"]

                if current_status == "RUNNING":

                    status_message = "running"
                    running = True

                elif current_status == "FINISHED":
                    status_message = "finished"
                    done = True

                elif current_status == "UNKNOWN":
                    if (
                        running is True
                    ):  # activity has been already run but doesn't exist anymore
                        done = True
                        status_message = "finished - result unknown"
                    else:
                        if action_name is None:
                            status_message = "not started yet"
                        else:
                            status_message = f"not started yet, {action_name} (background) is running"

            logger.info(
                f" [+] User activity on {node_name}, executing {task_infos}: {status_message}"
            )

        __get_user_activity_results(
            data=data,
            user_activity_file_results=user_activity_file_results,
            task_infos=task_infos,
        )

    return True


def user_activity_status(id_simulation: int, id_user_activity: str) -> Dict:
    """Get a particular user activity status on targeted simulation."""

    try:
        data = {
            "task_id": id_user_activity,
        }
        result = _get("/user_activity/status_user_activity", data=data)

        if result.status_code != 200:
            _handle_error(
                result, "Cannot get user activity status from user activity API. "
            )

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting user activity status: '{}'".format(e))


def all_activities_status(id_simulation: int) -> Dict:
    """Get all user activities status on targeted simulation."""

    try:
        result = _get(
            "/user_activity/all_activities_status",
            headers={"Content-Type": "application/json"},
        )

        if result.status_code != 200:
            _handle_error(
                result, "Cannot get user activity status from user activity API. "
            )

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting user activity status: '{}'".format(e))


def user_activity_result(id_simulation: int, id_user_activity: str) -> str:
    """Get user activity result on targeted simulation."""

    try:
        data = {
            "task_id": id_user_activity,
        }
        result = _get(
            "/user_activity/result_user_activity",
            data=data,
        )

        if result.status_code != 200:
            _handle_error(
                result, "Cannot get user activity result from user activity API"
            )

        return result.json()

    except Exception as e:
        raise Exception("Issue when getting user activity result: '{}'".format(e))


def user_activity_background_add_client_nodes(
    action_names: List[str] = list(),
    include_actions: bool = False,
    id_simulation: int = 1,
) -> str:
    """
    This function calls orchestrator_add_nodes and waits for successful completion.
    All nodes with "virtual_machine" type and "client" role will be added to the user activity background process, regarding to the ``action_names`` and include_actions parameters.

    :param action_names: The names of the meta ations to include or exclude for orchestrator process, default to empty list
    :type action_names: List[str], optional
    :param include_actions: If ``True`` the actions to consider are those declared in the list, if ``False`` all existing actions excepted those declared in the list. default to ``False``
    :type include_actions: boolean, optional
    :param id_simulation: The simulation ID to consider, defaults to 1
    :type id_simulation: int, optional

    """
    try:
        # keep only nodes of type 'virtual_machine' and role 'client'
        nodes = core_api.fetch_nodes(id_simulation)
        node_names = list()

        for node in nodes:
            if node["type"] == TypeEnum.VIRTUAL_MACHINE:
                if RoleEnum.CLIENT in node["roles"]:
                    node_name = node["name"]
                    logger.debug(
                        f"User activity background will be played on this virtual machine: {node_name}"
                    )
                    node_names.append(node_name)

        available_action_names = list()
        result = _get("/activity_orchestrator/orchestrator_predefined_scenarios_list")
        result.raise_for_status()
        result = result.json()
        available_action_names = result["action_names"]

        # check if action_names exist
        for action_name in action_names:
            if action_name not in available_action_names:
                message = f"The '{action_name}' predefined meta action is unknown."
                message += f" The available actions are the following: {available_action_names}"
                raise Exception(message)

        data = {
            "id_simulation": id_simulation,
            "node_names": str(node_names),
            "action_names": json.dumps(action_names),
            "include_actions": include_actions,
        }

        result = _post(
            "/activity_orchestrator/orchestrator_add_nodes",
            data=data,
        )

        if result.status_code != 200:
            _handle_error(
                result, "Cannot get user activity result from user activity API"
            )

        return result.json()

    except Exception as e:
        raise Exception("Issue when calling orchestrator_add_nodes: '{}'".format(e))


def user_activity_background_add_node(
    node_name: str,
    action_names: List[str] = list(),
    include_actions: bool = False,
    action_pack_categories: ActionPackCategoryList = list(),
    id_simulation: int = 1,
) -> str:
    """
    This function calls orchestrator_add_node and waits for successful completion.
    The "node_name" node will be added to the user activity background process.

    :param id_simulation: The simulation ID to consider, defaults to 1
    :type id_simulation: int
    :param node_name: The name of the node to register for orchestrator process
    :type node_name: str
    :param action_names: The names of the meta ations to include or exclude for orchestrator process, default to empty list
    :type action_names: List[str], optional
    :param include_actions: If ``True`` the actions to consider are those declared in the list, if ``False`` all existing actions excepted those declared in the list. default to ``False``
    :type include_actions: boolean, optional

    :param action_pack_categories: The list of the categories of the meta-actions to select randomly, default to empty list
    :type action_pack_categories: List[str], optional
    """
    try:
        data = {
            "id_simulation": id_simulation,
            "node_name": node_name,
            "action_names": json.dumps(action_names),
            "include_actions": include_actions,
            "action_pack_categories": json.dumps(action_pack_categories),
        }

        result = _post(
            "/activity_orchestrator/orchestrator_add_node",
            data=data,
        )

        if result.status_code != 200:
            _handle_error(
                result, "Cannot get user activity result from user activity API"
            )

        return result.json()

    except Exception as e:
        raise Exception("Issue when calling orchestrator_add_node: '{}'".format(e))


def user_activity_background_remove_node(node_name: str) -> str:
    """
    This function calls orchestrator_remove_node and waits for successful completion.
    The "node_name" node will be removed from the user activity background process.

    :param id_simulation: The simulation ID to consider, defaults to 1
    :type id_simulation: int
    :param node_name: The name of the node to unregister
    :type node_name: str
    """
    try:
        data = {"node_name": node_name}

        result = _post(
            "/activity_orchestrator/orchestrator_remove_node",
            data=data,
        )

        if result.status_code != 200:
            _handle_error(
                result, "Cannot get user activity result from user activity API"
            )

        return result.json()

    except Exception as e:
        raise Exception("Issue when calling orchestrator_remove_node: '{}'".format(e))


def user_activity_background_start(
    timeout: int = 3600 * 24,
    debug_mode: str = "full",
    speed: str = "normal",
    record_video: bool = True,
    write_logfile: bool = True,
) -> str:
    """
    This function starts orchestrator to play user activities in background on nodes

    :param timeout: The duration while the orchestrator is running, defaults to 24 hours
    :type timeout: int, optional
    :param debug_mode: The verbosity level of the user activities log messages, defaults to ``full`` (all messages including Sikulix messages). Other possible values are ``off`` (no message) or ``on`` (messages without Sikulix messages)
    :type debug_mode: str, optional
    :param speed: The speed of the user activities, defaults to ``normal``. Other possible values are ``slow`` (slower) or ``fast`` (faster)
    :type speed: str, optional
    :param record_video: If ``True`` The user activities are recorded in a video file, defaults to ``True``
    :type record_video: boolean, optional
    :param write_logfile: If ``True`` The user activities result is written in a json file, defaults to ``True``
    :type write_logfile: boolean, optional

    """
    try:
        logger.info("[+] Starting user activity orchestrator...")
        data = {
            "timeout": timeout,
            "debug_mode": debug_mode,
            "speed": speed,
            "record_video": record_video,
            "write_logfile": write_logfile,
        }

        result = _post(
            "/activity_orchestrator/orchestrator_start",
            data=data,
        )

        if result.status_code != 200:
            _handle_error(result, "Cannot start orchestrator.")
        logger.info("[+] Orchestrator started.")

        return result.json()

    except Exception as e:
        raise Exception("Issue when calling orchestrator_start: '{}'".format(e))


def user_activity_play_user_scenario(
    scenario_path: str,
    node_name: str,
    scenario_data: Dict = dict(),
    id_simulation: int = 1,
    debug_mode: str = "full",
    wait: bool = True,
    speed: str = "normal",
    record_video: bool = True,
    write_logfile: bool = True,
    user_activity_file_results: Optional[str] = None,
    action_packs: ActionPackSet = dict(),
) -> bool:
    """
    This function calls orchestrator_play_user_scenario and waits the end of the scenario if asked

    :param scenario_path: The local path where the scenario template file is stored
    :type scenario_path: str
    :param node_name: The name of the node where to play the scenario
    :type node_name: str
    :param scenario_data: A dictionary of many data (name/value) to apply to the scenario template, default to empty dictionary
    :type scenario_data: Dict[str, str], optional
    :param id_simulation: The simulation ID to consider, defaults to 1
    :type id_simulation: int, optional
    :param debug_mode: The verbosity level of the user activities log messages, defaults to ``full`` (all messages including Sikulix messages). Other possible values are ``off`` (no message) or ``on`` (messages without Sikulix messages)
    :type debug_mode: str, optional
    :param wait: if ``True``, wait for the scenario to end, default to ``True``
    :type wait: bool, optional
    :param speed: The speed of keystrokes and mouse activities (``slow``, ``normal``, ``fast``), default to ``normal``
    :type speed: str, optional
    :param record_video: if ``True``, record a video of user activities, default to ``False``
    :type record_video: bool, optional
    :param write_logfile: if ``True``, write server logs in a file, default to ``True``
    :type write_logfile: bool, optional
    :param user_activity_file_results: if ``True``, the name of a file which will contain the user activity results (written with JSON format) default to ``None``
    :type user_activity_file_results: str, optional
    :param action_packs: a dict of action packs to use to play the scenario, default to empty dict. Example: ``{'web_browser': 'web_browser/firefox'}``
    :type action_packs: Dict[str, str]
    """
    try:
        logger.info("[+] Play user scenario...")

        if not Path(scenario_path).exists():
            raise Exception(f"This scenario path doesn't exist: {scenario_path}")

        category_name = Path(scenario_path).parent.name
        action_name = Path(scenario_path).name
        scenario_name = str(Path(category_name) / action_name)

        if cbk_event is not None and callable(cbk_event) is True:
            event_data = f"Playing '{scenario_name}' activity"
            cbk_event(
                Notification(
                    event_data=event_data, stage=NotificationStage.user_activity
                )
            )

        data = {
            "scenario_name": scenario_name,
            "node_name": node_name,
            "scenario_data": json.dumps(scenario_data),
            "debug_mode": debug_mode,
            "speed": speed,
            "record_video": record_video,
            "write_logfile": write_logfile,
            "action_packs": json.dumps(action_packs),
        }

        with TemporaryDirectory(
            prefix="cyber_range_cr_user_activity_play_user_scenario"
        ) as temp_dir:
            # Zipping user activity files
            zip_file_name = _zip_user_activity(scenario_path, temp_dir)
            scenario_files = open(zip_file_name, "rb")
            files = {"scenario_files": scenario_files}

            try:
                activity_success = False
                request = _post(
                    "/activity_orchestrator/orchestrator_play_user_scenario",
                    data=data,
                    files=files,
                )

                if request.status_code != 200:
                    _handle_error(request, "Cannot play user scenario")

                result = request.json()

                _handle_result(result=result, context="play user scenario")

                # Wait for the operation to be completed in backend
                task_id = result["task_id"]

                logger.info(f"  [+]  User scenario task ID: {task_id}")

                activity_success = __handle_wait(
                    node_name=node_name,
                    wait=wait,
                    user_activity_file_results=user_activity_file_results,
                    id_simulation=id_simulation,
                    task_id=task_id,
                    extra_infos=scenario_name,
                )
                return activity_success

            finally:
                scenario_files.close()

    except ScenarioExecutionStopped:
        # Propagate exception to upper level
        raise
    except Exception as e:
        raise Exception("Issue when getting user scenario result: '{}'".format(e))


def user_activity_play_predefined_scenario(
    scenario_name: str,
    node_name: str,
    scenario_data: Dict = dict(),
    id_simulation: int = 1,
    debug_mode: str = "full",
    wait: bool = True,
    speed: str = "normal",
    record_video: bool = True,
    write_logfile: bool = True,
    user_activity_file_results: Optional[str] = None,
    action_packs: ActionPackSet = dict(),
) -> bool:
    """
    This function calls orchestrator_play and waits the end of the scenario if asked

    :param scenario_name: The name of the meta-action to play
    :type scenario_name: str
    :param node_name: The name of the node where to play the scenario
    :type node_name: str
    :param scenario_data: A dictionary of many data (name/value) to apply to the scenario template, defaults to empty dictionary
    :type scenario_data: Dict[str, str], optional
    :param id_simulation: The simulation ID to consider, defaults to 1
    :type id_simulation: int
    :param debug_mode: The verbosity level of the user activities log messages, defaults to ``full`` (all messages including Sikulix messages). Other possible values are ``off`` (no message) or ``on`` (messages without Sikulix messages)
    :type debug_mode: str, optional
    :param wait: if ``True``, wait for the scenario to end, defaults to ``True``
    :type wait: bool, optional
    :param speed: The speed of keystrokes and mouse activities (``slow``, ``normal``, ``fast``), default to ``normal``
    :type speed: str, optional
    :param record_video: if ``True``, record a video of user activities, default to ``True``
    :type record_video: bool, optional
    :param write_logfile: if ``True``, write server logs in a file, default to ``True``
    :type write_logfile: bool, optional
    :param user_activity_file_results: if ``True``, the name of a file which will contain the user activity results (written with JSON format) default to ``None``
    :type user_activity_file_results: str, optional
    :param action_packs: a dict of action packs to use to play the scenario, default to empty dict. Example: ``{'web_browser': 'web_browser/firefox'}``
    :type action_packs: Dict[str, str]

    """
    try:
        logger.info("[+] Play predefined scenario...")
        data = {
            "scenario_name": scenario_name,
            "node_name": node_name,
            "scenario_data": json.dumps(scenario_data),
            "debug_mode": debug_mode,
            "speed": speed,
            "record_video": record_video,
            "write_logfile": write_logfile,
            "action_packs": json.dumps(action_packs),
        }

        activity_success = False

        request = _post(
            "/activity_orchestrator/orchestrator_play_predefined_scenario",
            data=data,
        )

        if request.status_code != 200:
            _handle_error(request, "Cannot insert scenario in orchestrator.")

        result = request.json()

        _handle_result(result=result, context="play predefined scenario")

        task_id = result["task_id"]

        logger.info(f"  [+]  Predefined scenario task ID: {task_id}")

        activity_success = __handle_wait(
            node_name=node_name,
            wait=wait,
            user_activity_file_results=None,
            id_simulation=id_simulation,
            task_id=task_id,
            extra_infos=scenario_name,
        )

        return activity_success

    except Exception as e:
        raise Exception("Issue when getting predefined scenario result: '{}'".format(e))


def user_activity_background_stop(close_session=False) -> None:
    """
    This function calls orchestrator_stop and does not wait for return
    :param close_session: if ``True``, close all user sessions on nodes before stopping orchestrator, default to ``False``
    :type close_session: bool, optional
    """
    try:

        logger.info("[+] Stopping user activity orchestrator...")

        data = {"close_session": close_session}

        result = _post("/activity_orchestrator/orchestrator_stop", data=data)

        if result.status_code != 200:
            _handle_error(result, "Cannot stop orchestrator.")
        logger.info("[+] Orchestrator will stop after current background scenario end.")

        # waiting for orchestrator to be stopped
        stopped = False

        while not stopped:

            logger.info("[+] Waiting for user activity orchestrator to stop...")
            time.sleep(2)

            result = _get("/activity_orchestrator/orchestrator_is_running")

            result.raise_for_status()
            result = result.json()
            orchestrator_error = "ERROR" in result
            if orchestrator_error is True:
                error_message = f"Server error: {result['ERROR']}"
                logger.error(error_message)
                raise Exception(error_message)

            stopped = result["RUNNING"] is False

            if cbk_check_stopped is not None:
                if cbk_check_stopped() is True:
                    logger.info("   [+]    Current process was asked to stop")
                    return

        logger.info("[+] User activity orchestrator is stopped")

    except Exception as e:
        raise Exception("Issue when stopping orchestrator: '{}'".format(e))


def user_activity_background_override_predefined_scenario_default_value(
    scenario_name: str,
    param_name: str,
    param_value: Any,
) -> str:
    """
    This function calls orchestrator API in order to override predefined scenario parameter default value.

    :param scenario_name: The name of the predefined scenario to consider. Example: 'web_browser/visit_website'
    :type scenario_name: str
    :param param_name: The name of the parameter associated to the scenario. Example: 'URL'
    :type param_name: str
    :param param_value: The new parameter default value (any type is supported)
    :type param_value: Any

    """
    try:
        data = {
            "scenario_name": scenario_name,
            "param_name": param_name,
            "param_value": json.dumps(param_value),
        }

        route = "/activity_orchestrator/orchestrator_override_predefined_scenario_default_value"

        result = _post(route=route, data=data)

        if result.status_code != 200:
            _handle_error(result, "Cannot get result from orchestrator API")

        return result.json()

    except Exception as e:
        raise Exception(f"Issue when calling {route}: {e}")


def user_activity_background_reset_predefined_scenario_default_value(
    scenario_name: str,
    param_name: str,
) -> str:
    """
    This function calls orchestrator API in order to reset predefined scenario parameter default value.

    :param scenario_name: The name of the predefined scenario to consider. Example: 'web_browser/visit_website'
    :type scenario_name: str
    :param param_name: The name of the parameter associated to the scenario. Example: 'URL'
    :type param_name: str
    """
    try:
        data = {
            "scenario_name": scenario_name,
            "param_name": param_name,
        }

        route = "/activity_orchestrator/orchestrator_reset_predefined_scenario_default_value"

        result = _post(route=route, data=data)

        if result.status_code != 200:
            _handle_error(result, "Cannot get result from orchestrator API")

        return result.json()

    except Exception as e:
        raise Exception(f"Issue when calling {route}: {e}")
