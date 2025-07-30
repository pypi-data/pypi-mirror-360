#!/usr/bin/python3
import sys
from .argument_parser import ArgumentParser
from wowool.utility.default_arguments import make_document_collection

import logging
from wowool.apps.language_identifier.app_id import APP_ID
from wowool.apps.language_identifier import LanguageIdentifier
from wowool.io.console import console

logger = logging.getLogger(__name__)


def parse_arguments(*argv):
    """
    This is the Entity Graph
    """
    parser = ArgumentParser()
    return parser.parse_args(*argv)


def main(*argv):
    kwargs = dict(parse_arguments(*argv)._get_kwargs())
    logger.debug(kwargs)
    collection = make_document_collection(**kwargs)

    app_arguments = {**kwargs}
    del app_arguments["file"]
    del app_arguments["text"]

    lid = LanguageIdentifier(**app_arguments)
    for ip in collection:
        doc = lid(ip)
        console.print_json(doc.results(APP_ID))
    # collection.add_text()


if __name__ == "__main__":
    main(sys.argv[1:])
