import wowool.package.lib.wowool_sdk as cpp
from wowool.document.analysis.document import AnalysisDocument
from typing import Union
from wowool.native.core.app_id import APP_ID_WOWOOL_FILTER
from wowool.utility.apps.decorators import (
    exceptions_to_diagnostics,
    requires_analysis,
)
from wowool.diagnostic import Diagnostics


class Filter:
    """
    A Filter object can be used to filter your results.

    :param: filter: is a collection or a comma delimited string of the annotation you want to filter..
    :type: filter Union[list, set, str]


        For example:

    .. literalinclude:: dutch_filter_concepts.py
        :caption: filter_init.py

    """

    ID = APP_ID_WOWOOL_FILTER

    def __init__(self, filter: Union[list, set, str]):
        if isinstance(filter, str):
            filter = filter.split(",")

        if isinstance(filter, list):
            filter = set(filter)

        self._cpp = cpp.filter(filter)

    @exceptions_to_diagnostics
    @requires_analysis
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        """
        Filter a given Document object with your loaded domain.
        """
        analysis = document.analysis
        self._cpp.process(analysis._cpp)
        return document

    def info(self) -> list[str]:
        concepts = self._cpp.info()
        return concepts.split("|") if isinstance(concepts, str) else []
