"""
    Custom functions, which simplify development with command line
"""
from argparse import ArgumentParser


options = ArgumentParser()
__all__ = ('define', 'parse_command_line')


def define(name, default=None, help=None, type=None):
    """
        Defines an option in the global namespace

        Args:
            name - used argument/option in command line (e.c. -f or --foo)
            default - used value for argument or option if not specified
            help - full description for option, which used when invoked
                   program with -h flag
            type - prefered type for option
    """
    return options.add_argument(name, default=default, help=help, type=type)


def parse_command_line():
    """
        Parse options from the command line
    """
    return options.parse_args()
