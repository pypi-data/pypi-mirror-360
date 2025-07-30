import json
import wowool.package.lib.wowool_sdk as cpp
import logging
from wowool.native.core.engine import Engine
from wowool.common.pipeline.objects import ComponentInfo, createUUID, UUID
from pathlib import Path
from wowool.diagnostic import Diagnostics, Diagnostic, DiagnosticType
from wowool.document import Document
from wowool.document.analysis.text_analysis import APP_ID as APP_ID_WOWOOL_ANALYSIS
from typing import Optional, Dict
from wowool.common.utilities import strip_version
from dataclasses import dataclass
import ast
import typing
from wowool.native.core.pipeline_exceptions import (
    exception_factory,
    PipelineError,
    EXCEPTION_INVALID_ARGUMENT_SYNTAX,
    EXCEPTION_ARGUMENT_TYPE_MISMATCH,
    EXCEPTION_UNKNOWN_ARGUMENT,
    EXCEPTION_ARGUMENT_VALUE_ERROR,
    EXCEPTION_INVALID_MODULE_NAME,
    CPP_EXCEPTION_TYPE_NOT_FOUND,
    UnknownArgumentError,
    ArgumentTypeMismatchError,
    ArgumentValueError,
)
from wowool.typing.typing import is_typing_instance

logger = logging.getLogger(__name__)

try:
    from wowool.apps.info import aliases
except Exception as ex:
    logger.debug(ex)
    aliases = {}

AUTO = "auto"


def expand_auto(pipeline: str) -> str:
    if pipeline.startswith(AUTO):
        auto_pipeline = pipeline[len(AUTO) :]
        auto_pipeline = auto_pipeline.replace('"', '''\\"''')
        workflow_pipeline = """lid.app,workflow(rules=[{"action":"Run","config":{"pipeline":"{language}""" + auto_pipeline + """"}}]).app"""
        return workflow_pipeline
    return pipeline


class DiagnosticApp:
    def __init__(self, app_id: str, msg: str, diagnostic_type: DiagnosticType):
        self.app_id = app_id
        self.msg = msg
        self.diagnostic_type = diagnostic_type

    def __call__(self, document: Document) -> Document:
        if not document.has_diagnostics(self.app_id):
            document.add_diagnostics(self.app_id, Diagnostics())

        diagnostics = Diagnostics()
        diagnostics.add(Diagnostic(document.id, self.msg, self.diagnostic_type))
        document.add_diagnostics(self.app_id, diagnostics)
        return document


def ast_arg_object(arg):
    if isinstance(arg, ast.Name):
        if arg.id == "false":
            return False
        elif arg.id == "true":
            return True

        return f"{arg.id}"
    elif isinstance(arg, ast.List):
        argument = []
        for v in arg.elts:
            argument.append(ast_arg_object(v))
        return argument
    elif isinstance(arg, ast.Dict):
        argument = {}
        for k, v in zip(arg.keys, arg.values):
            argument[k.value] = ast_arg_object(v)
        return argument
    elif isinstance(arg, ast.keyword):
        return ast_arg_object(arg.value)
    elif isinstance(arg, ast.UnaryOp):
        if isinstance(arg.op, ast.USub):
            return -arg.operand.value
        else:
            raise Exception(f"Unsupported unary operator {arg.op}")
    else:
        return arg.value


def add_component_information(cpp_json_info: dict, ignore_on_error: bool = False, language: str = "") -> dict:
    for comp in cpp_json_info:
        if "exception_type" in comp:
            assert "exception_msg" in comp
            if ignore_on_error:
                comp["name"] = "PassThru"
                language_post_msg = f" for the {language} language" if language else ""
                comp["type"] = "app"
                comp["options"] = {
                    "app_id": APP_ID_WOWOOL_ANALYSIS,
                    "msg": f"""{comp["exception_msg"]},[{comp["original"]}] {language_post_msg}""",
                    "diagnostic_type": DiagnosticType.Warning,
                }
                comp["app"] = {
                    "module": "wowool.native.core.pipeline_resolver",
                    "class": "DiagnosticApp",
                }
            else:
                raise exception_factory(comp["exception_msg"], comp["exception_type"], comp["original"])
        if isinstance(comp["options"], str):
            if comp["options"] == "{}":
                comp["options"] = ""

            option_str = comp["options"].strip()
            try:
                # if option_str[0] == "[" or option_str[0] == "{":
                #     comp["options"] = json.loads(option_str) if "options" in comp else {}
                # else:
                option_str = comp["options"].strip()
                data = f"""test({option_str})"""
                tree = ast.parse(data)
                arguments = []

                expr: ast.Expr = typing.cast(ast.Expr, tree.body[0])
                assert isinstance(expr, ast.Expr)

                func: ast.Call | ast.Expr = typing.cast(ast.Call | ast.Expr, tree.body[0])

                call: ast.Call = typing.cast(ast.Call, func.value)
                assert isinstance(call, ast.Call)
                for arg in call.args:
                    arguments.append(ast_arg_object(arg))

                keywords = {}
                for kwarg in call.keywords:
                    keywords[kwarg.arg] = ast_arg_object(kwarg)

                comp["arguments"] = arguments
                comp["keywords"] = keywords

            except SyntaxError as ex:
                if comp["name"] == "snippet":
                    # for a snippet we assume the first section is the one.
                    # do to syntax checking on the source code.
                    comp["arguments"] = []
                    comp["keywords"] = {"source": option_str}
                else:
                    raise exception_factory(
                        f"""Invalid argument syntax: '{option_str}' {ex}""",
                        EXCEPTION_INVALID_ARGUMENT_SYNTAX,
                        comp["original"],
                    )

            except Exception as ex:
                logger.exception(ex)
                if "options" in comp:
                    raise exception_factory(
                        f"""Invalid argument syntax: '{option_str}' {ex}""",
                        EXCEPTION_INVALID_ARGUMENT_SYNTAX,
                        comp["original"],
                    )
                if "default_argument" in aliases[comp["name"]]:
                    comp["options"] = {aliases[comp["name"]]["default_argument"]: comp["options"]}
    return cpp_json_info


def add_component_name(comp: dict) -> str:
    if comp["type"] in ["language", "domain"]:
        comp["uid"] = Path(comp["filename"]).stem
        comp["name"] = strip_version(comp["uid"])
    elif comp["type"] == "app":
        ...
    else:
        raise ValueError(f"Invalid component type: {comp['type']}")
    return comp


def convert_pipeline_info(component_info: list[dict]) -> list[ComponentInfo]:
    return [ComponentInfo(**add_component_name(comp)) for comp in component_info]


@dataclass
class ComponentConverter:
    paths: list
    file_access: bool = True
    ignore_on_error: bool = False
    allow_dev_versions: bool = True
    use_initial_language: bool = True
    language: str = ""
    engine: Engine | None = None

    def __post_init__(self):
        self.paths_str = ",".join([str(pth) for pth in self.paths])

    def get_language(self, comp: dict) -> str:
        if "type" in comp and comp["type"] == "language":
            return Path(comp["filename"]).stem.split("@")[0]
        return ""

    def make_component(self, uid: str | UUID) -> dict:
        try:
            uid_ = createUUID(uid)
            cpp_json_info = json.loads(
                cpp.pipeline_expand(uid_.name, self.paths_str, self.file_access, self.allow_dev_versions, self.language)
            )
        except cpp.TirJsonException as exception:
            raise exception_factory(**json.loads(str(exception)))
        cpp_json_info = add_component_information(cpp_json_info, self.ignore_on_error, self.language)
        if uid_.options:
            cpp_json_info[0]["keywords"] = {**cpp_json_info[0]["keywords"], **uid_.options}
        if not self.language:
            self.language = self.get_language(cpp_json_info[0])
        return resolve_apps(cpp_json_info, self.engine, self.language, use_initial_language=self.use_initial_language)[0]

    def expand_auto_componemts(self, pipeline: list[UUID]) -> list[UUID]:
        expanded = []
        workflow_pipeline = []
        for comp in pipeline:
            if comp.name == AUTO:
                expanded.append(UUID("lid.app"))
                workflow_pipeline.append("{language}")
            else:
                workflow_pipeline.append(comp)

        options = {"rules": [{"action": "Run", "config": {"pipeline": workflow_pipeline}}]}
        workflow_app = UUID("workflow.app", options=options)
        expanded.append(workflow_app)
        return expanded

    def __call__(self, pipeline: list[UUID]) -> list[dict]:
        pl = [createUUID(uid) for uid in pipeline]
        if len(pl) > 0 and pl[0].name == "auto":
            pl = self.expand_auto_componemts(pl)
        return [self.make_component(uid) for uid in pl]


def resolve(
    pipeline: str,
    paths: list,
    file_access: bool = True,
    language: str = "",
    engine: Optional[Engine] = None,
    ignore_on_error: bool = False,
    allow_dev_versions: bool = True,
    use_initial_language: bool = True,
):
    paths_str = ",".join([str(pth) for pth in paths])
    _pipeline = expand_auto(pipeline)
    try:
        cpp_json_info = json.loads(cpp.pipeline_expand(_pipeline, paths_str, file_access, allow_dev_versions, language))
    except cpp.TirJsonException as exception:
        raise exception_factory(**json.loads(str(exception)))

    cpp_json_info = add_component_information(cpp_json_info, ignore_on_error, language)
    return resolve_apps(cpp_json_info, engine, language, use_initial_language=use_initial_language)


def check_cls_init(keywords: dict, cls, component_name):
    """check the type and the existence of the keyword options

    Args:
        keywords: dict with the options you want to check.
        cls: is the class object type.

    Raises: UnknownArgumentError, ArgumentTypeMismatchError or ArgumentValueError
    """
    function_annotations = cls.__init__.__annotations__
    check_function_arguments(keywords, function_annotations, component_name)


def check_function_arguments(keywords: dict, function: Dict[str, type], component_name):
    """check the type and the existence of the keyword options

    Args:
        keywords: dict with the options you want to check.
        function_annotations: is a dict with the function annotations
        component_name: the current processed component.

    Raises: UnknownArgumentError, ArgumentTypeMismatchError or ArgumentValueError
    """

    function_annotations = typing.get_type_hints(function)
    parameter = ""
    try:
        for key, value in keywords.items():
            parameter = key
            if key not in function_annotations:
                raise UnknownArgumentError(
                    f"""Unknown argument '{key}'""",
                    EXCEPTION_UNKNOWN_ARGUMENT,
                    component_name,
                    parameter,
                )
            else:
                item = function_annotations[key]

                if not is_typing_instance(item, type(value)):
                    raise ArgumentTypeMismatchError(
                        f"""Invalid argument type: expected type {item}, but received {type(value)} with value '{value}'""",
                        EXCEPTION_ARGUMENT_TYPE_MISMATCH,
                        component_name,
                        parameter,
                    )
    except ValueError as ex:
        raise ArgumentValueError(
            f"""Invalid argument value: {ex}""",
            EXCEPTION_ARGUMENT_VALUE_ERROR,
            component_name,
            parameter,
        )
    except TypeError as ex:
        raise ArgumentValueError(
            f"""Invalid argument value: {ex}""",
            EXCEPTION_ARGUMENT_VALUE_ERROR,
            component_name,
            parameter,
        )


def resolve_class_arguments(component: dict, engine: Engine, language: str, module_name, class_name):
    component_name = component["original"] if "original" in component else ""
    try:
        import importlib

        mod = importlib.import_module(module_name)
        cls = getattr(mod, class_name)

        keywords = component["keywords"]
        assert "options" in component

        if hasattr(cls.__init__, "__annotations__"):
            function_annotations = cls.__init__.__annotations__
            if language and "language" in function_annotations:
                keywords["language"] = language
            if engine and "engine" in function_annotations:
                keywords["engine"] = engine

            assert "arguments" in component
            assert "keywords" in component
            arguments = component["arguments"]

            if len(arguments):
                idx = 0
                for function_args, py_code_arg in zip(arguments, function_annotations.items()):
                    if (function_args == "true" or function_args == "false") and is_typing_instance(py_code_arg[1], bool):
                        keywords[py_code_arg[0]] = True if function_args == "true" else False
                        idx += 1
                        continue

                    keywords[py_code_arg[0]] = function_args
                    idx += 1
                if idx < len(arguments):
                    raise exception_factory(
                        f"Invalid number of arguments: expected {len(function_annotations)}, but received {len(arguments)}",
                        EXCEPTION_ARGUMENT_TYPE_MISMATCH,
                        component["original"],
                    )
                arguments = []

            for key, value in keywords.items():
                if key in function_annotations:
                    item = function_annotations[key]
                    if (value == "true" or value == "false") and isinstance(True, item):
                        keywords[key] = True if value == "true" else False

            check_function_arguments(keywords, cls.__init__, component_name)

            component["options"] = keywords
            component.pop("arguments", None)
            component.pop("keywords", None)

    except ImportError as ex:
        raise exception_factory(
            f"""Pipeline Error: Import Error {ex}""",
            CPP_EXCEPTION_TYPE_NOT_FOUND,
            component_name,
        )
    except PipelineError as ex:
        raise ex
    except Exception as ex:
        raise exception_factory(
            f"""Pipeline Error: Could not load application component. {ex}""",
            f"{type(ex).__name__}",
            component_name,
        )


def resolve_arguments(component: dict, engine: Engine, language: str):
    module_name = ""
    class_name = ""
    if component["type"] == "app":
        class_name = component["app"]["class"]
        module_name = component["app"]["module"]
    elif component["type"] == "language":
        class_name = "Language"
        module_name = "wowool.native.core.language"
    elif component["type"] == "domain":
        class_name = "Domain"
        module_name = "wowool.native.core.domain"

    assert module_name
    assert class_name

    return resolve_class_arguments(component, engine, language, module_name, class_name)


KNOWN_APPS = {
    "unit_test": "unit_test",
    "analysis-formatter": "analysis-formatter",
    "chunks": "chunks",
    "phones": "phones",
    "sentiments": "sentiments",
    "anonymizer": "anonymizer",
    "contact-info": "contact-info",
    "infobox": "infobox",
    "snippet": "snippet",
    "quotes": "quotes",
    "entity-graph": "entity-graph",
    "graph": "entity-graph",
    "topic-identifier": "topic-identifier",
    "topics": "topic-identifier",
    "entity-mapper": "entity-mapper",
    "numbers": "numbers",
    "semantic-themes": "semantic-themes",
    "themes": "semantic-themes",
}


def check_for_known_app_installation_message(component: dict):
    uid = component.get("uid")
    if not uid:
        return None
    if uid in KNOWN_APPS:
        return f"""The app '{KNOWN_APPS[uid]}' can be installed using the command: 'pip install wowool-{KNOWN_APPS[uid]}' for the"""


def resolve_apps(json_components: list[dict], engine: Engine, language: str, use_initial_language: bool = True):
    for component in json_components:
        if language == "" and component["type"] == "language":
            if use_initial_language:
                language = Path(component["filename"]).stem
                pos = language.rfind("@")
                if pos != -1:
                    language = language[:pos]

        elif component["type"] == "app":
            component_name = component["name"]
            pos = component_name.rfind("@")
            if pos != -1:
                component_name = component_name[:pos]

            if "app" not in component:
                if component_name in aliases:
                    alias = aliases[component_name]
                    component["uid"] = alias["uid"]
                    component["app"] = {
                        "module": alias["module"],
                        "class": alias["class"],
                    }
                else:
                    component["uid"] = component_name
                    module_delimiter = component_name.rfind(".")
                    if module_delimiter != -1:
                        component["app"] = {
                            "module": component_name[:module_delimiter],
                            "class": component_name[module_delimiter + 1 :],
                        }
                    else:
                        message = check_for_known_app_installation_message(component)
                        if message:
                            raise exception_factory(
                                message,
                                EXCEPTION_INVALID_MODULE_NAME,
                                component["original"],
                            )
                        else:
                            raise exception_factory(
                                "Could not find module name in app name.",
                                EXCEPTION_INVALID_MODULE_NAME,
                                component["original"],
                            )

        # create a name argument dict from the options and add the engine and language
        # if required by the app.
        resolve_arguments(component, engine, language)

    return json_components
