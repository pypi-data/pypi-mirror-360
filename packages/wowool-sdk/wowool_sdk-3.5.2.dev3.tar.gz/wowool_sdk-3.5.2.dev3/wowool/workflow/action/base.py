from typing import Union
from logging import getLogger
from wowool.document import Document

logger = getLogger(__name__)


class Action:
    def __init__(self, config_template: Union[dict, None] = None, *args, **kwargs):
        super(Action, self).__init__(*args, **kwargs)
        self.config_template = config_template or {}

    def __call__(self, document: Document, config: dict, language: str, engine):
        # This needs to be implemented by subclasses
        raise NotImplementedError()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
