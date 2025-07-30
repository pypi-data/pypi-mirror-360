from typing import Union, Optional, List
from wowool.native.core.engine import Component
from wowool.native.core import Language, Domain
from wowool.document import Document
from pathlib import Path
from wowool.document import DocumentInterface
from wowool.document.analysis.document import AnalysisDocument
from wowool.common.pipeline.objects import ComponentInfo
from wowool.native.core.pipeline_resolver import resolve, ComponentConverter, convert_pipeline_info
from wowool.native.core.engine import Engine
from wowool.native.core.pipeline_exceptions import ComponentError, EXCEPTION_ARGUMENT_VALUE_ERROR
from hashlib import sha256
import json


def convert_component_info(obj, **kwargs):
    if isinstance(obj, ComponentInfo):
        return obj.to_json()
    elif isinstance(obj, Engine):
        return None
    return obj


def create_components(pipeline_info: List[dict], **kwargs) -> List[dict]:
    components = []
    for component in pipeline_info:
        if component["type"] == "language":
            components.append(Language(component["filename"], **component["options"], **kwargs))
        elif component["type"] == "domain":
            components.append(Domain(component["filename"], **component["options"]))
        elif component["type"] == "app":
            import importlib

            if "app" in component:
                class_name = component["app"]["class"]
                module_name = component["app"]["module"]
            else:
                class_name = component["name"]
                module_name = component["namespace"]

            try:
                mod = importlib.import_module(module_name)
                cls = getattr(mod, class_name)
                components.append(cls(**component["options"]))
            except Exception as ex:
                raise ComponentError(
                    f"""Pipeline Error: could not load application component name: {component["name"]}, {ex}""",
                    EXCEPTION_ARGUMENT_VALUE_ERROR,
                    component["name"],
                )
        else:
            raise ValueError(f"Pipeline Error: Invalid component name: {components}")
    return components


def get_lxware_path(engine: Engine) -> List[Path]:
    info = engine.info()
    return [info["options"]["lxware"]] if "options" in info and "lxware" in info["options"] else []


class Pipeline(Component):
    """
    Wrapper object to quickly create a analysis pipeline.

    The components to pass to the pipeline are the language followed by the domains with or without the language affix. For instance, if we want to run english with english_entity and english_sentiment, we will pass (english,english-entity,english-sentiment) or (english,entity,sentiment).

    ex: 'english,entity' will load the english language modules and the english-entities.

    Args:
        pipeline (str): a comma separate list of components (Languages or Domains) to create. ex: english,entity
        path (Optional[List[Union[str, Path]]]): The paths where to find the component.
        options (dict, optional): [description]. Defaults to {}.

    Returns:
        Pipeline: Callable object.

    .. literalinclude:: english_pipeline_init.py
        :caption: english_pipeline_init.py

    """

    @staticmethod
    def expand(
        pipeline: str,
        paths: Union[List[str], List[Path]] = [],
        file_access: bool = True,
        language: str = "",
        engine: Optional[Engine] = None,
        ignore_on_error: bool = False,
        allow_dev_version: bool = True,
    ):
        retval = resolve(pipeline, paths, file_access, language, engine, ignore_on_error, allow_dev_version)
        return retval

    def __init__(
        self,
        pipeline: str | list = "",
        engine: Optional[Engine] = None,
        paths: Optional[Union[List[str], List[Path]]] = None,
        language: str = "",
        ignore_on_error=False,
        allow_dev_version=True,
        pipeline_components: list[dict] | None = None,
        option_create_components: bool = True,
        file_access: bool = True,
        use_initial_language: bool = True,
        allow_dev_versions: bool = True,
        **kwargs,
    ):
        """
        Create a pipeline object.

        :param pipeline: A comma separate list of components (Languages or Domains) to create. ex: english,entity
        :type pipeline: str
        :param engine: The engine that will be passed to the different components.
        :type engine: wowool.native.core.engine.Engine
        :param options: The options that will be passed to the components.
        :type options: dict
        :param paths: The paths where to find the component.
        :type paths: Optional[List[Union[str, Path]]]
        :param dbg: debug information requested. a comma delimited string, see wow++ for more info
        :type dbg: str

        """
        super(Pipeline, self).__init__(engine)
        self.pipeline_component_info_dict = []
        if not (isinstance(pipeline, str) or isinstance(pipeline, list)):
            raise ValueError("Pipeline Error: Invalid pipeline type: supports a string or a list of components")

        if pipeline_components:
            # we already have the pipeline components, we just need to load them.
            component_options = kwargs
            self.pipeline_component_info_dict = pipeline_components
            components = create_components(pipeline_components, **component_options)

            self._components = components
        else:

            if pipeline:
                paths_ = paths if paths else get_lxware_path(self.engine)
                component_options = kwargs
                if isinstance(pipeline, list):
                    # pipeline is a list of components
                    converter = ComponentConverter(
                        paths_, file_access, ignore_on_error, allow_dev_versions, use_initial_language, language, self.engine
                    )
                    self.pipeline_component_info_dict = converter(pipeline)

                elif pipeline:
                    # pipeline is a string
                    self.pipeline_component_info_dict = resolve(
                        pipeline,
                        paths_,
                        True,
                        language,
                        self.engine,
                        ignore_on_error,
                        allow_dev_version,
                    )

                if len(self.pipeline_component_info_dict) > 0 and self.pipeline_component_info_dict[0]["type"] == "domain":
                    # If the first component is a domain, we need to insert a Language component at the beginning
                    generic_pipeline = resolve(
                        "generic",
                        paths_,
                        True,
                        language,
                        self.engine,
                        ignore_on_error,
                        allow_dev_version,
                    )

                    self.pipeline_component_info_dict.insert(0, generic_pipeline[0])

                self.pipeline_component_info = convert_pipeline_info(self.pipeline_component_info_dict)

                if option_create_components:

                    components = create_components(self.pipeline_component_info_dict, **component_options)
                    self._components = components
            else:
                self.pipeline_component_info_dict = "(empty)"
                self.pipeline_component_info = []
                self._components = []

    def __call__(self, document: str | DocumentInterface, id=None, **kwargs) -> AnalysisDocument:
        """

        :param document: The document data to process.
        :type document: [ str, DocumentInterface]
        :param id: The id of the document data, this is only used in combination with a document as a str
        :param id: str
        :return: A document objects. see API docs.

        """
        if isinstance(document, str):
            ret_document = Document(document, id)
        elif isinstance(document, DocumentInterface):
            ret_document = document
        else:
            ret_document = document

        for component in self._components:
            if not callable(component):
                raise TypeError(f"Component {component} is not callable (type: {type(component)})")

            if isinstance(component, Language) or isinstance(component, Domain):
                ret_document = component(ret_document, **kwargs)
            else:
                # print(f"Running component {component}")
                ret_document = component(ret_document)

        # Ensure the return type is AnalysisDocument
        if not isinstance(ret_document, AnalysisDocument):
            raise TypeError(f"Pipeline did not return an AnalysisDocument, got {type(ret_document)}")

        return ret_document

    @property
    def components_info(self) -> list:
        """return a list of the components"""
        # from copy import deepcopy
        # info = deepcopy(self.pipeline_component_info_dict)
        # for component in info:
        #     if "options" in component and "engine" in component["options"]:
        #         del component["options"]["engine"]
        return self.pipeline_component_info

    @property
    def components(self) -> list:
        """return a list of the components"""
        return self._components

    @property
    def domains(self) -> list:
        return [component for component in self._components if isinstance(component, Domain)]

    @property
    def concepts(self) -> list[str]:
        concepts = set()

        for comp in self._components:
            if hasattr(comp, "concepts"):
                concepts |= set(comp.concepts)
        return list(concepts)

    @property
    def language(self) -> str:
        """language of the first Language object"""
        if len(self._components) >= 1 and isinstance(self._components[0], Language):
            return self._components[0].language
        return ""

    def __rep__(self):
        print(f"<Pipeline {self.pipeline_component_info_dict}>")

    def __str__(self) -> str:
        from io import StringIO

        with StringIO() as output:
            output.write("[ ")
            output.write(f"""{self.language}""")
            for component in self._components:
                output.write(f""", {component}""")
            output.write(" ]")
            return output.getvalue()

    @property
    def uid(self):
        if hasattr(self, "uid_"):
            return self.uid_
        pipeline_string = json.dumps(self.pipeline_component_info, sort_keys=True, default=convert_component_info).encode("utf-8")
        # Create a SHA-256 hash object
        hash_object = sha256(pipeline_string)
        # Get the hexadecimal representation of the hash
        self.uid_ = hash_object.hexdigest()
        return self.uid_

    def to_json(self) -> dict:
        retval: List[ComponentInfo] = self.pipeline_component_info
        for component in retval:
            component.options.pop("engine", None)  # Remove engine from options if present
            component.filename = None

        pipeline_string = json.dumps(retval, sort_keys=True, default=convert_component_info)
        return json.loads(pipeline_string)


PipeLine = Pipeline
