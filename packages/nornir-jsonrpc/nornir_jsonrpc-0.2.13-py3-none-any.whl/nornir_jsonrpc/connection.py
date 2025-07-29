from typing import Any

import httpx
from nornir.core.configuration import Config
from pydantic import BaseModel

CONNECTION_NAME = "JSONRPC"


class JSONRPC(BaseModel):
    """
    JSONRPC connection plugin for Nornir.
    """

    def open(
        self,
        hostname: str,
        username: str,
        password: str,
        port: int = 443,
        platform: str | None = None,
        extras: dict[str, Any] | None = None,
        configuration: Config | None = None,
    ) -> None:
        """
        Opens a connection to the device.

        Args:
            hostname: The hostname or IP address of the device.
            username: The username to use for authentication.
            password: The password to use for authentication.
            port: The port to use for the connection. Defaults to 443 (note: standard HTTPS is 443).
            platform: The platform of the device. Not used by this connection plugin.
            extras: Additional parameters for the connection.
            configuration: The Nornir configuration. Not used by this connection plugin.
        """
        if (
            extras
            and "connection" in extras
            and isinstance(extras["connection"], httpx.Client)
        ):
            self.connection = extras["connection"]
        else:
            self.connection = httpx.Client(
                base_url=f"https://{hostname}:{port}/jsonrpc",
                auth=(username, password),
                verify=False,
            )

    def close(self) -> None:
        """
        Closes the connection to the device.
        """
        self.connection.close()
