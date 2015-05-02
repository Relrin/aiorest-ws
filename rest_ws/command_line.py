from argparse import ArgumentParser

options = ArgumentParser()


def define(name, default=None, help=None, type=None, required=True):
    """
        Defines an option in the global namespace
    """
    return options.add_argument(name, default=default, help=help, type=type,
                                required=required)


def parse_command_line():
    """
        Parse options from the command line
    """
    return options.parse_args()
