"""
Remote MCP Scanner - A security scanner for MCP (Model Context Protocol) servers.

This package provides tools to test OAuth dynamic client registration vulnerabilities
in remote MCP servers, including XSS testing for redirect_uri and website_uri fields.
"""

__version__ = "1.0.0"
__author__ = "Nova Security"
__email__ = "info@novasecurity.co.nz"
__description__ = "A security scanner for remote MCP (Model Context Protocol) servers"

from .scanner import run_scan
from .cli import cli

__all__ = ["run_scan", "cli"]