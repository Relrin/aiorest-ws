"""
    Custom functions, which simplify development with command line

    Example:

    from aiorest_ws.server import run_server
    from aiorest_ws.command_line import define, parse_command_line

    define('-ip', default='127.0.0.1', help='used ip for server', type=str)
    define('-port', default=8080, help='listened on server', type=int)
    args = parse_command_line()

    run_server(args.ip, args.port)
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
