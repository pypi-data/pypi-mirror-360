"""
PDF2MD MCP Server

A Model Context Protocol server for converting PDF files to Markdown using AI sampling.
"""

__version__ = "0.1.0"
__author__ = "Gavin Huang"
__email__ = "shuminghuang@gmail.com"

from .server import main

__all__ = ["main"]
