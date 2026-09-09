#!/usr/bin/env python3
"""Exercise coverage.py against positive and negative localization fixtures."""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
COVERAGE = SCRIPT_DIR / "coverage.py"
AR_FILE = SCRIPT_DIR.parent / "src" / "translations" / "ar.json"
QA_FILE = SCRIPT_DIR / "qa_fix_v1_keys.json"


def run(assembly, repos_dir, ar_file=AR_FILE, qa_file=QA_FILE):
    return subprocess.run(
        [
            sys.executable,
            str(COVERAGE),
            "--assembly",
            str(assembly),
            "--repos-dir",
            str(repos_dir),
            "--ar-file",
            str(ar_file),
            "--qa-keys-file",
            str(qa_file),
        ],
        check=False,
        text=True,
        capture_output=True,
    )


def expect(result, code, snippets, label):
    output = result.stdout + result.stderr
    if result.returncode != code:
        raise SystemExit(f"{label}: expected exit {code}, got {result.returncode}\n{output}")
    for snippet in snippets:
        if snippet not in output:
            raise SystemExit(f"{label}: missing output {snippet!r}\n{output}")
    print(f"{label}: GREEN")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assembly", required=True)
    parser.add_argument("--repos-dir", required=True)
    args = parser.parse_args()

    assembly = Path(args.assembly)
    repos_dir = Path(args.repos_dir)

    qa_key_count = len(json.loads(QA_FILE.read_text(encoding="utf-8")))
    positive = run(assembly, repos_dir)
    expect(
        positive,
        0,
        [
            f"QA Fix V1: {qa_key_count}/{qa_key_count} keys covered",
            "Shell, Scenario A, and QA Fix V1 surfaces: complete.",
            "fe-invoice",
            "/ 246",
        ],
        "positive-control",
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        ar = json.loads(AR_FILE.read_text(encoding="utf-8"))

        qa_missing = dict(ar)
        del qa_missing["contract.amountDue"]
        qa_missing_file = tmp_path / "ar-missing-qa.json"
        qa_missing_file.write_text(json.dumps(qa_missing, ensure_ascii=False), encoding="utf-8")
        expect(
            run(assembly, repos_dir, ar_file=qa_missing_file),
            2,
            ["QA Fix V1 Arabic key(s) missing", "contract.amountDue"],
            "missing-qa-key-negative-control",
        )

        shell_missing = dict(ar)
        del shell_missing["menu.invoices"]
        shell_missing_file = tmp_path / "ar-missing-shell.json"
        shell_missing_file.write_text(json.dumps(shell_missing, ensure_ascii=False), encoding="utf-8")
        expect(
            run(assembly, repos_dir, ar_file=shell_missing_file),
            2,
            ["shell key(s) missing", "menu.invoices"],
            "missing-shell-key-negative-control",
        )

        qa_keys = json.loads(QA_FILE.read_text(encoding="utf-8"))
        qa_keys.append("qa.nonexistent.source.key")
        unknown_file = tmp_path / "qa-unknown.json"
        unknown_file.write_text(json.dumps(qa_keys), encoding="utf-8")
        expect(
            run(assembly, repos_dir, qa_file=unknown_file),
            2,
            ["do not exist in the measured English catalogs", "qa.nonexistent.source.key"],
            "unknown-source-key-negative-control",
        )

    print("COVERAGE-CONTROLS: GREEN")


if __name__ == "__main__":
    main()
