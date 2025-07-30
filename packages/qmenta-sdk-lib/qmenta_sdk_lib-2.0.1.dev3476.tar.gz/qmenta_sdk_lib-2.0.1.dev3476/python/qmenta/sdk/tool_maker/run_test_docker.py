#!/usr/bin/env python

"""
Basic QMENTA Tool Image Local Tester

Example:

$ python test_sdk_tool.py -v /home/apuente/repos/qmenta_imaging/tools/lesion_toads/tool.py:/qmenta/tool.py \
    gcr.io/hosting-setup-853/lesion_toads_neuro-269:1.0.366 \
    ~/data/lesion_toads/ \
    ~/data/output/ \
    --settings ./tools/lesion_toads/settings.json \
    --values ./tools/lesion_toads/mock_values.json

Usage:
 $ ./test_sdk_tool.py image_name inputs/ outputs
 $ ./test_sdk_tool.py image_name inputs/ outputs --settings settings.json --values values.json --tool package.tool -v \
    /host/path:/container/path

Compatible with Python 3 with no additional packages.
See https://docs.qmenta.com/sdk/testing.html for more information.
"""

import os
import random
import string
import subprocess
from os import listdir
from os.path import abspath, isdir

import sys


def random_seq(n):
    """
    Generates a random sequence of upper-cased characters of size n
    """
    return "".join(random.choice(string.ascii_uppercase) for x in range(n))


def run_command(cmd, verbose=True):
    """
    Execute command in shell
    """
    if verbose:
        print(" ".join(cmd))
    subprocess.call(cmd)


def error(msg):
    """
    Exit with error
    """
    print(msg)
    sys.exit(1)


def run_docker(
    image: str,
    inputs: str,
    outputs: str,
    settings: str,
    values: str,
    mounts: list,
    overwrite_output: bool,
    resources: str,
    stop_container: bool,
    delete_container: bool,
    attach_container: bool,
):
    """
    Script entrypoint
    """

    if not isdir(abspath(inputs)):
        error("Error: Input folder does not exist")
    if not isdir(abspath(outputs)):
        error("Error: Output folder does not exist")
    if not os.listdir(abspath(outputs)) == []:
        print(
            "Warning: Output folder is not empty (files could be overwritten)."
        )
        if not overwrite_output:
            sys.exit(1)
    if resources and not isdir(abspath(resources)):
        error("Error: Resource file does not exist")
    if settings and not values:
        error(
            "Error: Entering a custom settings file requires a settings values file"
        )

    # In-container paths
    c_settings_path = os.path.join("/", "qmenta", "local_exec_settings.json")
    c_values_path = os.path.join(
        "/", "qmenta", "local_exec_settings_values.json"
    )
    c_input_path = os.path.join("/", "qmenta", "local_exec_input/")
    c_output_path = os.path.join("/", "qmenta", "local_exec_output/")
    c_res_path = os.path.join("/", "qmenta", "local_exec_resources/")

    # If no tool_settings file is provided, use a generic one
    if not settings:
        settings_content = """[
    {
        "type": "container",
        "title": "Example Container",
        "id":"input",
        "mandatory":1,
        "batch":1,
        "file_filter": "c_files[1,*]<'', [], '.*'>",
        "in_filter":["mri_brain_data"],
        "out_filter":[],
        "anchor":1
    }
]"""

        settings = "./generic_settings.json"

        with open(settings, "w") as settings_file:
            settings_file.write(settings_content)

    # If no tool_settings_values file is provided, generate just the list of input files
    if not values:
        files = listdir(os.path.join(abspath(inputs), "input"))
        values_content = (
            '{"input":[\n'
            + ",\n".join(
                ['   {"path": "' + f + '"}' for f in files if not isdir(f)]
            )
            + "]\n}"
        )

        values = "./generic_values.json"

        with open(values, "w") as values_file:
            values_file.write(values_content)

    # Extra directories to be mounted (for instance, live version of source code)
    extra_volumes = []
    for volume in mounts or []:
        extra_volumes += ["-v", volume]

    # Launch the detached container
    c_name = "local_test_" + random_seq(5)
    print("\nStarting container {}...".format(c_name))
    run_command(
        [
            "docker",
            "run",
            "-dit",
            "-v",
            abspath(inputs) + ":" + c_input_path,
            "-v",
            abspath(outputs) + ":" + c_output_path,
        ]
        + extra_volumes
        + [
            "--entrypoint=/bin/bash",
            "--name=" + c_name,
            image,
        ]
    )
    # Copy the settings files to the container
    run_command(
        ["docker", "cp", abspath(settings), c_name + ":" + c_settings_path],
        verbose=False,
    )
    run_command(
        ["docker", "cp", abspath(values), c_name + ":" + c_values_path],
        verbose=False,
    )

    # Changing to local executor
    run_command(
        [
            "docker",
            "exec",
            c_name,
            "/bin/bash",
            "-c",
            r"sed -i.bak 's/\<qmenta.sdk\>/&.local/' /qmenta/entrypoint.sh",
        ],
        verbose=False,
    )

    # Run the local executor
    print("\nRunning tool.py:run()...\n")
    launch_cmd = [
        "docker",
        "exec",
        c_name,
        "/bin/bash",
        "/qmenta/entrypoint.sh",
        c_settings_path,
        c_values_path,
        c_input_path,
        c_output_path,
        "--tool-path",
        "tool:run",
    ]

    print(launch_cmd)
    # Additional resources (QMENTA)
    if resources:
        run_command(
            ["docker", "cp", abspath(resources), c_name + ":" + c_res_path],
            verbose=False,
        )
        launch_cmd += ["--res-folder", c_res_path]
    run_command(launch_cmd)
    if stop_container:
        run_command(["docker", "stop", c_name])
    if delete_container:
        run_command(["docker", "rm", c_name], verbose=True)
    if attach_container:
        run_command(["docker", "attach", c_name], verbose=True)
