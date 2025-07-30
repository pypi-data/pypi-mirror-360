"""
Command-line interface for scmcp.

This module provides a CLI entry point for the scmcp package.
"""
from enum import Enum
from scmcp_shared.cli import MCPCLI
from .server import SCMCPManager



class SCMCPCLI(MCPCLI):
    def __init__(self, name: str, help_text: str, manager=None):
        super().__init__(name, help_text, manager=manager)
        self.subcommands['run'][0].add_argument(
            '-m', '--module',
            nargs='+',
            default=["all"],
            choices=["all", "sc", "li", "cr", "dc"],
            help='specify module to run')

cli = SCMCPCLI(
    name="scmcp", 
    help_text="SCMCP Server CLI",
    manager=SCMCPManager,
)
