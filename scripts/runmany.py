#!/usr/bin/env python3

import csv
import json
import re
import subprocess
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def parse_scores(output):
    scores = {}
    current_test = None

    for line in output.splitlines():
        line = line.strip()

        match = re.match(r"^Running (\S+):", line)
        if match:
            current_test = match.group(1)
            continue

        match = re.match(r"^First:\s+([0-9.]+)", line)
        if match and current_test:
            score = float(match.group(1))
            scores[current_test + " First"] = score
            continue

        match = re.match(r"^Worst:\s+([0-9.]+)", line)
        if match and current_test:
            score = float(match.group(1))
            scores[current_test + " Worst"] = score
            continue

        match = re.match(r"^Average:\s+([0-9.]+)", line)
        if match and current_test:
            score = float(match.group(1))
            scores[current_test + " Average"] = score
            continue

        match = re.match(r"^Score:\s+([0-9.]+)", line)
        if match and current_test:
            score = float(match.group(1))
            scores[current_test] = score
            continue

        match = re.match(r"^Total Score:\s+([0-9.]+)", line)
        if match:
            score = float(match.group(1))
            scores["Total Score"] = score
            continue

    return scores

def run_benchmark(runs, tests):
    result_rows = []

    for i in range(1, runs + 1):
        eprint(f"\n--- Run {i} ---")
        try:
            process = subprocess.Popen(
                ["js", "cli.js", "--dump-json-results", *tests],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            output_lines = []
            for line in process.stdout:
                eprint(line, end="")             # Echo live output
                output_lines.append(line)

            process.wait()
            if process.returncode != 0:
                eprint(f"[Run {i}] Script exited with code {process.returncode}", file=sys.stderr)
                continue

            # after all, why shouldn't I? why shouldn't I print warnings on stdout?
            output = "".join([x for x in output_lines if x.startswith("{")])
            result = json.loads(output)["JetStream3.0"]

            testnames = [] # yes this is recalculated every loop. no I do not care
            row = []
            for testname, test in result["tests"].items():
                testnames.append(testname)
                row.append(test["metrics"]["Score"]["current"][0])
                row.append(test["tests"].get("First", {}).get("metrics", {}).get("Time", {}).get("current", ["-"])[0])
                row.append(test["tests"].get("Worst", {}).get("metrics", {}).get("Time", {}).get("current", ["-"])[0])
                row.append(test["tests"].get("Average", {}).get("metrics", {}).get("Time", {}).get("current", ["-"])[0])
            result_rows.append(row)

        except Exception as e:
            eprint(f"[Run {i}] Error: {e}", file=sys.stderr)

    return testnames, result_rows

def main():
    if len(sys.argv) < 2:
        eprint(f"Usage: python {sys.argv[0]} <num runs> [<test case>...]")
        sys.exit(1)

    try:
        runs = int(sys.argv[1])
    except ValueError:
        eprint("Number of runs must be an integer.")
        sys.exit(1)
    tests = sys.argv[2:]

    testnames, result_rows = run_benchmark(runs, tests)

    writer = csv.writer(sys.stdout)
    header_row = []
    for test in testnames:
        header_row.append(test)
        header_row.append(test + " First")
        header_row.append(test + " Worst")
        header_row.append(test + " Average")
    writer.writerow(header_row)
    for run in result_rows:
        writer.writerow(run)

if __name__ == "__main__":
    main()
