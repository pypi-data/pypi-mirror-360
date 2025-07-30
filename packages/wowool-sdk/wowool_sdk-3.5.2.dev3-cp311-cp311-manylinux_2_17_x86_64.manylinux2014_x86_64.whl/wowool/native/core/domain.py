import json
from pathlib import Path
from functools import wraps
import wowool.package.lib.wowool_sdk as cpp
from wowool.document.analysis.document import AnalysisDocument
from wowool.document.analysis.text_analysis import APP_ID
from wowool.error import Error
from typing import Union
from wowool.native.core.engine import Engine, Component
import logging
from wowool.native.core.app_id import APP_ID_WOWOOL_DOMAIN
from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
)
from wowool.diagnostic import Diagnostics, Diagnostic, DiagnosticType
from wowool.native.core.app_id import APP_ID_WOWOOL_ANALYSIS
import warnings

DOM_INFO = "dom_info"
DOM = "dom"
DI_CONCEPTS = "concepts"
DI_DEPENDENCIES = "dependencies"
DOMAIN_OBJECT_NOT_INITIALIZED = "cpp engine has not been initialized"

logger = logging.getLogger(__name__)


def get_concepts(domain: Union[str, Path]):
    """
    Return the concepts exported in the given domains

    :param: domains: a comma separated list of concepts used in the given domain.
    :returns: list of the concepts in the given domain.

    :raises: Error
    """
    assert Path(domain).exists, "Domain file not found"
    return json.loads(cpp.get_domain_info(str(domain)))


def check_cpp_object(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self._cpp:
            self._load()
        assert self._cpp is not None
        return f(self, *args, **kwargs)

    return wrapper


class Domain(Component):
    """
    A Domain object can be loaded from a .dom file that has been built with the compiler object.

    .. literalinclude:: english_domain_init_2.py
        :caption: english_domain_init_2.py

    A Domain object can also be used to apply rules or lexicons to an existing document object.

    .. literalinclude:: english_domain_init.py
        :caption: english_domain_init.py

    This results in the following output:

    .. literalinclude:: english_domain_init_output.txt
    """

    ID = APP_ID_WOWOOL_DOMAIN

    def _load(self, domain_descriptor, annotations=None, domain_name=None, cache=True):
        """
        Load a domain given a domain_descriptor or file
        """
        options = {}
        if annotations:
            if isinstance(annotations, list):
                options["annotation_filter"] = ",".join(annotations)
            else:
                options["annotation_filter"] = annotations
        if not cache:
            options["cache"] = False
        if domain_name:
            options["domain_name"] = domain_name

        try:
            self._cpp = cpp.domain(self.engine._cpp, str(domain_descriptor), options)
        except (Exception, cpp.TirException) as error:
            # logger.exception(error)
            # raise Error(error).with_traceback(sys.exc_info()[2])
            raise Error(error)

    def __init__(
        self,
        name=None,
        source=None,
        file=None,
        annotations=None,
        cache=True,
        engine: Engine | None = None,
        disable_plugin_calls=False,
    ):
        """

        :param name: The name of your domain you want to load.
        :type name: str
        :param source: The wowool source code of your domain.
        :type name: str
        :param file: A filename of the wowool source code of your domain.
        :type file: str
        :param annotations: The annotations you want to expose.
        :type file: list[str]
        :param cache: If you want to load this domain in the cache of the engine.
        :type cache: boolean
        :param engine: The engine that will be used to cache the domain files.
        :type engine: wowool.native.core.engine.Engine

        """
        super(Domain, self).__init__(engine)

        assert name or source or file, "At least one argument must be specified"
        self._cpp = None

        self.description = None
        if name and not source:
            self._load(name, annotations, cache=cache)
            self.description = name
        else:
            from wowool.native.core.compiler import Compiler

            compiler = Compiler()
            cache_domain = cache
            if source:
                compiler.add_source(source)
                self.description = f"source://{source[:20]}"
            if file:
                compiler.add_file(file)
                self.description = file

            # create a tmp file and load it into memory
            import tempfile

            with tempfile.NamedTemporaryFile(prefix="com.wowool.domain.file.", suffix=".dom") as tmp_filename_handel:
                tmp_filename = Path(tmp_filename_handel.name)
            compiler_errors = compiler.save(tmp_filename, disable_plugin_calls=disable_plugin_calls)
            if compiler_errors.status:
                self._load(tmp_filename, cache=cache_domain)
            else:
                logger.error(self.make_compiler_error_message(compiler_errors))
            if tmp_filename.exists():
                tmp_filename.unlink()

            if not compiler_errors.status:
                raise RuntimeError(
                    "Could not compile domain: ",
                    self.make_compiler_error_message(compiler_errors),
                )

    def make_compiler_error_message(self, compiler_errors):
        from io import StringIO

        with StringIO() as output:
            if "sink" in compiler_errors._results:
                for sink_id, sink in compiler_errors._results["sink"].items():
                    for error in sink:
                        if error["type"] == "error_marker":
                            pass
                        elif "line" in error:
                            output.write(f"source:{error['line']}:{error['column']}: {error['type']} {error['msg']}\n")
                        else:
                            output.write(f"source:{error['type']} {error['msg']}\n")
            if "message" in compiler_errors._results:
                output.write(compiler_errors._results["message"])
            return output.getvalue()

    @property
    @check_cpp_object
    def available_entities(self):
        """
        Get the concepts in the given domain

        :param: domains: a comma separated list of concepts used in the given domain.
        :returns: list of the concepts in the given domain.

        For example:

            ['Address', 'City', 'Company', 'Country' ]

        """
        assert self._cpp, DOMAIN_OBJECT_NOT_INITIALIZED
        jo = json.loads(self._cpp.info())

        if DOM_INFO in jo and jo[DOM_INFO] and DI_CONCEPTS in jo[DOM_INFO]:
            return jo[DOM_INFO][DI_CONCEPTS]
        else:
            if DI_CONCEPTS in jo[DOM]:
                return jo[DOM][DI_CONCEPTS]
        return []

    @property
    @check_cpp_object
    def concepts(self):
        """
        Get the concepts in the given domain

        .. literalinclude:: english_domain_concepts.py

        :param: domains: a comma separated list of concepts used in the given domain.
        :returns: list of the concepts in the given domain.

        For example:

            ['Address', 'City', 'Company', 'Country' ]

        """

        warnings.warn(
            "The 'concepts' property is deprecated and will be removed in a future version. " "Use 'available_entities' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.available_entities

    @property
    @check_cpp_object
    def dependencies(self):
        """
        Get the dependencies from this domain. These are other domain names that are required to run this domain.

        .. literalinclude:: english_domain_dependencies.py

        :param: dependencies: list of the dependency used in the given domain.
        :returns: list of the dependency in the given domain.

        """
        assert self._cpp, DOMAIN_OBJECT_NOT_INITIALIZED
        jo = json.loads(self._cpp.info())
        if DOM_INFO in jo:
            if DI_DEPENDENCIES in jo[DOM_INFO]:
                return jo[DOM_INFO][DI_DEPENDENCIES]
        return []

    @property
    @check_cpp_object
    def filename(self):
        assert self._cpp, DOMAIN_OBJECT_NOT_INITIALIZED
        return self._cpp.filename()

    @property
    @check_cpp_object
    def info(self):
        """
        Get the info in the given domain

        .. literalinclude:: english_domain_info.py

        :param: info: a dict
        :returns: dict with different information.

        Keys:
            * **concepts** (``list(str)``) A list of the concepts used in the domain.

            * **lexicons** (``dict``) Information about the size of the lexicons in the domain.

            * **rules** (``int``) The number of rules in the lexicon.

            * **config** (``dict``) The information listed in the '.dom_info' file

            * **config["annotations"]** (``dict``) A dictionary with the number of entries in the different lexicons.

            * **config['custom']** : Everything else you have added in the .dom_info file.

            * **sdk_version** (``str``) The version of sdk that was used to build the domain.

        """
        assert self._cpp, DOMAIN_OBJECT_NOT_INITIALIZED
        return json.loads(self._cpp.info())

    @exceptions_to_diagnostics
    @requires_analysis
    @check_cpp_object
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics, **kwargs) -> AnalysisDocument:
        """
        Annotate a given Document object with your loaded domain.

        For example:

        .. literalinclude:: english_domain_init_2.py
            :caption: english_domain_init_2.py
        """

        assert self._cpp, DOMAIN_OBJECT_NOT_INITIALIZED
        assert isinstance(document, AnalysisDocument), "Only wowool.document.Document object supported."
        assert document.has(APP_ID), "Document does not contain a Analysis Object"
        if document.has_results(APP_ID_WOWOOL_ANALYSIS):
            document.analysis.reset()

        analysis = document.results(app_id=APP_ID)

        assert analysis is not None, DOMAIN_OBJECT_NOT_INITIALIZED
        if isinstance(analysis._cpp, cpp.results):

            self._cpp.process(analysis._cpp)

            metadata = document.analysis.metadata
            if not isinstance(document.metadata, dict):
                document._metadata = {}

            if metadata:
                document._metadata |= metadata

            document.pipeline_concepts.update(self.available_entities)
            return document
        else:
            diagnostics.add(
                Diagnostic(
                    document.id,
                    f"Internal error: invalid results object returned, {type(cpp.results)}, {document._cpp}:{id(document._cpp)}",
                    DiagnosticType.Critical,
                )
            )
            return document

    def __str__(self):
        return f"<wowool.native.core.Domain {self.description} >"


def extract_concepts(domains_description):
    domain_names = domains_description.split(",")
    annotations = set()
    for dn in domain_names:
        annotations.update(get_concepts(dn))
    return annotations
