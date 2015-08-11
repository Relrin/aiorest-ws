# -*- coding: utf-8 -*-
from fixtures.command_line import default_command_line as cmd  # noqa


def test_define(cmd):  # noqa
    assert len(cmd.options._option_string_actions.keys()) == 4


def test_define_add_args(cmd):  # noqa
    cmd.define('-arg1', default='some value', help='arg #1', type=str)
    cmd.define('-arg2', default=8888, help='arg #2', type=int)
    assert len(cmd.options._option_string_actions.keys()) == 6


def test_define_ignore_duplicates(cmd):  # noqa
    cmd.define('-arg1', default='some value', help='arg #1', type=str)
    cmd.define('-arg2', default=8888, help='arg #2', type=int)
    assert len(cmd.options._option_string_actions.keys()) == 6

    # try to add one more time the same argument into parser
    cmd.define('-arg2', default=8888, help='arg #2', type=int)
    assert len(cmd.options._option_string_actions.keys()) == 6


def test_define_options(cmd):  # noqa
    cmd.define('--opt1', help='arg #1', type=int)
    cmd.define('--opt2', help='arg #2', type=str)
    assert len(cmd.options._option_string_actions.keys()) == 6
