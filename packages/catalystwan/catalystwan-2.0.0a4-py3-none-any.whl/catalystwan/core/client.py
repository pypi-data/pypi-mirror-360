from __future__ import annotations

import logging
from contextlib import contextmanager
from copy import copy
from inspect import isclass
from typing import TYPE_CHECKING, Generator, Optional, Type, TypeVar, Union, cast, overload

from catalystwan.core.apigw_auth import ApiGwAuth
from catalystwan.core.exceptions import CatalystwanException
from catalystwan.core.loader import load_client
from catalystwan.core.request_adapter import RequestAdapter
from catalystwan.core.request_limiter import RequestLimiter
from catalystwan.core.session import ManagerSession, create_base_url, create_manager_session
from catalystwan.core.vmanage_auth import vManageAuth
from typing_extensions import TypeGuard

if TYPE_CHECKING:
    from catalystwan.core.loader import ApiClient


class CatalystwanNotAClientException(CatalystwanException): ...


Client = TypeVar("Client")


# TODO: Better TypeGuards - it may be hard since we want to avoid direct imports
# For now, it's more of a hack for typing purposes
def _is_client_instance(obj: object) -> TypeGuard[ApiClient]:
    return not isclass(obj) and hasattr(obj, "api_version")


def _is_client_class(obj: object) -> TypeGuard[Type[ApiClient]]:
    return isclass(obj) and hasattr(obj, "api_version")


@overload
@contextmanager
def create_client_from_auth(
    url: str,
    auth: Union[vManageAuth, ApiGwAuth],
    port: Optional[int] = None,
    subdomain: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    request_limiter: Optional[RequestLimiter] = None,
) -> Generator[ApiClient, None, None]: ...


@overload
@contextmanager
def create_client_from_auth(
    url: str,
    auth: Union[vManageAuth, ApiGwAuth],
    port: Optional[int] = None,
    subdomain: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    request_limiter: Optional[RequestLimiter] = None,
    *,
    api_client_class: Type[Client],
) -> Generator[Client, None, None]: ...


@contextmanager
def create_client_from_auth(
    url: str,
    auth: Union[vManageAuth, ApiGwAuth],
    port: Optional[int] = None,
    subdomain: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    request_limiter: Optional[RequestLimiter] = None,
    api_client_class: Optional[Type[Client]] = None,
) -> Generator[Union[ApiClient, Client], None, None]:
    if logger is None:
        logger = logging.getLogger(__name__)
    session = ManagerSession(
        base_url=create_base_url(url, port),
        auth=auth,
        subdomain=subdomain,
        logger=logger,
        request_limiter=request_limiter,
    )
    with session.login():
        version = session.api_version.base_version
        if api_client_class is None:
            logger.debug(f"Choosing client for version {version}...")
            client = load_client(session.api_version.base_version)
            logger.debug(f"Client for version {version} loaded")
            yield client(RequestAdapter(session=session, logger=logger))
        elif _is_client_class(api_client_class):
            logger.debug(f"Creating instance for client class {api_client_class}")
            yield api_client_class(RequestAdapter(session=session, logger=logger))
        else:
            raise CatalystwanNotAClientException(f"{api_client_class} is not a client class")


@overload
@contextmanager
def create_client(
    url: str,
    username: str,
    password: str,
    port: Optional[int] = None,
    subdomain: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> Generator[ApiClient, None, None]: ...


@overload
@contextmanager
def create_client(
    url: str,
    username: str,
    password: str,
    port: Optional[int] = None,
    subdomain: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    *,
    api_client_class: Type[Client],
) -> Generator[Client, None, None]: ...


@contextmanager
def create_client(
    url: str,
    username: str,
    password: str,
    port: Optional[int] = None,
    subdomain: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    api_client_class: Optional[Type[Client]] = None,
) -> Generator[Union[ApiClient, Client], None, None]:
    if logger is None:
        logger = logging.getLogger(__name__)
    with create_manager_session(url, username, password, port, subdomain, logger) as session:
        if api_client_class is None:
            version = session.api_version.base_version
            logger.debug(f"Choosing client for version {version}...")
            client = load_client(session.api_version.base_version)
            logger.debug(f"Client for version {version} loaded")
            yield client(RequestAdapter(session=session, logger=logger))
        elif _is_client_class(api_client_class):
            logger.debug(f"Creating instance for client class {api_client_class}")
            yield api_client_class(RequestAdapter(session=session, logger=logger))
        else:
            raise CatalystwanNotAClientException(f"{api_client_class} is not a client class")


@contextmanager
def copy_client(client: Client) -> Generator[Client, None, None]:
    if _is_client_instance(client):
        request_adapter = copy(client._request_adapter)
        session = request_adapter.session
        with session.login():
            new_client = load_client(session.api_version.base_version)(request_adapter)
            assert new_client.api_version == client.api_version
            yield cast(Client, new_client)
    else:
        raise CatalystwanNotAClientException(f"{client} is not a client instance")
