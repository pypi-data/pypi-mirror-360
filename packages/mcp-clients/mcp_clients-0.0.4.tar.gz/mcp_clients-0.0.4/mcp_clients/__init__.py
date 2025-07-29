"""
MCP Clients

A Python package for creating Model Context Protocol (MCP) clients that integrate
with various AI models and services.

This package provides easy-to-use clients for connecting to MCP servers and 
facilitating communication between AI models and external tools/services.

Classes:
    Gemini: A client for Google's Gemini AI model with MCP server integration
    OpenAI: A client for OpenAI's GPT models with MCP server integration

Examples:
    Using Gemini client:
    >>> import asyncio
    >>> from mcp_clients import Gemini
    >>> 
    >>> async def main():
    ...     client = await Gemini.init(
    ...         server_script_path='path/to/your/mcp_server.py',
    ...         system_instruction='You are a helpful assistant.',
    ...         model='gemini-2.0-flash-exp'
    ...     )
    ...     try:
    ...         await client.chat_loop()
    ...     finally:
    ...         await client.cleanup()
    >>> 
    >>> asyncio.run(main())

    Using OpenAI client:
    >>> import asyncio
    >>> from mcp_clients import OpenAI
    >>> 
    >>> async def main():
    ...     client = await OpenAI.init(
    ...         server_script_path='path/to/your/mcp_server.py',
    ...         system_instruction='You are a helpful assistant.',
    ...         model='gpt-4o-mini'
    ...     )
    ...     try:
    ...         await client.chat_loop()
    ...     finally:
    ...         await client.cleanup()
    >>> 
    >>> asyncio.run(main())
"""

from .gemini_client import GeminiClient as Gemini
from .openai_client import OpenAIClient as OpenAI
from .version import __version__

__all__ = ["Gemini", "OpenAI", "__version__"]