from fixtures.command_line import default_command_line as cmd  # noqa


def test_define(cmd):  # noqa
    assert len(cmd.options._option_string_actions.keys()) == 4

    cmd.define('-arg1', default='some value', help='arg #1', type=str)
    cmd.define('-arg2', default=8888, help='arg #2', type=int)
    assert len(cmd.options._option_string_actions.keys()) == 6

    # try to add one more time the same argument into parser
    cmd.define('-arg2', default=8888, help='arg #2', type=int)
    assert len(cmd.options._option_string_actions.keys()) == 6

    cmd.define('--opt1', help='arg #1', type=int)
    cmd.define('--opt2', help='arg #2', type=str)
    assert len(cmd.options._option_string_actions.keys()) == 8
