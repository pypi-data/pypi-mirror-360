from mcp.client.session import ClientSession
from mcp.shared.exceptions import McpError
from client.oauth_client import OAuthClient

import asyncio
from datetime import timedelta
from mcp.client.streamable_http import streamablehttp_client


def sample_mcp_client():
    # Es necesario tener un servidor MCP corriendo en la direccion http://127.0.0.1:8000//example-server/mcp por httpstream
    server_url: str = "http://127.0.0.1:8000/example-server/mcp"
    oauth_server_url: str = "http://127.0.0.1:9000"

    # Es necesario tener un servidor OAuth corriendo en la direccion http://localhost:9000
    oauth_client: OAuthClient = OAuthClient(
        client_name="sample_client",
        server_url=oauth_server_url,
        authorized_username="user",
        authorized_username_password="password",
    )

    async def open_session():
        print("📡 Opening StreamableHTTP transport connection with auth...")
        async with streamablehttp_client(
            url=server_url,
            auth=oauth_client.oauth,
            timeout=timedelta(seconds=60),
        ) as (read_stream, write_stream, get_session_id):
            print("🤝 Initializing MCP session...")
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("✨ Session initialization complete!")

                print(f"\n✅ Connected to MCP server at {server_url}")
                if get_session_id:
                    session_id = get_session_id()
                    if session_id:
                        print(f"Session ID: {session_id}")

                tools = await session.list_tools()

                print("\n⚙️  Aviable Tools")
                for tool in tools.tools:
                    print(f"   • {tool.name}: {tool.description}")

    asyncio.run(open_session())
