# Python MCP Clients: Framework for LLM-Driven Tool Orchestration

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.0.4-blue.svg)](https://github.com/faizraza/mcp-clients)
[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-brightgreen.svg)](https://github.com/faizraza/mcp-clients)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io)
[![PyPI version](https://img.shields.io/pypi/v/mcp-clients.svg)](https://pypi.org/project/mcp-clients/)

`mcp-clients` is an open-source Python SDK designed for building and orchestrating LLM-powered tools using the **Model Context Protocol (MCP)**. It allows seamless integration with **OpenAI** and **Gemini**, enabling natural language interactions with databases, file systems, APIs, and more. Developers can easily connect to multiple MCP servers through a unified interface and create intelligent agents that interact with real-world tools. It is free to use, modify, and distribute under the **MIT license**.

## Features

- **AI Models Integration**: Built-in support for Google's Gemini and OpenAI models
- **MCP Protocol Support**: Seamless integration with MCP servers
- **Tool Calling**: Automatic tool discovery and execution
- **Interactive Chat**: Built-in chat interface with conversation history
- **Customizable**: Support for custom chat loops and system instructions
- **Easy Setup**: Simple configuration with environment variables
- **Async/Await**: Fully asynchronous for optimal performance

## Installation

Install using pip:

```bash
pip install mcp-clients
```

Or install from uv:

```bash
uv add mcp-clients
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Required: Your API key
YOUR_API_KEY=your_api_key_here

# Required: Your MCP server path
MCP_SERVER=/path/to/your/mcp_server.py
```

## Quick Start

### Basic Usage with OpenAI

```python
import asyncio
from dotenv import load_dotenv

from mcp_clients import OpenAI

load_dotenv()


async def main():
    client = await OpenAI.init(
        server_script_path="path_to_server_script",
    )
    try:
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
```

### Basic Usage with Gemini

```python
import asyncio
from dotenv import load_dotenv

from mcp_clients import Gemini

load_dotenv()


async def main():
    client = await Gemini.init(
        server_script_path="path_to_server_script",
    )
    try:
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Chat Loop

```python
async def custom_chat_handler(client):
    """Custom chat loop with enhanced features"""
    print("Enhanced Chat Started!")
    print("Commands: 'help', 'history', 'clear', 'quit'")
    
    while True:
        try:
            query = input("\n💬 You: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'help':
                print("Available commands: help, history, clear, quit")
                continue
            elif query.lower() == 'history':
                print(f"Conversation has {len(client.history)} messages")
                continue
            elif query.lower() == 'clear':
                client.history = []
                print("Chat history cleared!")
                continue
                
            response = await client.process_query(query)
            print(f"🤖 Assistant: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

# Use the custom chat loop
async def main():
    client = await Gemini.init(
        server_script_path='weather_server.py',
        custom_chat_loop=custom_chat_handler
    )
    
    try:
        await client.chat_loop()
    finally:
        await client.cleanup()
```

## API Reference

### Gemini Class

The Gemini client class for interacting with Gemini AI through MCP servers.

#### Initialization

```python
client = await Gemini.init(
    api_key=None,                    # Gemini API key (or use env var)
    server_script_path=None,         # Path to MCP server script
    model="gemini-2.5-flash",        # Gemini model to use
    system_instruction=None,         # Custom system instruction
    custom_chat_loop=None            # Custom chat loop function
)
```

### OpenAI Class

The OpenAI client class for interacting with Gemini AI through MCP servers.

#### Initialization

```python
client = await OpenAI.init(
    api_key=None,                    # Gemini API key (or use env var)
    server_script_path=None,         # Path to MCP server script
    model="gpt-4.1-nano",            # OpenAI model to use
    system_instruction=None,         # Custom system instruction
    custom_chat_loop=None            # Custom chat loop function
)
```

#### Methods

- **`process_query(query: str) -> str`**: Process a single query
- **`chat_loop()`**: Start interactive chat session
- **`cleanup()`**: Clean up resources (always call this!)
- **`connect_to_server()`**: Manually connect to MCP server

## 🔍 Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   Error: Invalid API key
   ```
   - Ensure your API key is correct
   - Check that the API key is properly set in your environment

2. **Server Connection Issues**
   ```
   Error: Server script must be a .py or .js file
   ```
   - Verify your MCP server script path is correct
   - Ensure the file has the proper extension (.py or .js)

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'mcp_clients'
   ```
   - Install the package: `pip install mcp-clients` or `uv add mcp-clients`
   - If installing from source: `pip install -e .`

## Examples

Check out the `examples/` directory for more usage examples:

- **gemini_client**: Simple chat with MCP tools using Gemini.
- **openai_client**: Simple chat with MCP tools using OpenAI.

## Contributing

I welcome contributions! Here's how you can help:

### Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/faizrazadec/mcp-clients.git
   cd mcp-clients
   ```

2. **Set up development environment**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   uv sync
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Guidelines

- **Code Style**: Follow PEP 8 and use `black` for formatting
- **Type Hints**: Add type hints to all functions and methods
- **Documentation**: Add docstrings and update README if needed
- **Testing**: Write tests for new features (pytest)
- **Commits**: Use conventional commit messages

### Types of Contributions

- **Bug Fixes**: Fix issues and improve stability
- **New Features**: Add new models, tools, or capabilities
- **Documentation**: Improve docs, examples, and tutorials
- **Testing**: Add tests and improve test coverage
- **UI/UX**: Improve user experience and interfaces

### Submitting Changes

1. **Run tests** (when available)
   ```bash
   pytest
   ```

2. **Format code**
   ```bash
   cd mcp_clients/
   black .
   ```

3. **Submit a pull request**
   - Describe your changes clearly
   - Link any related issues
   - Include examples if applicable

### Code of Conduct

Please be respectful and inclusive. We're building this together! 🌟

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Anthropic** for the Model Context Protocol specification
- **FastMCP** for the excellent MCP server framework
- **Contributors** who help make this project better

---

**Made with ❤️ by [Muhammad Faiz Raza](https://github.com/faizrazadec)**

*If you find this project helpful, please consider giving it a ⭐ on GitHub!*
