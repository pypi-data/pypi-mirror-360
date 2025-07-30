from wowool.native.core import LanguageIdentifier, Language, Domain
from wowool.annotation import Concept
from wowool.native.core import PipeLine
from wowool.document.analysis.document import AnalysisDocument
from wowool.string import *  # noqa
from sys import stderr
from sys import argv
import json
from wowool.document.factory import Factory
import logging
from pathlib import Path
import shutil
from wowool.utility import clean_up_empty_keywords
from .argument_parser import ArgumentParser
from wowool.io.console import console
from wowool.native.core.engine import default_engine

engine = default_engine()

logger = logging.getLogger(__name__)


def parse_arguments(*argv):
    parser = ArgumentParser()
    return parser.parse_args(*argv)


def get_language(language):
    return language


def folder(folder_name):
    if isinstance(folder_name, str):
        return "_".join(folder_name.split(" ")).lower()
    elif isinstance(folder_name, list):
        return [folder(name) for name in folder_name]


def _resolve_filename_lists(file_list):
    _multiple_copy = set()
    for file in file_list:
        add_file = True
        for idx, part in enumerate(file.parts):
            if part.startswith("["):
                add_file = False
                sub_sections = json.loads(str(part.replace("'", '"')))
                for section in sub_sections:
                    new_name = [*file.parts]
                    new_name[idx] = section
                    new_filename = Path(*new_name)
                    _multiple_copy.add(new_filename)

        if add_file:
            _multiple_copy.add(file)
    return list(_multiple_copy)


def _needs_resolving(file_list):
    for file in file_list:
        for idx, part in enumerate(file.parts):
            if part.startswith("["):
                return True
    return False


def resolve_filename_lists(file_list):
    new_list = file_list
    while _needs_resolving(new_list):
        new_list = _resolve_filename_lists(new_list)
    return new_list


def get_tool_required(output_format):
    tool_type = []
    if "language" in output_format:
        tool_type.append("lid")
    if "topic" in output_format:
        tool_type.append("topic")
    if "theme" in output_format:
        tool_type.append("theme")
    return tool_type


def main(*argv):
    lid = LanguageIdentifier()
    topic_it = {}
    theme_it = {}
    analyzer = {}
    kwargs = dict(parse_arguments(*argv)._get_kwargs())

    clean_up_empty_keywords(kwargs)
    logger.debug(kwargs)
    captures_to_find = None

    pipeline = PipeLine(kwargs["pipeline"]) if "pipeline" in kwargs else PipeLine()
    if "expression" in kwargs:
        expression = kwargs["expression"]
        if expression.startswith("rule:"):
            expression_domain = Domain(source=kwargs["expression"])
        else:
            expression_domain = Domain(source=f"""rule:{{ {kwargs["expression"]} }}=CAPTURE;""")
        captures_to_find = [uri for uri in expression_domain.concepts if uri != "Sentence"]

        # print("captures_to_find:", captures_to_find)
        pipeline.components.append(expression_domain)

    output_fallback = kwargs["output_fallback"] if "output_fallback" in kwargs else None
    overwrite = kwargs["overwrite"] if "overwrite" in kwargs else False
    tool_types = get_tool_required(kwargs["output"])

    #

    root_folder = Path(kwargs["file"])
    nrof_parts = len(root_folder.parts)

    dry_run = True if "dry_run" in kwargs else False
    file_action = kwargs["action"] if "action" in kwargs else "copy"
    mime_type = kwargs["mime_type"] if "mime_type" in kwargs else ""
    for counter, ip in enumerate(Factory.glob(root_folder, kwargs["pattern"], mime_type=mime_type)):
        file_path = Path(ip.id)
        doc = ip
        topic = None
        capture = None
        expression = None
        language = None
        if pipeline:
            language = pipeline.language
            doc = pipeline(doc)
            if captures_to_find:
                capture = [concept for concept in Concept.iter(doc, lambda concept: concept.uri in captures_to_find)]

        # print(doc)
        if capture:
            capture = capture[0] if capture else None
            expression = capture

        print("--->>", tool_types, language)
        for sort_type in tool_types:
            if sort_type == "lid":
                if isinstance(doc, AnalysisDocument) and doc.analysis is None:
                    input_text = ip.data

                    language = lid(input_text).language

                    if isinstance(language, str):
                        language = language.split("@")[0]

                    if isinstance(language, str) and language not in analyzer:
                        try:
                            analyzer[language] = Language(language)
                        except Exception:
                            analyzer[language] = Language("generic")
                    doc = analyzer[language](input_text)
            elif sort_type == "topic":
                if topic is None and isinstance(language, str) and language != "not_set":
                    try:
                        from wowool.topic_identifier import TopicIdentifier

                        topic = ["none"]
                        if language not in topic_it:
                            topic_it[language] = TopicIdentifier(language)
                        topic_it[language].add(doc)
                        doc = topic_it[language](doc)
                        topics = doc.topics
                        if topics:
                            topic = [topic.name for topic in topics]
                        else:
                            topic = ["none"]
                        print(f"topic: {topic}")
                    except ImportError as ex:
                        print(
                            f"You need to install the wowool_topic_identifier package.\nException {ex}",
                            file=stderr,
                        )

            elif sort_type == "theme":
                if isinstance(language, str) and language != "not_set":
                    try:
                        from wowool.semantic_themes import Themes

                        if language not in theme_it:
                            analyzer[language] = Language(language)
                            theme_it[language] = Themes()
                        if isinstance(doc, AnalysisDocument) and not doc.analysis:
                            doc = analyzer[language](ip)
                        doc = theme_it[language](doc)
                        themes = doc.themes
                        if themes:
                            theme = [k.name for k in themes if k.relevancy > 20]
                        else:
                            theme = []
                        if not len(theme):
                            theme = ["none"]

                    except ImportError as ex:
                        raise ImportError(
                            f"You need to install the wowool_semantic_themes package.\nException {ex}",
                        )

        fn_parts = list(file_path.parts)
        filename = Path(*fn_parts[nrof_parts:])  # noqa
        full_filename = ip.id
        fvalue = kwargs["output"]
        input_filename = Path(full_filename)
        ifilename = input_filename.resolve()
        suffix = ifilename.suffix  # noqa
        try:
            filename_value = eval('f"' + fvalue + '"')
            logger.debug(f"{fvalue} -> {filename_value}")
            if "None" in filename_value:
                raise RuntimeError("expression has not been resolved found 'None' in formatted result.")
            resolved_filename = Path(filename_value)
            multiple_copy = resolve_filename_lists([resolved_filename])
        except Exception as exception:
            if output_fallback:
                console.print(f"<warning>Warning:</warning> Using fall_back formatting: {ip.id} : {exception}' ")
                try:
                    filename_value = eval('f"' + output_fallback + '"')
                    multiple_copy = [Path(filename_value)]
                except Exception as exception:
                    console.print(f"<error>Error:</error> Skipping: {ip.id} , Could not resolve output_fallback '{exception}' ")
                    continue
            else:
                import sys

                console.print(
                    f"<warning>Warning:</warning> Skipping: {ip.id} , Note: use the output_fallback option. This was the exception: '{exception}' ",  # noqa
                    file=sys.stderr,
                )
                # traceback.print_exc(file=sys.stdout)
                continue

        console.print(f"[green]copy[/green]: {ip.id}")
        for target_fn in multiple_copy:
            full_target_fn = target_fn.expanduser()
            console.print(f"  [green]to[/green]: [bold]{full_target_fn}[/bold]")
            # print(f"copy: {ip.id} --> {full_target_fn}")
            if not dry_run:
                if not full_target_fn.exists() or overwrite:
                    full_target_fn.parent.mkdir(parents=True, exist_ok=True)
                    if file_action == "copy":
                        shutil.copy(ip.id, full_target_fn)
                    elif file_action == "text":
                        with open(full_target_fn, "w") as fh:
                            fh.write(ip.data)
                    elif file_action == "link":
                        full_target_fn.symlink_to(ifilename)
                    else:
                        assert False, f"action '{file_action}' is not supported."
                else:
                    print(f"Warning: file already exists {full_target_fn}")


if __name__ == "__main__":
    main(argv[1:])
