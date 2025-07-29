"""Revenium Platform API MCP Server.

A Model Context Protocol (MCP) server that enables AI assistants to interact
with Revenium's platform API for managing products, subscriptions, and sources.
"""

__version__ = "0.1.0"
__author__ = "Revenium"
__email__ = "support@revenium.io"

from .enhanced_server import main

__all__ = ["main"]
