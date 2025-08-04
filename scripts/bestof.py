#!/usr/bin/env python3

import subprocess
import sys
import re
import csv
from collections import defaultdict

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

def run_benchmark(js_file, runs):
    best_scores = defaultdict(float)

    for i in range(1, runs + 1):
        eprint(f"\n--- Run {i} ---")
        try:
            process = subprocess.Popen(
                ["js", js_file],
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

            for test, score in scores.items():
                if score > best_scores[test]:
                    best_scores[test] = score

        except Exception as e:
            eprint(f"[Run {i}] Error: {e}", file=sys.stderr)

    return best_scores

def main():
    if len(sys.argv) < 3:
        eprint(f"Usage: python {sys.argv[0]} <script.js> <num_runs>")
        sys.exit(1)

    js_file = sys.argv[1]
    try:
        runs = int(sys.argv[2])
    except ValueError:
        eprint("Number of runs must be an integer.")
        sys.exit(1)

    best_scores = run_benchmark(js_file, runs)

    writer = csv.writer(sys.stdout)
    writer.writerow(["Test Case", "Score"])
    for test in sorted(best_scores):
        if test != "Total Score":
            writer.writerow([test, f"{best_scores[test]:.3f}"])
    writer.writerow(["Total Score", f"{best_scores["Total Score"]:.3f}"])

if __name__ == "__main__":
    main()
