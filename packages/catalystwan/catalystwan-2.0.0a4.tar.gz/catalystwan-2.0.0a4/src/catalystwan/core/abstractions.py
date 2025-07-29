from typing import Optional, Protocol, TypeVar

from catalystwan.abc import SessionInterface, SessionType
from requests import PreparedRequest  # type: ignore

T = TypeVar("T")


ProviderView = SessionType.PROVIDER
TenantView = SessionType.TENANT
ProviderAsTenantView = SessionType.PROVIDER_AS_TENANT
SingleTenantView = SessionType.SINGLE_TENANT


class AuthProtocol(Protocol):
    """
    Additional interface for Auth to handle login/logout for multiple auth types by common ManagerSession
    """

    def logout(self, client: SessionInterface) -> None: ...

    def clear(self, last_request: Optional[PreparedRequest]) -> None: ...

    def increase_session_count(self) -> None: ...

    def decrease_session_count(self) -> None: ...
