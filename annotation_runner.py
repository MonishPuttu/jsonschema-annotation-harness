#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
from typing import TYPE_CHECKING
import json
import platform
import sys
import traceback

from jsonschema.validators import validator_for
from packaging.version import parse

jsonschema_version = metadata.version("jsonschema")
use_referencing_library = parse(jsonschema_version) >= parse("4.18.0")

if use_referencing_library:
    import referencing
    import referencing.jsonschema
else:
    from jsonschema.validators import RefResolver

if TYPE_CHECKING:
    import io
    from jsonschema.protocols import Validator


ANNOTATION_KEYS = [
    "title",
    "description",
    "default",
    "examples",
    "deprecated",
    "readOnly",
    "writeOnly",
    "contentEncoding",
    "contentMediaType",
]


@dataclass
class Runner:
    _started: bool = False
    _stdout: "io.TextIOWrapper" = sys.stdout
    _DefaultValidator: "Validator | None" = None
    _default_spec = None

    def run(self, stdin=sys.stdin):
        for line in stdin:
            if not line.strip():
                continue

            each = json.loads(line)
            cmd = each.pop("cmd")

            response = getattr(self, f"cmd_{cmd}")(**each)

            self._stdout.write(json.dumps(response) + "\n")
            self._stdout.flush()

    def cmd_start(self, version):
        assert version == 1
        self._started = True

        return dict(
            version=1,
            implementation=dict(
                language="python",
                name="jsonschema-annotations",
                version=jsonschema_version,
                homepage="https://python-jsonschema.readthedocs.io/",
                documentation="https://python-jsonschema.readthedocs.io/",
                issues="https://github.com/python-jsonschema/jsonschema/issues",
                source="https://github.com/python-jsonschema/jsonschema",
                dialects=[
                    "https://json-schema.org/draft/2020-12/schema",
                    "https://json-schema.org/draft/2019-09/schema",
                    "http://json-schema.org/draft-07/schema#",
                    "http://json-schema.org/draft-06/schema#",
                    "http://json-schema.org/draft-04/schema#",
                    "http://json-schema.org/draft-03/schema#",
                ],
                os=platform.system(),
                os_version=platform.release(),
                language_version=platform.python_version(),
            ),
        )

    def cmd_dialect(self, dialect):
        assert self._started

        self._DefaultValidator = validator_for({"$schema": dialect})

        if use_referencing_library:
            self._default_spec = referencing.jsonschema.specification_with(dialect)

        return {"ok": True}

    def extract_annotations(self, schema):
        annotations = {}

        if isinstance(schema, dict):

            for key in ANNOTATION_KEYS:
                if key in schema:
                    annotations.setdefault(key, []).append(schema[key])

            for value in schema.values():
                child = self.extract_annotations(value)

                for k, v in child.items():
                    annotations.setdefault(k, []).extend(v)

        elif isinstance(schema, list):

            for item in schema:
                child = self.extract_annotations(item)

                for k, v in child.items():
                    annotations.setdefault(k, []).extend(v)

        return annotations

    def cmd_run(self, case, seq):
        assert self._started

        schema = case["schema"]

        try:

            Validator = validator_for(schema, self._DefaultValidator)

            if use_referencing_library:

                registry = referencing.Registry().with_contents(
                    case.get("registry", {}).items(),
                    default_specification=self._default_spec,
                )

                validator = Validator(schema, registry=registry)

            else:

                registry = case.get("registry", {})

                resolver = RefResolver.from_schema(schema, store=registry)

                validator = Validator(schema, resolver=resolver)

            results = []

            for test in case.get("tests", []):

                instance = test["instance"]

                valid = validator.is_valid(instance)

                annotations = self.extract_annotations(schema)

                results.append(
                    {
                        "valid": valid,
                        "annotations": annotations,
                    }
                )

            return {"seq": seq, "results": results}

        except Exception:

            return {
                "errored": True,
                "seq": seq,
                "context": {"traceback": traceback.format_exc()},
            }

    def cmd_stop(self):
        sys.exit(0)


Runner().run()