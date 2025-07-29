import logging
from dataclasses import asdict, dataclass, field
from threading import RLock
from typing import Literal, Optional
from urllib.parse import urlparse

from catalystwan.abc import SessionInterface
from catalystwan.core.abstractions import AuthProtocol
from catalystwan.core.exceptions import CatalystwanException
from catalystwan.core.response import auth_response_debug
from requests import HTTPError, PreparedRequest, post
from requests.auth import AuthBase
from requests.exceptions import JSONDecodeError

LoginMode = Literal["machine", "user", "session"]


@dataclass
class ApiGwLogin:
    client_id: str
    client_secret: str
    org_name: str
    mode: Optional[LoginMode] = None
    username: Optional[str] = None
    session: Optional[str] = None
    tenant_user: Optional[bool] = None
    token_duration: int = field(default=10)


class ApiGwAuth(AuthBase, AuthProtocol):
    """Attaches ApiGateway Authentication to the given Requests object.

    1. Get a bearer token by sending a POST request to the /apigw/login endpoint.
    2. Use the token in the Authorization header for subsequent requests.
    """

    def __init__(
        self,
        login: ApiGwLogin,
        logger: Optional[logging.Logger] = None,
        verify: bool = False,
    ):
        self.login = login
        self.token = ""
        self.logger = logger or logging.getLogger(__name__)
        self.verify = verify
        self.session_count: int = 0
        self.lock: RLock = RLock()

    def __str__(self) -> str:
        return f"ApiGatewayAuth(mode={self.login.mode})"

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        with self.lock:
            self.handle_auth(request)
            self.build_digest_header(request)
        return request

    def handle_auth(self, request: PreparedRequest) -> None:
        if self.token == "":
            self.authenticate(request)

    def authenticate(self, request: PreparedRequest):
        assert request.url is not None
        url = urlparse(request.url)
        base_url = f"{url.scheme}://{url.netloc}"  # noqa: E231
        self.token = self.get_token(base_url, self.login, self.logger, self.verify)

    def build_digest_header(self, request: PreparedRequest) -> None:
        header = {
            "sdwan-org": self.login.org_name,
            "Authorization": f"Bearer {self.token}",
        }
        request.headers.update(header)

    @staticmethod
    def get_token(
        base_url: str,
        apigw_login: ApiGwLogin,
        logger: Optional[logging.Logger] = None,
        verify: bool = False,
    ) -> str:
        try:
            response = post(
                url=f"{base_url}/apigw/login",
                verify=verify,
                json=asdict(
                    apigw_login,
                    dict_factory=lambda d: {k: v for (k, v) in d if v is not None},
                ),
                timeout=10,
            )
            if logger is not None:
                logger.debug(auth_response_debug(response))
            response.raise_for_status()
            token = response.json()["token"]
        except JSONDecodeError:
            raise CatalystwanException(
                f"Incorrect response type from ApiGateway login request, ({response.text})"
            )
        except HTTPError as ex:
            raise CatalystwanException(
                f"Problem with connection to ApiGateway login endpoint, ({ex})"
            )
        except KeyError as ex:
            raise CatalystwanException(f"Not found token in login response from ApiGateway, ({ex})")
        else:
            if not token or not isinstance(token, str):
                raise CatalystwanException("Failed to get bearer token")
        return token

    def logout(self, client: SessionInterface) -> None:
        return None

    def _clear(self) -> None:
        with self.lock:
            self.token = ""

    def increase_session_count(self) -> None:
        with self.lock:
            self.session_count += 1

    def decrease_session_count(self) -> None:
        with self.lock:
            self.session_count -= 1

    def clear(self, last_request: Optional[PreparedRequest]) -> None:
        with self.lock:
            # extract previously used jsessionid
            if last_request is None:
                token = None
            else:
                token = last_request.headers.get("Authorization")

            if self.token == "" or f"Bearer {self.token}" == token:
                # used auth was up-to-date, clear state
                return self._clear()
            else:
                # used auth was out-of-date, repeat the request with a new one
                return
