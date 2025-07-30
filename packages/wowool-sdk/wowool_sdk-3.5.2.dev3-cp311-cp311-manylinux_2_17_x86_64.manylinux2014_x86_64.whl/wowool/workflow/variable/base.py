from wowool.document import Document


class Variable:
    def __init__(self, name: str, expression: str):
        self.name = name
        self.expression = expression

    def get(self, document: Document, **other_variables):
        # This needs to be implemented by subclasses
        raise NotImplementedError()

    def __repr__(self):
        return f"<{self.__class__.__name__}: name={self.name} expression={self.expression}>"
