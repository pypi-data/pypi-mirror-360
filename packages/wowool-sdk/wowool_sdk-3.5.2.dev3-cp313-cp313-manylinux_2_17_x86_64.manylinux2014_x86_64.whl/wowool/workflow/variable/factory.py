class VariableFactory:
    def __call__(self, variable_description: dict):
        resolver = variable_description["resolver"] if "resolver" in variable_description else "jsonpath"
        del variable_description["resolver"]
        if "jsonpath" == resolver:
            from wowool.workflow.variable.jsonpath import VariableFromJsonPath

            return VariableFromJsonPath(**variable_description)
        else:
            raise ValueError(f"Unknown resolver '{resolver}'")
