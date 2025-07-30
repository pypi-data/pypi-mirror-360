from logging import getLogger
from sys import exc_info
from typing import Union
import json
from wowool.native.core.app_id import APP_ID_WOWOOL_LANGUAGE_IDENTIFIER
from wowool.diagnostic import Diagnostics, Diagnostic, DiagnosticType
from wowool.document.document_interface import DocumentInterface
from wowool.document import Document
from wowool.document.analysis.document import AnalysisDocument

from wowool.error import Error
from wowool.native.core.engine import Engine, Component
import wowool.package.lib.wowool_sdk as cpp

logger = getLogger(__name__)


class LanguageIdentifier(Component):
    ID = APP_ID_WOWOOL_LANGUAGE_IDENTIFIER

    def __init__(
        self,
        default_language: str = "",
        language_candidates: Union[list[str], None] = None,
        sections: bool = False,
        section_data: bool = False,
        engine: Union[Engine, None] = None,
    ):
        """
        LanguageIdentifier is a class that will load and share the data that will be used by the language identifier. The options are the same as the keyword arguments.

        :param default_language:  The default language code to used when we cannot detect the language for a section. Default: ``english``
        :type default_language: ``str``
        :param language_candidates: List of the languages that will be considered
        :type language_candidates: ``list[str]``
        :param sections: Analyze the full document and return the sections with the corresponding language
        :type sections: ``bool``
        :param section_data: Add the data of the section in the results. Default: ``False``
        :type section_data: ``bool``

        .. literalinclude:: french_lid_init.py

        .. literalinclude:: french_lid_init_output.txt
        """
        super(LanguageIdentifier, self).__init__(engine)

        self.options = {}
        self.options["pytryoshka"] = "true"
        if default_language:
            self.options["default_language"] = default_language

        # convert the bool type c++ string.
        if section_data:
            self.options["section_data"] = "true"
        else:
            self.options["section_data"] = "false"

        # convert the bool type c++ string.
        if language_candidates:
            self.options["language_candidates"] = ",".join(language_candidates)

        self.request_sections = sections

        try:
            self._cpp = cpp.lid(self.engine._cpp, self.options)
        except (Exception, cpp.TirException) as error:
            logger.exception(error)
            raise Error(error).with_traceback(exc_info()[2])

    def __call__(self, document: str | DocumentInterface) -> AnalysisDocument:
        """
        :param document: document input data.
        :type document: Document or a str
        :return: a Document object with the language information.
        :rtype: Document

        .. code-block:: python

            lid = LanguageIdentifier()
            doc = lid(document)
            sections = doc.results( 'wowool_lid' )
            # prints the sections in the document data
            for section in sections:
                print(section)
        """
        diagnostics = Diagnostics()
        try:
            analysis_document = None
            if isinstance(document, str):
                analysis_document = AnalysisDocument(Document(document))
            elif isinstance(document, Document):
                analysis_document = AnalysisDocument(document)
            elif isinstance(document, AnalysisDocument):
                analysis_document = document
            elif isinstance(document, DocumentInterface):
                analysis_document = AnalysisDocument(document)

            results = {}

            if self.request_sections:
                results["sections"] = self.sections(analysis_document.input_document)
            else:
                results["language"] = self._language(analysis_document.input_document)

            analysis_document.add_results(APP_ID_WOWOOL_LANGUAGE_IDENTIFIER, results)
        except Exception as ex:
            logger.exception(ex)
            diagnostics.add(Diagnostic(analysis_document.id, f"Exception [{ex}]", DiagnosticType.Critical))

        assert isinstance(analysis_document, AnalysisDocument)
        if diagnostics:
            analysis_document.add_diagnostics(APP_ID_WOWOOL_LANGUAGE_IDENTIFIER, diagnostics)
        return analysis_document

    def _language(self, document: DocumentInterface) -> str:
        """
        :param document: document input data.
        :type document: Document
        :return: the language of the input document.
        """
        assert self._cpp is not None, "Operation on an invalid object"
        try:
            return self._cpp.language_identification(document.data)
        except (Exception, cpp.TirException) as error:
            raise Error(error).with_traceback(exc_info()[2])

    def identify(self, text: str) -> str:
        """
        :param document: document input data.
        :type document: Document
        :return: the language of the input document.
        """
        assert self._cpp is not None, "Operation on an invalid object"
        try:
            return self._cpp.language_identification(text)
        except (Exception, cpp.TirException) as error:
            raise Error(error).with_traceback(exc_info()[2])

    def _sections_json(self, document: str):
        """
        :param document: document input data.
        :type document: str
        :returns: the value of the requested property.
        :rtype: str

        .. literalinclude:: english_lid_section.py
            :caption: english_lid_section.py
        """
        try:
            return self._cpp.language_identification_section(document)
        except (Exception, cpp.TirException) as error:
            raise Error(error).with_traceback(exc_info()[2])

    def sections(self, document: DocumentInterface) -> list[dict]:
        """
        Return a list of the different section with there language in a given document

        :param document: document input data.
        :type document: Document
        :rtype: the a json object with the section in a document.

        .. literalinclude:: english_lid_section.py
            :caption: english_lid_section.py

        .. code-block:: json

            [
                {"begin_offset": 0, "end_offset": 50, "language": "spanish"},
                {"begin_offset": 50, "end_offset": 117, "language": "french"}
            ]

        """
        if isinstance(document, str):
            document = Document(document)

        try:
            return json.loads(self._sections_json(document.data))
        except (Exception, cpp.TirException) as error:
            raise Error(error).with_traceback(exc_info()[2])
