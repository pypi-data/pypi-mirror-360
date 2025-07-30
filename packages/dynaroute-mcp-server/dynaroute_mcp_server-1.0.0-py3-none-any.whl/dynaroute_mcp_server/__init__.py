"""
DynaRoute MCP Server

A Model Context Protocol (MCP) server for DynaRoute that provides intelligent 
chat completions with automatic model routing and cost optimization.
"""

__version__ = "1.0.0"
__author__ = "Mohammed Abraar"
__email__ = "abraar237@gmail.com"

from .server import DynaRouteMCPServer

__all__ = ["DynaRouteMCPServer"]