#!/usr/bin/env python3
"""
Compatibility wrapper for datagov-mcp server.

This file maintains backward compatibility for existing users who run:
    fastmcp dev server.py
    fastmcp install claude desktop server.py

The actual implementation is in the datagov_mcp package.
"""

from datagov_mcp.server import mcp

if __name__ == "__main__":
    # This code only runs when the file is executed directly
    mcp.run()
