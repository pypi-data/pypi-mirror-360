from jsonschema import validate as jsonschema_validate


schema = {
    "type": "array",
    "items": {
        type: "object",
    },
}


def validate(pipeline_descriptor: dict):
    jsonschema_validate(instance=pipeline_descriptor, schema=schema)
