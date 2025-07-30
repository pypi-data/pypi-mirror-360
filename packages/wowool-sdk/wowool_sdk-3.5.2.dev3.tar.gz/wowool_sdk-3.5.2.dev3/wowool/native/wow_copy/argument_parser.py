from wowool.io.console.argument_parser import ArgumentParser as ArgumentParserBase
import argparse


class ArgumentParser(ArgumentParserBase):

    def __init__(self):
        """EyeOnText Corpus Copy Tool, This tool rearranges a corpus folder using language identification, topics, semantic-themes and wowool rules.
        The output argument is formatted at runtime. --output ~/tmp/{language}/{filename} will sort all your files according to the language
        of the document.

        ex: using -n (dry_run)

        .. code-block::

            wow.cp -f ~/corpus/multi_lingual --output ~/tmp/{language}/{filename} -n

        Variables:

        * expression or capture (Concept): The Concept that has been captured with the -e or --expression argument.
        * language (str): language of the document
        * topic (list): topics found in the document.
        * theme (list): themes found in the document.
        * counter (int): file counter.
        * input_filename,ifilename (Path): Path object. which means you can use ifilename.name,ifilename.stem,ifilename.suffix.
        * suffix (str): filename extension.

        ex: using the first theme name

        .. code-block::

            wow.cp -f ~/corpus/multi_lingual --output ~/tmp/{language}/{theme[0]}/{filename} -n

        ex: This will copy the file in multiple locations, the first 2 theme's

        .. code-block::

            wow.cp -f ~/corpus/multi_lingual --output ~/tmp/{language}/{theme[:1]}/{filename} -n

        Functions:

        * folder(str): to lower casing and convert ' ' to '_'
        * camelize(str): converts 'Streaming service' -> 'StreamingService'
        * normalize(str): remove accents
        * initial_caps(str): converts ALlCaPs -> Allcaps

        ex: using wowool to sort your files using the gender of the person that has been captured.

        .. code-block::

            wow.cp -f ~/corpus/multi_lingual  -e 'Person' -p "english,entity" --output "~/tmp/{folder(expression.Person.gender)}/{filename}" -x ~/tmp/corpus_test/not_found/notfound_{counter}{suffix}

        .. note::

            -e,--expression : is the wowoolian expression, which is also used to create a variable that can be used in the output variable. In this case we are sorting by gender.
            -p,--pipeline : pipe line to run your expression
            -x,--output_fallback : In the case we cannot resolve the output filename, we will fallback on this format. If that fails we will skip the file.

            use the --action to either 'link' or 'text' to just extract the text of a file. This mean that if your input is html the text will be extracted.

        """
        super(ArgumentParserBase, self).__init__(
            prog="wow.cp", description=ArgumentParser.__init__.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self.add_argument("-f", "--file", help="folder or file", required=True)
        self.add_argument("--pattern", help="glob the given pattern, default '**/*", default="**/*")
        self.add_argument("-o", "--output", help="folder or file")
        self.add_argument("-x", "--output_fallback", help="exception if there was a exception in generating the output name.")
        self.add_argument("-l", "--language", help="language", default="auto")
        self.add_argument("-p", "--pipeline", help="pipeline")
        self.add_argument("-e", "--expression", help="expression to search")
        self.add_argument("--to_text", help="cleanup the documents", default=False, action="store_true")
        self.add_argument("-n", "--dry_run", help="dry run", default=False, action="store_true")
        self.add_argument("--action", help="what to do with the input file,[copy,link,text]", default="copy")
        self.add_argument("--overwrite", help="overwrite", default=False, action="store_true")
        self.add_argument("-m", "--mime_type", help="force the mime type: ex. html, pdf, text", default="")
