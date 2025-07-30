from importlib import import_module
from typing import List
from logging import getLogger

logger = getLogger(__name__)

MODULE_NAMES = ["wowool.workflow.action"]


class UnknownActionError(RuntimeError):
    def __init__(self, name: str):
        super(UnknownActionError, self).__init__()
        self.name = name


class ActionFactory:
    def __init__(self, module_names_extra: List[str] = []):
        super(ActionFactory, self).__init__()
        module_names = module_names_extra
        module_names.extend(MODULE_NAMES)
        logger.debug(f"Initializing action factory with module names: {module_names}")
        self._modules = list(map(import_module, module_names))

    def _load_action_class(self, name: str):
        logger.debug(f"Resolving action reference '{name}'")
        for module in self._modules:
            try:
                logger.debug(f"Trying module {module.__name__}")
                Action = getattr(module, name)
                logger.debug(f"Module {module.__name__} contains a '{name}' attribute: {Action}")
                return Action
            except AttributeError:
                logger.debug(f"Skipping module {module.__name__}: it does not contain a '{name}' class")
                pass
        raise UnknownActionError(name=name)

    def __call__(self, name: str, config: dict):
        logger.debug(f"Creating action {name} with config template {config}")
        Action = self._load_action_class(name)
        return Action(config_template=config)
