# Copyright (c) Huawei Technologies Co., Ltd. 2025. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Chariot datasystem CLI util module."""

from datetime import datetime, timezone
import json
import os
import subprocess
from typing import Any, Dict, List, Optional

from datasystem.cli.common.constant import ClusterConfig


def get_required_config(config, key):
    """Get a required configuration value from a dictionary.

    Args:
        config: The configuration dictionary.
        key: The key to retrieve from the dictionary.

    Raises:
        ValueError: If the key is not found in the configuration.
    """
    value = config.get(key)
    if value is None:
        raise ValueError(f"{key} not found in config")
    return value


def load_cluster_config(
    path: str, keys: Optional[List[ClusterConfig]] = None
) -> Dict[str, str]:
    """Load cluster configuration from a JSON file and extract specific keys.

    Args:
        path: Path to the JSON configuration file.
        keys: Optional list of ClusterConfig keys to extract. If None, all keys are used.

    Returns:
        A dictionary containing the extracted configuration values.

    Raises:
        ValueError: If the configuration file format is incorrect.
    """
    try:
        with open(path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"The configuration file {path} format is incorrect.") from e

    if keys is None:
        keys = list(ClusterConfig)

    result = {}
    for key in keys:
        keys_list = key.value.split(".")
        value = config
        for k in keys_list:
            value = get_required_config(value, k)
        result[key] = value
    return result


def ssh_execute(host, username, private_key, command):
    """Execute a command on a remote host via SSH.

    Args:
        host: The remote host to connect to.
        username: The username for SSH authentication.
        private_key: Path to the private key for SSH authentication.
        command: The command to execute on the remote host.

    Returns:
        The output of the executed command.

    Raises:
        RuntimeError: If the SSH connection fails or the command execution fails.
    """
    ssh_command = ["ssh", "-q", "-i", private_key, f"{username}@{host}", command]
    try:
        process = subprocess.Popen(
            ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(timeout=300)
        if process.returncode != 0:
            raise RuntimeError(
                f"Error executing on {host} (exit code {process.returncode}): {stderr.decode()}"
            )
        return stdout.decode()
    except Exception as e:
        raise RuntimeError(f"SSH connection to {host} failed: {e}") from e


def scp_upload(local_file, remote_host, remote_path, user_name, private_key):
    """Upload a file to a remote host via SCP.

    Args:
        local_file: Path to the local file to upload.
        remote_host: The remote host to upload the file to.
        remote_path: The destination path on the remote host.
        user_name: The username for SCP authentication.
        private_key: Path to the private key for SCP authentication.

    Raises:
        RuntimeError: If the file upload fails.
    """
    scp_command = [
        "scp",
        "-i",
        private_key,
        local_file,
        f"{user_name}@{remote_host}:{remote_path}",
    ]
    try:
        subprocess.check_call(scp_command, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to upload file to {remote_host}: {e}") from e


def scp_download(remote_host, remote_path, local_path, user_name, private_key):
    """Download a file/directory from a remote host via SCP.

    Args:
        remote_host: The remote host IP or hostname.
        remote_path: The source path on the remote host.
        local_path: The destination path on local machine.
        user_name: The username for SCP authentication.
        private_key: Path to the private key for SCP authentication.

    Raises:
        RuntimeError: If the file download fails.
    """
    os.makedirs(local_path, exist_ok=True)
    scp_command = [
        "scp",
        "-r",
        "-i",
        private_key,
        f"{user_name}@{remote_host}:{remote_path}",
        local_path,
    ]
    try:
        subprocess.check_call(scp_command, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to download from {remote_host}: {e}") from e


def get_timestamped_path(original_path: str) -> str:
    """
    Generate a timestamped version of the given path if it starts with "./chariotds".

    Args:
        original_path (str): The original path string to process.

    Returns:
        str: The modified path with a timestamp appended if it starts with "./chariotds",
             otherwise returns the original path.
    """
    if original_path.startswith("./chariotds"):
        return original_path.replace(
            "./chariotds",
            f"./chariotds{datetime.now(tz=timezone.utc).strftime('%Y%m%d%H%M%S')}",
            1,
        )
    return original_path


def compare_and_process_config(
    home_dir: str, config: Dict[str, Any], default_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare and process the user configuration with the default configuration.

    Args:
        home_dir (str): The home directory path used to resolve relative paths.
        config (Dict[str, Any]): The user configuration dictionary to be processed.
        default_config (Dict[str, Any]): The default configuration dictionary for comparison.

    Returns:
        Dict[str, Any]: A dictionary containing only the keys that were modified by the user.
    """
    modified = {}
    for key, item in default_config.items():
        default_value = str(item.get("value", ""))
        user_item = config.setdefault(key, {})
        user_value = str(user_item.get("value", ""))

        is_modified = user_value.strip() and str(default_value) != str(user_value)
        if is_modified:
            modified[key] = user_value
        else:
            user_item["value"] = default_value
            user_value = default_value

        if user_value.startswith("./"):
            if home_dir:
                user_item["value"] = os.path.join(home_dir, user_value[2:])
            elif is_modified:
                user_item["value"] = os.path.realpath(user_value)
            else:
                user_item["value"] = os.path.realpath(get_timestamped_path(user_value))

    return modified
