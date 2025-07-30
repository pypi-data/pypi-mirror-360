from mcp_oauth import OAuthClient
from mcp.client.auth import OAuthClientProvider
from ...tools.get_uri_args import get_args_from_uri
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import asyncio


class Service:
    """
    Objeto que representa un servicio brindado o expuesto por un servidor mcp. Falicita la manipulacion del mismo
    """

    def __init__(self, http: str, data, server: dict):
        self.http: str = http
        self.data = data
        self.name: str = data.name
        self.description: str = data.description
        self.args: dict[str, any] = None
        self.server: dict = server
        self.oauth_client: OAuthClient | None = server["oauth_client"]

    def __str__(self):
        return str(
            {
                "name": self.name,
                "description": self.description,
                "args": self.args,
            }
        )

    def __call__(self, args: dict[str, any]):
        Exception("Not Implemented")


class Tool(Service):
    def __init__(self, http, data, server):
        super().__init__(http, data, server)
        args = data.inputSchema["properties"]
        self.args = [{"name": key, "type": args[key]["type"]} for key in args.keys()]

    def __call__(self, args: dict[str, any]):
        return self.call(args)

    def call(self, args: dict[str, any]):
        return asyncio.run(
            Tool.async_call(self.http, self.name, args, self.oauth_client)
        )

    async def async_call(
        http: str, toolname: str, args: dict, oauth_client: OAuthClient | None
    ):
        oauth: OAuthClientProvider = (
            oauth_client.oauth if oauth_client is not None else None
        )
        async with streamablehttp_client(url=http, auth=oauth) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # Call a tool
                tool_result = await session.call_tool(toolname, args)
                return tool_result.content


class Resource(Service):
    def __init__(self, http, data, server):
        super().__init__(http, data, server)
        self.args = get_args_from_uri(data.uriTemplate)
        self.args = [{"name": arg, "type": "string"} for arg in self.args]

    def __call__(self, args: dict[str, any]):
        return self.read(args)

    def read(self, args: dict[str, str]):
        uri = self.data.uriTemplate
        for key in args:
            uri = uri.replace("{" + key + "}", str(args[key]))
        return asyncio.run(Resource.async_read(self.http, uri, self.oauth_client))

    async def _async_read(http: str, uri: str, oauth_client: OAuthClient | None):
        oauth: OAuthClientProvider = (
            oauth_client.oauth if oauth_client is not None else None
        )
        async with streamablehttp_client(url=http, auth=oauth) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # Read a resource
                resource_result = await session.read_resource(uri)
                return resource_result.contents


class Prompt(Service):
    def __init__(self, http, data, server):
        super().__init__(http, data, server)

    def __call__(self, args: dict[str, any]):
        return self.get(args)

    def get(self, args: dict[str, str]):
        pass
