from logging import getLogger
from jsonpath_ng import parse
from wowool.document.analysis.document import AnalysisDocument
from wowool.workflow.variable.base import Variable

logger = getLogger(__name__)


class VariableFromJsonPath(Variable):
    def __init__(self, **kwargs):
        super(VariableFromJsonPath, self).__init__(**kwargs)
        self.matcher = parse(self.expression)

    def get(self, document: AnalysisDocument, **other_variables):
        # TODO this is not very efficient, we should cache the json data. at this stage the wowool results are
        # not in json but are python objects
        document_json = document.data
        logger.debug(f"Finding matches for: {self.expression}")
        matches = [match.value for match in self.matcher.find(document_json)]
        logger.debug(f"Matches: {matches}")
        return matches
