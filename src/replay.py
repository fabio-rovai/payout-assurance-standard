#!/usr/bin/env python3
"""Replay encoded parametric products against observed historical events.

For every product in products/ and every event in data/, decide whether the trigger would
have fired and what share of the sum insured would have been paid. Then report where two
products diverge, which is where basis risk lives.

Usage:
    python3 src/replay.py               # human-readable table
    python3 src/replay.py --markdown    # emit docs/BASIS_RISK.md content
"""
import csv
import sys
from decimal import Decimal
from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS

PPAS = Namespace("https://w3id.org/ppas#")
ROOT = Path(__file__).resolve().parent.parent

COMPARATORS = {
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    "<": lambda a, b: a < b,
}


def load_products():
    products = []
    for path in sorted((ROOT / "products").glob("*.ttl")):
        g = Graph().parse(path, format="turtle")
        for prod in g.subjects(RDF.type, PPAS.ParametricProduct):
            triggers = []
            for trig in g.objects(prod, PPAS.hasTrigger):
                index = next(g.objects(trig, PPAS.observesIndex), None)
                triggers.append({
                    "threshold": Decimal(str(next(g.objects(trig, PPAS.thresholdValue)))),
                    "unit": str(next(g.objects(trig, PPAS.unit))),
                    "comparator": str(next(g.objects(trig, PPAS.comparator))),
                    "spatial_basis": str(next(g.objects(index, PPAS.spatialBasis), "unstated")),
                    "measurement_basis": str(next(g.objects(index, PPAS.measurementBasis), "unstated")),
                })
            tiers = []
            for tier in g.objects(prod, PPAS.hasPayoutTier):
                tiers.append((
                    Decimal(str(next(g.objects(tier, PPAS.tierThreshold)))),
                    Decimal(str(next(g.objects(tier, PPAS.tierPayoutRatio)))),
                ))
            tiers.sort(key=lambda t: t[0])
            products.append({
                "uri": str(prod),
                "label": str(next(g.objects(prod, RDFS.label), "")),
                "file": path.name,
                "triggers": triggers,
                "tiers": tiers,
                "sum_insured": Decimal(str(next(g.objects(prod, PPAS.sumInsured), "0"))),
                "currency": str(next(g.objects(prod, PPAS.currency), "")),
                "settlement_days": int(next(g.objects(prod, PPAS.settlementWindowDays), 0)),
                "confidence": str(next(g.objects(prod, PPAS.encodingConfidence), "unstated")),
            })
    return products


def load_events():
    with open(ROOT / "data" / "ph_typhoon_landfalls.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def payout_ratio(product, observed: Decimal) -> Decimal:
    fired = any(COMPARATORS[t["comparator"]](observed, t["threshold"]) for t in product["triggers"])
    if not fired:
        return Decimal("0")
    ratio = Decimal("0")
    for threshold, r in product["tiers"]:
        if observed >= threshold:
            ratio = r
    return ratio


def main(argv):
    products = load_products()
    events = load_events()
    md = "--markdown" in argv
    out = []

    out.append("# Basis-risk replay, PPAS v0.1.0")
    out.append("")
    out.append("Every product encoding in `products/` replayed against every observed event in")
    out.append("`data/ph_typhoon_landfalls.csv`. Wind figures are PAGASA ten-minute maximum sustained")
    out.append("winds at landfall, each row individually sourced in the CSV. Classes are computed under")
    out.append("PAGASA's post-March-2022 scale applied retrospectively.")
    out.append("")
    out.append("## Payout share of sum insured, by product and event")
    out.append("")
    header = "| Event | Landfall wind (km/h) | " + " | ".join(
        p["file"].replace(".ttl", "") for p in products) + " |"
    out.append(header)
    out.append("|" + "---|" * (2 + len(products)))
    for ev in events:
        observed = Decimal(ev["msw_kmh_10min"])
        cells = []
        for p in products:
            ratio = payout_ratio(p, observed)
            cells.append(f"{ratio * 100:.0f}%" if ratio else "no payout")
        out.append(f"| {ev['name_international']} ({ev['name_local']}), {ev['landfall_date']} "
                   f"| {ev['msw_kmh_10min']} | " + " | ".join(cells) + " |")
    out.append("")

    out.append("## Where the products disagree")
    out.append("")
    disagreements = 0
    for ev in events:
        observed = Decimal(ev["msw_kmh_10min"])
        ratios = {p["file"]: payout_ratio(p, observed) for p in products}
        if len(set(ratios.values())) > 1:
            disagreements += 1
            detail = ", ".join(f"{k.replace('.ttl','')} pays {v * 100:.0f}%" for k, v in ratios.items())
            out.append(f"- **{ev['name_international']} ({ev['name_local']})** at {ev['msw_kmh_10min']} km/h: {detail}.")
    if not disagreements:
        out.append("- On this event set, all encoded products agree on whether a payout is due.")
    out.append("")

    out.append("## The finding that matters: divergence detected from the encoding, not the payout table")
    out.append("")
    out.append("Read the table above carefully. On these four events the two products behave almost")
    out.append("identically, and the one difference is a tier ratio. That is not the interesting result,")
    out.append("and pretending otherwise would be the exact overclaim this standard exists to catch.")
    out.append("")
    out.append("The real finding is structural, and the validator extracts it without any event data at all:")
    out.append("")
    for p in products:
        for t in p["triggers"]:
            out.append(f"- `{p['file'].replace('.ttl','')}`: threshold {t['threshold']} {t['unit']} "
                       f"{t['comparator']}, measured at **{t['spatial_basis']}**, "
                       f"settlement promise {p['settlement_days']} days, encoding confidence "
                       f"*{p['confidence']}*.")
    out.append("")
    out.append("Two products, the same advertised 118 km/h headline, and two different promises. One pays")
    out.append("on where the storm centre crossed the coast; the other on what happened over the insured")
    out.append("parcel. One promises settlement in 5 days, the other in 14. On any brochure or national")
    out.append("product register these are the same product. In the field they are not.")
    out.append("")
    out.append("### Why the payout table cannot show this, and what would")
    out.append("")
    out.append("This replay feeds landfall wind to both products because per-parcel gridded wind fields")
    out.append("are not in this repository. So the table understates the divergence by construction. The")
    out.append("arithmetic below is an ILLUSTRATION with an assumed parcel wind, not an observation, and")
    out.append("is included only to show the mechanism the structural check is pointing at:")
    out.append("")
    illustrative_parcel_wind = Decimal("95")
    ev = events[2]
    out.append(f"> Take {ev['name_international']} ({ev['name_local']}), landfall wind "
               f"{ev['msw_kmh_10min']} km/h. Assume a fisher household roughly 200 km from the landfall")
    out.append(f"> point experiences {illustrative_parcel_wind} km/h over its own location, below typhoon")
    out.append("> strength, while losing gear to storm surge and swell.")
    out.append(">")
    for p in products:
        basis = p["triggers"][0]["spatial_basis"]
        observed = Decimal(ev["msw_kmh_10min"]) if "landfall" in basis else illustrative_parcel_wind
        ratio = payout_ratio(p, observed)
        verdict = f"pays {ratio * 100:.0f}% of sum insured" if ratio else "pays nothing"
        out.append(f"> - `{p['file'].replace('.ttl','')}` settles on {observed} km/h and {verdict}.")
    out.append(">")
    out.append("> Same storm, same household, opposite outcomes, decided entirely by a field that most")
    out.append("> product documentation does not state. That is basis risk, and it is why a farmer who")
    out.append("> was not paid concludes the product is a fraud rather than that the index missed.")
    out.append("")
    out.append("## Limits of this replay")
    out.append("")
    out.append("- Four events. This is a demonstration set, not a full historical ingest. Extending to the")
    out.append("  complete IBTrACS and PAGASA record is month-one work under the FIRST Fund plan.")
    out.append("- Landfall-point wind is used as the observed value for both products, because gridded")
    out.append("  per-parcel wind fields are not in this repository. That means the divergence shown here")
    out.append("  is a *lower bound* on real spatial basis risk.")
    out.append("- Tier values in the reconstructed rice product are PAGASA class boundaries used as")
    out.append("  stand-ins. No issuer's published payout table is reproduced anywhere in this repository.")
    out.append("- No claim is made here about any named issuer's actual payout behaviour.")

    text = "\n".join(out)
    if md:
        target = ROOT / "docs" / "BASIS_RISK.md"
        target.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT)}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
