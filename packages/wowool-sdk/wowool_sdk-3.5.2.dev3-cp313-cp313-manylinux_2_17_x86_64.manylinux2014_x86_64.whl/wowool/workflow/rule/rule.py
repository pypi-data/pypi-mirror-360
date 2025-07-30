from typing import List
from logging import getLogger
from wowool.native.core.app_id import APP_ID_WOWOOL_LANGUAGE_IDENTIFIER
from wowool.diagnostic import Diagnostic, DiagnosticType
from wowool.document.analysis.document import AnalysisDocument

from wowool.workflow.action import Action
from wowool.workflow.rule.config import render_template, MissingImplicitVariable

logger = getLogger(__name__)


def _collect_all_variables(document: AnalysisDocument, language: str, custom_variables: dict) -> dict:
    variables = dict(**custom_variables)

    def _add_document(document: AnalysisDocument):
        if "document" not in variables and document:
            variables["document"] = document

    def _add_language(language: str):
        if "language" not in variables:
            if language:
                variables["language"] = language
            else:
                lid_results = document.results(APP_ID_WOWOOL_LANGUAGE_IDENTIFIER)
                if lid_results and "language" in lid_results:
                    variables["language"] = lid_results["language"]

    _add_document(document)
    _add_language(language)

    return variables


class Rule:
    def __init__(self, action: Action, required_variables: List[str]):
        self.action = action
        self.required_variables = required_variables

    def __call__(self, document: AnalysisDocument, rule_id: str, variables: dict, language: str, engine):
        """
        Apply the rule if it matches. If it does not match, return ``None``. Otherwise, return the action result
        """
        logger.debug("Verifying explicitly required variables...")
        # If required variables are listed, make sure they're present
        if self.required_variables:
            for variable in self.required_variables:
                if variable not in variables:
                    return Diagnostic(
                        id=rule_id,
                        message=f"Skipped, missing explicitly required variable '{variable}'",
                        type=DiagnosticType.Info,
                    )

        # Resolve the configuration
        logger.debug("Verifying implicitly required variables...")
        try:
            all_variables = _collect_all_variables(document, language, variables)
            # logger.debug(f"Rendering configuration template with variables: {all_variables}")
            config = render_template(
                self.action.config_template,
                **all_variables,
            )
            # logger.debug(f"Rendered config template as: {config}")
        except MissingImplicitVariable as error:
            return Diagnostic(
                id=rule_id,
                message=f"Skipped, missing implicitly required variable: {error}",
                type=DiagnosticType.Info,
            )
        if "language" in all_variables:
            language = all_variables["language"]
        # Apply the action
        logger.debug(f"Applying action '{self.action.__class__.__name__}'...")
        try:
            document = self.action(
                document=document,
                config=config,
                language=language,
                engine=engine,
            )
            assert isinstance(
                document, AnalysisDocument
            ), f"Action '{self.action.__class__.__name__}' must return a Document, not '{type(document)}'"
            return Diagnostic(
                id=rule_id,
                message="Applied",
                type=DiagnosticType.Info,
            )
        except Exception as error:
            logger.exception(error)
            return Diagnostic(
                id=rule_id,
                message=f"Failed: {error}",
                type=DiagnosticType.Error,
            )

    def __repr__(self):
        requires = ",".join(self.required_variables)
        return f"<Rule: action={self.action} requires={requires}>"
