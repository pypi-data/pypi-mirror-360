import copy
from wowool.error import Error
from jsonschema import validate as jsonschema_validate
from jsonschema.exceptions import ValidationError


file_keys = set(["tokenizer", "hmm", "postagger", "abbreviations", "apostrophe", "measure"])
ignore_keys = set(["short_description", "conditions", "detect_headers", "no_crlf", "tokenizer_mapper"])

FILE = "file"
GUESSER = "guesser"

schema_example = {
    "type": "object",
    "required": ["concept", "sample", "desc"],
    "additionalProperties": False,
    "properties": {
        "concept": {"type": "string"},
        "sample": {"type": "string"},
        "desc": {"type": "string"},
    },
}

schema = {
    "type": "object",
    # "required": ["concepts", "short_description"],
    "properties": {
        "short_description": {"type": "string", "maxLength": 128},
        "long_description": {"type": "string", "maxLength": 1024},
        "unknown_things": {"type": "boolean"},
        "instances": {"type": "boolean"},
        "concepts": {
            "type": "array",
            "items": {
                "type": "string",
                "properties": {
                    "type": {"type": "string"},
                    "value": {"type": "string"},
                    "action": {"type": "string"},
                    "input": {"type": "string"},
                },
            },
        },
        "dependencies": {
            "type": "array",
            "items": {
                "type": "string",
                "properties": {
                    "type": {"type": "string"},
                    "value": {"type": "string"},
                    "action": {"type": "string"},
                    "input": {"type": "string"},
                },
            },
        },
        "examples": {
            "type": "array",
            "items": schema_example,
        },
    },
    "additionalProperties": False,
}


class Parser:
    def __init__(self, callback, strict: bool = True):
        self.callback = callback
        self.schema = schema.copy()
        if strict:
            self.schema["required"] = ["concepts", "short_description"]

    def __call__(self, jo):
        try:
            jsonschema_validate(instance=jo, schema=self.schema)
            jou = copy.deepcopy(jo)
            if self.callback is not None:
                for key in jou:
                    if key == "dependencies":
                        jou[key] = self.callback(jou[key])
        except ValidationError as ex:
            raise Error(str(ex))

        return jou


def parser(jo, callback=None, strict: bool = True):
    parser = Parser(callback, strict=strict)
    return parser(jo)


def validate(domain_info: dict):
    jsonschema_validate(instance=domain_info, schema=schema)
