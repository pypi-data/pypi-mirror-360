import os
import json
from mcp_oauth import OAuthClient
from ..config.logger import logger


class Servers:
    """
    Extrae las credenciales de cada uno de los servers en la configuracion `.config.json`. Aternativamente puede pasarse otro archivo `.json`
    como argumento `config_file_path`
    """

    def __init__(
        self, config_file_path: str = "config.json", app_name: str = "mcp-llm-client"
    ):
        self.app_name = app_name
        self.config_file_path: str = config_file_path
        self.mcp_servers: dict[str, dict] | None = {}
        self.load_servers()

    def load_servers(self):
        """Carga cada uno de los credenciales de los servidores que se le conectan desde el `.config`"""
        with open(f"{os.getcwd()}{os.path.sep}{self.config_file_path}", "r") as file:
            json_config: dict = json.loads(file.read())
        self.mcp_servers = json_config["mcp_servers"]

        for server in self.mcp_servers.values():
            self.create_oauth_client(server=server)

    def create_oauth_client(self, server: dict[str, dict]) -> None:
        """Genera un oauth client para este servidor, usando los datos proporcionados en `config.json`"""
        oauth_client: OAuthClient | None = None

        if server.keys().__contains__("auth") and (
            server["auth"].keys().__contains__("required")
            and server["auth"]["required"]
        ):
            server_url: str = server["auth"]["server"]
            server_name: str | None = (
                server["name"] if server.keys().__contains__("name") else None
            )
            server_full_name: str = (
                f""" "{server_name}[{server_url}]" """
                if server_name is not None
                else f""" "[{server_url}]" """
            )

            username: str = None
            password: str = None

            try:
                if server["auth"].keys().__contains__("secrets"):
                    username = server["auth"]["secrets"]["username"]
                    password = server["auth"]["secrets"]["password"]
            except:
                pass

            if username is None or password is None:
                logger.info(
                    f"Server {server_full_name} require manual login in webbrowser that will be open."
                )
            oauth_client = OAuthClient(
                client_name=self.app_name,
                server_url=server_url,
                authorized_username=username,
                authorized_username_password=password,
            )

        server["oauth_client"] = oauth_client
