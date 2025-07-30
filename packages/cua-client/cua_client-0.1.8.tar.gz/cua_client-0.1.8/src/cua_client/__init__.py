# This file makes the client directory a Python package
"""
CUA Client - Computer Use Automation Client

A Python package for remote function execution and computer automation tasks
via WebSocket connections.
"""

from .remote_function_client import RemoteFunctionClient, RemoteFunctionRouter
from .computer_use import ComputerUseFunction
from .main import ClientConfig, load_config, main
from .reset_windows import reset_cli

__version__ = "0.1.8"
__author__ = "168x Project"
__email__ = "admin@168x.com"

__all__ = [
    "RemoteFunctionClient",
    "RemoteFunctionRouter", 
    "ComputerUseFunction",
    "ClientConfig",
    "load_config",
    "main",
    "reset_cli",
] 