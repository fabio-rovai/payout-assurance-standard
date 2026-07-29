# Build report

An honest account of how this repository was produced: what was fetched, what was computed, what
was reconstructed, and what could not be obtained. If you are deciding whether to trust anything
here, read this file before the README.

The standard's own first rule is that an encoding without stated provenance is an assertion rather
than a certification. That obligation applies to the repository itself.

## What was fetched, and from where

| Item | Source | Status |
|---|---|---|
| PAGASA tropical cyclone classification (post-March-2022 scale) | PAGASA public learning-tools page on Tropical Cyclone Wind Signal | Fetched, used for class boundaries and as the stand-in tier thresholds |
| Mangkhut (Ompong) landfall wind, 205 km/h | PAGASA tropical cyclone summary PDF, `pubfiles.pagasa.dost.gov.ph/tamss/weather/tc_summary/TY_Ompong_MANGKHUT_2018.pdf` | Fetched. **Primary source** |
| Haiyan (Yolanda) landfall wind, 235 km/h | Wikipedia, quoting PAGASA | Secondary. Marked `secondary` in the CSV |
| Rai (Odette) landfall wind, 195 km/h | Rappler, reporting the PAGASA bulletin of 16 Dec 2021 | Secondary |
| Doksuri (Egay) landfall wind, 175 km/h | Rappler, reporting the PAGASA bulletin of 26 Jul 2023 | Secondary |
| Nalgae (Paeng) landfall wind, 110 km/h | JMA ten-minute value as reported; landfall at Virac, Catanduanes, 29 Oct 2022 | Secondary, and a **different agency** from the other four. Marked in the `agency` column |
| Nalgae casualties and agricultural loss | OCHA flash update (31 Oct 2022) and Philippine Department of Agriculture figures reported alongside it: 101 dead, over 2 million affected, roughly 67,000 tonnes and about PHP 1.3 billion in agricultural losses, bulk in rice | Fetched |
| PCIC parametric pilot for rice, structural facts | Philippine Department of Agriculture, "PCIC launches parametric insurance to expedite claims payouts", 17 July 2025, fetched directly | Fetched. Names **PhilSA and PhilRice**. See correction below |
| Fisher parametric product, terms and funders | Willis (WTW) and Rare press releases and ORRAA project materials, 12 November 2025 | Fetched |

## What could NOT be obtained

- **PAGASA per-storm summary PDFs for 2013, 2021, 2022 and 2023.** The public archive at
  `pubfiles.pagasa.dost.gov.ph/tamss/weather/tc_summary/` was enumerated directly. It carries annual
  reports for 2017 to 2020 and individual storm summaries for 2018 only. This is why four of five
  events rest on secondary sourcing, and why "primary sourcing for every event" is a roadmap item
  rather than an afternoon's work.
- **Any issuer's published payout table.** Trigger thresholds, tier boundaries and payout ratios for
  real Philippine parametric products are not in the public domain. Everything in `products/` is
  therefore labelled `ppas:encodingConfidence "reconstructed"`, and the tier values are PAGASA class
  boundaries used as stand-ins. No issuer's terms are reproduced anywhere in this repository.
- **Gridded per-parcel wind fields.** Without them the replay must feed landfall wind to every
  product regardless of the product's declared spatial basis, which means the payout table
  *understates* spatial basis risk by construction. This is stated in `docs/BASIS_RISK.md` at the
  point where a reader might otherwise over-read the result.
- **Any real payout ledger or register.** Every file in `examples/` is synthetic. No beneficiary
  data, real or derived, is present in this repository.
- **Any field evidence about behaviour.** The standard shows that a promise can be encoded and
  checked. It shows nothing about whether a household that is shown a certified card behaves
  differently. That question needs fieldwork and is unanswered here.

## What was computed rather than asserted

- The payout outcome for each of the 5 events against each of the 2 encoded products, in
  `src/replay.py`, from the declared trigger comparator and the sorted tier table.
- The documented false negative: Nalgae at 110 km/h against a 118 km/h trigger, an 8 km/h shortfall,
  reported alongside the documented agricultural loss for the same storm. This is arithmetic over
  sourced inputs, not an estimate.
- The structural divergence between the two encoded products, extracted from the encodings alone
  with no event data involved: same 118 km/h headline, different spatial basis, different settlement
  window.
- All twelve rule outcomes, by `pyshacl`, over the ontology plus the file under test.

## A correction made during the build

An earlier version of this repository stated that the PCIC parametric pilot was developed "with
PAGASA, PhilRice and IRRI", and described it as launched. Both were wrong, and both were caught by
adversarial review before anyone else read them:

- The Department of Agriculture announcement names the **Philippine Space Agency (PhilSA)** and the
  Philippine Rice Research Institute. It does not name PAGASA, and it does not name IRRI. The error
  came from conflating that announcement with a separate satellite-based crop insurance and
  agro-advisory programme involving IRRI. PhilSA and PAGASA are a space agency and a weather bureau,
  which is not a trivial slip in a document whose method depends on knowing which authority measures
  an index.
- It is a **pilot being readied**, not a launched product, and the three-to-five-day settlement
  figure is a design target rather than demonstrated performance.

Both are fixed. The commit history preserves the error rather than hiding it, because a standard
about verifiability should be checkable on its own record.

## Reproducing everything here

```bash
python3 -m pip install rdflib pyshacl
python3 tests/test_rules.py                                       # all twelve rules, positive and negative
python3 src/validate.py "products/*.ttl" "examples/ledger-*.ttl"
python3 src/validate.py --payability "examples/register-*.ttl"
python3 src/replay.py --markdown                                  # regenerates docs/BASIS_RISK.md
```

Every number in `docs/BASIS_RISK.md` is regenerated by that last command from
`data/ph_typhoon_landfalls.csv` and the files in `products/`. Nothing in it is hand-written.

## Standing invitation

The most useful contribution anyone can make to this repository is an official product wording, so
that a `reconstructed` encoding can become an `official` one. The second most useful is telling us
where the vocabulary fails to describe a product you actually run.

Fabio Rovai, fabio@thetesseractacademy.com
