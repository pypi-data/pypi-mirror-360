#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2024 AMOSSYS
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
# PYTHON_ARGCOMPLETE_OK
import argparse
import configparser
import json
import os
import pprint
import shutil
import sys
import time
import uuid
from collections import OrderedDict
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Set

import argcomplete
import requests
from mantis_dataset_model.dataset_analysis_model import DatasetAnalysisResult
from omegaconf import OmegaConf

try:
    from colorama import init
    from termcolor import colored

    HAS_COLOUR = True
except ImportError:
    HAS_COLOUR = False

import cr_api_client
import cr_api_client.core_api as core_api
import cr_api_client.provisioning_api as provisioning_api
from cr_api_client.cli_parser.provisioning_parser import add_provisioning_parser
import cr_api_client.redteam_api as redteam_api
import cr_api_client.user_activity_api as user_activity_api
from cr_api_client.config import cr_api_client_config
from cr_api_client.logger import logger
from cr_api_client.logger import configure_logger


# Initialize colorama
if HAS_COLOUR:
    init(autoreset=True)
else:
    # Override colored function to return first argument
    def colored(string: str, *args: Any, **kwargs: Any) -> str:  # noqa
        return string


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

    client_version = cr_api_client.__version__
    client_vers = Version(str_vers=client_version)
    client_fullversion = cr_api_client.__fullversion__
    logger.info(
        f"[+] cr_api_client version: {client_version} ({client_fullversion})".format(
            client_version
        )
    )

    logger.info("[+] APIs status")

    # Core API
    it_simulation_api_is_down = False
    logger.info("  [+] IT Simulation API")
    logger.info("    [+] address: {}".format(cr_api_client_config.core_api_url))
    try:
        core_api_version = core_api.get_version()
        core_vers = Version(str_vers=core_api_version)
    except requests.exceptions.ConnectionError:
        exit_code = 1
        it_simulation_api_is_down = True
        logger.warning(
            "    [-] API status: " + colored("not running !", "white", "on_red")
        )
    else:
        logger.info("    [+] API status: " + colored("OK", "grey", "on_green"))
        logger.info("    [+] version: {}".format(core_api_version))
        if core_vers.major != client_vers.major:
            exit_code = 1
            logger.info(
                "    [-] "
                + colored(
                    "Error: Core API major version ({}) mismatchs with cr_api_client major version ({})".format(
                        core_vers.major, client_vers.major
                    ),
                    "white",
                    "on_red",
                )
            )

    # User activity API
    logger.info("  [+] User activity API")
    logger.info(
        "    [+] address: {}".format(cr_api_client_config.user_activity_api_url)
    )
    try:
        user_activity_api_version = user_activity_api.get_version()
        user_activity_vers = Version(str_vers=user_activity_api_version)
    except requests.exceptions.ConnectionError:
        exit_code = 1
        logger.warning(
            "    [-] API status: " + colored("not running !", "white", "on_red")
        )
    else:
        logger.info("    [+] API status: " + colored("OK", "grey", "on_green"))
        logger.info("    [+] version: {}".format(user_activity_api_version))
        if user_activity_vers.major != client_vers.major:
            exit_code = 1
            logger.info(
                "    [-] "
                + colored(
                    "Error: User activity API major version ({}) mismatchs with cr_api_client major version ({})".format(
                        user_activity_vers.major, client_vers.major
                    ),
                    "white",
                    "on_red",
                )
            )

    # Provisioning API
    logger.info("  [+] Provisioning API")
    logger.info("    [+] address: {}".format(cr_api_client_config.provisioning_api_url))
    try:
        provisioning_api_version = provisioning_api.get_version()
        provisioning_vers = Version(str_vers=provisioning_api_version)
    except requests.exceptions.ConnectionError:
        exit_code = 1
        logger.warning(
            "    [-] API status: " + colored("not running !", "white", "on_red")
        )
    else:
        logger.info("    [+] API status: " + colored("OK", "grey", "on_green"))
        logger.info("    [+] version: {}".format(provisioning_api_version))
        if provisioning_vers.major != client_vers.major:
            exit_code = 1
            logger.info(
                "    [-] "
                + colored(
                    "Error: Provisioning API major version ({}) mismatchs with cr_api_client major version ({})".format(
                        provisioning_vers.major, client_vers.major
                    ),
                    "white",
                    "on_red",
                )
            )

    # Redteam API
    logger.info("  [+] Redteam API")
    logger.info("    [+] address: {}".format(cr_api_client_config.redteam_api_url))
    try:
        redteam_api_version = redteam_api.get_version()
        redteam_vers = Version(str_vers=redteam_api_version)
    except requests.exceptions.ConnectionError:
        exit_code = 1
        logger.warning(
            "    [-] API status: " + colored("not running !", "white", "on_red")
        )
    else:
        logger.info("    [+] API status: " + colored("OK", "grey", "on_green"))
        logger.info("    [+] version: {}".format(redteam_api_version))
        if redteam_vers.major != client_vers.major:
            exit_code = 1
            logger.info(
                "    [-] "
                + colored(
                    "Error: Redteam API major version ({}) mismatchs with cr_api_client major version ({})".format(
                        redteam_vers.major, client_vers.major
                    ),
                    "white",
                    "on_red",
                )
            )

    # Compute infractructure (manager + servers)
    logger.info("[+] Compute Servers")
    try:
        compute_infra_status = core_api.compute_infrastructure_status()
    except Exception as e:
        exit_code = 1
        if it_simulation_api_is_down:
            logger.warning(
                "  [-] "
                + colored("unknown, IT Simulation API is down", "white", "on_red")
            )
        else:
            logger.warning(
                "  [-] "
                + colored("Error", "white", "on_red")
                + " while fetching status of compute server: "
                + str(e)
            )
    else:
        for compute_server in compute_infra_status["compute_servers"]:
            if compute_server["api_activate"]:
                compute_server["api"] = "on tcp:" + str(compute_server["api_port"])
                if compute_server["api_ping"] is True:
                    compute_server["api_status"] = colored("OK", "grey", "on_green")
                else:
                    compute_server["api_status"] = colored("NOK", "white", "on_red")
            else:
                compute_server["api"] = "deactivated"
                compute_server["api_status"] = colored("NA", "white", "on_grey")

            # Libvirt is special: it is always installed and must be responding, even
            # if it is not used activly to run VMs on the compute server
            compute_server["libvirt"] = "on tcp: {}".format(
                compute_server["libvirt_port"]
            )
            if compute_server["libvirt_ping"] is True:
                compute_server["libvirt_status"] = colored("OK", "grey", "on_green")
            else:
                compute_server["libvirt_status"] = colored("NOK", "white", "on_red")

            if not compute_server["libvirt_activate"]:
                compute_server["libvirt_status"] += " (deactivated)"

            if compute_server["docker_activate"]:
                compute_server["docker"] = "on tcp: {}".format(
                    compute_server["docker_port"]
                )
                if compute_server["docker_ping"] is True:
                    compute_server["docker_status"] = colored("OK", "grey", "on_green")
                else:
                    compute_server["docker_status"] = colored("NOK", "white", "on_red")
            else:
                compute_server["docker"] = "deactivated"
                compute_server["docker_status"] = colored("NA", "white", "on_grey")

            if compute_server["is_master"] is True:
                is_master = " - master"
            else:
                is_master = ""

            logger.info(
                "  [+] '{}' (id {} uuid {}){}".format(
                    compute_server["name"],
                    compute_server["id"],
                    compute_server["uuid"],
                    is_master,
                )
            )
            logger.info(
                "    [+] cluster address: {cluster_host}".format_map(compute_server)
            )
            logger.info(
                "    [+] external address: {external_host}".format_map(compute_server)
            )
            logger.info(
                "    [+] {:24s}{}".format(
                    "api " + compute_server["api"], compute_server["api_status"]
                )
            )
            logger.info(
                "    [+] {:24s}{}".format(
                    "libvirt " + compute_server["libvirt"],
                    compute_server["libvirt_status"],
                )
            )
            logger.info(
                "    [+] {:24s}{}".format(
                    "docker " + compute_server["docker"],
                    compute_server["docker_status"],
                )
            )
            if compute_server["is_master"] is True:
                if compute_server["ovn_docker_driver_ping"] is True:
                    compute_server["ovn_docker_driver_status"] = colored(
                        "OK", "grey", "on_green"
                    )
                else:
                    compute_server["ovn_docker_driver_status"] = colored(
                        "NOK", "white", "on_red"
                    )
                logger.info(
                    "    [+] {:24s}{}".format(
                        "ovn docker driver ", compute_server["ovn_docker_driver_status"]
                    )
                )
                if compute_server["ovn_nb_ping"] is True:
                    compute_server["ovn_nb_status"] = colored("OK", "grey", "on_green")
                else:
                    compute_server["ovn_nb_status"] = colored("NOK", "white", "on_red")
                logger.info(
                    "    [+] {:24s}{}".format(
                        "ovn north bridge ", compute_server["ovn_nb_status"]
                    )
                )
                if compute_server["ovn_sb_ping"] is True:
                    compute_server["ovn_sb_status"] = colored("OK", "grey", "on_green")
                else:
                    compute_server["ovn_sb_status"] = colored("NOK", "white", "on_red")
                logger.info(
                    "    [+] {:24s}{}".format(
                        "ovn south bridge ", compute_server["ovn_nb_status"]
                    )
                )

            logger.info(
                "    [+] is_down {is_down}, last_heartbeat={last_heartbeat_timestamp}".format(
                    **compute_server
                )
            )

    if exit_code != 0:
        sys.exit(exit_code)


#
# 'init' related functions
#
def init_handler(args: Any) -> None:
    """Process initialization of mysql db and snapshots path."""

    logger.info("[+] Checking version")

    # Check version
    client_version = cr_api_client.__version__
    client_vers = Version(str_vers=client_version)

    try:
        core_api_version = core_api.get_version()
        core_vers = Version(str_vers=core_api_version)
    except requests.exceptions.ConnectionError:
        logger.info(
            "    [-] API status: " + colored("not running !", "white", "on_red")
        )
        sys.exit(1)
    if core_vers.major != client_vers.major:
        logger.info(
            "    [-] "
            + colored(
                "Error: Core API major version ({}) mismatchs with cr_api_client major version ({})".format(
                    core_vers.major, client_vers.major
                ),
                "white",
                "on_red",
            )
        )
        sys.exit(1)
    else:
        logger.info("  [+] client API version: {}".format(client_version))
        logger.info("  [+] server API version: {}".format(core_api_version))

    logger.info(
        "[+] Initialize IT Simulation API (reset database, reset compute servers, stop VMs, stop Docker containers, delete snaphots, ...)"
    )
    if args.delete_compute_servers:
        logger.info(
            "[+] Will also delete all compute server from database and forget about them"
        )
    core_api.reset(args.delete_compute_servers, keep_db=args.keep_db)


def baseboxes_fetch(args: Any) -> None:
    """Fetch baseboxes on compute servers"""
    logger.info("[+] Download baseboxes from remote storage")
    try:
        if args.basebox_id is not None:
            core_api.download_baseboxes_by_id(baseboxes=args.basebox_id)
        elif args.topology_file is not None:
            core_api.download_baseboxes_by_topology(topology_file=args.topology_file)
    except Exception as e:
        logger.error(f"Error when downloading baseboxes: '{e}'")
        sys.exit(1)


#
# 'basebox_list' related functions
#
def baseboxes_list_handler(args: Any) -> None:
    """List available baseboxes, for use in simulations."""
    logger.info(
        "[+] List of baseboxes, ordered by system_type and operating_system (available baseboxes are in green, with path mentioned)"
    )
    baseboxes = core_api.fetch_baseboxes()

    # Build a list of system_type ('windows', 'linux', ...) and a dict of
    # operating_system where keys are system_type and values are operating_system name
    # ('Windows 7', 'Ubuntu 20.04', ...)
    system_type_list = set()
    operating_system_dict: Dict = OrderedDict()
    for basebox in baseboxes:
        if (
            "system_type" not in basebox.keys()
            or "operating_system" not in basebox.keys()
        ):
            logger.info(
                f"[-] The following basebox does not contain the required information (system_type or operating_system): {basebox}"
            )
            continue

        system_type = basebox["system_type"]
        system_type_list.add(system_type)

        if system_type not in operating_system_dict.keys():
            operating_system_dict[system_type] = set()
        operating_system_dict[system_type].add(basebox["operating_system"])

    # Trick to order the system_type set
    sorted_system_type_list = sorted(list(system_type_list))

    # Display baseboxes ordered by system_type and operating_system
    for current_system_type in sorted_system_type_list:
        logger.info("  [+] " + colored(f"{current_system_type}", attrs=["bold"]))

        for system_type, operating_system_list in operating_system_dict.items():
            if current_system_type == system_type:
                # Trick to order the operating_system_list set
                operating_system_list = sorted(list(operating_system_list))

                for operating_system in operating_system_list:
                    logger.info(
                        "    [+] " + colored(f"{operating_system}", attrs=["bold"])
                    )

                    for basebox in baseboxes:
                        if (
                            basebox["system_type"] == current_system_type
                            and basebox["operating_system"] == operating_system
                        ):
                            # Check if basebox is in local catalog
                            logger.info(
                                "      [+] '{}': {} (role: {}, language: {})".format(
                                    basebox["id"],
                                    basebox["description"],
                                    basebox["role"],
                                    basebox["language"],
                                )
                            )


#
# 'baseboxes_reload' related function
#
def baseboxes_reload_handler(args: Any) -> None:
    """List available baseboxes, for use in simulations."""
    logger.info("[+] Reload list of available baseboxes")
    core_api.reload_baseboxes()
    logger.info("[+] Done")


#
# 'baseboxes_verify' related function
#
def baseboxes_verify_handler(args: Any) -> None:
    """
    Handler for the verification of the baseboxes
    :param args: args.basebox_id (optional)
    :return: None
    """

    requested_basebox_id = args.basebox_id

    if requested_basebox_id is None:
        _baseboxes_verify_all_handler()
    else:
        _baseboxes_verify_one_handler(requested_basebox_id)


def _baseboxes_verify_all_handler() -> None:
    """
    Handler for the verification of all the baseboxes
    :return: None
    """
    logger.info("[+] Verifying the checksums of available baseboxes")
    result = core_api.verify_baseboxes()
    if "result" not in result or not result["result"]:
        logger.warning("[+] No result received...")
    else:
        compute_servers_with_valid_checksums: Dict[str, List[str]] = {}
        compute_servers_with_nonmissing_result: Dict[str, List[str]] = {}
        all_baseboxes: Set[str] = set()
        for compute_server_name, baseboxes_checksums in result["result"].items():
            for bb_id, verification_result in baseboxes_checksums.items():
                all_baseboxes.add(bb_id)
                if bb_id not in compute_servers_with_valid_checksums:
                    compute_servers_with_valid_checksums[bb_id] = []
                if bb_id not in compute_servers_with_nonmissing_result:
                    compute_servers_with_nonmissing_result[bb_id] = []

                if verification_result is not None:
                    compute_servers_with_nonmissing_result[bb_id].append(
                        compute_server_name
                    )
                if verification_result:
                    compute_servers_with_valid_checksums[bb_id].append(
                        compute_server_name
                    )

        for bb_id in all_baseboxes:
            compute_servers_with_missing_result = [
                cs_name
                for cs_name in result["result"].keys()
                if cs_name not in compute_servers_with_nonmissing_result[bb_id]
            ]
            compute_servers_with_invalid_checksums = [
                cs_name
                for cs_name in result["result"].keys()
                if cs_name not in compute_servers_with_valid_checksums[bb_id]
                and cs_name in compute_servers_with_nonmissing_result[bb_id]
            ]
            if (
                compute_servers_with_invalid_checksums
                or compute_servers_with_missing_result
            ):
                if compute_servers_with_invalid_checksums:
                    logger.error(
                        f"[+] {bb_id} has an incorrect checksum on {len(compute_servers_with_invalid_checksums)} (out of {len(result['result'])}) compute severs: {', '.join(compute_servers_with_invalid_checksums)}."
                    )
                if compute_servers_with_missing_result:
                    logger.error(
                        f"[+] No result for verification of {bb_id} on {len(compute_servers_with_missing_result)} (out of {len(result['result'])}) compute severs: {', '.join(compute_servers_with_missing_result)}."
                    )
            else:
                logger.info(
                    f"[+] {bb_id} has the correct checksum on all compute servers."
                )
    logger.info("[+] Done")


def _baseboxes_verify_one_handler(requested_basebox_id: str) -> None:
    logger.info("[+] Verifying the checksum of basebox {}".format(requested_basebox_id))
    result = core_api.verify_basebox(requested_basebox_id)
    if "result" not in result or not result["result"]:
        logger.warning("[+] No result received...")
    else:
        compute_servers_with_invalid_checksums: List[str] = []
        compute_servers_with_missing_result: List[str] = []
        for compute_server_name, baseboxes_checksums in result["result"].items():
            if (
                requested_basebox_id not in baseboxes_checksums
                or baseboxes_checksums[requested_basebox_id] is None
            ):
                compute_servers_with_missing_result.append(compute_server_name)
            elif not baseboxes_checksums[requested_basebox_id]:
                compute_servers_with_invalid_checksums.append(compute_server_name)

        if (
            compute_servers_with_invalid_checksums
            or compute_servers_with_missing_result
        ):
            if compute_servers_with_invalid_checksums:
                logger.error(
                    f"[+] {requested_basebox_id} has an incorrect checksum on {len(compute_servers_with_invalid_checksums)} (out of {len(result['result'])}) compute severs: {', '.join(compute_servers_with_invalid_checksums)}."
                )
            if compute_servers_with_missing_result:
                logger.error(
                    f"[+] No result for verification of {requested_basebox_id} on {len(compute_servers_with_missing_result)} (out of {len(result['result'])}) compute severs: {', '.join(compute_servers_with_missing_result)}."
                )
        else:
            logger.info(
                f"[+] {requested_basebox_id} has the correct checksum on all compute servers."
            )

    logger.info("[+] Done")


#
# 'websites_list' related functions
#
def websites_list_handler(args: Any) -> None:
    """List available websites, for use in simulations."""
    logger.info("[+] List of available websites")
    websites = core_api.fetch_websites()

    for website in websites:
        logger.info("  [+] {}".format(website))


#
# 'simu_create' simulation related functions
#
def simu_create_handler(args: Any) -> None:
    """Process YAML topology file and a resource folder and request core API to create a new
    simulation.

    """

    # Parameters
    topology_file = args.topology_file
    basebox_id = args.basebox_id
    topology_resources_paths = args.topology_resources_paths
    add_internet = args.add_internet
    add_host = args.add_host
    allocation_strategy = args.allocation_strategy

    # Sanity checks
    if topology_file is not None and basebox_id is not None:
        raise Exception(
            "Either a topology (-t) or a basebox ID (-b) is required to create a new simulation, but not both options"
        )
    if topology_file is not None:
        if add_internet:
            raise Exception("--add-internet is only available with -b option")
        if add_host:
            raise Exception("--add-host is only available with -b option")
    elif basebox_id is not None:
        if topology_resources_paths:
            raise Exception("-r <resource_path> is only available with -t option")
    else:
        raise Exception(
            "Either a topology (-t) or a basebox ID (-b) is required to create a new simulation"
        )

    # Compute elpased time
    t1 = time.time()

    try:
        if topology_file is not None:
            (id_simulation, new_nodes) = core_api.create_simulation_from_topology(
                topology_file=topology_file,
                topology_resources_paths=topology_resources_paths,
                allocation_strategy=allocation_strategy,
            )
        elif basebox_id is not None:
            (id_simulation, new_nodes) = core_api.create_simulation_from_basebox(
                basebox_id=basebox_id,
                add_internet=add_internet,
                add_host=add_host,
                allocation_strategy=allocation_strategy,
            )

        logger.info("[+] Created simulation ID: '{}'".format(id_simulation))
    except Exception as e:
        logger.error(f"Error when creating new simulation: '{e}'")
        sys.exit(1)
    finally:
        t2 = time.time()
        time_elapsed = t2 - t1
        logger.info("[+] Time elapsed: {0:.2f} seconds".format(time_elapsed))


#
# 'simu_extend' simulation related functions
#
def simu_extend_handler(args: Any) -> None:
    """Process YAML topology file and a resource folder and request IT
    simulation API to extend an existing simulation with new nodes and
    links.

    """

    # Parameters
    id_simulation = args.id_simulation
    topology_file = args.topology_file
    topology_resources_paths = args.topology_resources_paths
    allocation_strategy = args.allocation_strategy
    basebox_id = args.basebox_id
    switch_name = args.switch_name

    # Sanity checks
    if topology_file is not None and basebox_id is not None:
        raise Exception(
            "Either a topology (-t) or a basebox ID (-b) is required to extend a simulation, but not both options"
        )
    if topology_file is not None:
        pass
    elif basebox_id is not None:
        if topology_resources_paths:
            raise Exception("-r <resource_path> is only available with -t option")
        if switch_name is None:
            raise Exception(
                "With -b option, it is mandatory to define the switch name on which to plug the new node, with -s switch_name option"
            )
    else:
        raise Exception(
            "Either a topology (-t) or a basebox ID (-b) is required to extend a simulation"
        )

    # Compute elpased time
    t1 = time.time()

    try:
        if topology_file is not None:
            (id_simulation, new_nodes) = core_api.extend_simulation_from_topology(
                topology_file=topology_file,
                topology_resources_paths=topology_resources_paths,
                allocation_strategy=allocation_strategy,
                id_simulation=id_simulation,
            )
        elif basebox_id is not None:
            (id_simulation, new_nodes) = core_api.extend_simulation_from_basebox(
                basebox_id=basebox_id,
                switch_name=switch_name,
                allocation_strategy=allocation_strategy,
                id_simulation=id_simulation,
            )

        logger.info("[+] Extend simulation ID: '{}'".format(id_simulation))
    except Exception as e:
        logger.error(f"Error when extending simulation: '{e}'")
        sys.exit(1)
    finally:
        t2 = time.time()
        time_elapsed = t2 - t1
        logger.info("[+] Time elapsed: {0:.2f} seconds".format(time_elapsed))


#
# 'user_activity_play_user_scenario' simulation
#
def user_activity_play_user_scenario_handler(args: Any) -> None:
    """Play user_activity on targeted simulation."""
    # Parameters
    id_simulation = args.id_simulation
    scenario_path = args.scenario_path
    node_name = args.node_name
    file_results = args.user_activity_file_results
    debug_mode = args.user_activity_debug_mode
    speed = args.user_activity_speed
    record_video = args.user_activity_record_video
    write_logfile = args.user_activity_write_logfile
    wait = not args.user_activity_nowait

    try:
        user_activity_api.user_activity_play_user_scenario(
            id_simulation=id_simulation,
            scenario_path=scenario_path,
            node_name=node_name,
            debug_mode=debug_mode,
            wait=wait,
            speed=speed,
            record_video=record_video,
            write_logfile=write_logfile,
            user_activity_file_results=file_results,
        )
    except Exception as e:
        logger.info(f"Error when playing user_activity: '{e}'")
        sys.exit(1)


#
# 'user_activity_status' simulation
#
def user_activity_status_handler(args: Any) -> None:
    """Get user_activity status on targeted simulation."""
    # Parameters
    id_simulation = args.id_simulation
    task_id = args.task_id

    logger.info("[+] Get user_activity status for task '{}'".format(task_id))
    status = user_activity_api.user_activity_status(id_simulation, task_id)
    logger.info("  [+] Current status: {}".format(status["status"]))


#
# 'all_activities_status' simulation
#
def all_activities_status_handler(args: Any) -> None:
    """Get user_activity status on targeted simulation."""
    # Parameters
    id_simulation = args.id_simulation
    logger.info("[+] Get user_activity status for all user activities.")
    status = user_activity_api.all_activities_status(id_simulation)
    for task_id in status:
        logger.info("   [+] ID: '{}', STATUS: '{}'".format(task_id, status[task_id][0]))
        logger.info("       [+] Impacted machines:")
        for machine in status[task_id][1]:
            logger.info("           [+] '{}'".format(machine))


#
# 'simu_run' simulation
#
def simu_run_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    use_install_time = args.use_install_time
    net_start_probe = args.net_start_probe
    probe_id = args.probe_id
    timeout = args.timeout
    nodes = args.nodes  # Optional arg to filter on nodes concerned by the opration

    # Compute elpased time
    t1 = time.time()

    try:
        if net_start_probe is True:
            capture_in_progress = core_api.fetch_probe(probe_id)["capture_in_progress"]

            if capture_in_progress is True:
                errorMessage = "A capture is already in progress"
                raise ValueError(errorMessage)

            core_api.start_simulation(
                id_simulation,
                use_install_time,
                timeout=timeout,
                nodes=nodes,
            )

            try:
                core_api.net_start_probe(id_simulation, probe_id)
            except Exception as e:
                logger.info(e)
                sys.exit(1)
            else:
                logger.info("[+] Redirect network traffic to the probe interface")
        else:
            core_api.start_simulation(
                id_simulation,
                use_install_time,
                timeout=timeout,
                nodes=nodes,
            )
    except Exception as e:
        logger.info(f"Error when starting simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info("[+] Simulation is running...")
    finally:
        t2 = time.time()
        time_elapsed = t2 - t1
        logger.info("[+] Time elapsed: {0:.2f} seconds".format(time_elapsed))


#
# 'simu_status' of simulation
#
def simu_status_handler(args: Any) -> None:
    # Parameters
    requested_simulation_id = args.id_simulation

    simulations = core_api.fetch_simulations()

    for simulation in simulations:
        if (
            requested_simulation_id is None
            or requested_simulation_id == simulation["id"]
        ):
            id_simulation = simulation["id"]

            logger.info("[+] simulation id {}:".format(id_simulation))
            logger.info("  [+] name: {}".format(simulation["name"]))
            logger.info("  [+] status: {}".format(simulation["status"]))
            logger.info("  [+] error: {}".format(simulation["error_msg"]))

            # Fetch associated nodes
            nodes = core_api.fetch_nodes(id_simulation)

            logger.info("  [+] nodes:")
            for node in nodes:
                logger.info(
                    "    [+] ID: {}, name: {}, type: {}".format(
                        node["id"], node["name"], node["type"]
                    )
                )
                logger.info("      [+] status: {}".format(node["status"]))
                logger.info("      [+] start: {}".format(node["node_start_time"]))

                if node["hidden"] is True:
                    logger.info("      [+] hidden: {}".format(node["hidden"]))

                if node["active"] is False:
                    logger.info("      [+] active: {}".format(node["active"]))
                    continue

                if node["type"] == "virtual_machine":
                    logger.info(
                        "      [+] node stats: {} Mo, {} core(s)".format(
                            node["memory_size"],
                            node["nb_proc"],
                        )
                    )

                    # fetch basebox name
                    logger.info(
                        "      [+] basebox: {}".format(
                            node["basebox_id"],
                        )
                    )
                    logger.info(
                        "      [+] roles: {}".format(
                            node["roles"],
                        )
                    )
                    logger.info(
                        "      [+] current basebox path: {}".format(node["hard_drive"])
                    )
                    logger.info("      [+] uuid: {}".format(node["system_uid"]))
                    logger.info(
                        "      [+] SPICE url: {:>36}".format(
                            "spice://"
                            + node["compute_server_host"]
                            + ":"
                            + str(node["spice_port"])
                        )
                    )
                    logger.info(
                        "      [+] VNC url: {:>38}".format(
                            "vnc://"
                            + node["compute_server_host"]
                            + ":"
                            + str(node["vnc_port"])
                        )
                    )
                    logger.info(
                        "      [+] VNC websocket url: {:>28}".format(
                            "ws://"
                            + node["compute_server_host"]
                            + ":"
                            + str(node["vnc_websocket_port"])
                        )
                    )
                    if node["remote_password"] is not None:
                        logger.info(
                            f"      [+] Remote password (VNC/SPICE): {node['remote_password']}"
                        )
                    if node["username"] is not None:
                        logger.info(
                            "      [+] user account: {}:{}".format(
                                node["username"], node["password"]
                            )
                        )
                    else:
                        logger.info("      [+] user account: None")
                    if node["admin_username"] is not None:
                        logger.info(
                            "      [+] admin account: {}:{}".format(
                                node["admin_username"], node["admin_password"]
                            )
                        )
                    else:
                        logger.info("      [+] admin account: None")

                    if "cpe" in node and node["cpe"] is not None:
                        # Reworking CPE variable for proper display purposes :
                        split_cpe = node["cpe"].split()
                        logger.info("      [+] cpe:")
                        for i, cpe in enumerate(split_cpe):
                            logger.info(
                                "        [+] {}: {}".format(
                                    i,
                                    cpe,
                                )
                            )
                    else:
                        logger.info("      [+] cpe: Unknown")

                if node["type"] == "physical_machine":
                    logger.info(
                        "      [+] roles: {}".format(
                            node["roles"],
                        )
                    )
                elif node["type"] == "docker":
                    logger.info(
                        "      [+] node stats: {} Mo, {} core(s)".format(
                            node["memory_size"],
                            node["nb_proc"],
                        )
                    )
                    logger.info(
                        "      [+] docker image: {}".format(
                            node["base_image"],
                        )
                    )
                    logger.info(
                        "      [+] Interactive port: {}".format(node["terminal_port"])
                    )

                if node["type"] != "switch":
                    # Display network information
                    logger.info("      [+] network:")
                    for network_interface in node["network_interfaces"]:
                        logger.info(
                            "        [+] {}: IP address: {} (at runtime: {}), MAC address: {}".format(
                                network_interface["name"],
                                network_interface["ip_address"],
                                network_interface["ip_address_runtime"],
                                network_interface["mac_address"],
                            )
                        )
                        for domain in network_interface["domains"]:
                            logger.info(
                                "          [+] Domain name: '{}'".format(
                                    domain,
                                )
                            )


#
# 'simu_node_allocation' of simulation
#
def simu_node_allocation_handler(args: Any) -> None:
    # Parameters
    requested_simulation_id = args.id_simulation

    # Fetch associated nodes
    nodes = core_api.fetch_nodes(requested_simulation_id)
    compute_servers = core_api.fetch_compute_servers()

    cs_to_nodes: Dict = {}
    cs_used_resources = {}
    cs_id_to_cs = {}
    for node in nodes:
        if node["type"] not in ["virtual_machine", "docker"]:
            continue

        if not node["compute_server_id"]:
            k = None
        else:
            k = node["compute_server_id"]

        if k not in cs_used_resources:
            cs_to_nodes[k] = []
        cs_to_nodes[k].append(node)

        if k not in cs_used_resources:
            cs_used_resources[k] = {"cpu": 0, "mem": 0}
        cs_used_resources[k]["cpu"] += node["nb_proc"]
        cs_used_resources[k]["mem"] += node["memory_size"]

    for cs in compute_servers:
        cs_id_to_cs[cs["id"]] = cs

    for cs_id, cs_nodes in cs_to_nodes.items():
        if cs_id is None:
            logger.info("[+] Not allocated")
        else:
            logger.info(
                "[+] On compute server {name} (Host {external_host})".format(
                    **(cs_id_to_cs[cs_id])
                )
            )

        logger.info(
            "  [+] Total {cpu} CPU(s), {mem} memory".format(
                **(cs_used_resources[cs_id])
            )
        )

        for n in cs_nodes:
            logger.info(
                "  [+] Node {name} (id {id}, {nb_proc} CPU(s), {memory_size} memory)".format(
                    **n
                )
            )


#
# 'simu_domain' simulation
#
def simu_domains_handler(args: Any) -> None:
    # Parameters
    # id_simulation = args.id_simulation

    try:
        domains_dict = core_api.fetch_domains()
        if len(domains_dict) == 0:
            logger.info("[+] No domains défined in this simulation")
        else:
            logger.info("[+] Domains defined:")
            for domain_name, ip_address in domains_dict.items():
                logger.info(
                    "  [+] {}: {}".format(
                        ip_address,
                        domain_name,
                    )
                )
    except Exception as e:
        logger.info(f"Error when getting simulation domains: '{e}'")
        sys.exit(1)


#
# 'simu_pause' simulation
#
def simu_pause_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        core_api.pause_simulation(id_simulation)
    except Exception as e:
        logger.info(f"Error when pausing simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info("Simulation paused")


#
# 'simu_unpause' simulation
#
def simu_unpause_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        core_api.unpause_simulation(id_simulation)
    except Exception as e:
        logger.info(f"Error when unpausing simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info("Simulation unpaused")


#
# 'simu_create_backup' simulation
#
def simu_create_backup_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    nodes = args.nodes  # Optional arg to filter on nodes concerned by the opration

    try:
        core_api.create_backup_simulation(id_simulation, nodes=nodes)
    except Exception as e:
        logger.info(f"Error when creating backup of a simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info("Simulation backed up")


#
# 'simu_restore_backup' simulation
#
def simu_restore_backup_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    nodes = args.nodes  # Optional arg to filter on nodes concerned by the opration

    try:
        core_api.restore_backup_simulation(id_simulation, nodes=nodes)
    except Exception as e:
        logger.info(f"Error when restoring backup of a simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info("Simulation restored")


#
# 'simu_halt' simulation
#
def simu_halt_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    nodes = args.nodes

    try:
        core_api.halt_simulation(id_simulation, nodes=nodes)
    except Exception as e:
        logger.info(f"Error when halting simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info("Simulation halted")


#
# 'dataset_create_handler'
#
def dataset_create_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    dont_check_logs_path = args.dont_check_logs_path

    try:
        core_api.create_dataset(
            id_simulation, dont_check_logs_path=dont_check_logs_path
        )
    except Exception as e:
        logger.info(f"Error when creating dataset: '{e}'")
        sys.exit(1)
    else:
        logger.info("Dataset created")


def dataset_verify_handler(args: Any) -> None:
    dataset_id = args.dataset_id
    result: DatasetAnalysisResult
    try:
        if dataset_id is None:
            core_api.verify_dataset_all()
        else:
            result = core_api.verify_dataset(
                dataset_id,
            )
            logger.info("Dataset verification done")
            res: DatasetAnalysisResult = DatasetAnalysisResult(**result.dict())
            res.display(logger)
    except Exception as e:
        logger.info(f"Error when verifying dataset: '{e}'")
        sys.exit(1)


#
# 'simu_destroy' simulation
#
def simu_destroy_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        core_api.destroy_simulation(id_simulation)
    except Exception as e:
        logger.info(f"Error when destroying simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info("Simulation destroyed")


#
# 'simu_clone' simulation
#
def simu_clone_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        id_new_simulation = core_api.clone_simulation(id_simulation)
    except Exception as e:
        logger.info(f"Error when cloning simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info("Simulation cloned")
        logger.info("Created simulation ID: '{}'".format(id_new_simulation))


#
# 'net_create_probe' simulation
#
def net_create_probe_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    iface = args.iface
    pcap = args.pcap
    filter = args.filter
    direction = args.direction

    simu_nodes = {"switchs": args.switchs, "nodes": args.nodes}

    if direction not in ["both", "ingress", "egress"]:
        raise Exception(
            "Probe creation: parameter 'direction' should either be 'ingress', 'egress' or 'both'"
        )

    try:
        if not pcap and filter:
            errorMessage = "Filter defined without --pcap option"
            raise ValueError(errorMessage)
        probe_id = core_api.net_create_probe(
            id_simulation, simu_nodes, iface, pcap, filter, direction
        )
    except Exception as e:
        logger.info(f"Error when creating probe on simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info(f"Creating the probe '{probe_id}'")


#
# 'net_delete_probe' simulation
#
def net_delete_probe_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    probe_id = args.probe_id

    try:
        capture_in_progress = core_api.fetch_probe(probe_id)["capture_in_progress"]

        if capture_in_progress is True:
            core_api.net_stop_probe(id_simulation, probe_id)

        while capture_in_progress is True:
            time.sleep(1)
            capture_in_progress = core_api.fetch_probe(probe_id)["capture_in_progress"]

        core_api.delete_probe(probe_id)
    except Exception as e:
        logger.info(f"Error when deleting probe on simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info(f"Delete simulation probe {probe_id}")


#
# 'net_list_probes' simulation
#
def net_list_probes_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        result = core_api.fetch_list_probes(id_simulation)
        for probe_id, probe_items in result.items():
            logger.info("[+] Probe id : " + str(probe_id))
            logger.info("   [+] Interface : " + str(probe_items["iface"]))
            logger.info("   [+] Generate pcap file : " + str(probe_items["pcap"]))
            logger.info("   [+] Tcpdump filter : " + str(probe_items["filter"]))
            logger.info(
                "   [+] Capture in progress : "
                + str(probe_items["capture_in_progress"])
            )
            logger.info(
                "   [+] Collecting points : " + str(probe_items["collecting_points"])
            )
            logger.info("   [+] Mirorring direction : " + str(probe_items["direction"]))
    except Exception as e:
        logger.info(f"Error when printing the probe informations on simulation: '{e}'")
        sys.exit(1)


#
# 'net_start_probe' simulation
#
def net_start_probe_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    probe_id = args.probe_id

    try:
        probe = core_api.fetch_probe(probe_id)

        if probe["network_interfaces"] is None:
            errorMessage = "No capture points defined"
            raise ValueError(errorMessage)
        if probe["capture_in_progress"] is True:
            errorMessage = "A capture is already in progress"
            raise ValueError(errorMessage)

        core_api.net_start_probe(id_simulation, probe_id)
    except Exception as e:
        logger.info(e)
        sys.exit(1)
    else:
        logger.info("Redirect network traffic to the probe interface")


#
# 'net_stop_probe' simulation
#
def net_stop_probe_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    probe_id = args.probe_id

    try:
        capture_in_progress = core_api.fetch_probe(probe_id)["capture_in_progress"]

        if capture_in_progress is False:
            errorMessage = "No capture in progress"
            raise ValueError(errorMessage)

        core_api.net_stop_probe(id_simulation, probe_id)
    except Exception as e:
        logger.info(f"Error when stopping probe: '{e}'")
        sys.exit(1)
    else:
        logger.info("Stop redirection of network traffic to the probe interface")


#
# 'node_stats' simulation
#
def node_stats_handler(args: Any) -> None:
    try:
        if hasattr(args, "id_node"):
            response = core_api.get_node_statistics_by_id(args.id_node)
        else:
            raise AttributeError(
                "Unknown arguments for node_stats command: {}".format(args)
            )

    except Exception as e:
        logger.info(f"Error when getting statistics on simulation: '{e}'")
        sys.exit(1)

    stats = json.loads(response)
    logger.debug("Statistics on simulation gathered")
    logger.info(json.dumps(stats))


#
# 'node_logs' simulation
#
def node_logs_handler(args: Any) -> None:
    try:
        if hasattr(args, "id_node"):
            logs = core_api.node_logs(args.id_node)
            logger.info(f"[+] Node logs:\n{logs}")
        else:
            raise AttributeError(
                "Unknown arguments for node_logs command: {}".format(args)
            )

    except Exception as e:
        logger.error(e.__str__())
        sys.exit(1)


#
# 'node_exec' simulation
#
def node_exec_handler(args: Any) -> None:
    try:
        if hasattr(args, "id_node") and hasattr(args, "command"):
            (exit_code, stdout, stderr) = core_api.node_exec(args.id_node, args.command)
            logger.info(f"[+] exit code: {exit_code}")

            if stdout is not None:
                logger.info(f"[+] stdout:\n{stdout}")
            else:
                logger.info("[+] stdout:")

            if stderr is not None:
                logger.info(f"[+] stderr:\n{stderr}")
            else:
                logger.info("[+] stderr:")
        else:
            raise AttributeError(
                "Unknown arguments for node_exec command: {}".format(args)
            )

    except Exception as e:
        logger.error(e.__str__())
        sys.exit(1)


#
# 'node_memorydump' simulation
#
def node_memorydump_handler(args: Any) -> None:
    try:
        if hasattr(args, "id_node"):
            file_path, file_size = core_api.node_memorydump(args.id_node)
        else:
            raise AttributeError(
                "Unknown arguments for node_memorydump command: {}".format(args)
            )

    except Exception as e:
        logger.error(e.__str__())
        sys.exit(1)


#
# 'simu_delete' simulation
#
def simu_delete_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation

    try:
        core_api.delete_simulation(id_simulation)
    except Exception as e:
        logger.info(f"Error when deleting simulation: '{e}'")
        sys.exit(1)
    else:
        logger.info("[+] VMs destroyed")
        logger.info("[+] VMs snapshots deleted")
        logger.info("[+] Simulation deleted from database")


#
# 'simu_snap' simulation
#
def simu_snap_handler(args: Any) -> None:
    # Parameters
    id_simulation = args.id_simulation
    # core generates a YAML topology file
    # that will be located to /cyber_range_stuff...
    # This outfile is merely a copy of the generated
    # file
    output_file = args.output

    try:
        yaml = core_api.snapshot_simulation(id_simulation)
        with open(output_file, "w") as w:
            w.write(yaml)
        logger.info(f"[+] Snapshot done. Topology file stored at {output_file}")
    except Exception as e:
        logger.info(f"Error when creating snapshot for simulation: '{e}'")
        sys.exit(1)


#
# 'topo_add_websites' handler
#
def topo_add_websites_handler(args: Any) -> None:
    """Process YAML topology file and add docker websites node."""

    # Parameters
    input_topology_file = args.input_topology_file
    output_topology_file = args.output_topology_file
    websites = args.websites
    switch_name = args.switch_name

    try:
        topology_yaml = core_api.topology_file_add_websites(
            input_topology_file, websites, switch_name
        )
        with open(output_topology_file, "w") as w:
            w.write(topology_yaml)
        logger.info(
            f"[+] Topology updated. New topology stored at '{output_topology_file}'"
        )
    except Exception as e:
        logger.info(f"Error when adding websites to a topology: '{e}'")
        sys.exit(1)


#
# 'topo_add_dga' handler
#
def topo_add_dga_handler(args: Any) -> None:
    """Process YAML topology file and add dga on a docker node."""

    # Parameters
    input_topology_file = args.input_topology_file
    output_topology_file = args.output_topology_file
    resources_dir = args.resources_dir
    algorithm = args.algorithm
    switch_name = args.switch_name
    number = args.number

    try:
        # get the absolute path
        resources_dir = os.path.abspath(resources_dir)

        # Verify that the destination folder does not exist
        proceed = True
        if os.path.exists(resources_dir):
            logger.info(f"{resources_dir} already exists. It will be replaced.")
            while (reply := input("Continue? [y/n]").lower()) not in {  # noqa: E231
                "y",
                "n",
            }:
                logger.info(f"{resources_dir} already exists. It will be replaced.")
            if reply == "y":
                proceed = True
            if reply == "n":
                proceed = False

            if not proceed:
                logger.info("Stopping.")
                sys.exit(1)
            else:
                # remove resources_dir
                try:
                    if os.path.isfile(resources_dir):
                        os.remove(resources_dir)
                    else:
                        shutil.rmtree(resources_dir)
                except OSError as e:
                    logger.info("Error: %s - %s." % (e.filename, e.strerror))

        (topology_yaml, domains) = core_api.topology_file_add_dga(
            input_topology_file, algorithm, switch_name, number, resources_dir
        )
        # write the topology
        with open(output_topology_file, "w") as w:
            w.write(topology_yaml)
        logger.info(
            f"[+] Topology updated. New topology stored at '{output_topology_file}'"
        )

        # write the resources (empty html file by default)
        resources_path = os.path.join(os.getcwd(), resources_dir)
        os.mkdir(resources_path)

        websites_path = os.path.join(resources_path, "websites")
        os.mkdir(websites_path)

        nginx_conf_path = os.path.join(resources_path, "nginx-conf.d")
        os.mkdir(nginx_conf_path)

        # Create empty html file for each website
        for d in domains:
            os.mkdir(f"{websites_path}/{d}")
            Path(f"{websites_path}/{d}/index.html").touch()

        # write default nginx conf
        nginx_default = """
        server {
            listen       80;
            listen  [::]:80;
            server_name  localhost;
            location / {
                root   /usr/share/nginx/html;
                index  index.html index.htm;
            }
            error_page   500 502 503 504  /50x.html;
            location = /50x.html {
                root   /usr/share/nginx/html;
            }
        }
        """
        with open(f"{nginx_conf_path}/default.conf", "w") as default_conf:
            default_conf.write(nginx_default)

        # write local nginx conf
        template_generated_domains = """
                 server {{
                     listen      80;
                     listen      443;
                     server_name {0};
                     location / {{
                         root    /usr/share/nginx/html/{0};
                     }}
                 }}
                 """
        with open(f"{nginx_conf_path}/local-websites.conf", "a") as nginx_conf:
            for d in domains:
                nginx_conf.write(template_generated_domains.format(d))

        logger.info(f"[+] Resources created. They are stored at '{resources_path}'")
        logger.info(f"[+] Domains added: '{domains}'")

    except Exception as e:
        logger.info(f"Error when adding domains to a topology: '{e}'")
        sys.exit(1)


#
# 'topo_add_dns_server' handler
#
def topo_add_dns_server_handler(args: Any) -> None:
    """Process a YAML topology file and add a DNS server."""

    # Parameters
    input_topology_file = args.input_topology_file
    output_topology_file = args.output_topology_file
    switch_name = args.switch_name

    try:
        # get the absolute path
        input_topology_file = os.path.abspath(input_topology_file)
        resources_dir = os.path.join(os.path.dirname(output_topology_file), "resources")

        # Verify that the destination folder does not exist
        if os.path.exists(resources_dir):
            logger.info(f"[+] {resources_dir} already exists. It will be reused.")
        else:
            os.mkdir(resources_dir)

        (topology_yaml, dns_conf_content) = core_api.topology_file_add_dns_server(
            input_topology_file, switch_name, resources_dir
        )
        # write the topology
        with open(output_topology_file, "w") as w:
            w.write(topology_yaml)
        logger.info(
            f"[+] Topology updated. New topology stored at '{output_topology_file}'"
        )

        # write the resources
        dnsmasq_d_dir = os.path.join(resources_dir, "dnsmasq.d")
        if os.path.exists(dnsmasq_d_dir):
            logger.info(f"[+] {dnsmasq_d_dir} already exists. It will be replaced.")
            try:
                if os.path.isfile(dnsmasq_d_dir):
                    os.remove(dnsmasq_d_dir)
                else:
                    shutil.rmtree(dnsmasq_d_dir)
            except OSError as e:
                logger.info(
                    f"[+] Error while removing {dnsmasq_d_dir} on processing {e.filename}: {e.strerror}."
                )
        os.mkdir(dnsmasq_d_dir)

        dns_conf_file = os.path.join(dnsmasq_d_dir, "dns.conf")
        Path(dns_conf_file).touch()
        with open(dns_conf_file, "w") as conf_file:
            conf_file.write(dns_conf_content)

        logger.info(
            f"[+] Resources created. DNS configuration stored in '{dns_conf_file}'"
        )

    except Exception as e:
        logger.info(f"Error when adding a DNS server to a topology: '{e}'")
        sys.exit(1)


def compute_server_list_handler(args: Any) -> None:
    try:
        compute_servers = core_api.fetch_compute_servers()
    except Exception as e:
        logger.info(f"Error when fetching compute servers: '{e}'")
        sys.exit(1)
    else:
        # Compute Servers
        logger.info("[+] List of Compute Servers")
        for compute_server in compute_servers:
            if compute_server["is_master"] is True:
                is_master = " - master"
            else:
                is_master = ""

            logger.info(
                "  [+] '{}' (id {} uuid {}){}".format(
                    compute_server["name"],
                    compute_server["id"],
                    compute_server["uuid"],
                    is_master,
                )
            )
            logger.info("    [+] Host: {external_host}".format_map(compute_server))
            logger.info(
                "    [+] API is active ? {api_activate}. On port {api_port}".format(
                    **compute_server
                )
            )
            logger.info(
                "    [+] Libvirt is active ? {libvirt_activate}. With (tcp) port {libvirt_port}".format(
                    **compute_server
                )
            )
            logger.info(
                "    [+] Docker is active ? {docker_activate}. With (tcp) port {docker_port}".format(
                    **compute_server
                )
            )
            logger.info(
                "    [+] is_down {is_down}, last_heartbeat={last_heartbeat_timestamp}".format(
                    **compute_server
                )
            )


def compute_server_delete_handler(args: Any) -> None:
    # Parameters
    id_compute_server = args.id_compute_server

    try:
        core_api.delete_compute_server(id_compute_server)
    except Exception as e:
        logger.info(f"Error when deleting compute server: '{e}'")
        sys.exit(1)
    else:
        logger.info("Compute server deleted.")
        logger.info(
            "Note that it may be re-added automatically if the IT Simulation server receives a heartbeat from it."
        )


#
# 'redteam_tactics' related functions
#
def redteam_tactics_handler(args: Any) -> None:
    """List available Redteam tactics (based on MITRE ATT&CK)."""

    logger.info("[+] List of redteam tactics")
    tactics = redteam_api.list_tactics()

    for tactic in tactics:
        logger.info(f"  [+] {tactic['id']} - {tactic['name']}")

    logger.info("====")
    logger.info(f"  [+] Number of available redteam tactics: {len(tactics)}")


#
# 'redteam_workers' related functions
#
def redteam_workers_handler(args: Any) -> None:
    """List available Redteam workers."""

    # Parameters
    filter_tactic = args.filter_tactic
    filter_technique = args.filter_technique

    logger.info("[+] List of redteam workers")
    workers = redteam_api.list_workers()

    filter_count = 0
    for worker in workers:
        select = True

        if filter_tactic is not None:
            select = False
            for tactic in worker["mitre_data"]["tactics"]:
                if filter_tactic.lower() in [
                    tactic["name"].lower(),
                    tactic["id"].lower(),
                ]:
                    if filter_technique is not None:
                        if filter_technique == worker["mitre_data"]["technique"]["id"]:
                            select = True
                            filter_count += 1
                    else:
                        select = True
                        filter_count += 1
        else:
            # No filter_tactic
            if filter_technique is not None:
                select = False
                if filter_technique == worker["mitre_data"]["technique"]["id"]:
                    select = True
                    filter_count += 1

        if select:
            logger.info("----")
            logger.info(f"  [+] {worker['id']} - {worker['name']}")
            logger.info(
                f"    [+] Technique: {worker['mitre_data']['technique']['id']} - {worker['mitre_data']['technique']['name']}"
            )
            if (
                "id" in worker["mitre_data"]["subtechnique"].keys()
                and "name" in worker["mitre_data"]["subtechnique"].keys()
            ):
                logger.info(
                    f"    [+] Sub-technique: {worker['mitre_data']['subtechnique']['id']} - {worker['mitre_data']['subtechnique']['name']}"
                )
            logger.info(f"    [+] Description: {worker['description']}")
            logger.info("    [+] Tactics:")
            for tactic in worker["mitre_data"]["tactics"]:
                logger.info(f"      [+] {tactic['id']} - {tactic['name']}")

    logger.info("====")
    logger.info(f"  [+] Number of available redteam workers: {len(workers)}")

    if filter_count > 0:
        logger.info(f"  [+] Number of filtered workers: {filter_count}")


#
# 'redteam_worker' related functions
#
def redteam_worker_handler(args: Any) -> None:
    """Retrieve Redteam worker info."""

    # Parameters
    id_worker = args.id_worker

    logger.info("f[+] Redteam worker info for ID: {id_worker}")
    worker = redteam_api.worker_infos(id_worker)

    logger.info(f"  [+] {worker['id']} - {worker['name']}")
    logger.info(
        f"    [+] Technique: {worker['mitre_data']['technique']['id']} - {worker['mitre_data']['technique']['name']}"
    )
    if (
        "id" in worker["mitre_data"]["subtechnique"].keys()
        and "name" in worker["mitre_data"]["subtechnique"].keys()
    ):
        logger.info(
            f"    [+] Sub-technique: {worker['mitre_data']['subtechnique']['id']} - {worker['mitre_data']['subtechnique']['name']}"
        )
    logger.info(f"    [+] Description: {worker['description']}")
    logger.info("    [+] Tactics:")
    for tactic in worker["mitre_data"]["tactics"]:
        logger.info(f"      [+] {tactic['id']} - {tactic['name']}")


#
# 'redteam_attacks' related functions
#
def redteam_attacks_handler(args: Any) -> None:
    """List all attacks available and done."""

    # Parameters
    filter_status = args.filter_status

    logger.info("[+] List of available attacks")
    attacks = redteam_api.list_attacks()

    attack_sessions = redteam_api.attack_sessions()

    knowledge = redteam_api.attack_knowledge()

    filter_count = 0

    # Show available attacks by attack sessions
    for session in attack_sessions:
        # Try to find IP of compromised host on which the attack session is active
        compromised_host_ip = None
        if "hosts" in knowledge:
            for host in knowledge["hosts"]:
                for nic in host:
                    if (
                        nic is not None
                        and "ip" in nic
                        and "idHost" in nic
                        and nic["idHost"] == session["idHost"]
                    ):
                        compromised_host_ip = nic["ip"]

        logger.info(
            f"  [+] attack session: {session['idAttackSession']} - compromised host: {compromised_host_ip} - type: {session['type']} - direct_access: {session['direct_access']} - privilege_level: {session['privilege_level']} - uuid: {session['identifier']}"
        )

        for attack in attacks:
            # Find associated attack session

            # FIXME: attack['values'] is currently a string! Do not provide string dict from REST API
            dict_values = json.loads(attack["values"])
            if not isinstance(dict_values, dict):
                continue

            if "attack_session_id" not in dict_values:
                continue

            attack_session_id = dict_values["attack_session_id"]

            if attack_session_id != session["identifier"]:
                continue

            select = True
            if filter_status is not None:
                select = False
                if filter_status.lower() == attack["status"].lower():
                    select = True
                    filter_count += 1

            if select:

                # Retrieve attacks values, after removing redondant attack session infos
                attack_values = dict_values.copy()
                attack_values.pop("attack_session_type", None)
                attack_values.pop("attack_session_source", None)
                attack_values.pop("attack_session_id", None)

                logger.info(
                    f"    [+] {attack['idAttack']} - {attack['worker']['id']} - {attack['worker']['mitre_data']['technique']['name']} - {attack['worker']['name']} - {attack['status']} - values:{attack_values}"
                )

    # Show available attacks not tied to an attack session
    logger.info("  [+] direct attacks (no attack session)")
    for attack in attacks:
        # Find attacks with no attack session
        in_attack_session = True

        # FIXME: attack['values'] is currently a string! Do not provide string dict from REST API
        dict_values = json.loads(attack["values"])
        if not isinstance(dict_values, dict):
            in_attack_session = False
        else:
            if "attack_session_id" not in dict_values:
                in_attack_session = False

        if in_attack_session is False:

            # Retrieve attacks values, after removing redondant attack session infos
            attack_values = dict_values.copy()

            logger.info(
                f"    [+] {attack['idAttack']} - {attack['worker']['id']} - {attack['worker']['mitre_data']['technique']['name']} - {attack['worker']['name']} - {attack['status']} - values:{attack_values}"
            )

    logger.info("====")
    logger.info(f"  [+] Number of available attacks: {len(attacks)}")

    if filter_status is not None:
        logger.info(f"  [+] Number of filtered attacks: {filter_count}")


#
# 'redteam_attack' related functions
#
def redteam_attack_handler(args: Any) -> None:
    """Return status, output and infrastructure for an attack."""

    # Parameters
    id_attack = args.id_attack

    logger.info("[+] Attack infos")
    result = redteam_api.attack_infos(id_attack)

    logger.info(f"  [+] Status: {result['status']}")
    logger.info(f"  [+] Output: {result['output']}")
    logger.info(f"  [+] Infrastructure: {result['infrastructure']}")


#
# 'redteam_knowledge' related functions
#
def redteam_knowledge_handler(args: Any) -> None:
    """Get the attack knowledge (attack hosts and sessions)."""

    logger.info("[+] Attack knowledge")
    knowledge = redteam_api.attack_knowledge()

    pp = pprint.PrettyPrinter(compact=True, width=160)
    pp.pprint(knowledge)


#
# 'redteam_sessions' related functions
#
def redteam_sessions_handler(args: Any) -> None:
    """Show available redteam attack sessions."""

    logger.info("[+] Attack sessions")
    attack_sessions = redteam_api.attack_sessions()

    knowledge = redteam_api.attack_knowledge()

    for session in attack_sessions:
        compromised_host_ip = None
        if "hosts" in knowledge:
            for host in knowledge["hosts"]:
                for nic in host:
                    if nic is not None:
                        if "ip" in nic and "idHost" in nic:
                            if nic["idHost"] == session["idHost"]:
                                compromised_host_ip = nic["ip"]
        logger.info(
            f"  [+] {session['idAttackSession']} - compromised host: {compromised_host_ip} - type: {session['type']} - direct_access: {session['direct_access']} - privilege_level: {session['privilege_level']} - uuid: {session['identifier']}"
        )


#
# 'redteam_infras' related functions
#
def redteam_infras_handler(args: Any) -> None:
    """Show redteam attack infrastructures."""

    logger.info("[+] Attack infrastructures")
    infras = redteam_api.infrastructures()

    for infra in infras:
        logger.info(f"  [+] {infra}")


#
# 'redteam_play' related functions
#
def redteam_play_handler(args: Any) -> None:
    """Play an attack based on its ID."""

    # Parameters
    id_attack = args.id_attack
    wait = not args.redteam_nowait
    debug = args.debug_mode

    logger.info(f"[+] Play attack ID {id_attack}")

    # Retrieve attack name
    # TODO: attack_name seems to be useless in this API. Only the id_attack is necessary.
    redteam_api.execute_attack_by_id(
        id_attack, "ATTACK_NAME", waiting_worker=wait, debug=debug
    )

    logger.info("[+] Attack executed")


#
# 'redteam_reset' related functions
#
def redteam_reset_handler(args: Any) -> None:
    """Reset redteam API."""

    logger.info("[+] Reset redteam API")
    redteam_api.reset_redteam()


#
# 'redteam_logs' related functions
#
def redteam_logs_handler(args: Any) -> None:
    """Get logs from redteam workers."""

    logger.info("[+] Logs from redteam workers")
    redteam_logs = redteam_api.logs()

    attacks = redteam_api.list_attacks()

    for id_source_log, logs in redteam_logs.items():
        print("")  # Empty print to enhance visibility of log separation

        for attack in attacks:
            if str(attack["idAttack"]) == str(id_source_log):
                logger.warning(
                    f"  [+] Source log: {id_source_log} - attack: {attack['worker']['id']}"
                )
                break
        else:
            logger.warning(f"  [+] Source log: {id_source_log} (no associated attack)")

        print("")  # Empty print to enhance visibility of log separation

        for log in logs:
            print(log)


#
# 'redteam_log' related functions
#
def redteam_log_handler(args: Any) -> None:
    """Get logs from a specific redteam worker."""

    # Parameters
    id_attack = args.id_attack

    logger.info(f"[+] Logs from redteam worker {id_attack}")
    redteam_logs = redteam_api.attack_logs(id_attack)

    print("")  # Empty print to enhance visibility of log separation

    if not redteam_logs:
        logger.warning(f"  [+] Source log: {id_attack} (no associated attack)")

    for log in redteam_logs:
        print(log)


#
# 'redteam_report' related functions
#
def redteam_report_handler(args: Any) -> None:
    """Get the redteam report."""

    logger.info("[+] Report from redteam API")
    report = redteam_api.scenario_result()

    pp = pprint.PrettyPrinter(width=160)
    pp.pprint(report)


def create_cyber_range_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    # Config file argument
    parser.add_argument("--config", help="Configuration file")

    # Common debug argument
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug_mode",
        help="Activate debug mode (default: %(default)s)",
    )

    parser.add_argument(
        "--core-url",
        dest="core_api_url",
        help="Set core API URL (default: %(default)r)",
    )

    parser.add_argument(
        "--user-activity-url",
        dest="user_activity_api_url",
        help="Set user_activity API URL (default: %(default)r)",
    )

    parser.add_argument(
        "--provisioning-url",
        dest="provisioning_api_url",
        help="Set provisioning API URL (default: %(default)r)",
    )

    parser.add_argument(
        "--redteam-url",
        dest="redteam_api_url",
        help="Set redteam API URL (default: %(default)r)",
    )

    parser.add_argument("--cacert", dest="cacert", help="Set path to CA certs")

    parser.add_argument("--cert", dest="cert", help="Set path to client cert")

    parser.add_argument("--key", dest="key", help="Set path to client key")

    subparsers = parser.add_subparsers()

    # 'status' command
    parser_status = subparsers.add_parser("status", help="Get platform status")
    parser_status.set_defaults(func=status_handler)

    # 'init' command
    parser_init = subparsers.add_parser(
        "init",
        help="Initialize database (override previous simulations!)",
    )
    parser_init.add_argument(
        "--delete-compute-servers",
        action="store_true",
        default=False,
        help="If specified, will also delete all compute servers from the database (default %(default)s)",
    )
    parser_init.add_argument(
        "--keep-db",
        action="store_true",
        help="If specified, will NOT drop database if it already exists",
    )
    parser_init.set_defaults(func=init_handler)

    # 'websites_list' command
    parser_websites_list = subparsers.add_parser(
        "websites_list",
        help="List available websites",
    )
    parser_websites_list.set_defaults(func=websites_list_handler)

    # -----------------------
    # --- Basebox options
    # -----------------------

    # 'baseboxes_list' command
    parser_bb_list = subparsers.add_parser(
        "baseboxes_list",
        help="List available baseboxes",
    )
    parser_bb_list.set_defaults(func=baseboxes_list_handler)

    # 'baseboxes_reload' command
    parser_bb_reload = subparsers.add_parser(
        "baseboxes_reload",
        help="Reload available baseboxes",
    )
    parser_bb_reload.set_defaults(func=baseboxes_reload_handler)

    # 'baseboxes_verify' command
    parser_bb_verify = subparsers.add_parser(
        "baseboxes_verify",
        help="Verify available baseboxes",
    )
    parser_bb_verify.add_argument(
        "basebox_id", type=str, nargs="?", help="The basebox id"
    )
    parser_bb_verify.set_defaults(func=baseboxes_verify_handler)

    # 'baseboxes_fetch' command
    parser_bb_fetch = subparsers.add_parser(
        "baseboxes_fetch",
        help="Fetch baseboxes",
    )
    parser_bb_fetch_source = parser_bb_fetch.add_mutually_exclusive_group(required=True)
    parser_bb_fetch_source.add_argument(
        "-t",
        action="store",
        required=False,
        dest="topology_file",
        help="Input path of a YAML topology file",
    )
    parser_bb_fetch_source.add_argument(
        "-b",
        action="append",
        required=False,
        dest="basebox_id",
        help="ID of the basebox to fetch",
    )
    parser_bb_fetch.set_defaults(func=baseboxes_fetch)

    # -----------------------
    # --- Core/simu options
    # -----------------------

    # 'simu_create' simulation command
    parser_simu_create = subparsers.add_parser(
        "simu_create",
        help="Create a new simulation",
    )
    parser_simu_create.set_defaults(func=simu_create_handler)
    parser_simu_create.add_argument(
        "-t",
        action="store",
        required=False,
        dest="topology_file",
        help="Input path of a YAML topology file",
    )
    parser_simu_create.add_argument(
        "-b",
        action="store",
        required=False,
        dest="basebox_id",
        help="Basebox ID with which to create a simulation",
    )
    parser_simu_create.add_argument(
        "--add-internet",
        action="store_true",
        dest="add_internet",
        help="Add internet connectivity (only available with -b option)",
    )
    parser_simu_create.add_argument(
        "--add-host",
        action="store_true",
        dest="add_host",
        help="Add host connectivity (only available with -b option)",
    )
    parser_simu_create.add_argument(
        "--allocation-strategy",
        action="store",
        type=str,
        required=False,
        dest="allocation_strategy",
        help="Allocation strategy to use for allocating nodes to compute servers",
    )
    parser_simu_create.add_argument(
        "-r",
        action="store",
        required=False,
        nargs="*",
        dest="topology_resources_paths",
        help="Input path(s) for the simulation resources",
    )

    # 'simu_extend' simulation command
    parser_simu_extend = subparsers.add_parser(
        "simu_extend",
        help="Extend new nodes and links to an existing simulation",
    )
    parser_simu_extend.set_defaults(func=simu_extend_handler)
    parser_simu_extend.add_argument(
        "--id",
        type=int,
        action="store",
        required=True,
        dest="id_simulation",
        help="The simulation id",
    )
    parser_simu_extend.add_argument(
        "-t",
        action="store",
        required=False,
        dest="topology_file",
        help="Input path of a YAML topology file",
    )
    parser_simu_extend.add_argument(
        "--allocation-strategy",
        action="store",
        type=str,
        required=False,
        dest="allocation_strategy",
        help="Allocation strategy to use for allocating nodes to compute servers",
    )
    parser_simu_extend.add_argument(
        "-r",
        action="store",
        required=False,
        nargs="*",
        dest="topology_resources_paths",
        help="Input path(s) for the simulation resources",
    )
    parser_simu_extend.add_argument(
        "-b",
        action="store",
        required=False,
        dest="basebox_id",
        help="Basebox ID with which to extend a simulation",
    )
    parser_simu_extend.add_argument(
        "-s",
        action="store",
        required=False,
        dest="switch_name",
        help="Switch on which to plug the new node (only available with -b option)",
    )

    # 'simu_run' simulation command
    parser_simu_run = subparsers.add_parser("simu_run", help="Run a simulation")
    parser_simu_run.set_defaults(func=simu_run_handler)
    parser_simu_run.add_argument("id_simulation", type=int, help="The simulation id")
    parser_simu_run.add_argument(
        "--use_install_time",
        action="store_true",
        dest="use_install_time",
        help="Indicates that VM installation time will be used to set VMs boot time",
    )
    parser_simu_run.add_argument(
        "--net_start_probe",
        action="store_true",
        dest="net_start_probe",
        help="Redirect network traffic to the probe interface",
    )
    parser_simu_run.add_argument("probe_id", type=int, nargs="?", help="The probe id")
    parser_simu_run.add_argument(
        "--timeout",
        action="store",
        type=int,
        required=False,
        dest="timeout",
        default=300,
        help="Timeout for starting simulation (default to %(default)s seconds)",
    )
    parser_simu_run.add_argument(
        "-n",
        action="append",
        dest="nodes",
        help="Specify nodes to start. Can be called multiple times. By default, all simulation nodes will be started.",
    )

    # 'simu_status' simulation command
    parser_simu_status = subparsers.add_parser(
        "simu_status", help="Get status of a simulation or all simulations"
    )
    parser_simu_status.set_defaults(func=simu_status_handler)
    parser_simu_status.add_argument(
        "id_simulation", type=int, nargs="?", help="The simulation id"
    )

    # 'simu_node_allocation' simulation command
    parser_simu_node_allocation = subparsers.add_parser(
        "simu_node_allocation",
        help="Get repartition of nodes on compute servers for a given simulation",
    )
    parser_simu_node_allocation.set_defaults(func=simu_node_allocation_handler)
    parser_simu_node_allocation.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    # 'simu_domains' simulation command
    parser_simu_domains = subparsers.add_parser(
        "simu_domains",
        help="Get list of domains and related IP addresses for the simulation",
    )
    parser_simu_domains.set_defaults(func=simu_domains_handler)
    parser_simu_domains.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    # 'simu_pause' simulation command
    parser_simu_pause = subparsers.add_parser(
        "simu_pause",
        help="Pause a simulation (suspend VMs)",
    )
    parser_simu_pause.set_defaults(func=simu_pause_handler)
    parser_simu_pause.add_argument("id_simulation", type=int, help="The simulation id")

    # 'simu_unpause' simulation command
    parser_simu_unpause = subparsers.add_parser(
        "simu_unpause",
        help="Unpause a simulation (resume VMs)",
    )
    parser_simu_unpause.set_defaults(func=simu_unpause_handler)
    parser_simu_unpause.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    # 'simu_create_backup' simulation command
    parser_simu_create_backup = subparsers.add_parser(
        "simu_create_backup",
        help="Create backup of a simulation (that can be restored with simu_restore_backup command). Currently, only virtual machines are backed up.",
    )
    parser_simu_create_backup.set_defaults(func=simu_create_backup_handler)
    parser_simu_create_backup.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_simu_create_backup.add_argument(
        "-n",
        action="append",
        dest="nodes",
        help="Specify nodes to backup. Can be called multiple times. By default, all simulation nodes will be backed up.",
    )

    # 'simu_restore_backup' simulation command
    parser_simu_restore_backup = subparsers.add_parser(
        "simu_restore_backup",
        help="Restore backup of a simulation (that has been created with simu_create_backup command)",
    )
    parser_simu_restore_backup.set_defaults(func=simu_restore_backup_handler)
    parser_simu_restore_backup.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_simu_restore_backup.add_argument(
        "-n",
        action="append",
        dest="nodes",
        help="Specify nodes to restored from a backup. Can be called multiple times. By default, all simulation nodes will be restored.",
    )

    # 'simu_halt' simulation command
    parser_simu_halt = subparsers.add_parser(
        "simu_halt",
        help="Halt a simulation (stop VMs and save VMs state)",
    )
    parser_simu_halt.set_defaults(func=simu_halt_handler)
    parser_simu_halt.add_argument("id_simulation", type=int, help="The simulation id")
    parser_simu_halt.add_argument(
        "-n",
        action="append",
        dest="nodes",
        help="Specify nodes to halt. Can be called multiple times. By default, all simulation nodes will be stopped.",
    )

    # 'dataset_create' simulation command
    parser_dataset_create = subparsers.add_parser(
        "dataset_create",
        help="Create the dataset after stopping a simulation",
    )
    parser_dataset_create.set_defaults(func=dataset_create_handler)
    parser_dataset_create.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_dataset_create.add_argument(
        "--dont-check-logs-path",
        action="store_true",
        dest="dont_check_logs_path",
        help="Bypass the check for the logs path in the topology file",
    )

    # 'dataset_verify' simulation command
    parser_dataset_verify = subparsers.add_parser(
        "dataset_verify",
        help="Launch the dataset verification analysis",
    )
    parser_dataset_verify.set_defaults(func=dataset_verify_handler)
    parser_dataset_verify.add_argument(
        "-d",
        "--dataset_id",
        nargs="?",
        type=uuid.UUID,
        help="The simulation UUID4. If unspecified, assuming all datasets will be verified.",
    )

    # 'simu_destroy' simulation command
    parser_simu_destroy = subparsers.add_parser(
        "simu_destroy",
        help="Destroy a simulation (stop VMs and delete VMs state)",
    )
    parser_simu_destroy.set_defaults(func=simu_destroy_handler)
    parser_simu_destroy.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    # 'simu_snap' simulation command
    parser_simu_snap = subparsers.add_parser(
        "simu_snap",
        help="Create a snapshot of the entire simulation, that can be restored afterwards",
    )
    parser_simu_snap.set_defaults(func=simu_snap_handler)
    parser_simu_snap.add_argument("id_simulation", type=int, help="The simulation id")
    parser_simu_snap.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Path to the output YAML topology file",
    )

    # 'simu_clone' simulation command
    parser_simu_clone = subparsers.add_parser("simu_clone", help="Clone a simulation")
    parser_simu_clone.set_defaults(func=simu_clone_handler)
    parser_simu_clone.add_argument("id_simulation", type=int, help="The simulation id")

    # 'simu_delete' simulation command
    parser_simu_delete = subparsers.add_parser(
        "simu_delete",
        help="Delete a simulation",
    )
    parser_simu_delete.set_defaults(func=simu_delete_handler)
    parser_simu_delete.add_argument("id_simulation", type=int, help="The simulation id")

    # 'net_start_probe' simulation command
    parser_net_start_probe = subparsers.add_parser(
        "net_start_probe",
        help="Redirect network traffic to the probe interface",
    )
    parser_net_start_probe.set_defaults(func=net_start_probe_handler)
    parser_net_start_probe.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_net_start_probe.add_argument("probe_id", type=int, help="The probe id")

    # 'net_stop_probe' simulation command
    parser_net_stop_probe = subparsers.add_parser(
        "net_stop_probe",
        help="Stop redirection of network traffic to the probe interface",
    )
    parser_net_stop_probe.set_defaults(func=net_stop_probe_handler)
    parser_net_stop_probe.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_net_stop_probe.add_argument("probe_id", type=int, help="The probe id")

    # 'net_create_probe' simulation command
    parser_net_create_probe = subparsers.add_parser(
        "net_create_probe",
        help="Configure the network collecting points",
    )
    parser_net_create_probe.set_defaults(func=net_create_probe_handler)
    parser_net_create_probe.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_net_create_probe.add_argument(
        "--switch",
        required=False,
        nargs="+",
        action="append",
        dest="switchs",
        help="List of simulation nodes",
    )
    parser_net_create_probe.add_argument(
        "--node",
        type=str,
        action="append",
        required=False,
        dest="nodes",
        help="List of simulation nodes",
    )
    parser_net_create_probe.add_argument(
        "--iface",
        type=str,
        dest="iface",
        default=None,
        help="The probe network interface",
    )
    parser_net_create_probe.add_argument(
        "--pcap",
        action="store_true",
        dest="pcap",
        default=False,
        help="Records network streams in a pcap",
    )
    parser_net_create_probe.add_argument(
        "--filter", type=str, dest="filter", default=None, help="Tcpdump filter"
    )
    parser_net_create_probe.add_argument(
        "--direction",
        type=str,
        dest="direction",
        default="both",
        help="Select which traffic to monitor on the mirrored interface(s): either 'ingress' (traffic arriving), 'egress' (traffic sent) or 'both'",
    )

    # 'net_delete_probe' simulation command
    parser_net_delete_probe = subparsers.add_parser(
        "net_delete_probe",
        help="Reset the network collecting points configuration",
    )
    parser_net_delete_probe.set_defaults(func=net_delete_probe_handler)
    parser_net_delete_probe.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_net_delete_probe.add_argument("probe_id", type=int, help="The probe id")

    # 'net_list_probes' simulation command
    parser_net_list_probes = subparsers.add_parser(
        "net_list_probes",
        help="Print the network collecting points configuration",
    )
    parser_net_list_probes.set_defaults(func=net_list_probes_handler)
    parser_net_list_probes.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    # 'node_stats' simulation command
    parser_node_stats = subparsers.add_parser(
        "node_stats",
        help="Get resource statistics of a node. Note: you can get the node IDs using the simu_status command.",
    )
    parser_node_stats.set_defaults(func=node_stats_handler)
    parser_node_stats.add_argument("id_node", type=int, help="The node unique id")

    # 'node_logs' simulation command
    parser_node_logs = subparsers.add_parser(
        "node_logs",
        help="Retrieve logs from specified node (only work for Docker node).",
    )
    parser_node_logs.set_defaults(func=node_logs_handler)
    parser_node_logs.add_argument("id_node", type=int, help="The node unique id")

    # 'node_exec' simulation command
    parser_node_exec = subparsers.add_parser(
        "node_exec",
        help="Execute a command on specified node (only work for Docker node).",
    )
    parser_node_exec.set_defaults(func=node_exec_handler)
    parser_node_exec.add_argument("id_node", type=int, help="The node unique id")
    parser_node_exec.add_argument(
        "command",
        type=str,
        help="Command to execute",
    )

    # 'node_memorydump' simulation command
    parser_node_memorydump = subparsers.add_parser(
        "node_memorydump",
        help="Get the full raw memory dump of a node's RAM. Note: you can get the node IDs using the simu_status command.",
    )
    parser_node_memorydump.set_defaults(func=node_memorydump_handler)
    parser_node_memorydump.add_argument("id_node", type=int, help="The node unique id")

    # --------------------
    # --- Topology options
    # --------------------

    # 'topo_add_websites' command
    parser_topo_add_websites = subparsers.add_parser(
        "topo_add_websites", help="Add docker websites node to a topology"
    )
    parser_topo_add_websites.set_defaults(func=topo_add_websites_handler)
    parser_topo_add_websites.add_argument(
        "-t",
        "--topology",
        type=str,
        required=True,
        dest="input_topology_file",
        help="Path to the input YAML topology file",
    )
    parser_topo_add_websites.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        dest="output_topology_file",
        help="Path to the output YAML topology file that will be created",
    )
    parser_topo_add_websites.add_argument(
        "-s" "--switch",
        type=str,
        required=True,
        dest="switch_name",
        help="Switch name on which to add a docker node",
    )
    parser_topo_add_websites.add_argument(
        "-w" "--websites",
        type=str,
        required=True,
        nargs="+",
        dest="websites",
        help="List of websites to add, taken from the websites catalog",
    )

    # 'topo_add_dga' command
    parser_topo_add_dga = subparsers.add_parser(
        "topo_add_dga",
        help="Add docker websites node to a topology using a domain generation algorithm",
    )
    parser_topo_add_dga.set_defaults(func=topo_add_dga_handler)
    parser_topo_add_dga.add_argument(
        "-t",
        "--topology",
        type=str,
        required=True,
        dest="input_topology_file",
        help="Path to the input YAML topology file",
    )
    parser_topo_add_dga.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        dest="output_topology_file",
        help="Path to the output YAML topology file that will be created",
    )
    parser_topo_add_dga.add_argument(
        "-s",
        "--switch",
        type=str,
        required=True,
        dest="switch_name",
        help="Switch name on which to add a docker node",
    )
    parser_topo_add_dga.add_argument(
        "-a",
        "--algorithm",
        type=str,
        required=True,
        dest="algorithm",
        help="Algorithm to choose for the generation of the domains",
    )
    parser_topo_add_dga.add_argument(
        "-n",
        "--number",
        type=int,
        required=True,
        dest="number",
        help="Number of domains to generate",
    )
    parser_topo_add_dga.add_argument(
        "-r",
        "--resources_dir",
        type=str,
        required=True,
        dest="resources_dir",
        help="Directory to write the resources",
    )

    # 'topo_add_dns_server' command
    parser_topo_add_dns_server = subparsers.add_parser(
        "topo_add_dns_server", help="Add a DNS server to a topology."
    )
    parser_topo_add_dns_server.set_defaults(func=topo_add_dns_server_handler)
    parser_topo_add_dns_server.add_argument(
        "-t",
        "--topology",
        type=str,
        required=True,
        dest="input_topology_file",
        help="Path to the input YAML topology file",
    )
    parser_topo_add_dns_server.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        dest="output_topology_file",
        help="Path to the output YAML topology file that will be created",
    )
    parser_topo_add_dns_server.add_argument(
        "-s",
        "--switch",
        type=str,
        required=True,
        dest="switch_name",
        help="Switch name on which to add a DNS server",
    )

    # -----------------------
    # --- Provisioning options
    # -----------------------

    add_provisioning_parser(root_parser=parser, subparsers=subparsers)

    # -----------------------
    # --- User activity options
    # -----------------------

    # 'user_activity_play_user_scenario' command
    parser_user_activity_play_user_scenario = subparsers.add_parser(
        "user_activity_play_user_scenario",
        help="Play user_activity (scenario from user) on a simulation",
    )
    parser_user_activity_play_user_scenario.set_defaults(
        func=user_activity_play_user_scenario_handler
    )
    parser_user_activity_play_user_scenario.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )
    parser_user_activity_play_user_scenario.add_argument(
        "scenario_path",
        type=str,
        help="The complete path of the scenario, in the form <path> / <category> / <action>. Example: data/user_activity/web_browser/activate_payload. ",
    )

    parser_user_activity_play_user_scenario.add_argument(
        "node_name", type=str, help="The node (target) name"
    )

    parser_user_activity_play_user_scenario.add_argument(
        "-o",
        action="store",
        required=False,
        dest="user_activity_file_results",
        help="Absolute name of user_activity results (JSON format)",
    )

    parser_user_activity_play_user_scenario.add_argument(
        "-d",
        action="store",
        required=False,
        dest="user_activity_debug_mode",
        default="off",
        help="Debug mode ('off', 'on', 'full')",
    )
    parser_user_activity_play_user_scenario.add_argument(
        "-t",
        action="store",
        required=False,
        dest="user_activity_speed",
        default="normal",
        help="user_activity speed ('slow', 'normal', 'fast')",
    )
    parser_user_activity_play_user_scenario.add_argument(
        "--record-video",
        action="store_true",
        default=False,
        dest="user_activity_record_video",
        help="Record video of the scenario play. For debug purpose only. Video will be saved on server simulation resources.",
    )
    parser_user_activity_play_user_scenario.add_argument(
        "--write-logfile",
        action="store_true",
        default=False,
        dest="user_activity_write_logfile",
        help="Write logging messages of the scenario play in a file. For debug purpose only. Logs will be saved on server simulation resources.",
    )
    parser_user_activity_play_user_scenario.add_argument(
        "--no-wait",
        action="store_true",
        default=False,
        dest="user_activity_nowait",
        help="Don't wait for the task to be done",
    )

    # 'user_activity_status' command
    parser_user_activity_status = subparsers.add_parser(
        "user_activity_status", help="Get user_activity status on a simulation"
    )
    parser_user_activity_status.set_defaults(func=user_activity_status_handler)
    parser_user_activity_status.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    parser_user_activity_status.add_argument(
        "-id",
        action="store",
        nargs="?",
        required=True,
        dest="task_id",
        help="Task ID to get status from",
    )

    # 'all_activities_status' command
    parser_all_activities_status = subparsers.add_parser(
        "all_activities_status",
        help="Get user_activity statuses for all user activities on a targeted simulation",
    )
    parser_all_activities_status.set_defaults(func=all_activities_status_handler)
    parser_all_activities_status.add_argument(
        "id_simulation", type=int, help="The simulation id"
    )

    # 'compute_server_list' command
    parser_compute_server_list = subparsers.add_parser(
        "compute_server_list",
        help="List all compute servers as they are known by IT Simulation",
    )
    parser_compute_server_list.set_defaults(func=compute_server_list_handler)

    # 'compte_server_delete' command
    parser_compute_server_delete = subparsers.add_parser(
        "compute_server_delete",
        help="Delete a compute server",
    )
    parser_compute_server_delete.set_defaults(func=compute_server_delete_handler)
    parser_compute_server_delete.add_argument(
        "id_compute_server",
        type=int,
        help="The compute server id (obtained by 'cyber_range status')",
    )

    # 'redteam_tactics' command
    parser_redteam_tactics = subparsers.add_parser(
        "redteam_tactics",
        help="Retrieve redteam tactic list",
    )
    parser_redteam_tactics.set_defaults(func=redteam_tactics_handler)

    # 'redteam_workers' command
    parser_redteam_workers = subparsers.add_parser(
        "redteam_workers",
        help="Retrieve redteam worker list",
    )
    parser_redteam_workers.set_defaults(func=redteam_workers_handler)
    parser_redteam_workers.add_argument(
        "-T",
        "--tactic",
        action="store",
        nargs="?",
        dest="filter_tactic",
        help="Filter workers according to ATT&CK tactics, either a name or its ID (see redteam_tactics command for the available tactic list)",
    )
    parser_redteam_workers.add_argument(
        "-t",
        "--technique",
        action="store",
        nargs="?",
        dest="filter_technique",
        help="Filter workers according to ATT&CK technique ID",
    )

    # 'redteam_worker' command
    parser_redteam_worker = subparsers.add_parser(
        "redteam_worker",
        help="Retrieve redteam worker info",
    )
    parser_redteam_worker.set_defaults(func=redteam_worker_handler)
    parser_redteam_worker.add_argument(
        "-i",
        "--id",
        action="store",
        required=True,
        dest="id_worker",
        help="Retrieve redteam worker info from its ID",
    )

    # 'redteam_attacks' command
    parser_redteam_attacks = subparsers.add_parser(
        "redteam_attacks",
        help="Retrieve available redteam attacks",
    )
    parser_redteam_attacks.set_defaults(func=redteam_attacks_handler)
    parser_redteam_attacks.add_argument(
        "-s",
        "--status",
        action="store",
        nargs="?",
        dest="filter_status",
        help="Filter attacks based on its status (success, failed, error, running, runnable)",
    )

    # 'redteam_attack' command
    parser_redteam_attack = subparsers.add_parser(
        "redteam_attack",
        help="Return status and output for an attack based on its ID",
    )
    parser_redteam_attack.set_defaults(func=redteam_attack_handler)
    parser_redteam_attack.add_argument(
        "-i",
        "--id",
        action="store",
        required=True,
        dest="id_attack",
        help="Retrieve attack info from its ID",
    )

    # 'redteam_knowledge' command
    parser_redteam_knowledge = subparsers.add_parser(
        "redteam_knowledge",
        help="Retrieve redteam knowledge about targeted system",
    )
    parser_redteam_knowledge.set_defaults(func=redteam_knowledge_handler)

    # 'redteam_sessions' command
    parser_redteam_sessions = subparsers.add_parser(
        "redteam_sessions",
        help="Show available redteam attack sessions",
    )
    parser_redteam_sessions.set_defaults(func=redteam_sessions_handler)

    # 'redteam_infras' command
    parser_redteam_infras = subparsers.add_parser(
        "redteam_infras",
        help="Show available redteam attack infrastructures",
    )
    parser_redteam_infras.set_defaults(func=redteam_infras_handler)

    # 'redteam_play' command
    parser_redteam_play = subparsers.add_parser(
        "redteam_play",
        help="Play a redteam attack based on its ID",
    )
    parser_redteam_play.set_defaults(func=redteam_play_handler)
    parser_redteam_play.add_argument(
        "-i",
        "--id",
        action="store",
        required=True,
        dest="id_attack",
        help="Attack ID to play (IDs are available with command redteam_attacks)",
    )
    parser_redteam_play.add_argument(
        "--no-wait",
        action="store_true",
        default=False,
        dest="redteam_nowait",
        help="If specified, redteam API will not wait for the worker to finish",
    )

    # 'redteam_reset' command
    parser_redteam_reset = subparsers.add_parser(
        "redteam_reset",
        help="Reset redteam API",
    )
    parser_redteam_reset.set_defaults(func=redteam_reset_handler)

    # 'redteam_logs' command
    parser_redteam_logs = subparsers.add_parser(
        "redteam_logs",
        help="Get redteam worker logs",
    )
    parser_redteam_logs.set_defaults(func=redteam_logs_handler)

    # 'redteam_log' command
    parser_redteam_log = subparsers.add_parser(
        "redteam_log",
        help="Get redteam specific attack log",
    )
    parser_redteam_log.set_defaults(func=redteam_log_handler)
    parser_redteam_log.add_argument(
        "-i",
        "--id",
        action="store",
        required=True,
        dest="id_attack",
        help="Attack ID (IDs are available with command redteam_attacks)",
    )

    # 'redteam_report' command
    parser_redteam_report = subparsers.add_parser(
        "redteam_report",
        help="Get redteam scenario report",
    )
    parser_redteam_report.set_defaults(func=redteam_report_handler)

    return parser


def main() -> None:
    configure_logger()
    parser = create_cyber_range_cli_parser()

    argcomplete.autocomplete(parser)

    parser_defaults = {
        k: cr_api_client_config[k]
        for k in cr_api_client_config
        if not OmegaConf.is_missing(cr_api_client_config, k)
    }
    parser.set_defaults(
        func=lambda ns: parser.print_help(), **parser_defaults
    )  # all arguments must be set at same time
    logger.info("[+] Config")

    args, left_argv = parser.parse_known_args()

    # Manage options passed in config file
    # Note that if an option is defined both in command line and config file,
    # the command line value takes precedences
    if args.config:
        # Load config file options
        configfile_path = args.config
        logger.info(f"  [+] Using config file: {configfile_path}")
        if not os.path.exists(configfile_path):
            raise Exception(f"Path '{configfile_path}' does not exist.")
        config = configparser.ConfigParser()
        fp = open(configfile_path)
        config.read_file(fp)

        # Common options to access remote API
        options_by_dest = dict()
        options_by_dest["core_api_url"] = "--core-url"
        options_by_dest["user_activity_api_url"] = "--user-activity-url"
        options_by_dest["provisioning_api_url"] = "--provisioning-url"
        options_by_dest["redteam_api_url"] = "--redteam-url"
        options_by_dest["cacert"] = "--cacert"
        options_by_dest["cert"] = "--cert"
        options_by_dest["key"] = "--key"

        # find options defined in command line
        args_in_command_line = list()
        args_as_dict = vars(args)
        for key, value in args_as_dict.items():
            if key in options_by_dest and value is not None:
                args_in_command_line.append(options_by_dest[key])

        for k, v in config.items("DEFAULT"):
            # if the argument is also in the command line, it overwrites the one present in the config file
            if k in args_in_command_line:
                logger.info(
                    f"  [+] Skipping '{k}' option defined in config file (already defined in command line)"
                )
            else:
                parser.parse_args([str(k), str(v)], args)

        fp.close()

    # Parse remaining args from command line (overriding potential config file
    # parameters)
    args = parser.parse_args(left_argv, args)

    # Merge back cli values to config object
    for k in cr_api_client_config:
        v = getattr(args, k)
        # Keep interpolated values safe
        if cr_api_client_config.get(k) != v:
            cr_api_client_config[k] = v
            logger.info(f"  [+] Using {k}: {cr_api_client_config[k]}")

    # # If DEBUG mode, set environment variable and enrich logger (default logger config
    # # is in __init__.py) to add timestamp
    # if args.debug_mode:
    #     os.environ["CR_DEBUG"] = "1"
    #     logger.configure(
    #         handlers=[
    #             {
    #                 "sink": sys.stdout,
    #                 "format": "|<green>{time:HH:mm:ss}</green>|<level>{level: ^7}</level>| {message}",
    #             }
    #         ],
    #     )

    args.func(args)
    sys.exit(0)


if __name__ == "__main__":
    main()
