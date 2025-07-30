import pytest

from dasl_client import Client

from .constants import *


@pytest.fixture(scope="session")
def api_client():
    client = Client.new_workspace(
        admin_email="test@antimatter.io",
        app_client_id=app_client_id,
        service_principal_id=databricks_client_id,
        service_principal_secret=databricks_client_secret,
        workspace_url=databricks_host,
        dasl_host=dasl_host,
    )
    yield client
