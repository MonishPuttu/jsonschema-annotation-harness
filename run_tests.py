import json
import subprocess
from pathlib import Path

TEST_DIR = "tests"

for file in Path(TEST_DIR).glob("*.json"):

    print("\nRunning file:", file)

    data = json.load(open(file))

    for suite in data["suite"]:

        schema = suite["schema"]

        for test in suite["tests"]:

            instance = test["instance"]

            case = {
                "cmd": "run",
                "seq": 1,
                "case": {
                    "schema": schema,
                    "tests": [{"instance": instance}]
                }
            }

            process = subprocess.Popen(
                ["docker", "run", "-i", "bowtie-python-annotations"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )

            process.stdin.write(json.dumps({"cmd":"start","version":1})+"\n")
            process.stdin.write(json.dumps({"cmd":"dialect","dialect":"https://json-schema.org/draft/2020-12/schema"})+"\n")
            process.stdin.write(json.dumps(case)+"\n")

            process.stdin.close()

            print(process.stdout.read())
