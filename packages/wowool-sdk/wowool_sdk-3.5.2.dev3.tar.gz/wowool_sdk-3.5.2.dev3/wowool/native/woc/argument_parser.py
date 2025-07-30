from wowool.io.console.argument_parser import ArgumentParser as ArgumentParserBase


class ArgumentParser(ArgumentParserBase):

    def __init__(self):
        """
        Wowool Compiler Driver
        """
        super(ArgumentParserBase, self).__init__(prog="woc", description=ArgumentParser.__call__.__doc__)
        self.add_argument("--version", help="Version information", default=False, action="store_true")
        self.add_argument("-f", "--force", help="Force a full rebuild", action="store_true")
        self.add_argument("-l", "--language", help="Language to be used to perform checks on stems")
        self.add_argument("--lxware", help="location of the language files")
        self.add_argument("-s", "--strict", help="compile in strict mode.", action="store_true")
        self.add_argument("-t", "--unit-test", help="Perform the unit-test in the wow files.", action="store_true")
        self.add_argument(
            "--disable-plugin-calls",
            help="Disable call to the plugin module",
            action="store_true",
        )
        self.add_argument("-o", "--output_file", help="Name of the output filename (.dom)")
        self.add_argument("-v", "--verbose", help="Verbosity level: trace,debug,info,warning,error,fatal", default="info")
        self.add_argument("-j", "--threads", help="Number of threads to use.", type=int, default=4)
        self.add_argument("input_files", type=str, nargs="*", help="Sources file to compile (.wow)")
        self.add_argument("-p", "--project", help="Use the given .wopr project file")
        self.add_argument("-c", "--create", help="Create a project file", metavar="PROJECT")
        self.add_argument(
            "--ignore-codes",
            help="disable/enable warnings, see help for all the possible values or use the hex values in the messages itself.",
            type=lambda x: int(x, 0),
        )
