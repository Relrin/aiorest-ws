import pytest

from aiorest_ws.command_line import define


@pytest.fixture(scope="module", autouse=True)
def default_options():
    define('-ip', default='127.0.0.1', help='used ip for server', type=str)
    define('-port', default=8080, help='listened on server', type=int)
