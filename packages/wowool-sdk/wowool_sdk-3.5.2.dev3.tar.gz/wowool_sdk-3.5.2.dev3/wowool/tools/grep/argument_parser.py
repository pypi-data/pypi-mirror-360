from wowool.io.console.argument_parser import ArgumentParser as ArgumentParserBase

choices = [
    "plain",
    "github",
    "grid",
    "fancy_grid",
    "pipe",
    "presto",
    "pretty",
    "rst",
    "html",
]


class ArgumentParser(ArgumentParserBase):
    def __init__(self):
        """
        Wowool Semantic Grep
        """
        super(ArgumentParserBase, self).__init__(prog="wow.grep", description=ArgumentParser.__call__.__doc__)
        self.add_argument("-f", "--file", help="folder or file")
        self.add_argument("-i", "--text", help="The input text to process")
        self.add_argument("-p", "--pipeline", help="pipeline description", required=True)
        self.add_argument("-e", "--expression", help="pipeline description", required=True)
        self.add_argument("--lemma", help="will return the grep result using the lemma.", default=False, action="store_true")
        self.add_argument(
            "-t",
            "--table-format",
            help=f"table format see python tabulate module for the different formats or set a environment variable `WOWOOL_TABLE_FORMAT` choices={choices}",
        )
