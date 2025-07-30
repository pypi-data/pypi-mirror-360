from wowool.io.console.argument_parser import ArgumentParser as ArgumentParserBase


class ArgumentParser(ArgumentParserBase):

    def __init__(self):
        """
        Wowool Language Identifier
        """
        super(ArgumentParserBase, self).__init__(prog="lid", description=ArgumentParser.__call__.__doc__)
        self.add_argument("-f", "--file", help="folder or file")
        self.add_argument("-i", "--text", help="The input text to process")
        self.add_argument(
            "--sections", help="return the language sections in a multi language document.", default=False, action="store_true"
        )
        self.add_argument("--section_data", help="The text of the section.", default=False, action="store_true")
