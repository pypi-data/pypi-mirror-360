from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import asyncio


def call_tool(http: str, toolname: str, args: dict) -> any:
    return asyncio.run(async_call_tool(http, toolname, args))


async def async_call_tool(http: str, toolname: str, args: dict):
    async with streamablehttp_client(http) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Call a tool
            tool_result = await session.call_tool(toolname, args)
            return tool_result.content
