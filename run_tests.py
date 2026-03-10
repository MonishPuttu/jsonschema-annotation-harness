import json
import subprocess
from pathlib import Path

TEST_DIR = "tests"

process = subprocess.Popen(
    ["docker", "run", "-i", "bowtie-python-annotations"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

def send(cmd):
    process.stdin.write(json.dumps(cmd) + "\n")
    process.stdin.flush()
    return process.stdout.readline()

print(send({"cmd":"start","version":1}))
print(send({
    "cmd":"dialect",
    "dialect":"https://json-schema.org/draft/2020-12/schema"
}))

seq = 1

for file in Path(TEST_DIR).glob("*.json"):

    print("\nRunning file:", file)

    data = json.load(open(file))

    if "suite" not in data:
        print("Skipping:", file)
        continue

    for suite in data["suite"]:

        schema = suite["schema"]

        for test in suite["tests"]:

            instance = test["instance"]

            expected_annotations = {}

            if "assertions" in test:
                for assertion in test["assertions"]:
                    keyword = assertion["keyword"]
                    expected_annotations[keyword] = assertion["expected"]

            case = {
                "cmd": "run",
                "seq": seq,
                "case": {
                    "schema": schema,
                    "tests": [{"instance": instance}]
                }
            }

            send(case)

            result = json.loads(process.stdout.readline())

            returned = result["results"][0].get("annotations", {})

            print("Returned:", returned)
            print("Expected:", expected_annotations)

            if expected_annotations:
                if keyword in returned:
                    print("PASS")
                else:
                    print("MISSING:", keyword)

            seq += 1

process.stdin.close()
process.wait()