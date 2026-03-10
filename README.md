# JSON Schema Annotation Harness

Bowtie-compatible harness for the python-jsonschema implementation that reports JSON Schema annotations.

## Supported annotations

- title
- description
- default
- examples
- deprecated
- readOnly
- writeOnly

## Build

docker build -t bowtie-python-annotations .

## Run

docker run -i bowtie-python-annotations

Example session:

{"cmd":"start","version":1}
{"cmd":"dialect","dialect":"https://json-schema.org/draft/2020-12/schema"}
{"cmd":"run","seq":1,"case":{"schema":{"title":"User"},"tests":[{"instance":{}}]}}

Expected result:

{
"seq":1,
"results":[
{
"valid":true,
"annotations":{"title":["User"]}
}
]
}

## Tests

Annotation tests were copied from the official JSON Schema Test Suite

Files were taken from annotations/tests and placed in tests/.

Run them with:

python run_tests.py

The runner executes the tests against the harness and compares returned annotations with expected values.

Notes

- Used a streaming execution model (single container session)
- Runs official annotation tests locally against the harness
