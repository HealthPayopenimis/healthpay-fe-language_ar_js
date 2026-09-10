#!/usr/bin/env python3
"""Report Arabic-pack coverage for EVERY module in the frontend assembly.

A missing key renders as its raw key string in the operator UI (Scenario A
criterion A-8). The first version of this script measured a hand-picked list of
six modules, which is how `tasksManagement.tasksMainMenu` reached a browser: the
tasks module contributes a menu entry to the persistent app shell, so it appears
on every authenticated screen, but it was not in the list.

The module list is therefore derived from the assembly's own openimis.json —
the same source the build uses — so a module cannot be in the build and outside
the measurement.

Three thresholds:
  * SHELL keys (mainMenu / menu.* / appBar) render on every authenticated
    screen. Any gap here is a hard failure (exit 2).
  * Scenario A keys remain a hard failure because that acceptance surface is
    already frozen and green.
  * The exact QA Fix V1 and V2 keys in qa_fix_v1_keys.json and
    qa_fix_v2_keys.json are hard failures. Both fixtures must resolve to real
    English-catalog keys, preventing no-op translations or misspelled identifiers.

All catalogs are flattened recursively before comparison. This matches the
runtime locale loader and prevents nested catalogs (notably fe-invoice) from
being silently under-counted. All other keys are reported as a coverage
percentage; --strict makes any remaining gap a failure (exit 1).

Usage:
    python3 script/coverage.py --assembly /path/to/healthpay-fe_js \
                               --repos-dir /path/to/cloned/modules [--strict]
"""
import argparse
import json
import os
import re
import sys

SHELL_RE = re.compile(r"(mainMenu|MainMenu|menu\.|appBar)")

# Modules whose keys render on Scenario A screens. fe-payment is included even
# though no Scenario A step is "a payment": it CONTRIBUTES panels to the family
# overview (Premiums / Payments sections), which is the same screen used to add
# members, the policy and the contribution. Omitting it is how bare `Premiums`,
# `Payments` and payment.payment.* keys reached an operator. A module belongs
# here if any of its keys can appear on a Scenario A route, not if the scenario
# names it.
QA_FIX_V1_PATH = os.path.join(os.path.dirname(__file__), "qa_fix_v1_keys.json")
QA_FIX_V2_PATH = os.path.join(os.path.dirname(__file__), "qa_fix_v2_keys.json")

SCENARIO_A_MODULES = {
    "fe-core", "fe-home", "fe-location", "fe-insuree",
    "fe-policy", "fe-contribution", "fe-payment",
    # fe-product: the policy form embeds product.ProductPicker, so its keys
    # (label, placeholder, none-label) render on the Scenario A policy screen.
    "fe-product",
}


def flatten_messages(value, prefix=""):
    flattened = {}
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else key
            flattened.update(flatten_messages(child, child_prefix))
    else:
        flattened[prefix] = value
    return flattened


def module_dirs(assembly, repos_dir):
    cfg = json.load(open(os.path.join(assembly, "openimis.json"), encoding="utf-8"))
    names = []
    for mod in cfg.get("modules", []):
        spec = mod.get("npm", "")
        m = re.search(r"healthpay-(fe-[a-z_0-9]+)_js", spec) or re.search(r"@openimis/(fe-[a-z_0-9]+)", spec)
        if m:
            names.append(m.group(1))
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assembly", required=True)
    ap.add_argument("--repos-dir", required=True)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument(
        "--ar-file",
        default=os.path.join(os.path.dirname(__file__), "..", "src", "translations", "ar.json"),
        help="Arabic catalog override used by deterministic negative controls",
    )
    ap.add_argument(
        "--qa-keys-file",
        default=QA_FIX_V1_PATH,
        help="QA Fix V1 key-contract override used by deterministic negative controls",
    )
    ap.add_argument(
        "--qa-v2-keys-file",
        default=QA_FIX_V2_PATH,
        help="QA Fix V2 key-contract override used by deterministic negative controls",
    )
    args = ap.parse_args()

    ar = flatten_messages(json.load(open(args.ar_file, encoding="utf-8")))
    qa_v1_required = set(json.load(open(args.qa_keys_file, encoding="utf-8")))
    qa_v2_required = set(json.load(open(args.qa_v2_keys_file, encoding="utf-8")))
    qa_required = qa_v1_required | qa_v2_required
    shell_gaps, scenario_gaps, total, covered, missing_dirs = [], [], 0, 0, []
    measured_keys = set()

    for name in module_dirs(args.assembly, args.repos_dir):
        if name.startswith("fe-language_"):
            continue  # language packs carry no en.json of their own
        d = os.path.join(args.repos_dir, name)
        p = os.path.join(d, "src", "translations", "en.json")
        if not os.path.exists(p):
            missing_dirs.append(name)
            continue
        en = flatten_messages(json.load(open(p, encoding="utf-8")))
        measured_keys.update(en)
        miss = [k for k in en if k not in ar]
        qa_module_gaps = [k for k in miss if k in qa_required]
        total += len(en)
        covered += len(en) - len(miss)
        shell = [k for k in miss if SHELL_RE.search(k)]
        shell_gaps.extend(shell)
        if name in SCENARIO_A_MODULES and miss:
            scenario_gaps.extend(f"{name}:{k}" for k in miss)
        pct = 100 * (len(en) - len(miss)) / len(en) if en else 100
        flag = "SHELL-GAP" if shell else ("QA-GAP" if qa_module_gaps else ("SCENARIO-A-GAP" if (name in SCENARIO_A_MODULES and miss) else ("GAP" if miss else "OK ")))
        print(f"{flag:9} {name:26} {len(en)-len(miss):4}/{len(en):4}  {pct:5.1f}%")
        for k in shell:
            print(f"            SHELL KEY MISSING: {k}")

    qa_v1_unknown = sorted(qa_v1_required - measured_keys)
    qa_v2_unknown = sorted(qa_v2_required - measured_keys)
    qa_v1_gaps = sorted(key for key in qa_v1_required if key not in ar)
    qa_v2_gaps = sorted(key for key in qa_v2_required if key not in ar)

    print("=" * 64)
    print(f"overall: {covered}/{total} ({100*covered/total:.1f}%)")
    print(f"QA Fix V1: {len(qa_v1_required) - len(qa_v1_gaps)}/{len(qa_v1_required)} keys covered")
    print(f"QA Fix V2: {len(qa_v2_required) - len(qa_v2_gaps)}/{len(qa_v2_required)} keys covered")
    if missing_dirs:
        print(f"NOT MEASURED (repo not cloned): {', '.join(missing_dirs)}")
        print("  -> clone every assembly module before trusting this report")
        return 2
    if qa_v1_unknown or qa_v2_unknown:
        unknown = qa_v1_unknown + qa_v2_unknown
        print(f"FAIL: {len(unknown)} QA contract key(s) do not exist in the measured English catalogs:")
        for key in unknown:
            print("   ", key)
        return 2
    if qa_v1_gaps or qa_v2_gaps:
        gaps = qa_v1_gaps + qa_v2_gaps
        print(f"FAIL: {len(gaps)} QA Fix Arabic key(s) missing:")
        for key in gaps:
            print("   ", key)
        return 2
    if shell_gaps:
        print(f"FAIL: {len(shell_gaps)} shell key(s) missing — these render on every screen")
        return 2
    if scenario_gaps:
        print(f"FAIL: {len(scenario_gaps)} key(s) missing in Scenario A modules:")
        for g in scenario_gaps[:15]:
            print("   ", g)
        if len(scenario_gaps) > 15:
            print(f"    … and {len(scenario_gaps)-15} more")
        return 2
    if args.strict and covered < total:
        print("FAIL (--strict): non-shell coverage gaps remain")
        return 1
    print("Shell, Scenario A, and QA Fix V1/V2 surfaces: complete. Remaining gaps require reviewed localization scope.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
