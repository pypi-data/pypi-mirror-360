from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from mcp_oauth import OAuthClient
import asyncio


def read_resource(http: str, uri: str, oauth_client: OAuthClient) -> any:
    return asyncio.run(_async_read_resource(http=http, uri=uri))


async def _async_read_resource(http: str, uri: str, oauth_client: OAuthClient):
    async with streamablehttp_client(url=http, auth=oauth_client.oauth) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Read a resource
            resource_result = await session.read_resource(uri)
            return resource_result.contents
