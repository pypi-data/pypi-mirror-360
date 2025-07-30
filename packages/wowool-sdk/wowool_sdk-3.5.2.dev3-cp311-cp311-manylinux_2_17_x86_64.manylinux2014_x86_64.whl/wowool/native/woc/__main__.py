import sys
from wowool.io.console import console
from wowool.native.woc.command import CommandFactory
from wowool.native.woc.argument_parser import ArgumentParser
from functools import wraps
from sys import stderr
from wowool.error import Error as CommonError


def parse_arguments(*argv):
    """
    Parses the command line arguments.
    """
    from .argument_parser import ArgumentParser

    parser = ArgumentParser()
    kwargs = parser.parse_args(*argv)
    return kwargs


def handle_errors(prog: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except (Exception, CommonError) as error:
                console.print(f"<prog>{prog}</prog>: <error>error</error>: {error}", file=stderr)
                raise error

        return wrapper

    return decorator


class CLI:
    def __init__(self, argument_parser, command_factory):
        self._parse_arguments = argument_parser
        self._create_command = command_factory

    def __call__(self, *argv):
        @handle_errors(self._parse_arguments.prog)
        def run(*argv):
            kwargs = self._parse_arguments(argv)
            command = self._create_command(**kwargs)
            exit(command(**kwargs))

        run(*argv)


def main(*argv):
    argv = argv or sys.argv[1:]
    cli = CLI(ArgumentParser(), CommandFactory())
    cli(*argv)


if "__main__" == __name__:
    main()
