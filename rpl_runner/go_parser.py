import re
import sys
import json

def parse(file):
    tests = []
    passed = 0
    failed = 0
    errored = 0

    message = ""
    for line in file:
        if (line == "FAIL" or line == "PASS"):
            continue
        new_test = re.findall(r"=== RUN\s*(.*)", line)
        if new_test:
            tests.append({ "name": new_test[0] })
        elif re.findall(r"--- PASS.*", line):
            tests[-1]["status"] = "PASSED"
            tests[-1]["messages"] = None
            passed += 1
        elif re.findall(r"--- FAIL.*", line):
            tests[-1]["status"] = "FAILED"
            tests[-1]["messages"] = message
            message = ""
            failed += 1
        else:
            message += line
    return {
        "tests": tests,
        "passed": passed,
        "failed": failed,
        "errored": errored
    }

def main():
    result = parse(sys.stdin)
    with open("unit_test_results_output.json", "w") as of:
        of.write(json.dumps(result, indent=4))

main()