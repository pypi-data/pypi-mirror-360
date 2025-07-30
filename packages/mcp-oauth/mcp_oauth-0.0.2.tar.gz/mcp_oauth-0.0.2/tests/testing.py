import click
from services.client.client import sample_mcp_client
from services.server.server import sample_fastapi_mcp_server
from mcp_oauth import OAuthServer


def run_client():
    sample_mcp_client()


def run_server():
    sample_fastapi_mcp_server()


def run_oauth():
    oauth_server: OAuthServer = OAuthServer()
    oauth_server.run_starlette_server()


@click.command()
@click.option("--service", default="server", help="Port to listen on")
def main(service: str):
    if service == "server":
        run_server()
    elif service == "client":
        run_client()
    elif service == "oauth" or service == "auth":
        run_oauth()
    else:
        raise Exception(f"Not found service: {service}")


if __name__ == "__main__":
    main()  # type: ignore[call-arg]
