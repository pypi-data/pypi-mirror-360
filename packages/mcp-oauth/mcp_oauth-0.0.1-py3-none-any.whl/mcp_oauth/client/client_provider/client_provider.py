from mcp.client.auth import (
    OAuthClientProvider,
    TokenStorage,
    httpx,
    AsyncGenerator,
    Awaitable,
    Callable,
    OAuthClientMetadata,
    MCP_PROTOCOL_VERSION,
    logger,
)
from ..features.token_storage import FileTokenStorage


class SimpleOAuthClientProvider(OAuthClientProvider):
    def __init__(
        self,
        server_url: str,
        client_metadata: OAuthClientMetadata,
        storage: TokenStorage,
        redirect_handler: Callable[[str], Awaitable[None]],
        callback_handler: Callable[[], Awaitable[tuple[str, str | None]]],
        timeout: float = 300.0,
    ):
        """Initialize OAuth2 authentication."""
        super().__init__(
            server_url=server_url,
            client_metadata=client_metadata,
            storage=storage,
            redirect_handler=redirect_handler,
            callback_handler=callback_handler,
            timeout=timeout,
        )
        self._initialized = False
        self.storage: FileTokenStorage = storage
        """`FileTokenStorage` reference for use class methods"""

    async def _perform_authorization(self) -> tuple[str, str]:
        response = await super()._perform_authorization()
        return response

    async def _exchange_token(
        self, auth_code: str, code_verifier: str
    ) -> httpx.Request:
        response = await super()._exchange_token(
            auth_code=auth_code, code_verifier=code_verifier
        )
        return response

    async def _handle_token_response(self, response: httpx.Response) -> None:
        response = await super()._handle_token_response(response=response)
        return response

    async def _refresh_token(self) -> httpx.Request:
        response = await super()._refresh_token()
        return response

    async def _handle_refresh_response(self, response: httpx.Response) -> bool:
        response = await super()._handle_refresh_response(response=response)
        return response

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        """HTTPX auth flow integration."""
        async with self.context.lock:
            end_flow: bool = False
            max_cicles: int = 10
            cicles_count: int = 0
            while not end_flow:
                end_flow = True  # Flow end for default
                if not self._initialized:
                    await self._initialize()

                # Capture protocol version from request headers
                self.context.protocol_version = request.headers.get(
                    MCP_PROTOCOL_VERSION
                )

                # Perform OAuth flow if not authenticated
                if not self.context.is_token_valid():
                    try:
                        # OAuth flow must be inline due to generator constraints
                        # Step 1: Discover protected resource metadata (spec revision 2025-06-18)
                        discovery_request = await self._discover_protected_resource()
                        discovery_response = yield discovery_request
                        await self._handle_protected_resource_response(
                            discovery_response
                        )

                        # Step 2: Discover OAuth metadata (with fallback for legacy servers)
                        oauth_request = await self._discover_oauth_metadata()
                        oauth_response = yield oauth_request
                        handled = await self._handle_oauth_metadata_response(
                            oauth_response, is_fallback=False
                        )

                        # If path-aware discovery failed with 404, try fallback to root
                        if not handled:
                            fallback_request = (
                                await self._discover_oauth_metadata_fallback()
                            )
                            fallback_response = yield fallback_request
                            await self._handle_oauth_metadata_response(
                                fallback_response, is_fallback=True
                            )

                        # Step 3: Register client if needed
                        registration_request = await self._register_client()
                        if registration_request:
                            registration_response = yield registration_request
                            await self._handle_registration_response(
                                registration_response
                            )

                        # Step 4: Perform authorization
                        auth_code, code_verifier = await self._perform_authorization()

                        # Step 5: Exchange authorization code for tokens
                        token_request = await self._exchange_token(
                            auth_code, code_verifier
                        )
                        token_response = yield token_request
                        await self._handle_token_response(token_response)
                    except Exception as e:
                        logger.error(f"OAuth flow error: {e}")
                        raise

                # Add authorization header and make request
                self._add_auth_header(request)
                response = yield request

                # Handle 401 responses
                if response.status_code == 401 and self.context.can_refresh_token():
                    # Try to refresh token
                    refresh_request = await self._refresh_token()
                    refresh_response = yield refresh_request

                    if await self._handle_refresh_response(refresh_response):
                        # Retry original request with new token
                        self._add_auth_header(request)
                        yield request
                    else:
                        # Refresh failed, need full re-authentication
                        self._initialized = False

                        # OAuth flow must be inline due to generator constraints
                        # Step 1: Discover protected resource metadata (spec revision 2025-06-18)
                        discovery_request = await self._discover_protected_resource()
                        discovery_response = yield discovery_request
                        await self._handle_protected_resource_response(
                            discovery_response
                        )

                        # Step 2: Discover OAuth metadata (with fallback for legacy servers)
                        oauth_request = await self._discover_oauth_metadata()
                        oauth_response = yield oauth_request
                        handled = await self._handle_oauth_metadata_response(
                            oauth_response, is_fallback=False
                        )

                        # If path-aware discovery failed with 404, try fallback to root
                        if not handled:
                            fallback_request = (
                                await self._discover_oauth_metadata_fallback()
                            )
                            fallback_response = yield fallback_request
                            await self._handle_oauth_metadata_response(
                                fallback_response, is_fallback=True
                            )

                        # Step 3: Register client if needed
                        registration_request = await self._register_client()
                        if registration_request:
                            registration_response = yield registration_request
                            await self._handle_registration_response(
                                registration_response
                            )

                        # Step 4: Perform authorization
                        auth_code, code_verifier = await self._perform_authorization()

                        # Step 5: Exchange authorization code for tokens
                        token_request = await self._exchange_token(
                            auth_code, code_verifier
                        )
                        token_response = yield token_request
                        await self._handle_token_response(token_response)

                        # Retry with new tokens
                        self._add_auth_header(request)
                        yield request

                if response.status_code == 401 and not self.context.can_refresh_token():
                    # if unauthorized and not can refresh token the is needed login again with credentials
                    self.storage.delete_current_server_credentials_data()
                    # initialice with empty tokens and client_info
                    await self._initialize()

                    if cicles_count < max_cicles:
                        # Not end flow, again is needed repeat the proccess
                        end_flow = False
                        cicles_count += 1
