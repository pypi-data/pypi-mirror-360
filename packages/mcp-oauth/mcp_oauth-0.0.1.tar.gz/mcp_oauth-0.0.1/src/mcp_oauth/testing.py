
import click
from tests.run import run_server, run_client, run_oauth


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
