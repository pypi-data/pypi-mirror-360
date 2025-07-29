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
