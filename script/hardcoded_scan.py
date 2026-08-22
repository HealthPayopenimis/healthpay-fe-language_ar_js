#!/usr/bin/env python3
"""Scan Scenario A modules for user-visible text that bypasses translation.

The Arabic pack cannot fix what never goes through the translation layer.
PolicyValuesPanel.js rendered <Typography>General</Typography> and four
siblings as literal English, so no amount of pack coverage would have caught it
— coverage.py compares KEY SETS and is blind to text with no key at all.

Flags JSX text nodes that are plain Latin words inside common text elements.
Heuristic by nature: `--list` prints findings for review rather than failing a
build, and reviewed acceptable cases go in ALLOWLIST.

Usage: python3 script/hardcoded_scan.py /path/to/repos [--fail]
"""
import os
import re
import sys

SCENARIO_A = ("fe-core", "fe-home", "fe-location", "fe-insuree",
              "fe-policy", "fe-contribution", "fe-payment", "fe-product")

# Latin text directly inside a text element, e.g. <Typography ...>General</Typography>
PATTERN = re.compile(
    r"<(Typography|InputLabel|FormLabel|Button|Tooltip|TableCell|Chip)\b[^>]*>\s*"
    r"([A-Z][A-Za-z][A-Za-z \-&/']{2,60})\s*</\1>"
)

ALLOWLIST = {
    # add reviewed, deliberate literals here with a reason
}


def main():
    root = sys.argv[1]
    fail = "--fail" in sys.argv
    findings = []
    for mod in SCENARIO_A:
        base = os.path.join(root, mod, "src")
        for dirpath, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in ("node_modules", "translations")]
            for f in files:
                if not f.endswith((".js", ".jsx")):
                    continue
                path = os.path.join(dirpath, f)
                try:
                    src = open(path, encoding="utf-8").read()
                except OSError:
                    continue
                for m in PATTERN.finditer(src):
                    text = m.group(2).strip()
                    if text in ALLOWLIST:
                        continue
                    line = src[: m.start()].count("\n") + 1
                    findings.append((mod, os.path.relpath(path, root), line, text))

    for mod, path, line, text in findings:
        print(f"HARDCODED  {path}:{line}  {text!r}")
    print("=" * 60)
    print(f"{len(findings)} hardcoded Latin text node(s) in Scenario A modules")
    return 1 if (findings and fail) else 0


if __name__ == "__main__":
    sys.exit(main())
