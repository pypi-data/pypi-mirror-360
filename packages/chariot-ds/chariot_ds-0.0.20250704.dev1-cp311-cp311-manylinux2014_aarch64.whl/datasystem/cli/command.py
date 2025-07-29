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
"""Chariot datasystem CLI command module."""

import argparse
import logging
import os
import stat
import sys

from importlib import import_module

import pkg_resources

from . import __version__


class BaseCommand:
    """Base command class."""

    name = ""
    description = ""

    logger = None

    SUCCESS = 0
    FAILURE = 1

    def __init__(self):
        """Initialize of command"""
        if BaseCommand.logger is None:
            BaseCommand._configure_logging()

        self._base_dir = pkg_resources.resource_filename("datasystem", "")

    @classmethod
    def _configure_logging(cls):
        """Configure logging format and handlers."""
        if cls.logger is not None:
            return

        cls.logger = logging.getLogger("dscli")
        formatter = logging.Formatter("[%(levelname)s] %(message)s")

        # Console handler (shows INFO and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        cls.logger.setLevel(logging.INFO)
        cls.logger.addHandler(console_handler)

    def add_arguments(self, parser):
        """
        Add arguments to parser.

        Args:
            parser (ArgumentParser): specify parser to which arguments are added.
        """

    def run(self, args):
        """
        Implementation of command logic.

        Args:
            args (Namespace): parsed arguments to hold customized parameters.
        """
        raise NotImplementedError(
            "subclasses of BaseCommand must provide a run() method"
        )

    def invoke(self, args):
        """
        Invocation of command.

        Args:
            args (Namespace): parsed arguments to hold customized parameters.
        """
        return self.run(args)


def main():
    """Entry point for Chariot datasystem CLI."""
    if (sys.version_info.major, sys.version_info.minor) < (3, 8):
        logging.error("Python version should be at least 3.8")
        sys.exit(1)

    # set umask to 0o077
    os.umask(stat.S_IRWXG | stat.S_IRWXO)

    parser = argparse.ArgumentParser(
        prog="dscli",
        description="Chariot datasystem CLI entry point (version: {})".format(
            __version__
        ),
        allow_abbrev=False,
    )

    parser.add_argument(
        "--version", action="version", version="%(prog)s ({})".format(__version__)
    )

    subparsers = parser.add_subparsers(
        dest="cli",
        title="subcommands",
        description="the following subcommands are supported",
    )

    commands = {}
    modules = [
        "start",
        "stop",
        "up",
        "down",
        "runscript",
        "generate_helm_chart",
        "generate_cpp_template",
        "generate_config",
        "collect_log",
    ]
    for m in modules:
        module = import_module(f"datasystem.cli.{m}")
        command_cls = getattr(module, "Command", None)
        if command_cls is None or not issubclass(command_cls, BaseCommand):
            continue

        command = command_cls()
        command_parser = subparsers.add_parser(
            command.name, help=command.description, allow_abbrev=False
        )
        command.add_arguments(command_parser)
        commands[command.name] = command
    argv = sys.argv[1:]
    if not argv or argv[0] == "help":
        argv = ["-h"]
    args = parser.parse_args(argv)
    cli = args.__dict__.pop("cli")
    command = commands[cli]
    if command.invoke(args) != BaseCommand.SUCCESS:
        sys.exit(1)
