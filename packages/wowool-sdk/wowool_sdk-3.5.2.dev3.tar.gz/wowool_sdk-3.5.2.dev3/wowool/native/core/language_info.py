import copy
from wowool.error import Error
from jsonschema import validate as jsonschema_validate
from jsonschema.exceptions import ValidationError


file_keys = set(["tokenizer", "hmm", "postagger", "abbreviations", "apostrophe", "measure"])
ignore_keys = set(["short_description", "conditions", "detect_headers", "no_crlf", "tokenizer_mapper"])

FILE = "file"
GUESSER = "guesser"

schema_morph = {
    "type": "object",
    "properties": {
        "file": {"type": "string"},
        "guesser": {"type": "string"},
        "lookup": {
            "type": "string",
            "enum": [
                "plain",
                "compound_v2",
                "compound_v3",
                "endings",
                "tag",
                "guesser",
                "compound_numbers",
                "cleaner",
            ],
        },
        "transform": {"type": "string", "enum": ["none", "tolower"]},
    },
}

schema = {
    "type": "object",
    "properties": {
        "tokenizer": {"type": "string"},
        "tokenizer_locale": {"type": "string"},
        "sentyziser": {"type": "string"},
        "hmm": {"type": "string"},
        "postagger": {"type": "string"},
        "abbreviations": {"type": "string"},
        "apostrophe": {"type": "string"},
        "measure": {"type": "string"},
        "short_description": {"type": "string", "maxLength": 128},
        "detect_headers": {"type": "boolean"},
        "conditions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "value": {"type": "string"},
                    "action": {"type": "string"},
                    "input": {"type": "string"},
                },
            },
        },
        "no_crlf": {"type": "array", "items": {"type": "string"}},
        "morph_chain": {
            "type": "array",
            "items": schema_morph,
        },
        "not_found": {
            "type": "array",
            "items": schema_morph,
        },
        "property_chain": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": schema_morph,
            },
        },
        "tokenizer_mapper": {
            "type": "array",
            "items": {
                "type": "array",
                "prefixItems": [{"type": "number"}, {"type": "string"}],
                "items": {"type": "string"},
            },
        },
    },
    "additionalProperties": False,
}


class Parser:
    def __init__(self, callback):
        self.callback = callback

    def parse_morph_item(self, morph_entries, idx, item):
        if GUESSER in item:
            morph_entries[idx][GUESSER] = self.callback(morph_entries[idx][GUESSER])
        if FILE in item:
            morph_entries[idx][FILE] = self.callback(morph_entries[idx][FILE])

    def parse_morph_list(self, morph_entries):
        for idx, item in enumerate(morph_entries):
            self.parse_morph_item(morph_entries, idx, item)

    def __call__(self, jo):
        try:
            jsonschema_validate(instance=jo, schema=schema)
            jou = copy.deepcopy(jo)
            for key in jou:
                if key in file_keys:
                    jou[key] = self.callback(jou[key])
                elif key == "property_chain":
                    for item in jou[key]:
                        self.parse_morph_list(jou[key][item])
                elif key == "not_found" or key == "morph_chain":
                    self.parse_morph_list(jou[key])
                elif key in ignore_keys:
                    # no need to check this keys
                    pass
                else:
                    raise Error(f"invalid key '{key}' in language file.")
        except ValidationError as ex:
            raise Error(str(ex))

        return jou


def parser(jo, callback):
    parser = Parser(callback)
    return parser(jo)


def validate(language_info: dict):
    jsonschema_validate(instance=language_info, schema=schema)
