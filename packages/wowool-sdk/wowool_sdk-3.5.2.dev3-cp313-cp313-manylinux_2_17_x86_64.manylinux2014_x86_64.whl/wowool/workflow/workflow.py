from logging import getLogger
from typing import Union, List
from wowool.native.core.engine import Engine
from wowool.diagnostic import Diagnostics
from wowool.document.analysis.document import AnalysisDocument
from wowool.workflow.action import ActionFactory
from wowool.workflow.rule import RuleFactory
from wowool.workflow.variable import VariableFactory
from wowool.utility.apps.decorators import exceptions_to_diagnostics
from wowool.workflow.app_id import APP_ID

logger = getLogger(__name__)


class Workflow:
    ID = APP_ID

    def __init__(
        self,
        rules: List[dict],
        variables: Union[List[dict], None] = None,
        language: str = "",
        engine: Engine | None = None,
        variable_factory=None,
        action_factory=None,
    ):
        assert engine
        self.language = language
        self.engine: Engine = engine

        # Variables
        to_variable = variable_factory or VariableFactory()
        variables = variables if variables else []
        self._custom_variables = list(map(to_variable, variables))

        # Rules
        to_action = action_factory or ActionFactory()
        to_rule = RuleFactory(action_factory=to_action)
        self._rules = list(map(to_rule, rules))

    @exceptions_to_diagnostics
    def __call__(self, document: AnalysisDocument, diagnostics: Diagnostics) -> AnalysisDocument:
        """
        Apply any rules that match
        """
        variables = self._create_custom_variables(document)
        nr_rules = len(self._rules)
        for rule_idx, rule in enumerate(self._rules):
            logger.debug(f"Considering rule {rule_idx + 1} of {nr_rules}...")
            rule_id = f"Rule #{rule_idx}: {rule.action.__class__.__name__}"
            diagnostics.add(
                rule(
                    document=document,
                    rule_id=rule_id,
                    variables=variables,
                    language=self.language,
                    engine=self.engine,
                )
            )
        logger.debug("Finished rules")
        document.add_diagnostics(self.ID, diagnostics)
        return document

    def _create_custom_variables(self, document: AnalysisDocument) -> dict:
        logger.debug("Creating variable variables...")
        custom_variables = {}
        for variable in self._custom_variables:
            logger.debug(f"Considering production of {variable.__class__.__name__} variable '{variable.name}'")
            value = variable.get(
                document=document,
                **custom_variables,
            )
            if not value:
                logger.debug(f"Variable '{variable.name}' skipped")
                continue
            custom_variables[variable.name] = value
            logger.debug(f"Variable '{variable.name}' set to: {value}")
        return custom_variables

    def __repr__(self):
        variables = ",".join(repr(variable) for variable in self._custom_variables)
        rules = ",".join(repr(rule) for rule in self._rules)
        return f"<Workflow: variables={variables} rules={rules}>"
