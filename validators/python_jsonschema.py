import jsonschema
from .base import ValidatorProtocol


ANNOTATION_KEYWORDS = {
    "title",
    "description",
    "default",
    "examples",
    "deprecated",
    "readOnly",
    "writeOnly",
    "contentEncoding",
    "contentMediaType",
}


def collect_annotations(schema, annotations):
    if isinstance(schema, dict):
        for key, value in schema.items():

            if key in ANNOTATION_KEYWORDS:
                annotations.setdefault(key, []).append(value)

            collect_annotations(value, annotations)

    elif isinstance(schema, list):
        for item in schema:
            collect_annotations(item, annotations)


class JsonSchemaValidator(ValidatorProtocol):

    def validate(self, schema, instance):

        validator = jsonschema.Draft202012Validator(schema)

        errors = list(validator.iter_errors(instance))

        valid = len(errors) == 0

        annotations = {}
        collect_annotations(schema, annotations)

        return valid, annotations