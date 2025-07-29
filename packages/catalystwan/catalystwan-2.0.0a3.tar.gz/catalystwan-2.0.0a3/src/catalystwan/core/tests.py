import os
import pytest

from catalystwan.core.session import create_manager_session
from catalystwan.core.request_adapter import RequestAdapter

@pytest.fixture(scope="package")
def catalystwan_requests():
    url = os.environ["SDWAN_URL"]
    port = int(os.environ["SDWAN_PORT"])
    username = os.environ["SDWAN_USERNAME"]
    password = os.environ["SDWAN_PASSWORD"]
    print(f"Connecting to {url}:{port}...")
    with create_manager_session(url, username, password, port) as session:
        yield RequestAdapter(session=session)
