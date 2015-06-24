import pytest

from aiorest_ws.command_line import CommandLine


@pytest.fixture(scope="function")
def default_command_line():
    cmd = CommandLine()
    cmd.define('-ip', default='127.0.0.1', help='used ip', type=str)
    cmd.define('-port', default=8080, help='listened port', type=int)
    return cmd
