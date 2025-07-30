import os
import sys
import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional
import logging
import platform
from datetime import datetime

from kumoapi.typing import Dtype, Stype

from kumoai.client.client import KumoClient
from kumoai._logging import initialize_logging, _ENV_KUMO_LOG
from kumoai._singleton import Singleton
from kumoai.futures import create_future, initialize_event_loop
from kumoai.spcs import (
    _get_active_session,
    _get_spcs_token,
    _run_refresh_spcs_token,
)

initialize_logging()
initialize_event_loop()


@dataclass
class GlobalState(metaclass=Singleton):
    r"""Global storage of the state needed to create a Kumo client object. A
    singleton so its initialized state can be referenced elsewhere for free.
    """

    # NOTE fork semantics: CoW on Linux, and re-execed on Windows. So this will
    # likely not work on Windows unless we have special handling for the shared
    # state:
    _url: Optional[str] = None
    _api_key: Optional[str] = None
    _snowflake_credentials: Optional[Dict[str, Any]] = None
    _spcs_token: Optional[str] = None
    _snowpark_session: Optional[Any] = None

    thread_local: threading.local = threading.local()

    def clear(self) -> None:
        if hasattr(self.thread_local, '_client'):
            del self.thread_local._client
        self._url = None
        self._api_key = None
        self._snowflake_credentials = None
        self._spcs_token = None

    @property
    def initialized(self) -> bool:
        return self._url is not None and (
            self._api_key is not None or self._snowflake_credentials
            is not None or self._snowpark_session is not None)

    @property
    def client(self) -> KumoClient:
        r"""Accessor for the Kumo client. Note that clients are stored as
        thread-local variables as the requests Session library is not
        guaranteed to be thread-safe.

        For more information, see https://github.com/psf/requests/issues/1871.
        """
        if self._url is None or (self._api_key is None
                                 and self._spcs_token is None
                                 and self._snowpark_session is None):
            raise ValueError(
                "Client creation or authentication failed; please re-create "
                "your client before proceeding.")

        if hasattr(self.thread_local, '_client'):
            return self.thread_local._client

        client = KumoClient(self._url, self._api_key, self._spcs_token)
        self.thread_local._client = client
        return client

    @property
    def is_spcs(self) -> bool:
        return (self._api_key is None
                and (self._snowflake_credentials is not None
                     or self._snowpark_session is not None))


global_state: GlobalState = GlobalState()


def init(
    url: Optional[str] = None,
    api_key: Optional[str] = None,
    snowflake_credentials: Optional[Dict[str, str]] = None,
    snowflake_application: Optional[str] = None,
    log_level: str = "INFO",
) -> None:
    r"""Initializes and authenticates the API key against the Kumo service.
    Successful authentication is required to use the SDK.

    Example:
        >>> import kumoai
        >>> kumoai.init(url="<api_url>", api_key="<api_key>")  # doctest: +SKIP

    Args:
        url: The Kumo API endpoint. Can also be provided via the
            ``KUMO_API_ENDPOINT`` envronment variable. Will be inferred from
            the provided API key, if not provided.
        api_key: The Kumo API key. Can also be provided via the
            ``KUMO_API_KEY`` environment variable.
        snowflake_credentials: The Snowflake credentials to authenticate
            against the Kumo service. The dictionary should contain the keys
            ``"user"``, ``"password"``, and ``"account"``. This should only be
            provided for SPCS.
        snowflake_application: The Snowflake application.
        log_level: The logging level that Kumo operates under. Defaults to
            INFO; for more information, please see
            :class:`~kumoai.set_log_level`. Can also be set with the
            environment variable ``KUMOAI_LOG``.
    """  # noqa
    # Avoid mutations to the global state after it is set:
    if global_state.initialized:
        print(
            "Client has already been created. To re-initialize Kumo, please "
            "start a new interpreter. No changes will be made to the current "
            "session.")
        return

    set_log_level(os.getenv(_ENV_KUMO_LOG, log_level))

    # Get API key:
    api_key = api_key or os.getenv("KUMO_API_KEY")

    snowpark_session = None
    if snowflake_application:
        if url is not None:
            raise ValueError(
                "Client creation failed: both snowflake_application and url "
                "are specified. If running from a snowflake notebook, specify"
                "only snowflake_application.")
        snowpark_session = _get_active_session()
        if not snowpark_session:
            raise ValueError(
                "Client creation failed: snowflake_application is specified "
                "without an active snowpark session. If running outside "
                "a snowflake notebook, specify a URL and credentials.")
        description = snowpark_session.sql(
            f"DESCRIBE SERVICE {snowflake_application}."
            "USER_SCHEMA.KUMO_SERVICE").collect()[0]
        url = f"http://{description.dns_name}:8888/public_api"

    if api_key is None and not snowflake_application:
        if snowflake_credentials is None:
            raise ValueError(
                "Client creation failed: Neither API key nor snowflake "
                "credentials provided. Please either set the 'KUMO_API_KEY' "
                "or explicitly call `kumoai.init(...)`.")
        if (set(snowflake_credentials.keys())
                != {'user', 'password', 'account'}):
            raise ValueError(
                f"Provided credentials should be a dictionary with keys "
                f"'user', 'password', and 'account'. Only "
                f"{set(snowflake_credentials.keys())} were provided.")

    # Get or infer URL:
    url = url or os.getenv("KUMO_API_ENDPOINT")
    try:
        if api_key:
            url = url or f"http://{api_key.split(':')[0]}.kumoai.cloud/api"
    except KeyError:
        pass
    if url is None:
        raise ValueError(
            "Client creation failed: endpoint URL not provided. Please "
            "either set the 'KUMO_API_ENDPOINT' environment variable or "
            "explicitly call `kumoai.init(...)`.")

    # Assign global state after verification that client can be created and
    # authenticated successfully:
    spcs_token = _get_spcs_token(
        snowflake_credentials
    ) if not api_key and snowflake_credentials else None
    client = KumoClient(url=url, api_key=api_key, spcs_token=spcs_token)
    if client.authenticate():
        global_state._url = client._url
        global_state._api_key = client._api_key
        global_state._snowflake_credentials = snowflake_credentials
        global_state._spcs_token = client._spcs_token
        global_state._snowpark_session = snowpark_session
    else:
        raise ValueError("Client authentication failed. Please check if you "
                         "have a valid API key.")

    if not api_key and snowflake_credentials:
        # Refresh token every 10 minutes (expires in 1 hour):
        create_future(_run_refresh_spcs_token(minutes=10))

    logger = logging.getLogger('kumoai')
    log_level = logging.getLevelName(logger.getEffectiveLevel())
    logger.info(
        "Successfully initialized the Kumo SDK against deployment %s, with "
        "log level %s.", url, log_level)


def set_log_level(level: str) -> None:
    r"""Sets the Kumo logging level, which defines the amount of output that
    methods produce.

    Example:
        >>> import kumoai
        >>> kumoai.set_log_level("INFO")  # doctest: +SKIP

    Args:
        level: the logging level. Can be one of (in order of lowest to highest
            log output) :obj:`DEBUG`, :obj:`INFO`, :obj:`WARNING`,
            :obj:`ERROR`, :obj:`FATAL`, :obj:`CRITICAL`.
    """
    # logging library will ensure `level` is a valid string, and raise a
    # warning if not:
    logging.getLogger('kumoai').setLevel(level)


# Try to initialize purely with environment variables:
if ("pytest" not in sys.modules and "KUMO_API_KEY" in os.environ
        and "KUMO_API_ENDPOINT" in os.environ):
    init()

import kumoai.connector  # noqa
import kumoai.encoder  # noqa
import kumoai.graph  # noqa
import kumoai.pquery  # noqa
import kumoai.trainer  # noqa
import kumoai.utils  # noqa
import kumoai.databricks  # noqa

from kumoai.connector import (  # noqa
    SourceTable, SourceTableFuture, S3Connector, SnowflakeConnector,
    DatabricksConnector, BigQueryConnector, FileUploadConnector)
from kumoai.graph import Column, Edge, Graph, Table  # noqa
from kumoai.pquery import (  # noqa
    PredictionTableGenerationPlan, PredictiveQuery,
    TrainingTableGenerationPlan, TrainingTable, TrainingTableJob,
    PredictionTable, PredictionTableJob)
from kumoai.trainer import (  # noqa
    ModelPlan, Trainer, TrainingJobResult, TrainingJob,
    BatchPredictionJobResult, BatchPredictionJob)

__all__ = [
    'Dtype',
    'Stype',
    'SourceTable',
    'SourceTableFuture',
    'S3Connector',
    'SnowflakeConnector',
    'DatabricksConnector',
    'BigQueryConnector',
    'FileUploadConnector',
    'Column',
    'Table',
    'Graph',
    'Edge',
    'PredictiveQuery',
    'TrainingTable',
    'TrainingTableJob',
    'TrainingTableGenerationPlan',
    'PredictionTable',
    'PredictionTableJob',
    'PredictionTableGenerationPlan',
    'Trainer',
    'TrainingJobResult',
    'TrainingJob',
    'BatchPredictionJobResult',
    'BatchPredictionJob',
    'ModelPlan',
]

try:
    from importlib.metadata import version
    assert __package__ is not None
    __version__ = version(__package__)
except Exception:
    __version__ = '2.4'


def authenticate(api_url: str, redirect_port: int = 8765) -> str:
    """Starts a local HTTP server to handle OAuth2 or similar login flow, opens
    the browser for user login, and returns the access token.

    Args:
        api_url: The base URL for authentication (login page).
        redirect_port: The port for the local callback server (default: 8765).

    Returns:
        The access token as a string.
    """
    import http.server
    from socketserver import TCPServer
    import threading
    import webbrowser
    import urllib.parse
    import time
    from typing import Any, Dict

    logger = logging.getLogger('kumoai')

    token_status: Dict[str, Any] = {
        'token': None,
        'token_name': None,
        'failed': False
    }

    # Generate a token name
    token_name = (f"SDK_{platform.node()}_" +
                  datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed_path = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_path.query)
            token = params.get('token', [None])[0]
            received_token_name = params.get('token_name', [None])[0]

            if token:
                token_status['token'] = token
                token_status['token_name'] = received_token_name
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
            else:
                token_status['failed'] = True
                self.send_response(400)
                self.end_headers()

            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authenticate SDK</title>
                <style>
                    body {
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        font-family:
                            -apple-system,
                            BlinkMacSystemFont,
                            'Segoe UI', Roboto, sans-serif;
                    }
                    .container {
                        text-align: center;
                        padding: 40px;
                    }
                    svg {
                        margin-bottom: 20px;
                    }
                    p {
                        font-size: 18px;
                        color: #333;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <?xml version="1.0" encoding="UTF-8"?>
                    <svg xmlns="http://www.w3.org/2000/svg"
                        id="kumo-logo" width="183.908" height="91.586"
                        viewBox="0 0 183.908 91.586">
                        <g id="c">
                            <g id="Group_9893" data-name="Group 9893">
                                <path id="Path_4831" data-name="Path 4831"
                                    d="M67.159,67.919V46.238L53.494,59.491,
                                    68.862,82.3H61.567L49.1,63.74l-7.011,6.8V82.3h-6.02V29.605h6.02V62.182l16.642-16.36H73.109v22.1c0,5.453,3.611,9.419,9.277,9.419,5.547,0,9.14-3.9,9.2-9.282V0H0V91.586H91.586V80.317a15.7,15.7,0,0,1-9.2,2.828c-8.569,0-15.226-6.02-15.226-15.226Z"
                                    fill="#d40e8c">
                                </path>
                                <path id="Path_4832" data-name="Path 4832"
                                    d="M233.452,121.881h-6.019V98.3c0-4.745-3.117-8.286-7.932-8.286s-7.932,3.541-7.932,8.286v23.583h-6.02V98.3c0-4.745-3.116-8.286-7.932-8.286s-7.932,3.541-7.932,8.286v23.583h-6.02V98.51c0-7.932,5.736-14.023,13.952-14.023a12.106,12.106,0,0,1,10.906,6.02,12.3,12.3,0,0,1,10.978-6.02c8.285,0,13.951,6.091,13.951,14.023v23.37Z"
                                    transform="translate(-86.054 -39.585)"
                                    fill="#d40e8c">
                                </path>
                                <path id="Path_4833" data-name="Path 4833"
                                    d="M313.7,103.751c0,10.481-7.932,
                                    19.051-18.342,19.051-10.341,
                                    0-18.343-8.569-18.343-19.051,0-10.623,
                                    8-19.263,18.343-19.263C305.767,84.488,
                                    313.7,93.128,313.7,103.751Zm-6.02,
                                    0c0-7.436-5.523-13.527-12.322-13.527-6.728
                                    ,0-12.252,6.091-12.252,13.527,0,7.295,
                                    5.524,13.244,12.252,13.244,6.8,0,
                                    12.322-5.949,12.322-13.244Z"
                                    transform="translate(-129.791 -39.585)"
                                    fill="#d40e8c">
                                </path>
                            </g>
                        </g>
                    </svg>

                    <div id="success-div"
                        style="background: #f2f8f0;
                            border: 1px solid #1d8102;
                            border-radius: 1px;
                            padding: 24px 32px;
                            margin: 24px auto 0 auto;
                            max-width: 400px;
                            text-align: left;
                            display: none;"
                    >
                        <div style="font-size: 1.1em;
                            font-weight: bold;
                            margin-bottom: 10px;
                            text-align: left;"
                        >
                            Request successful
                        </div>
                        <div style="font-size: 1.1em;">
                            Kumo SDK has been granted a token.
                            You may now close this window.
                        </div>
                    </div>

                    <div id="failure-div"
                        style="background: #ffebeb;
                            border: 1px solid #ff837a;
                            border-radius: 1px;
                            padding: 24px 32px;
                            margin: 24px auto 0 auto;
                            max-width: 400px;
                            text-align: left;
                            display: none;"
                    >
                        <div style="font-size: 1.1em;
                            font-weight: bold;
                            margin-bottom: 10px;
                            text-align: left;"
                        >
                            Request failed
                        </div>
                        <div style="font-size: 1.1em;">
                            Failed to generate a token.
                            Please try again or contact Kumo
                            for further assistance.
                        </div>
                    </div>

                    <script>
                        // Show only the appropriate div based on the result
                        const search = window.location.search
                        const urlParams = new URLSearchParams(search);
                        const hasToken = urlParams.has('token');
                        if (hasToken) {
                            document
                                .getElementById('success-div')
                                .style.display = 'block';
                        } else {
                            document
                                .getElementById('failure-div')
                                .style.display = 'block';
                        }
                    </script>
                </div>
            </body>
            </html>
            '''
            self.wfile.write(html.encode('utf-8'))

        def log_message(self, format: str, *args: object) -> None:
            return  # Suppress logging

    # Find a free port if needed
    port = redirect_port
    for _ in range(10):
        try:
            with TCPServer(("", port), CallbackHandler) as _:
                break
        except OSError:
            port += 1
    else:
        raise RuntimeError(
            "Could not find a free port for the callback server.")

    # Start the server in a thread
    def serve() -> None:
        with TCPServer(("", port), CallbackHandler) as httpd:
            httpd.timeout = 60
            while token_status['token'] is None:
                httpd.handle_request()

    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()

    # Construct the login URL with callback_url and token_name
    callback_url = f"http://127.0.0.1:{port}/"
    login_url = (api_url +
                 f"?callback_url={urllib.parse.quote(callback_url)}" +
                 f"&token_name={urllib.parse.quote(token_name)}")
    webbrowser.open(login_url)

    # Wait for the token (timeout after 120s)
    start = time.time()
    while token_status['token'] is None and not token_status[
            'failed'] and time.time() - start < 120:
        time.sleep(1)

    if token_status['failed']:
        raise ValueError("Authentication failed.")

    if not isinstance(token_status['token'], str) or not token_status['token']:
        raise TimeoutError("Timed out waiting for authentication.")

    os.environ['KUMO_API_KEY'] = token_status['token']

    logger.info(f"Generated token \"{token_status['token_name']}\" " +
                "and saved to KUMO_API_KEY env variable")

    return token_status['token']
