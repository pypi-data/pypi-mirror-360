from mcp.client.auth import TokenStorage
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from jose import jwt
from dotenv import load_dotenv
import os
import json

load_dotenv()
CLIENT_ENV_PATH = "data/oauth.client.json"


class FileTokenStorage(TokenStorage):
    """Simple in-file token storage implementation."""

    def __init__(self, server_name: str):
        self.server_name: str = server_name
        self.data: dict[str, dict[str, str]] = {}
        self.__load_data()

        self._tokens: OAuthToken | None = None
        self._client_info: OAuthClientInformationFull | None = None

        if self.data.keys().__contains__(self.server_name):
            if self.data[self.server_name].keys().__contains__("OAuthToken"):
                self._tokens = Criptografy.get_oauthtoken(
                    self.data[self.server_name]["OAuthToken"]
                )
            if self.data[self.server_name].keys().__contains__("ClientInfo"):
                self._client_info = Criptografy.get_clientinfo(
                    self.data[self.server_name]["ClientInfo"]
                )

    async def get_tokens(self) -> OAuthToken | None:
        """This funtion is called by `def initialize()` from [`OAuthClientProvider`](src/mcp_oauth/client/client_provider/client_provider.py)"""
        return self._tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self._tokens = tokens
        criptografy_token: str = Criptografy.generate_oauthtoken(self._tokens)

        if self.data.keys().__contains__(self.server_name):
            self.data[self.server_name]["OAuthToken"] = criptografy_token
        else:
            self.data[self.server_name] = {"OAuthToken": criptografy_token}

        self.__save_data()
        pass

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        """This funtion is called by `def initialize()` from [`OAuthClientProvider`](src/mcp_oauth/client/client_provider/client_provider.py)"""
        return self._client_info

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self._client_info = client_info
        criptografy_token: str = Criptografy.generate_clientinfo(self._client_info)
        if self.data.keys().__contains__(self.server_name):
            self.data[self.server_name]["ClientInfo"] = criptografy_token
        else:
            self.data[self.server_name] = {"ClientInfo": criptografy_token}

        self.__save_data()
        pass

    def __load_data(self) -> bool:
        data_path: str = os.path.join(os.getcwd(), CLIENT_ENV_PATH)
        if os.path.exists(data_path):
            with open(data_path, "r") as file:
                self.data = json.load(file)
                return True
        return False

    def __save_data(self) -> None:
        data_path: str = os.path.join(os.getcwd(), CLIENT_ENV_PATH)
        os.makedirs(os.path.dirname(data_path), exist_ok=True)

        with open(data_path, "w") as file:
            json.dump(self.data, file)

    def delete_current_server_credentials_data(self):
        """Empty and delete data from current connected server"""
        if self.data.keys().__contains__(self.server_name):
            del self.data[self.server_name]
            self._tokens = None
            self._client_info = None
            # self.__save_data()


CRIPTOGRAFY_KEY = os.getenv("CRIPTOGRAFY_KEY")


class Criptografy:
    def generate_oauthtoken(tokens: OAuthToken) -> str:
        payload = {"base_model": tokens.model_dump_json()}
        encoded_jwt = jwt.encode(payload, CRIPTOGRAFY_KEY, algorithm="HS256")
        return encoded_jwt

    def get_oauthtoken(token: str) -> OAuthToken:
        payload = jwt.decode(token, CRIPTOGRAFY_KEY, algorithms=["HS256"])
        payload = payload["base_model"]
        oauthtoken: OAuthToken = OAuthToken.model_validate_json(payload)
        return oauthtoken

    def generate_clientinfo(client_info: OAuthClientInformationFull) -> str:
        payload = {"base_model": client_info.model_dump_json()}
        encoded_jwt = jwt.encode(payload, CRIPTOGRAFY_KEY, algorithm="HS256")
        return encoded_jwt

    def get_clientinfo(token: str) -> OAuthClientInformationFull:
        payload = jwt.decode(token, CRIPTOGRAFY_KEY, algorithms=["HS256"])
        payload = payload["base_model"]
        client_info: OAuthClientInformationFull = (
            OAuthClientInformationFull.model_validate_json(payload)
        )
        return client_info
