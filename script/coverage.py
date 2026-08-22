#!/usr/bin/env python3
"""Report Arabic-pack coverage against each frontend module's en.json.

A missing key renders as the raw key string in the UI (Scenario A criterion
A-8), so coverage gaps must be visible here rather than discovered in a browser.

Usage:
    python3 script/coverage.py /path/to/repos/healthpay-fe-*_js
Exit 1 if any module is below 100%.
"""
import glob
import json
import os
import sys

ar = json.load(open(os.path.join(os.path.dirname(__file__), "..", "src", "translations", "ar.json"),
                    encoding="utf-8"))
paths = sys.argv[1:] or glob.glob("../healthpay-fe-*_js")
worst = 0
for p in sorted(paths):
    en_path = os.path.join(p, "src", "translations", "en.json")
    if not os.path.exists(en_path):
        continue
    en = json.load(open(en_path, encoding="utf-8"))
    missing = [k for k in en if k not in ar]
    pct = 100 * (len(en) - len(missing)) / len(en) if en else 100
    flag = "OK " if not missing else "GAP"
    print(f"{flag} {os.path.basename(p):45} {len(en)-len(missing):4}/{len(en):4}  {pct:5.1f}%")
    if missing:
        worst = 1
        for k in missing[:10]:
            print(f"       missing: {k}")
        if len(missing) > 10:
            print(f"       … and {len(missing)-10} more")
sys.exit(worst)
