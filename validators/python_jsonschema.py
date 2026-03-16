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

    def walk_schema(schema, path=""):
        locations = {}

        if isinstance(schema, dict):

            for key, value in schema.items():

                new_path = f"{path}/{key}" if path else f"/{key}"

                if key in ANNOTATION_KEYWORDS:
                    locations[id(value)] = new_path

                child_locations = walk_schema(value, new_path)
                locations.update(child_locations)

        elif isinstance(schema, list):

            for i, item in enumerate(schema):
                new_path = f"{path}/{i}"
                child_locations = walk_schema(item, new_path)
                locations.update(child_locations)

        return locations

    def validator_factory(schema):

        keyword_locations = walk_schema(schema)

        for keyword in ANNOTATION_KEYWORDS:

            def handler(validator, value, instance, schema, keyword=keyword):

                keyword_location = keyword_locations.get(id(value), f"/{keyword}")

                annotations.append({
                    "keywordLocation": keyword_location,
                    "instanceLocation": "",
                    "annotation": value,
                })

                return []

            validators[keyword] = handler

        return extend(base, validators)(schema)

    return validator_factory


class JsonSchemaValidator(ValidatorProtocol):

    def validate(self, schema, instance):

        annotations = []

        AnnotationValidatorFactory = make_validator(annotations)

        validator = AnnotationValidatorFactory(schema)

        errors = list(validator.iter_errors(instance))

        valid = len(errors) == 0

        return valid, annotations