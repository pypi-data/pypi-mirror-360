"""
Simple OAuth system integrated with `"mcp[cli]"`
"""

from dotenv import load_dotenv

load_dotenv()

from .client.oauth_client import OAuthClient
from .server.oauth_server import OAuthServer, SimpleAuthSettings, AuthServerSettings
from .server.token_verifier.token_verifier import IntrospectionTokenVerifier

__all__ = [
    "OAuthClient",
    "OAuthServer",
    "IntrospectionTokenVerifier",
    "SimpleAuthSettings",
    "AuthServerSettings",
]
