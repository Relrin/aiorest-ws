# -*- coding: utf-8 -*-
"""
    Custom functions, which simplify development with command line

    Example:

    from server import run_server
    from command_line import CommandLine

    cmd = CommandLine()
    cmd.define('-ip', default='127.0.0.1', help='used ip', type=str)
    cmd.define('-port', default=8080, help='listened port', type=int)
    args = cmd.parse_command_line()

    run_server(ip=args.ip, port=args.port)
"""
from argparse import ArgumentParser

__all__ = ('CommandLine', )


class CommandLine(object):
    options = ArgumentParser()

    def define(self, name, default=None, help=None, type=None):
        """
            Defines an option in the global namespace

            Args:
                name - used argument/option in command line (e.c. -f or --foo)
                default - used value for argument or option if not specified
                help - full description for option, which used when invoked
                       program with -h flag
                type - preferred type for option

            Note: argument or option already defined has been ignored!
        """
        if name not in self.options._option_string_actions.keys():
            self.options.add_argument(name, default=default, help=help,
                                      type=type)

    def parse_command_line(self):
        """
            Parse options from the command line
        """
        return self.options.parse_args()
