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
"""Chariot datasystem CLI up command."""

import json
import os

import datasystem.cli.common.util as util
from datasystem.cli.command import BaseCommand
from datasystem.cli.common.constant import ClusterConfig
from datasystem.cli.common.parallel import ParallelMixin


class Command(BaseCommand, ParallelMixin):
    """
    Startup chariot datasystem worker on cluster nodes.
    """

    name = "up"
    description = "startup chariot datasystem worker on cluster nodes"

    _config = {}
    _home_dir = ""
    _hidden_config_path = ""

    def add_arguments(self, parser):
        """
        Add arguments to parser.

        Args:
            parser (ArgumentParser): Specify parser to which arguments are added.
        """
        parser.add_argument(
            "-f",
            "--cluster_config_path",
            metavar="FILE",
            required=True,
            help=(
                "path of cluster configuration file (JSON format), "
                "which can be obtained through the generate_config command"
            ),
        )

        parser.add_argument(
            "-d",
            "--chariotds_home_dir",
            metavar="DIR",
            help=(
                "directory to replace the current paths in the configuration, "
                "e.g. if the config contains './chariotds/log_dir', "
                "'.' will be replaced with the chariotds_home_dir."
            ),
        )

    def run(self, args):
        """
        Execute for up command.

        Args:
            args (Namespace): Parsed arguments to hold customized parameters.

        Returns:
            int: Exit code, 0 for success, 1 for failure.
        """
        try:
            self._config = util.load_cluster_config(args.cluster_config_path)
            self._config[ClusterConfig.SSH_PRIVATE_KEY] = os.path.realpath(
                os.path.expanduser(self._config[ClusterConfig.SSH_PRIVATE_KEY])
            )
            if args.chariotds_home_dir:
                self._home_dir = os.path.realpath(
                    os.path.expanduser(args.chariotds_home_dir)
                )

            self.update_worker_config()
            self.execute_parallel(self._config[ClusterConfig.WORKER_NODES])
        except Exception as e:
            self.logger.error(f"Up cluster failed: {e}")
            return self.FAILURE
        return self.SUCCESS

    def process_node(self, node):
        """
        Process startup of worker on a single node.

        Args:
            node (str): The node to start the worker on.
        """
        user_name = self._config[ClusterConfig.SSH_USER_NAME]
        private_key = self._config[ClusterConfig.SSH_PRIVATE_KEY]
        worker_port = self._config[ClusterConfig.WORKER_PORT]

        util.ssh_execute(
            node,
            user_name,
            private_key,
            f"mkdir -p -- {os.path.dirname(self._hidden_config_path)}",
        )

        # Upload the modified worker config to remote
        util.scp_upload(
            self._hidden_config_path,
            node,
            self._hidden_config_path,
            user_name,
            private_key,
        )

        # Update worker_address
        sed_command = (
            r"sed -i "
            r'"/\"worker_address\"/,/}/ s/\"value\"\s*:\s*\"[^\"]*\"/\"value\": \"%s\"/g" '
            r"%s"
        ) % (f"{node}:{worker_port}", self._hidden_config_path)
        util.ssh_execute(
            node,
            user_name,
            private_key,
            sed_command,
        )

        # Startup worker
        util.ssh_execute(
            node,
            user_name,
            private_key,
            f"bash -l -c 'dscli start -f {self._hidden_config_path}'",
        )
        self.logger.info(f"Start worker service @ {node}:{worker_port} success.")

    def update_worker_config(self):
        """
        Update the worker configuration.

        Raises:
            ValueError: If the configuration file format is incorrect.
        """
        config_path = os.path.realpath(
            os.path.expanduser(self._config[ClusterConfig.WORKER_CONFIG_PATH])
        )
        default_config_path = os.path.join(self._base_dir, "worker_config.json")
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            with open(default_config_path, "r") as f:
                default_config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"The configuration file {config_path} format is incorrect."
            ) from e

        modified = util.compare_and_process_config(self._home_dir, config, default_config)
        for key, val in modified.items():
            self.logger.info(f"Modifed config - {key}: {val}")
        log_dir = config.get("log_dir", {}).get("value", "")
        self.logger.info(f"Log directory configured at: {log_dir}")

        dir_name = os.path.dirname(config_path)
        base_name = os.path.basename(config_path)
        self._hidden_config_path = os.path.join(dir_name, f".{base_name}")
        try:
            with open(self._hidden_config_path, "w") as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            raise ValueError(f"Failed to write to {self._hidden_config_path}.") from e
