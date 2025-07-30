from typing import Any
from logging import getLogger
from jinja2 import Template, UndefinedError, StrictUndefined

logger = getLogger(__name__)


class MissingImplicitVariable(RuntimeError):
    def __init__(self, message: str):
        super(MissingImplicitVariable, self).__init__(message)


def render_template(value: Any, **variables):
    if isinstance(value, dict):
        return {k: render_template(v, **variables) for k, v in value.items()}
    elif isinstance(value, list):
        return [render_template(v, **variables) for v in value]
    elif isinstance(value, str):
        try:
            return Template(
                value,
                variable_start_string="{",
                variable_end_string="}",
                undefined=StrictUndefined,
            ).render(**variables)
        except UndefinedError as error:
            raise MissingImplicitVariable(
                message=str(error),
            )
    else:
        return value
