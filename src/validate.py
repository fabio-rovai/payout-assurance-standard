#!/usr/bin/env python3
"""PPAS validator: check a product encoding or a payout ledger against the assurance rules.

Usage:
    python3 src/validate.py products/ph-typhoon-rice-parametric.ttl
    python3 src/validate.py --payability "examples/register-*.ttl"
    python3 src/validate.py examples/*.ttl

Exit code 0 if every file conforms, 1 otherwise. This is the whole point of the standard:
a third party can run it without asking the issuer's permission.
"""
import sys
import glob
from pathlib import Path

from rdflib import Graph
from pyshacl import validate

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "ontology" / "ppas.ttl"
SHAPES = ROOT / "shapes" / "ppas-shapes.ttl"
PAYABILITY_SHAPES = ROOT / "shapes" / "ppas-payability-shapes.ttl"


def validate_file(path: Path, payability: bool = False):
    data = Graph()
    data.parse(ONTOLOGY, format="turtle")
    data.parse(path, format="turtle")
    shapes = Graph().parse(PAYABILITY_SHAPES if payability else SHAPES, format="turtle")
    conforms, _, text = validate(
        data_graph=data,
        shacl_graph=shapes,
        advanced=True,
        inplace=False,
    )
    return conforms, text


def main(argv):
    args = [a for a in argv[1:] if a != "--payability"]
    payability = "--payability" in argv
    if not args:
        print(__doc__)
        return 2
    paths = []
    for arg in args:
        paths.extend(sorted(Path(p) for p in glob.glob(arg)))
    if not paths:
        print("no input files matched")
        return 2

    failures = 0
    for path in paths:
        conforms, text = validate_file(path, payability=payability)
        status = "PASS" if conforms else "FAIL"
        try:
            shown = path.resolve().relative_to(ROOT)
        except ValueError:
            shown = path
        print(f"[{status}] {shown}")
        if not conforms:
            failures += 1
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("Message:"):
                    print(f"         {line[len('Message:'):].strip()}")
    print(f"\n{len(paths) - failures}/{len(paths)} files conform to PPAS v0.2.1")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
