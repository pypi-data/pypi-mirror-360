from wowool.io.console.argument_parser import ArgumentParser as ArgumentParserBase


class ArgumentParser(ArgumentParserBase):
    def __init__(self):
        """
        Wowool Console Argument Parser
        """
        super(ArgumentParserBase, self).__init__(prog="wow", description=ArgumentParser.__call__.__doc__)
        self.add_argument("-f", "--file", help="folder or file")
        self.add_argument("-p", "--pipeline", help="pipeline description", required=True)
        self.add_argument("-i", "--text", help="The input text to process", nargs="*")
        self.add_argument("--lxware", help="location of lxware")
        self.add_argument("-a", "--annotations", help="filter the annotations")
        self.add_argument(
            "-t",
            "--tool",
            help="name of the tool raw, json, concepts, grep, stagger, text, apps, info, none",
            default="raw",
            choices=[
                "raw",
                "json",
                "concepts",
                "grep",
                "stagger",
                "text",
                "apps",
                "info",
                "input_text",
                "canonical",
                "none",
            ],
        )
        self.add_argument("-v", "--verbose", help="debug levels, trace,debug,...", default="error")
        self.add_argument("--utf8", help="display the utf8 offsets", default=False, action="store_true")
        self.add_argument(
            "--dbg",
            help="Switches on the extensive debugger options. Current options: print_annotations, nofilter, insertion, rule_trigger, matcher, hmm, rule_info, streams, stream_lookup, overlap",
        )
        self.add_argument("-e", "--expression", help="wowoolian expression, will force the tool grep.")
        self.add_argument("--grep-lemma", help="will return the grep result using the lemma.", default=False, action="store_true")
        self.add_argument("--encoding", help="set the encoding for reading the input file", default="utf-8")
        self.add_argument("--sentyziser", help="""set the number of lines breaks (\n) in one sentence.""")
        self.add_argument("--allow-dev-version", help="use the lingware dev version if available", default=True, action="store_false")
        self.add_argument("-j", "--nrof_threads", help="number of threads to process.", default=1, type=int)
        self.add_argument("--show-metadata", help="show metadata", default=False, action="store_true")
