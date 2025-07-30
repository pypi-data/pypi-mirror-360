"""
Simple OAuth system integrated with `"mcp[cli]"`
"""

from .client.oauth_client import OAuthClient
from .server.oauth_server import OAuthServer, SimpleAuthSettings, AuthServerSettings
from .server.token_verifier.token_verifier import IntrospectionTokenVerifier
from .start_env import main as start_env_base

__all__ = [
    "OAuthClient",
    "OAuthServer",
    "IntrospectionTokenVerifier",
    "SimpleAuthSettings",
    "AuthServerSettings",
    "start_env_base",
]
