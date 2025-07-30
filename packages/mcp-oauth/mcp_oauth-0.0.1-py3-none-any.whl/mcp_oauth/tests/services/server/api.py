import contextlib
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from server.token_verifier.token_verifier import (
    IntrospectionTokenVerifier,
)


class ServerSettings(BaseSettings):
    """Settings for the MCP Server."""

    model_config = SettingsConfigDict(env_prefix="MCP_RESOURCE_")

    # Server settings
    host: str = "localhost"
    port: int = 8000
    server_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

    # Authorization Server settings
    auth_server_url: AnyHttpUrl = AnyHttpUrl("http://localhost:9000")
    auth_server_introspection_endpoint: str = "http://localhost:9000/introspect"

    # MCP settings
    mcp_scope: str = "user"

    # RFC 8707 resource validation
    oauth_strict: bool = False


def create_mcp_server(settings: ServerSettings = ServerSettings()) -> FastMCP:
    token_verifier = IntrospectionTokenVerifier(
        introspection_endpoint=settings.auth_server_introspection_endpoint,
        server_url=str(settings.server_url),
        validate_resource=settings.oauth_strict,  # Only validate when --oauth-strict is set
    )

    mcp: FastMCP = FastMCP(
        name="example-server",
        instructions="This server specializes in private operations of user profiles data",
        debug=True,
        # Auth configuration for RS mode
        token_verifier=token_verifier,
        auth=AuthSettings(
            issuer_url=settings.auth_server_url,
            required_scopes=[settings.mcp_scope],
            resource_server_url=settings.server_url,
        ),
    )

    @mcp.tool(
        name="set_user_profile",
        description="Set the user profile information in database from user data",
    )
    async def set_user_profile(data: dict) -> dict:
        """Set the user profile information in database for user_id"""

        # TODO: Implement any logic here. Eg. database call or request profile
        # information from your user auth system.

        return {
            "status": "success",
            "message": "User added to dataset successfully",
            "data": data,
        }

    return mcp


def create_app(
    servers: list[FastMCP],
    settings: ServerSettings = ServerSettings(),
) -> FastAPI:

    # Create a combined lifespan to manage both session managers
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        async with contextlib.AsyncExitStack() as stack:
            for server in servers:
                await stack.enter_async_context(server.session_manager.run())
            yield

    app = FastAPI(lifespan=lifespan)
    for server in servers:
        app.mount(
            f"/{server.name}",
            server.streamable_http_app(),
        )

    @app.get("/")
    async def redirect_to_help():
        return RedirectResponse(url="/aviable-servers")

    @app.get("/aviable-servers", include_in_schema=False)
    async def aviable_servers():
        return {
            "aviable-servers": [
                f"http://{settings.host}:{settings.port}/{server.name}/mcp"
                for server in servers
            ]
        }

    return app


server_settings: ServerSettings = ServerSettings()
app: FastAPI = create_app(
    servers=[create_mcp_server(settings=server_settings)],
    settings=server_settings,
)
