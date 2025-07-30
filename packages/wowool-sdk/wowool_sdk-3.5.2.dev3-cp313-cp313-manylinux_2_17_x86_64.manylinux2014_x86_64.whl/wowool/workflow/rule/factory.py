from typing import Union
from wowool.workflow.rule.rule import Rule
from wowool.workflow.action import ActionFactory


class RuleFactory:
    def __init__(self, action_factory: Union[ActionFactory, None] = None):
        self._to_action = action_factory or ActionFactory()

    def __call__(self, rule_description: dict):
        # Action
        assert "action" in rule_description, "Missing 'action' in rule description"
        name = rule_description["action"]
        del rule_description["action"]
        config = {}
        if "config" in rule_description:
            config = rule_description["config"]
        action = self._to_action(name=name, config=config)

        # Requires
        required_variables = rule_description["requires"] if "requires" in rule_description else []

        return Rule(action=action, required_variables=required_variables)
