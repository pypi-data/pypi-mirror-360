from .client_provider.client_provider import (
    SimpleOAuthClientProvider,
    OAuthClientProvider,
)
from mcp.shared.auth import OAuthClientMetadata
from .features.token_storage import FileTokenStorage
from .features.callbacks import CallbackFunctions


# TODO: Dar opcion a otras redirect_uris que no sea el server local
class OAuthClient:
    """MCP client with auth support."""

    def __init__(
        self,
        client_name: str,
        server_url: str,
        authorized_username: str = None,
        authorized_username_password: str = None,
        redirect_uris: list[str] = ["http://localhost:3030/callback"],
        redirect_uri_port=3030,
    ):
        self.client_name: str = client_name
        self.redirect_uri_port: int = redirect_uri_port
        self.redirect_uris = redirect_uris
        self.authorized_username: str = authorized_username
        self.authorized_username_password: str = authorized_username_password

        self.server_url: str = server_url
        self.token_storage = FileTokenStorage(server_name=self.server_url)

        self.__oauth: SimpleOAuthClientProvider | None = None
        """private class variable"""

    @property
    def oauth(self) -> OAuthClientProvider:
        if self.__oauth is not None:
            return self.__oauth

        try:
            callback_functions: CallbackFunctions = CallbackFunctions(
                username=self.authorized_username,
                password=self.authorized_username_password,
                port=self.redirect_uri_port,
            )
            client_metadata_dict = {
                "client_name": self.client_name,
                "redirect_uris": self.redirect_uris,
                "grant_types": ["authorization_code", "refresh_token"],
                "response_types": ["code"],
                "token_endpoint_auth_method": "client_secret_post",
            }

            self.__oauth = SimpleOAuthClientProvider(
                server_url=self.server_url.replace("/mcp", ""),
                client_metadata=OAuthClientMetadata.model_validate(
                    client_metadata_dict
                ),
                # storage=FileTokenStorage(server_name=self.server_url),
                storage=self.token_storage,
                redirect_handler=callback_functions._default_redirect_handler,
                callback_handler=callback_functions.callback_handler,
            )
            return self.__oauth
        except:
            return None

    def delete_server_credentials_data(self):
        """Delete credentials (token and client_info) from the current_server"""
        self.token_storage.delete_current_server_credentials_data()
