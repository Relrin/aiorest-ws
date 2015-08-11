import pytest

from aiorest_ws.command_line import CommandLine


def clear_command_line(cmd):
    default_command_list = ['-h', '--help']
    deleted_commands = [key for key in cmd.options._option_string_actions
                        if key not in default_command_list]
    for key in deleted_commands:
        cmd.options._option_string_actions.pop(key)


@pytest.fixture(scope="function", autouse=True)
def default_command_line():
    cmd = CommandLine()
    clear_command_line(cmd)
    cmd.define('-ip', default='127.0.0.1', help='used ip', type=str)
    cmd.define('-port', default=8080, help='listened port', type=int)
    return cmd
