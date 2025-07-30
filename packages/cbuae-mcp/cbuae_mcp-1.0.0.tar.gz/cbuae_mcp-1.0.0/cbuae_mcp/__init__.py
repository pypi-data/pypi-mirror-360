"""
CBUAE MCP Server - A Model Context Protocol server for CBUAE policies and regulations.

This package provides tools for:
- Searching CBUAE policies using fuzzy matching
- Analyzing gaps between bank policies and CBUAE regulations
- Web scraping live CBUAE website content
- Hybrid search combining local database and web results
"""

__version__ = "1.0.0"
__author__ = "CBUAE MCP Team"
__email__ = "contact@example.com"
__description__ = "CBUAE Policy Agent - Search and analyze Central Bank of UAE policies"

from .server import create_server
from .web_scraper import CBUAEWebScraper

__all__ = ["create_server", "CBUAEWebScraper"]