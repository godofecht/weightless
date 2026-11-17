#!/usr/bin/env python3
"""Differential fixture runner. The production chatbot remains entirely Flow."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

REFERENCE = r"""
import json
import random
import sys
from bot import runtime

random.seed(0)
memory = {}
for raw in sys.stdin:
    text = raw.rstrip("\r\n")
    if text == "/reset":
        memory = {}
        continue
    result = runtime.turn(text, memory)
    print(json.dumps({
        "reply": " ".join(str(result["reply"]).split()),
        "module": result.get("module") or "",
    }, ensure_ascii=False), flush=True)
"""


def run_checked(argv: list[str], cwd: Path, input_text: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        argv,
        cwd=cwd,
        input=input_text,
        text=True,
        capture_output=True,
        env=env,
        timeout=240,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"{' '.join(argv)} returned {result.returncode}\n"
            f"stdout:\n{result.stdout[-6000:]}\nstderr:\n{result.stderr[-6000:]}"
        )
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--flow", type=Path, required=True)
    parser.add_argument("--weightless", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    upstream = args.upstream.resolve()
    flow = args.flow.resolve()
    weightless = args.weightless.resolve()
    fixture_file = weightless / "fixtures" / "differential.json"
    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    sessions = fixture["sessions"]

    lines = []
    labels = []
    for session in sessions:
        lines.append("/reset")
        for turn in session["turns"]:
            if "\n" in turn or turn.strip() == "/reset":
                raise ValueError(f"unsupported fixture: {session['name']}")
            lines.append(turn)
            labels.append(session["name"])
    input_text = "\n".join(lines) + "\n"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(upstream)
    reference_out = run_checked(
        [sys.executable, "-c", REFERENCE],
        upstream,
        input_text,
        env,
    )
    reference = [json.loads(line) for line in reference_out.splitlines() if line.strip()]

    weightless_out = run_checked(
        [str(flow / "flow"), "run", str(weightless / "src" / "main.flow"), "--", "--trace"],
        flow,
        input_text,
    )
    weightless_results = []
    for line in weightless_out.splitlines():
        if line.startswith("WEIGHTLESS_RESULT\t"):
            parts = line.split("\t", 2)
            if len(parts) != 3:
                raise ValueError(f"malformed trace: {line}")
            weightless_results.append({"module": parts[1], "reply": parts[2].strip()})

    if len(reference) != len(labels) or len(weightless_results) != len(labels):
        raise RuntimeError(
            f"result count mismatch: expected {len(labels)}, "
            f"upstream {len(reference)}, Weightless {len(weightless_results)}"
        )

    total = len(labels)
    exact = 0
    module_matches = 0
    examples = []
    for i, session in enumerate(labels):
        a = reference[i]
        b = weightless_results[i]
        a_reply = " ".join(a["reply"].split())
        b_reply = " ".join(b["reply"].split())
        reply_equal = a_reply == b_reply
        module_equal = a["module"] == b["module"]
        exact += int(reply_equal)
        module_matches += int(module_equal)
        examples.append({
            "session": session,
            "input": next(
                x["turns"][sum(1 for j in range(i) if labels[j] == session)]
                for x in sessions if x["name"] == session
            ),
            "reference": a,
            "weightless": b,
            "reply_exact": reply_equal,
            "module_exact": module_equal,
        })

    report = {
        "upstream_repo": fixture["source"],
        "upstream_commit": fixture["source_commit"],
        "total_turns": total,
        "exact_reply_matches": exact,
        "exact_module_matches": module_matches,
        "reply_parity": round(exact / total, 4) if total else 0,
        "module_parity": round(module_matches / total, 4) if total else 0,
        "comparisons": examples,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"PyBot differential: {exact}/{total} exact replies "
        f"({100 * report['reply_parity']:.2f}%), "
        f"{module_matches}/{total} module matches "
        f"({100 * report['module_parity']:.2f}%)."
    )
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
