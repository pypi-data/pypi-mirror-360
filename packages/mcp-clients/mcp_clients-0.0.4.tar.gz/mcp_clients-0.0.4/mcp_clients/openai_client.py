"""
OpenAI MCP Client

This module provides a client for integrating OpenAI's GPT models with 
Model Context Protocol (MCP) servers. It enables seamless communication between
OpenAI models and external tools/services through MCP.

Classes:
    OpenAIClient: Main client class for OpenAI models with MCP integration

Example:
    >>> import asyncio
    >>> from mcp_clients import OpenAIClient
    >>> 
    >>> async def main():
    ...     client = await OpenAIClient.init(
    ...         server_script_path='weather_server.py',
    ...         system_instruction='You are a weather assistant.',
    ...         model='gpt-4o-mini'
    ...     )
    ...     try:
    ...         response = await client.process_query("What's the weather like?")
    ...         print(response)
    ...     finally:
    ...         await client.cleanup()
    >>> 
    >>> asyncio.run(main())
"""

import os
import json
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from contextlib import AsyncExitStack
from openai import OpenAI
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()


class OpenAIClient:
    """
    A client for OpenAI's GPT models with MCP server integration.

    This class provides an interface to interact with OpenAI models while leveraging
    Model Context Protocol (MCP) servers for enhanced functionality. It supports
    tool calling, conversation history, and customizable chat interfaces.

    Attributes:
        session (Optional[ClientSession]): MCP client session for server communication
        exit_stack (AsyncExitStack): Context manager for resource cleanup
        _client (OpenAI): OpenAI API client
        model (str): OpenAI model name to use
        server_script_path (Optional[str]): Path to the MCP server script
        history (list): Conversation history for context preservation
        custom_chat_loop (callable): Custom chat loop function if provided
        system_instruction (str): System instruction for the AI model

    Example:
        >>> client = await OpenAIClient.init(
        ...     api_key="your-api-key",
        ...     server_script_path="path/to/server.py",
        ...     system_instruction="You are a helpful assistant.",
        ...     model="gpt-4o-mini"
        ... )
        >>> await client.chat_loop()
        >>> await client.cleanup()
    """

    def __init__(
        self,
        api_key: Optional[str] = os.getenv("OPENAI_API_KEY"),
        model: str = "gpt-4.1-nano",
        server_script_path: Optional[str] = os.getenv("MCP_SERVER"),
        custom_chat_loop=None,
        system_instruction: str = None,
    ):
        """
        Initialize the OpenAI client.

        Args:
            api_key (Optional[str]): OpenAI API key. If None, uses OPENAI_API_KEY env var.
            model (str): OpenAI model name. Defaults to "gpt-4o-mini".
            server_script_path (Optional[str]): Path to MCP server script. If None, uses MCP_SERVER env var.
            custom_chat_loop (callable): Custom chat loop function. If None, uses default.
            system_instruction (str): System instruction for the AI model. If None, uses default.

        Note:
            This constructor is typically not called directly. Use the `init` class method instead.
        """

        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._client = OpenAI(api_key=api_key)
        self.model = model
        self.server_script_path = server_script_path
        self.history = []
        self.custom_chat_loop = custom_chat_loop
        self.system_instruction = system_instruction

    @classmethod
    async def init(
        cls,
        system_instruction=None,
        api_key=None,
        server_script_path=None,
        model="gpt-4.1-nano",
        custom_chat_loop=None,
    ):
        """
        Factory method to create and initialize an OpenAI client.

        This is the recommended way to create an OpenAI client instance as it properly
        handles async initialization and server connection.

        Args:
            system_instruction (Optional[str]): System instruction for the AI model.
                If None, defaults to "You are a helpful assistant."
            api_key (Optional[str]): OpenAI API key. If None, uses OPENAI_API_KEY env var.
            server_script_path (Optional[str]): Path to MCP server script (.py or .js).
                If None, uses MCP_SERVER env var.
            model (str): OpenAI model name. Defaults to "gpt-4o-mini".
            custom_chat_loop (callable): Custom chat loop function. If provided, it will
                be called instead of the default chat loop.

        Returns:
            OpenAIClient: An initialized OpenAI client instance ready for use.

        Raises:
            ValueError: If the server script path is provided but not a .py or .js file.

        Example:
            >>> client = await OpenAIClient.init(
            ...     system_instruction="You are a weather assistant.",
            ...     server_script_path="weather_server.py"
            ... )
        """
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")

        if server_script_path is None:
            server_script_path = os.getenv("MCP_SERVER")

        if system_instruction is None:
            system_instruction = "You are a helpful assistant."

        client = cls(
            api_key=api_key,
            model=model,
            server_script_path=server_script_path,
            custom_chat_loop=custom_chat_loop,
            system_instruction=system_instruction,
        )
        if server_script_path:
            await client.connect_to_server()
        return client

    async def connect_to_server(self):
        """
        Connect to the MCP server specified in server_script_path.

        This method establishes a connection to an MCP server using stdio transport.
        It supports both Python (.py) and JavaScript (.js) server scripts.

        Raises:
            ValueError: If the server script path doesn't end with .py or .js

        Note:
            This method is automatically called by the `init` class method if a
            server_script_path is provided.
        """
        is_python = self.server_script_path.endswith(".py")
        is_js = self.server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        import sys

        command = sys.executable if is_python else "node"
        server_params = StdioServerParameters(
            command=command, args=[self.server_script_path], env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str):
        """
        Process a user query using OpenAI models with MCP tool integration.

        This method handles the complete flow of processing a user query:
        1. Adds the query to conversation history
        2. Gets available tools from the MCP server
        3. Sends the query to OpenAI with tool definitions
        4. Handles tool calls if the model decides to use them
        5. Returns the final response

        Args:
            query (str): The user's query or question

        Returns:
            str: The AI's response, potentially enhanced with tool results

        Example:
            >>> response = await client.process_query("What's the weather in New York?")
            >>> print(response)
        """

        self.history.append({
            'role': 'user', 
            'content': query
        })

        response = await self.session.list_tools()

        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "type": "function",
            "parameters": tool.inputSchema
        } for tool in response.tools]

        response = self._client.responses.create(
            model=self.model,
            tools=available_tools,
            instructions=self.system_instruction,
            input=self.history,
        )

        final_text = []

        if response.output[0].type == "function_call":

            function_call = response.output[0]

            self.history.append(function_call)

            result = await self.session.call_tool(function_call.name, json.loads(function_call.arguments))

            self.history.append({
                "type": "function_call_output",
                "call_id": function_call.call_id,
                "output": str(result.content[0].text)
            })

            fallback_response = self._client.responses.create(
                model="gpt-4.1-nano",
                input=self.history,
                tools=available_tools,
            )

            self.history.append({
                'role': 'assistant',
                'content': fallback_response.output_text
            })

            final_text.append(fallback_response.output_text)

        else:
            print("No function call found in the response.")

            self.history.append({
                'role': 'assistant',
                'content': response.output_text
            })

            final_text.append(response.output_text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """
        Start an interactive chat loop.

        This method starts either a custom chat loop (if provided during initialization)
        or the default chat loop. The chat loop allows continuous interaction with the
        AI model until the user chooses to exit.

        Example:
            >>> await client.chat_loop()
            # This will start an interactive session where you can type queries
        """
        if self.custom_chat_loop:
            await self.custom_chat_loop(self)
        else:
            await self._default_chat_loop()

    async def _default_chat_loop(self):
        """
        Default interactive chat loop implementation.

        This method provides a simple command-line interface for chatting with the AI.
        Users can type queries and receive responses. Type 'quit' to exit the loop.

        Note:
            This is an internal method. Use `chat_loop()` instead.
        """
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """
        Clean up resources and close connections.

        This method properly closes all connections and cleans up resources used by
        the client. It should always be called when you're done using the client,
        preferably in a try/finally block or async context manager.

        Example:
            >>> try:
            ...     await client.chat_loop()
            ... finally:
            ...     await client.cleanup()
        """
        await self.exit_stack.aclose()
