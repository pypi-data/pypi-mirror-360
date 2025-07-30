from wowool.tools.grep.argument_parser import ArgumentParser


def parse_arguments(*argv):
    """
    This is the Entity Mapper
    """
    parser = ArgumentParser()
    # add_argument_parser(parser)
    return parser.parse_args(*argv)


def driver(kwargs):

    import os

    argv = ["--tool", "grep"]
    if kwargs["file"]:
        argv.append("-f")
        argv.append(kwargs["file"])

    if kwargs["text"]:
        argv.append("-i")
        argv.append(kwargs["text"])

    argv.append("-e")
    argv.append(kwargs["expression"])

    argv.append("-p")
    argv.append(kwargs["pipeline"])

    if kwargs["table_format"] is not None:
        os.environ["WOWOOL_TABLE_FORMAT"] = kwargs["table_format"]

    if kwargs["lemma"]:
        argv.append("--grep-lemma")

    from wowool.native.wow.__main__ import main as wow

    wow(argv)


def main(*argv):
    kwargs = dict(parse_arguments(*argv)._get_kwargs())
    driver(kwargs)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
