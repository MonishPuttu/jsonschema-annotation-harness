import jsonschema
from jsonschema.validators import extend
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


def make_validator(annotations):

    base = jsonschema.Draft202012Validator

    validators = {}

    for keyword in ANNOTATION_KEYWORDS:

        def handler(validator, value, instance, schema, keyword=keyword):

            annotations.setdefault(keyword, []).append(value)

            return []

        validators[keyword] = handler

    return extend(base, validators)


class JsonSchemaValidator(ValidatorProtocol):

    def validate(self, schema, instance):

        annotations = {}

        AnnotationValidator = make_validator(annotations)

        validator = AnnotationValidator(schema)

        errors = list(validator.iter_errors(instance))

        valid = len(errors) == 0

        return valid, annotations