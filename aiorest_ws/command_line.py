# -*- coding: utf-8 -*-
"""
    Custom functions and classes, which help working with the command line.
"""
from argparse import ArgumentParser

__all__ = ('CommandLine', )


class CommandLine(object):
    """Wrapper over ArgumentParser class for working with command line."""
    options = ArgumentParser()

    def define(self, name, default=None, help=None, type=None):
        """Defines an option in the global namespace.

        Note: already defined argument or option has been ignored and not
              appended again!

        :param name: used argument/option in command line (e.c. -f or --foo).
        :param default: used value for argument or option if not specified.
        :param help: full description for option, which used when invoked
                     program with -h flag.
        :param type: preferred type for option.
        """
        if name not in self.options._option_string_actions.keys():
            self.options.add_argument(name, default=default, help=help,
                                      type=type)

    def parse_command_line(self):
        """Parse options from the command line."""
        return self.options.parse_args()
