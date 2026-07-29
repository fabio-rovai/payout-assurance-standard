# Parametric Payout Assurance Standard (PPAS)

**An open standard for checking, by machine, whether a parametric climate insurance product
actually paid what it promised to the people it promised.**

Version 0.1.0. Licensed CC BY 4.0. Built by
[The Tesseract Academy](https://gov.tesseract.academy/) (Kampakis and Co Ltd).

---

## Why this exists

Southeast Asia is betting on parametric cover. The Philippine Crop Insurance Corporation
launched a parametric typhoon product for rice farmers in July 2025, settling on remote-sensed
wind velocity and georeferenced farm data with payment targeted in three to five days, built
with PAGASA, PhilRice and IRRI. A world-first parametric product for small-scale fishers has
been launched in the same market.

A parametric product only changes behaviour if the farmer or fisher believes it will pay. Two
failures break that belief, and neither is visible in the systems that exist today.

**Basis risk.** The trigger does not fire when the loss is real. Two products can advertise the
same headline threshold and pay on completely different sets of storms, purely because one
settles on wind at the storm centre at landfall and the other on wind over the insured parcel.
Most product documentation does not state which.

**Delivery opacity.** The payout is owed, but nobody can show it arrived. Field research on
Philippine last-mile climate insurance payouts found money moving through mobile wallets,
remittance agents and cheques with no consistent way to verify whether payments were received,
and friction at exactly the moment a household is most exposed.

The result is that the promise is unverifiable at the moment it matters most. Capital is not the
binding constraint on adaptation finance at the last mile. Verifiability is.

## What PPAS does

PPAS is a vocabulary plus a set of validation rules that make the promise and the delivery
checkable as one object.

1. **It certifies the promise.** Encode a product's trigger, index, data source, payout tiers,
   settlement window and exclusions, then replay that logic against observed historical events.
2. **It verifies the delivery.** A shared payout record schema reconciles the fragmented last
   mile: trigger fired, who was entitled, what was disbursed, through which channel, confirmed
   received.

It runs on records the insurer, public insurer, cooperative or wallet provider already holds. It
requires no new app, no smartphone and no KYC document from the beneficiary, because
beneficiaries are modelled as pseudonymous identifiers. The people most exposed to climate risk
are frequently the people without documentation, so needing documentation to verify their payout
would defeat the purpose.

## The rules, and the failure each one catches

| Rule | Catches |
|---|---|
| R1 | The unspecifiable promise: a product with no testable trigger, no source documentation, or no stated settlement speed |
| R2 | The untraceable trigger: a threshold with no measuring authority, no unit, or an implicit comparator |
| R3 | The incomparable index: no stated measurement basis, or no stated spatial basis. This is the principal basis-risk disclosure |
| R4 | The ambiguous payout: a tier with no threshold or a ratio outside 0 to 1 |
| R5 | The orphan entitlement: an amount owed with no event, product or beneficiary behind it |
| R6 | **The entitlement that vanished: owed, never disbursed, invisible in every existing system** |
| R7 | **The unverified payment: paid into a channel with no receipt confirmation and no stated reason why receipt is unknown** |
| R8 | Short payment: less disbursed than owed |

R6 and R7 are the rules that encode the last-mile findings directly. An honest "we do not know
whether this cheque was banked" is a conformant PPAS record. Silence is not.

## Run it

Requires Python 3.9 or later with `rdflib` and `pyshacl`.

```bash
python3 src/validate.py "products/*.ttl" "examples/*.ttl"   # certify encodings and ledgers
python3 src/replay.py                                        # basis-risk replay
python3 src/replay.py --markdown                             # regenerate docs/BASIS_RISK.md
python3 tests/test_rules.py                                  # assert the rules do real work
```

Current state of this repository:

```
[PASS] products/ph-fisher-landfall-parametric.ttl
[PASS] products/ph-typhoon-rice-parametric.ttl
[FAIL] examples/ledger-broken.ttl     <- fails on R6, R7, R8, by design
[PASS] examples/ledger-clean.ttl
```

## What is real here and what is not

This section matters more than the rest of the README. A certification standard that overstates
its own evidence is worthless.

**Real.** The vocabulary, the eight validation rules, the validator, the replay engine, and the
test that proves the rules fire on the failures they target. The four historical typhoon events
in `data/ph_typhoon_landfalls.csv` are real, with PAGASA ten-minute maximum sustained winds at
landfall and a source URL on every row.

**Reconstructed, and labelled as such.** The encoded products carry
`ppas:encodingConfidence "reconstructed"`. Structural facts about the Philippine rice product are
taken from public announcements. **Tier thresholds and payout ratios are not published by any
issuer and are stand-ins drawn from PAGASA class boundaries.** No issuer's payout table is
reproduced in this repository, and no claim is made about any named issuer's actual payout
behaviour. Replacing stand-ins with official terms needs an issuer relationship, not a desk.

**Synthetic.** Every payout ledger in `examples/`. They demonstrate the shape of a conformant and
a non-conformant ledger. No real beneficiary data is present anywhere in this repository.

**Not yet done.** A full IBTrACS and PAGASA historical ingest. Gridded per-parcel wind fields,
without which the replay understates spatial basis risk by construction. Any field evidence that
certified transparency changes what farmers and fishers actually do. That last one is the point:
the standard proves the logic is encodable, and proves nothing about behaviour. Establishing
whether it moves enrolment intent requires fieldwork with farmers and fishers, which is the step
we are seeking to fund.

## Roadmap

- **v0.2** Full historical ingest; six to eight products certified; published basis-risk league table.
- **v0.3** Generated beneficiary-facing payout cards in Tagalog, Cebuano and Vietnamese, produced
  from the certified logic rather than written by hand, so the document and the contract cannot drift apart.
- **v1.0** Frozen vocabulary, packaged validator, one live reconciliation against real disbursement
  records, and published field results including negative ones.

## Citing and contributing

Issues and pull requests welcome, particularly from insurers, public insurers, cooperatives and
regulators who can tell us where the vocabulary fails to describe their actual products. If you
hold official product terms and want them encoded properly, that is the most useful contribution
available.

Contact: Fabio Rovai, fabio@thetesseractacademy.com

## Sources

- Philippine Department of Agriculture, PCIC parametric insurance launch, July 2025.
- PAGASA, Tropical Cyclone Wind Signal reference and the post-March-2022 classification scale.
- Per-event source URLs in `data/ph_typhoon_landfalls.csv`.
- Peer-reviewed index-insurance literature on basis risk, trust and uptake, including evidence
  that farmers taught how their trigger works become more likely to purchase.
