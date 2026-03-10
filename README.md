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
