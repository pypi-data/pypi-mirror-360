from logging import getLogger
from wowool.document import Document
from wowool.workflow.action import Action

logger = getLogger(__name__)


class Ping(Action):
    """
    Returns the received data. Only useful for debugging purposes.
    """

    def __call__(self, document: Document, config: dict, language: str, engine):
        logger.debug(config)
        config["data"] if "data" in config else None
        return document
