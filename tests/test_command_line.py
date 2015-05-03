from rest_ws.command_line import options, define, parse_command_line
from fixtures.cmd import default_options


def test_define(default_options):
    assert len(options._option_string_actions.keys()) == 4


def test_define_with_user_arguments(default_options):
    define('-arg1', default='127.0.0.1', help='used ip for server', type=str)
    define('-arg2', default=8080, help='listened on server', type=int)
    assert len(options._option_string_actions.keys()) == 6


def test_define_with_user_arguments_and_options(default_options):
    define('-arg1', default='127.0.0.1', help='used ip for server', type=str)
    define('-arg2', default=8080, help='listened on server', type=int)
    define('--opt1', help='arg #1', type=int)
    define('--opt2', help='arg #2', type=str)
    assert len(options._option_string_actions.keys()) == 8


def test_parse_command_line(default_options):
    res = parse_command_line()
    assert res.ip == '127.0.0.1'
    assert res.port == 8080
