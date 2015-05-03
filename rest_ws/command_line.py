from argparse import ArgumentParser

options = ArgumentParser()


def define(name, default=None, help=None, type=None, *args, **kwargs):
    """
        Defines an option in the global namespace
    """
    return options.add_argument(name, default=default, help=help, type=type,
                                *args, **kwargs)


def parse_command_line(args=None):
    """
        Parse options from the command line
    """
    return options.parse_args()
