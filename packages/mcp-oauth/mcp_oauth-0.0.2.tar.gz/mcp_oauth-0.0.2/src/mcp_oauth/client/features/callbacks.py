import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import requests
import urllib.parse


class CallbackHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler to capture OAuth callback."""

    def __init__(
        self, request, client_address, server, callback_data, timeout: int = 300
    ):
        """Initialize with callback data storage."""
        self.callback_data = callback_data
        self.timeout: int = 300
        super().__init__(request, client_address, server)

    def do_GET(self):
        """Handle GET request from OAuth redirect."""
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)

        if "code" in query_params:
            self.callback_data["authorization_code"] = query_params["code"][0]
            self.callback_data["state"] = query_params.get("state", [None])[0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""
            <html>
            <body>
                <h1>Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                <script>setTimeout(() => window.close(), 2000);</script>
            </body>
            </html>
            """
            )
        elif "error" in query_params:
            self.callback_data["error"] = query_params["error"][0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                f"""
            <html>
            <body>
                <h1>Authorization Failed</h1>
                <p>Error: {query_params['error'][0]}</p>
                <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """.encode()
            )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class CallbackServer:
    """Simple server to handle OAuth callbacks."""

    def __init__(self, port=3000):
        self.port = port
        self.server = None
        self.thread = None
        self.callback_data = {"authorization_code": None, "state": None, "error": None}
        self.is_started: bool = False

    def _create_handler_with_data(self):
        """Create a handler class with access to callback data."""
        callback_data = self.callback_data

        class DataCallbackHandler(CallbackHandler):
            def __init__(self, request, client_address, server):
                super().__init__(request, client_address, server, callback_data)

        return DataCallbackHandler

    def start(self):
        """Start the callback server in a background thread."""
        if not self.is_started:
            self.is_started = True
            handler_class = self._create_handler_with_data()
            self.server = HTTPServer(("localhost", self.port), handler_class)
            self.thread = threading.Thread(
                target=self.server.serve_forever, daemon=True
            )
            self.thread.start()
            print(f"🖥️  Started callback server on http://localhost:{self.port}")

    def stop(self):
        """Stop the callback server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=1)
        self.is_started = False

    def wait_for_callback(self, timeout=300):
        """Wait for OAuth callback with timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.callback_data["authorization_code"]:
                return self.callback_data["authorization_code"]
            elif self.callback_data["error"]:
                raise Exception(f"OAuth error: {self.callback_data['error']}")
            time.sleep(0.1)
        raise Exception("Timeout waiting for OAuth callback")

    def get_state(self):
        """Get the received state parameter."""
        return self.callback_data["state"]


class CallbackFunctions:
    def __init__(
        self,
        username: str,
        password: str,
        port: int = 3030,
        sequre_site: bool = True,
        timeout: int = 300,
    ):
        self.port: int = port
        self.username: str = username
        self.password: str = password
        self.sequre_site: bool = sequre_site
        self.time_out: int = timeout

        self.callback_server: CallbackServer = CallbackServer(port=self.port)

    async def callback_handler(self) -> tuple[str, str | None]:
        callback_server = self.callback_server

        """Wait for OAuth callback and return auth code and state."""
        print("⏳ Waiting for authorization callback...")
        try:
            auth_code = callback_server.wait_for_callback(timeout=300)
            return auth_code, callback_server.get_state()
        finally:
            callback_server.stop()

    async def _default_redirect_handler(self, authorization_url: str) -> None:
        """Default redirect handler that GET the URL from requests."""
        # start callback server
        self.callback_server.start()

        if (
            not authorization_url.startswith("https")
            and not authorization_url.startswith("http://localhost")
            and not authorization_url.startswith("http://127.0.0.1")
            and not authorization_url.startswith("http://0.0.0.0")
            and self.sequre_site
        ):
            raise Exception("No sequre site")

        if self.username is not None and self.password is not None:
            payload = {
                "username": self.username,
                "password": self.password,
            } | get_params_from_uri(authorization_url)
            authorization_url = authorization_url.split("?")[0]

            response = requests.post(
                authorization_url, data=payload, allow_redirects=False
            )

            # Esto es para usar el form del post, ya que en la redireccion se pierden datos de credenciales y no se pude tocar el codigo fuente
            if response.status_code in (301, 302, 303, 307, 308):
                redirect_url = response.headers["Location"]
                requests.post(redirect_url, data=payload)
        else:
            webbrowser.open(authorization_url)


def get_params_from_uri(url: str):
    parsed_url = urllib.parse.urlparse(url)
    query = parsed_url.query
    params = urllib.parse.parse_qs(query)
    return params
