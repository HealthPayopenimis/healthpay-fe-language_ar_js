#!/usr/bin/env python3
"""Exercise hardcoded_scan.py against positive and negative fixtures."""
import argparse
import pathlib
import subprocess
import sys
import tempfile

SCANNER = pathlib.Path(__file__).resolve().parent / "hardcoded_scan.py"


def run(root):
    return subprocess.run(
        [sys.executable, str(SCANNER), str(root), "--fail"],
        check=False,
        text=True,
        capture_output=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos-dir", required=True)
    args = parser.parse_args()

    positive = run(pathlib.Path(args.repos_dir))
    if positive.returncode != 0 or "0 hardcoded Latin text node(s)" not in positive.stdout:
        raise SystemExit(f"positive-control failed\n{positive.stdout}{positive.stderr}")
    print("positive-control: GREEN")

    with tempfile.TemporaryDirectory() as tmp:
        source = pathlib.Path(tmp) / "fe-admin" / "src" / "HardcodedProbe.js"
        source.parent.mkdir(parents=True)
        source.write_text(
            'export default () => <Typography>Hardcoded English Label</Typography>;\n',
            encoding="utf-8",
        )
        negative = run(pathlib.Path(tmp))
        output = negative.stdout + negative.stderr
        if negative.returncode != 1 or "Hardcoded English Label" not in output:
            raise SystemExit(f"negative-control failed\n{output}")
        print("hardcoded-literal-negative-control: GREEN")

    print("HARDCODED-SCAN-CONTROLS: GREEN")


if __name__ == "__main__":
    main()
