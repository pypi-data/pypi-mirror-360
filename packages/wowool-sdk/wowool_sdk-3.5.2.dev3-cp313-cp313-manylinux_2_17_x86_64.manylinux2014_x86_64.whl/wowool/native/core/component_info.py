from dataclasses import dataclass


@dataclass
class ComponentInfo:
    """
    Represents information about a component.
    """

    name: str
    version: str
    type: str
    description: str = ""
