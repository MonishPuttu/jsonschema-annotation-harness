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
    line = process.stdout.readline()
    return json.loads(line)


# Start harness
print(send({"cmd": "start", "version": 1}))
print(send({
    "cmd": "dialect",
    "dialect": "https://json-schema.org/draft/2020-12/schema"
}))

seq = 1


def find_test_groups(data):
    """
    Extract JSON Schema test groups regardless of file structure.
    """

    groups = []

    if isinstance(data, list):
        groups.extend(data)

    elif isinstance(data, dict):

        if "schema" in data and "tests" in data:
            groups.append(data)

        for value in data.values():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "schema" in item and "tests" in item:
                        groups.append(item)

    return groups


for file in Path(TEST_DIR).glob("*.json"):

    print("\nRunning:", file)

    with open(file) as f:
        data = json.load(f)

    groups = find_test_groups(data)

    if not groups:
        print("Skipping file (no test groups)")
        continue

    for group in groups:

        schema = group["schema"]

        for test in group["tests"]:

            instance = test.get("data", test.get("instance"))

            case = {
                "cmd": "run",
                "seq": seq,
                "case": {
                    "schema": schema,
                    "tests": [{"instance": instance}]
                }
            }

            result = send(case)

            # Handle harness errors
            if result.get("errored"):
                print("Harness error:")
                print(result["context"]["traceback"])
                continue

            annotations = result["results"][0].get("annotations", {})

            print("Instance:", instance)
            print("Annotations:", annotations)

            seq += 1


process.stdin.close()
process.wait()