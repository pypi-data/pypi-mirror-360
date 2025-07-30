from logging import getLogger
from wowool.document import Document
from wowool.workflow.action import Action
from wowool.native.core import PipeLine
from wowool.native.core.engine import Engine
from wowool.utility.apps.decorators import exceptions_to_diagnostics
from wowool.diagnostic import Diagnostics, Diagnostic, DiagnosticType
from wowool.common.pipeline.objects import UUID, ComponentInfo
import json
from hashlib import sha256

logger = getLogger(__name__)


def has_diagnostic(comp: ComponentInfo | dict):
    if isinstance(comp, dict):
        if "options" in comp and "diagnostic_type" in comp["options"]:
            return True
    elif isinstance(comp, ComponentInfo):
        if comp.options and "diagnostic_type" in comp.options:
            return True

    return False


class RunBase(Action):
    """
    Runs a pipeline on the current document.
    """

    ID = "wowool_workflow_run"

    def __init__(self, *args, **kwargs):
        super(RunBase, self).__init__(*args, **kwargs)
        self.pipelines = {}

    def hash_pipeline(self, pipeline_description: str | list):
        if isinstance(pipeline_description, list):
            retval = ""
            for item in pipeline_description:
                if isinstance(item, str):
                    retval += item
                elif isinstance(item, UUID):
                    retval += item.name
                    if item.options:
                        retval += json.dumps(item.options, sort_keys=True, ensure_ascii=True)
                elif isinstance(item, dict):
                    retval += json.dumps(item.options, sort_keys=True, ensure_ascii=True)
                else:
                    raise ValueError(f"Invalid pipeline description: {pipeline_description}")
                retval += ","

            return sha256(retval.encode()).hexdigest()
        else:
            return sha256(pipeline_description.encode()).hexdigest()

    @exceptions_to_diagnostics
    def __call__(
        self,
        document: Document,
        diagnostics: Diagnostics,
        config: dict,
        language: str,
        engine: Engine,
    ):
        logger.debug(config)
        assert "pipeline" in config, "Missing 'pipeline' in configuration"

        pipeline_description = config["pipeline"]
        pipeline_uid = self.hash_pipeline(pipeline_description)
        if pipeline_uid in self.pipelines:
            pipeline = self.pipelines[pipeline_description]
        else:
            pipeline = self.create_pipeline(pipeline_description, language, engine, diagnostics)
            self.pipelines[pipeline_uid] = pipeline
        return pipeline(document)

    def create_pipeline(
        self,
        pipeline_description: str,
        language: str,
        engine: Engine,
        diagnostics: Diagnostics,
    ):
        raise NotImplementedError()


class Run(RunBase):
    def __init__(self, *args, **kwargs):
        super(Run, self).__init__(*args, **kwargs)

    def create_pipeline(
        self,
        pipeline_description: str,
        language: str,
        engine: Engine,
        diagnostics: Diagnostics,
    ):
        pipeline = PipeLine(pipeline_description, language=language, engine=engine, ignore_on_error=True)
        pipeline_diagnostics = [comp for comp in pipeline.pipeline_component_info if has_diagnostic(comp)]
        for _diagnostic in pipeline_diagnostics:
            diagnostics.add(Diagnostic(self.ID, _diagnostic["exception_msg"], DiagnosticType.Warning))

        return pipeline
