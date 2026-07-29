# Parametric Payout Assurance Standard (PPAS)

**An open standard for checking, by machine, whether a parametric climate insurance product
actually paid what it promised to the people it promised.**

Version 0.2.1. Standard CC BY 4.0, tooling Apache-2.0. Built by
[The Tesseract Academy](https://gov.tesseract.academy/) (Kampakis and Co Ltd).

---

## Why this exists

Southeast Asia is betting on parametric cover, and the Philippines is where the bet is being
placed first.

In November 2025 the Bureau of Fisheries and Aquatic Resources became policyholder for the
country's first parametric cover for small-scale fishers, with the Philippine Crop Insurance
Corporation, Rare and Willis (a WTW business), developed through the Ocean Risk and Resilience
Action Alliance with funding from the Government of Canada and the UK Government's Blue Planet
Fund. It reaches 14,200 fishers across 24 coastal municipalities, pays up to USD 100 per policy
cycle, and is offered as a benefit of fisher registration. Separately, on 17 July 2025 the
Department of Agriculture announced that PCIC is readying a parametric typhoon pilot for rice
farmers with the Philippine Space Agency and the Philippine Rice Research Institute, settling on
remote-sensed wind velocity and georeferenced farm data, targeting computation of compensation
within three to five days.

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

**And it fails earlier than either of those.** Where cover is premium-subsidised or donor-paid
and enrolled in bulk from a public register, the household often makes no purchase decision and
sometimes does not know it is covered. What decides whether they are actually paid is register
integrity: name spelled correctly, right barangay, a georeferenced parcel or registered gear, and
a live payout instrument in a matching name. A misspelling or a dormant cash card defeats a
perfectly designed trigger. Because the Philippine fisher product ties cover to registration, the
register is not administrative background. It is the enrolment mechanism.

## What PPAS does

PPAS is a vocabulary plus two sets of validation rules covering all three failure points.

1. **Pre-event payability (P1 to P4).** Run the rules over a register and a payout file and get a
   list of which registered households could not currently be paid, and why. Every finding is
   fixable while there is still time to fix it.
2. **It certifies the promise (R1 to R4).** Encode a product's trigger, index, data source, payout
   tiers, settlement window and exclusions, then replay that logic against observed events.
3. **It verifies the delivery (R5 to R8).** A shared payout record schema reconciles the
   fragmented last mile: trigger fired, who was entitled, what was disbursed, through which
   channel, confirmed received.

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
| P1 | The unreconcilable register entry: no register id, name, barangay, municipality or linked product |
| P2 | **No georeference, so a trigger settled on the insured location cannot be evaluated for this household at all** |
| P3 | **Nowhere for the money to land: no payout instrument, or a dormant or closed one** |
| P4 | The unexplained name mismatch between the instrument and the register, which is what fails at the counter |

R6 and R7 encode the last-mile settlement findings. P1 to P4 encode the pre-event failures, and
they are the ones worth running first, because a payability report is a to-do list rather than a
post-mortem. An honest "we do not know whether this cheque was banked" is a conformant PPAS
record, and so is a declared legitimate name mismatch such as a married name. Silence is not.

## Run it

Requires Python 3.9 or later with `rdflib` and `pyshacl`.

```bash
python3 src/validate.py "products/*.ttl" "examples/ledger-*.ttl"  # certify encodings and ledgers
python3 src/validate.py --payability "examples/register-*.ttl"    # pre-event payability audit
python3 src/replay.py                                             # basis-risk replay
python3 src/replay.py --markdown                                  # regenerate docs/BASIS_RISK.md
python3 tests/test_rules.py                                       # assert the rules do real work
```

Current state of this repository, which is what `tests/test_rules.py` asserts:

```
ok   product ph-typhoon-rice-parametric.ttl conforms
ok   product ph-fisher-landfall-parametric.ttl conforms
ok   ledger-clean.ttl conforms
ok   ledger-broken.ttl fails on ['R6', 'R7', 'R8'] as designed
ok   product-broken.ttl fails on ['R1', 'R2', 'R3', 'R4', 'R5', 'R6'] as designed
ok   register-clean.ttl conforms (including a declared legitimate name mismatch)
ok   register-broken.ttl fails on ['P1', 'P2', 'P3', 'P4'] as designed
```

Every one of the twelve rules has a case built to trip it. A rule that is only ever asserted to
pass on well-formed input is decoration, so `examples/product-broken.ttl` is a brochure-grade
encoding ("cover against typhoons") that nothing could ever settle or dispute.

The most useful single output is the documented false negative in
[`docs/BASIS_RISK.md`](docs/BASIS_RISK.md): Severe Tropical Storm Nalgae (Paeng), October 2022,
came ashore at 110 km/h, 8 km/h short of a 118 km/h typhoon trigger. It killed over a hundred
people, affected more than two million, and destroyed roughly 67,000 tonnes of mostly rice, worth
about PHP 1.3 billion. Both encoded products pay nothing. A farmer who lost a field to Nalgae and
received nothing did not experience an index limitation. They experienced a broken promise.

## What is real here and what is not

This section matters more than the rest of the README. A certification standard that overstates
its own evidence is worthless.

**Real.** The vocabulary, the twelve validation rules (R1 to R8 and P1 to P4), the validator, the
replay engine, and the tests, which assert that every one of the twelve fires on a case built to
trip it. The five historical events in `data/ph_typhoon_landfalls.csv` are real, with landfall
wind, the measuring agency, and a source URL on every row. The facts above about the fisher product
and the PCIC pilot are taken from the Willis, Rare and Department of Agriculture announcements, and
the partner institutions are named as those sources name them.

**Weakly sourced, and now labelled per row.** Only one of the five events (Mangkhut) cites a PAGASA
primary document. The others rest on reputable secondary reporting of PAGASA bulletins, and one row
(Haiyan) cites Wikipedia. A standard that says overstating your own evidence is worthless cannot
quietly cite an encyclopedia for a landfall wind speed, so `data/ph_typhoon_landfalls.csv` now
carries a `source_type` column marking each row primary or secondary. PAGASA's public archive does
not currently publish per-storm summaries for 2013, 2021, 2022 or 2023, so replacing these with
primary values is real work rather than a search, and it is tracked in the roadmap. Nalgae's figure
is the JMA ten-minute value, not PAGASA, and the `agency` column says so.

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
whether it improves what households understand about their own cover requires fieldwork, which is the step
we are seeking to fund.

## Roadmap

- **v0.3** Primary PAGASA sourcing for every event, replacing the secondary rows; full historical ingest; a payability audit on a real register; two products certified with the issuer in the room, replacing reconstructed tiers with official terms.
- **v0.4** Generated beneficiary-facing payout cards in Filipino and Cebuano, produced
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
