#!/usr/bin/env python3
"""Assert that the PPAS rules do useful work.

A validation rule set that passes everything is decoration. These tests assert that the
known-good ledger conforms and that the known-bad ledger fails on the specific rules it was
built to trip. Run from the repository root:

    python3 tests/test_rules.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from validate import validate_file  # noqa: E402

EXPECTED_BROKEN_RULES = {"R6", "R7", "R8"}
EXPECTED_BROKEN_PAYABILITY_RULES = {"P1", "P2", "P3", "P4"}


def rules_in(report: str) -> set:
    found = set()
    for line in report.splitlines():
        line = line.strip()
        if line.startswith("Message:"):
            msg = line[len("Message:"):].strip()
            code = msg.split(":", 1)[0].strip()
            if code[:1] in ("R", "P") and code[1:].isdigit():
                found.add(code)
    return found


def main():
    failures = []

    for name in ("ph-typhoon-rice-parametric.ttl", "ph-fisher-landfall-parametric.ttl"):
        conforms, report = validate_file(ROOT / "products" / name)
        if not conforms:
            failures.append(f"product {name} should conform but did not:\n{report}")
        else:
            print(f"ok   product {name} conforms")

    conforms, report = validate_file(ROOT / "examples" / "ledger-clean.ttl")
    if not conforms:
        failures.append(f"ledger-clean.ttl should conform but did not:\n{report}")
    else:
        print("ok   ledger-clean.ttl conforms")

    conforms, report = validate_file(ROOT / "examples" / "ledger-broken.ttl")
    if conforms:
        failures.append("ledger-broken.ttl conformed, so the rules are not doing any work")
    else:
        found = rules_in(report)
        missing = EXPECTED_BROKEN_RULES - found
        if missing:
            failures.append(
                f"ledger-broken.ttl failed, but rules {sorted(missing)} did not fire. "
                f"Fired: {sorted(found)}")
        else:
            print(f"ok   ledger-broken.ttl fails on {sorted(found)} as designed")

    conforms, report = validate_file(ROOT / "examples" / "register-clean.ttl", payability=True)
    if not conforms:
        failures.append(f"register-clean.ttl should conform but did not:\n{report}")
    else:
        print("ok   register-clean.ttl conforms (including a declared legitimate name mismatch)")

    conforms, report = validate_file(ROOT / "examples" / "register-broken.ttl", payability=True)
    if conforms:
        failures.append("register-broken.ttl conformed, so the payability rules are not doing any work")
    else:
        found = rules_in(report)
        missing = EXPECTED_BROKEN_PAYABILITY_RULES - found
        if missing:
            failures.append(
                f"register-broken.ttl failed, but rules {sorted(missing)} did not fire. "
                f"Fired: {sorted(found)}")
        else:
            print(f"ok   register-broken.ttl fails on {sorted(found)} as designed")

    if failures:
        print("\nFAILED")
        for f in failures:
            print(" -", f)
        return 1
    print("\nall assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
