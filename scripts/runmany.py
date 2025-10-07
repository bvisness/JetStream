#!/usr/bin/env python3

import subprocess
import sys
import re
import csv

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
                ["js", "cli.js", *tests],
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

            output = ''.join(output_lines)
            scores = parse_scores(output)

            row = []
            for test in tests:
                row.append(scores[test])
                row.append(scores[test + " First"])
                row.append(scores[test + " Worst"])
                row.append(scores[test + " Average"])
            row.append(scores["Total Score"])
            result_rows.append(row)

        except Exception as e:
            eprint(f"[Run {i}] Error: {e}", file=sys.stderr)

    return result_rows

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

    run_scores = run_benchmark(runs, tests)

    writer = csv.writer(sys.stdout)
    header_row = []
    for test in tests:
        header_row.append(test)
        header_row.append(test + " First")
        header_row.append(test + " Worst")
        header_row.append(test + " Average")
    header_row.append("Total Score")
    writer.writerow(header_row)
    for run in run_scores:
        writer.writerow(run)

if __name__ == "__main__":
    main()
