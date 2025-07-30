from typing import Optional


# list of exception type from the cpp
CPP_EXCEPTION_TYPE_NOT_FOUND = "not_found"
CPP_EXCEPTION_TYPE_PIPELINE_ERROR = "pipeline_error"

# mapped to internal
CPP_EXCEPTION_TYPE_STD = "std"

EXCEPTION_INVALID_ARGUMENT_SYNTAX = "invalid_argument_syntax"
EXCEPTION_UNKNOWN_ARGUMENT = "unknown_argument"
EXCEPTION_ARGUMENT_TYPE_MISMATCH = "argument_type_mismatch"
EXCEPTION_INTERNAL_EXCEPTION = "internal"
EXCEPTION_ARGUMENT_VALUE_ERROR = "argument_value_error"
EXCEPTION_INVALID_MODULE_NAME = "invalid_module_name"


class PipelineError(RuntimeError):
    def __init__(self, exception_msg: str, exception_type: str, name: Optional[str] = None):
        super(PipelineError, self).__init__(exception_msg)

        jex = {
            "exception_msg": exception_msg,
            "exception_type": exception_type,
            "name": name,
        }

        self.jex = jex

    @property
    def name(self):
        return self.jex["name"]

    @property
    def component(self):
        """return the name of the component in the pipeline"""
        return self.jex["name"]

    @property
    def exception_type(self):
        return self.jex["exception_type"]

    @property
    def message(self):
        return self.jex["exception_msg"]

    def __str__(self) -> str:
        if "name" in self.jex and self.jex["name"]:
            return f"""{self.jex["exception_msg"]} {self.jex["name"]}"""
        return f"""{self.jex["exception_msg"]}"""


class ComponentNotFoundError(PipelineError):
    def __init__(self, exception_msg: str, exception_type: str, name: Optional[str] = None):
        super(ComponentNotFoundError, self).__init__(exception_msg, exception_type, name)
        try:
            from wowool.apps.info import aliases

            if exception_type == "not_found" and name and name in aliases:
                self.jex["exception_msg"] = f"Did you forgot the application extension for {name}(...).app?"
        except Exception:
            pass


class ComponentError(PipelineError):
    def __init__(self, exception_msg: str, exception_type: str, name: Optional[str] = None):
        super(ComponentError, self).__init__(exception_msg, exception_type, name)


class InvalidArgumentSyntaxError(PipelineError):
    def __init__(self, exception_msg: str, exception_type: str, name: Optional[str] = None):
        super(InvalidArgumentSyntaxError, self).__init__(exception_msg, exception_type, name)


class InternalError(PipelineError):
    def __init__(self, exception_msg: str, exception_type: str, name: Optional[str] = None):
        super(InternalError, self).__init__(exception_msg, exception_type, name)


class InvalidModuleNameError(PipelineError):
    def __init__(self, exception_msg: str, exception_type: str, name: Optional[str] = None):
        super(InvalidModuleNameError, self).__init__(exception_msg, exception_type, name)


class PipelineComponentArgumentError(PipelineError):
    def __init__(self, exception_msg: str, exception_type: str, name: str, parameter: str):
        super(PipelineComponentArgumentError, self).__init__(exception_msg, exception_type, name)
        self.jex["parameter"] = parameter

    @property
    def parameter(self) -> str:
        return self.jex["parameter"]

    @property
    def argument(self) -> str:
        return self.parameter


class UnknownArgumentError(PipelineComponentArgumentError):
    def __init__(self, exception_msg: str, exception_type: str, name: str, parameter: str):
        super(UnknownArgumentError, self).__init__(exception_msg, exception_type, name, parameter)


class ArgumentTypeMismatchError(PipelineComponentArgumentError):
    def __init__(self, exception_msg: str, exception_type: str, name: str, parameter: str):
        super(ArgumentTypeMismatchError, self).__init__(exception_msg, exception_type, name, parameter)


class ArgumentValueError(PipelineComponentArgumentError):
    def __init__(self, exception_msg: str, exception_type: str, name: str, parameter: str):
        super(ArgumentValueError, self).__init__(exception_msg, exception_type, name, parameter)


_exception_mapping = {
    CPP_EXCEPTION_TYPE_NOT_FOUND: ComponentNotFoundError,
    CPP_EXCEPTION_TYPE_PIPELINE_ERROR: ComponentError,
    EXCEPTION_INVALID_ARGUMENT_SYNTAX: InvalidArgumentSyntaxError,
    EXCEPTION_INTERNAL_EXCEPTION: InternalError,
    EXCEPTION_INVALID_MODULE_NAME: InvalidModuleNameError,
}


def exception_factory(exception_msg: str, exception_type: str, name: Optional[str] = None):
    return _exception_mapping.get(exception_type, InternalError)(exception_msg, exception_type, name)
