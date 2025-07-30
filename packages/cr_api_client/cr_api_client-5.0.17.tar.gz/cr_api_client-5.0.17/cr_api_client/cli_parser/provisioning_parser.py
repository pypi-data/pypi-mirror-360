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
import sys
from typing import Any

import cr_api_client.provisioning_api as provisioning_api


#
# 'provisioning_execute' related functions
#
def provisioning_execute_handler(args: Any) -> None:
    """Process YAML topology file and execute a new provisioning
    chronology (generate + play)).

    """

    # Parameters
    id_simulation = args.id_simulation
    machines_file = args.machines_file
    provisioning_file = args.provisioning_file
    debug = args.debug_mode
    wait = not args.provisioning_nowait
    timeout = args.timeout
    ansible_verbosity = args.provisioning_ansible_verbosity
    stream_ansible = args.provisioning_stream_ansible
    reload_provisioning_agent = args.provisioning_reload_agent

    try:
        provisioning_api.provisioning_execute(
            id_simulation=id_simulation,
            machines_file=machines_file,
            provisioning_file=provisioning_file,
            debug=debug,
            wait=wait,
            timeout=timeout,
            ansible_verbosity=ansible_verbosity,
            stream_ansible=stream_ansible,
            reload_provisioning_agent=reload_provisioning_agent,
        )
    except Exception as e:
        print(f"Error during provisioning: '{e}'")
        sys.exit(1)


#
# 'provisioning_ansible' related functions
#
def provisioning_ansible_handler(args: Any) -> None:
    """Apply ansible playbook on targets."""

    # Parameters
    id_simulation = args.id_simulation
    machines_file = args.machines_file
    playbook_path = args.provisioning_playbook_path
    provisioning_extra_vars = args.provisioning_extra_vars
    provisioning_target_roles = args.provisioning_target_roles
    provisioning_target_system_types = args.provisioning_target_system_types
    provisioning_target_operating_systems = args.provisioning_target_operating_systems
    provisioning_target_names = args.provisioning_target_names
    provisioning_host_vars = args.provisioning_host_vars
    provisioning_gather_facts_override = args.provisioning_gather_facts_override
    provisioning_ansible_verbosity = args.provisioning_ansible_verbosity
    debug = args.debug_mode
    wait = not args.provisioning_nowait
    timeout = args.timeout
    provisioning_stream_ansible = args.provisioning_stream_ansible
    provisioning_reload_agent = args.provisioning_reload_agent

    # TODO: check that only one target type is defined

    if provisioning_target_operating_systems is None:
        provisioning_target_operating_systems = []
    if provisioning_target_system_types is None:
        provisioning_target_system_types = []
    if provisioning_target_roles is None:
        provisioning_target_roles = []
    if provisioning_target_names is None:
        provisioning_target_names = []
    if provisioning_host_vars is None:
        provisioning_host_vars = []

    if (
        len(provisioning_target_operating_systems)
        + len(provisioning_target_system_types)
        + len(provisioning_target_roles)
        + len(provisioning_target_names)
        == 0
    ):
        raise SyntaxError(
            "At least one of the following options should be defined: -n, -r, -s, -o."
        )

    try:
        provisioning_api.provisioning_ansible(
            id_simulation=id_simulation,
            machines_file=machines_file,
            playbook_path=playbook_path,
            extra_vars=provisioning_extra_vars,
            target_roles=provisioning_target_roles,
            target_system_types=provisioning_target_system_types,
            target_operating_systems=provisioning_target_operating_systems,
            target_names=provisioning_target_names,
            host_vars=provisioning_host_vars,
            gather_facts_override=provisioning_gather_facts_override,
            debug=debug,
            ansible_verbosity=provisioning_ansible_verbosity,
            wait=wait,
            timeout=timeout,
            stream_ansible=provisioning_stream_ansible,
            reload_provisioning_agent=provisioning_reload_agent,
        )
    except Exception as e:
        error_msg = str(e)
        error_msg = error_msg.replace("\\n", "\n")
        print(f"Error during provisioning: {error_msg}")
        sys.exit(1)


#
# 'provisioning_inventory' related functions
#
def provisioning_inventory_handler(args: Any) -> None:
    """Generate ansible inventory files."""

    # Parameters
    id_simulation = args.id_simulation
    machines_file = args.machines_file
    output_dir = args.output_inventory_dir
    debug = args.debug_mode

    try:
        provisioning_api.provisioning_inventory(
            id_simulation=id_simulation,
            machines_file=machines_file,
            output_dir=output_dir,
            debug=debug,
        )
    except Exception as e:
        error_msg = str(e)
        error_msg = error_msg.replace("\\n", "\n")
        print(f"Error during provisioning: {error_msg}")
        sys.exit(1)


#
# 'provisioning_stop' related functions
#
def provisioning_stop_handler(args: Any) -> None:
    """Stop provisioning currently running"""

    # Parameters
    task_id = args.task_id

    print("[+] Stopping provisioning task with id '{}'".format(task_id))

    try:
        provisioning_api.provisioning_stop(task_id)
        print("[+] Stopping done.")

    except Exception as e:
        error_msg = str(e)
        error_msg = error_msg.replace("\\n", "\n")
        print(f"[-] Error while stopping provisioning: {error_msg}")
        sys.exit(1)


#
# 'provisioning_status' related functions
#
def provisioning_status_handler(args: Any) -> None:
    """Status provisioning currently running"""

    # Parameters
    task_id = args.task_id

    print("[+] Provisioning task status with id '{}'".format(task_id))

    try:
        result = provisioning_api.provisioning_status(task_id)
        status = result["status"]
        if status is None:
            print(
                f"[+] Status unknown, this task id doesn't exist or is finished: {task_id}"
            )
        else:
            print(f"[+] Status: {status}")

    except Exception as e:
        error_msg = str(e)
        error_msg = error_msg.replace("\\n", "\n")
        print(f"[-] Error while provisioning status: {error_msg}")
        sys.exit(1)


#
# 'provisioning_report' related functions
#
def provisioning_report_handler(args: Any) -> None:
    """Report of all currently running provisioning agents"""

    print("[+] Provisioning report: ")
    task_id = args.task_id

    try:
        result = provisioning_api.provisioning_report(task_id)
        print("  [+] --------------------------------------")
        print(f"  [+] {task_id}:")
        print("  [+] --------------------------------------")
        print(result["logs"])

    except Exception as e:
        error_msg = str(e)
        error_msg = error_msg.replace("\\n", "\n")
        print(
            f"[-] Error while retrieving provisioning report for {task_id} : {error_msg}"
        )
        sys.exit(1)


def add_provisioning_parser(
    root_parser: argparse.ArgumentParser, subparsers: Any
) -> None:
    # Subparser provisioning
    parser_provisioning = subparsers.add_parser(
        "provisioning",
        help="Provisioning actions in running labs",
        formatter_class=root_parser.formatter_class,
    )
    subparsers_provisioning = parser_provisioning.add_subparsers()
    parser_provisioning.set_defaults(func=lambda _: parser_provisioning.print_help())

    # 'execute' command
    parser_provisioning_execute = subparsers_provisioning.add_parser(
        "execute",
        help="Execute provisioning chronology for a simulation",
        formatter_class=root_parser.formatter_class,
    )
    parser_provisioning_execute.set_defaults(func=provisioning_execute_handler)
    parser_provisioning_execute.add_argument(
        "--id",
        type=int,
        action="store",
        required=False,
        dest="id_simulation",
        help="The simulation id",
    )
    parser_provisioning_execute.add_argument(
        "--machines",
        action="store",
        required=False,
        dest="machines_file",
        help="Input path of machines configuration (YAML format)",
    )
    parser_provisioning_execute.add_argument(
        "-c",
        action="store",
        required=True,
        dest="provisioning_file",
        help="Input path of provisioning configuration",
    )
    parser_provisioning_execute.add_argument(
        "--no-wait",
        action="store_true",
        default=False,
        dest="provisioning_nowait",
        help="Don't wait for the task to be done",
    )
    parser_provisioning_execute.add_argument(
        "--timeout",
        action="store",
        type=int,
        required=False,
        default=10800,
        dest="timeout",
        help="Timeout of the provisioning task (default to 10800 seconds - 3 hours)",
    )

    parser_provisioning_execute.add_argument(
        "--ansible-verbosity",
        "-v",
        action="store",
        type=int,
        required=False,
        default=0,
        dest="provisioning_ansible_verbosity",
        help="Determines the verbosity of the ansible output (and the number of '-v' passed to ansible)",
    )
    parser_provisioning_execute.add_argument(
        "--stream-ansible",
        action="store_true",
        required=False,
        default=False,
        dest="provisioning_stream_ansible",
        help="If set, will stream the ansible output during the provisioning task",
    )
    parser_provisioning_execute.add_argument(
        "--reload-provisioning-agent",
        action="store_true",
        required=False,
        default=False,
        dest="provisioning_reload_agent",
        help="If set, will force the reloading of the provisioning agent docker container",
    )

    # 'ansible' command
    parser_provisioning_ansible = subparsers_provisioning.add_parser(
        "ansible",
        help="""Apply ansible playbook(s) on specific target(s).""",
        formatter_class=root_parser.formatter_class,
    )
    parser_provisioning_ansible.set_defaults(func=provisioning_ansible_handler)
    parser_provisioning_ansible.add_argument(
        "--id",
        type=int,
        action="store",
        required=False,
        dest="id_simulation",
        help="The simulation id",
    )
    parser_provisioning_ansible.add_argument(
        "--machines",
        action="store",
        required=False,
        dest="machines_file",
        help="Input path of machines configuration (YAML format)",
    )
    parser_provisioning_ansible.add_argument(
        "-c",
        action="store",
        required=True,
        dest="provisioning_playbook_path",
        help="Input directory containing ansible playbook(s)",
    )
    parser_provisioning_ansible.add_argument(
        "-r",
        action="append",
        dest="provisioning_target_roles",
        help="Role used to filter targets ('client', 'activate_directory', 'file_server', 'admin', ...)",
    )
    parser_provisioning_ansible.add_argument(
        "-s",
        action="append",
        dest="provisioning_target_system_types",
        help="System type used to filter targets ('linux', 'windows')",
    )
    parser_provisioning_ansible.add_argument(
        "-o",
        action="append",
        dest="provisioning_target_operating_systems",
        help="Operating system used to filter targets ('Windows 7', 'Windows 10', 'Debian', 'Ubuntu', ...)",
    )
    parser_provisioning_ansible.add_argument(
        "-n",
        action="append",
        dest="provisioning_target_names",
        help="Machine name used to filter targets",
    )
    parser_provisioning_ansible.add_argument(
        "--host-vars",
        action="append",
        required=False,
        dest="provisioning_host_vars",
        help="Host vars given as a dictionary",
    )
    parser_provisioning_ansible.add_argument(
        "-e",
        "--extra-vars",
        action="store",
        dest="provisioning_extra_vars",
        help="Variables for the ansible playbook(s)",
    )
    parser_provisioning_ansible.add_argument(
        "--no-wait",
        action="store_true",
        default=False,
        dest="provisioning_nowait",
        help="Don't wait for the task to be done",
    )
    parser_provisioning_ansible.add_argument(
        "--force-gather-facts",
        action="store_true",
        default=None,
        dest="provisioning_gather_facts_override",
        help="Force 'gather_facts' to 'yes' in the ansible playbook, regardless of its default value and its value in the playbook.",
    )
    parser_provisioning_ansible.add_argument(
        "--force-no-gather-facts",
        action="store_false",
        default=None,
        dest="provisioning_gather_facts_override",
        help="Force 'gather_facts' to 'no' in the ansible playbook, regardless of its default value and its value in the playbook.",
    )
    parser_provisioning_ansible.add_argument(
        "--timeout",
        action="store",
        type=int,
        required=False,
        default=3600,
        dest="timeout",
        help="Timeout of the provisioning task (default to 3600 seconds - 1 hour)",
    )
    parser_provisioning_ansible.add_argument(
        "--ansible-verbosity",
        "-v",
        action="store",
        type=int,
        required=False,
        default=0,
        dest="provisioning_ansible_verbosity",
        help="Determines the verbosity of the ansible output (and the number of '-v' passed to ansible)",
    )
    parser_provisioning_ansible.add_argument(
        "--stream-ansible",
        action="store_true",
        required=False,
        default=False,
        dest="provisioning_stream_ansible",
        help="If set, will stream the ansible output during the provisioning task",
    )
    parser_provisioning_ansible.add_argument(
        "--reload-provisioning-agent",
        action="store_true",
        required=False,
        default=False,
        dest="provisioning_reload_agent",
        help="If set, will force the reloading of the provisioning agent docker container",
    )

    # 'stop' command
    parser_provisioning_stop = subparsers_provisioning.add_parser(
        "stop",
        help="Stop a provisioning task",
        formatter_class=root_parser.formatter_class,
    )
    parser_provisioning_stop.set_defaults(func=provisioning_stop_handler)
    parser_provisioning_stop.add_argument(
        "task_id", type=str, help="The provisioning task id"
    )

    # 'status' command
    parser_provisioning_status = subparsers_provisioning.add_parser(
        "status",
        help="Get status of a provisioning task",
        formatter_class=root_parser.formatter_class,
    )
    parser_provisioning_status.set_defaults(func=provisioning_status_handler)
    parser_provisioning_status.add_argument(
        "task_id", type=str, help="The provisioning task id"
    )

    # 'report' command
    parser_provisioning_report = subparsers_provisioning.add_parser(
        "report",
        help="Print report of all active provisioning tasks",
        formatter_class=root_parser.formatter_class,
    )
    parser_provisioning_report.set_defaults(func=provisioning_report_handler)
    parser_provisioning_report.add_argument(
        "task_id", type=str, help="The provisioning task id"
    )

    # 'inventory' command
    parser_provisioning_inventory = subparsers_provisioning.add_parser(
        "inventory",
        help="Generate ansible inventory files from targets information",
        formatter_class=root_parser.formatter_class,
    )
    parser_provisioning_inventory.set_defaults(func=provisioning_inventory_handler)
    parser_provisioning_inventory.add_argument(
        "--id",
        type=int,
        action="store",
        required=False,
        dest="id_simulation",
        help="The simulation id",
    )
    parser_provisioning_inventory.add_argument(
        "--machines",
        action="store",
        required=False,
        dest="machines_file",
        help="Input path of machines configuration (YAML format)",
    )
    parser_provisioning_inventory.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        dest="output_inventory_dir",
        help="Path to the output inventory directory that will be created",
    )
