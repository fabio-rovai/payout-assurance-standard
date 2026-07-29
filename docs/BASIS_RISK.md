# Basis-risk replay, PPAS v0.1.0

Every product encoding in `products/` replayed against every observed event in
`data/ph_typhoon_landfalls.csv`. Wind figures are PAGASA ten-minute maximum sustained
winds at landfall, each row individually sourced in the CSV. Classes are computed under
PAGASA's post-March-2022 scale applied retrospectively.

## Payout share of sum insured, by product and event

| Event | Landfall wind (km/h) | ph-fisher-landfall-parametric | ph-typhoon-rice-parametric |
|---|---|---|---|
| Haiyan (Yolanda), 2013-11-08 | 235 | 100% | 100% |
| Mangkhut (Ompong), 2018-09-15 | 205 | 100% | 100% |
| Rai (Odette), 2021-12-16 | 195 | 100% | 100% |
| Doksuri (Egay), 2023-07-26 | 175 | 40% | 50% |

## Where the products disagree

- **Doksuri (Egay)** at 175 km/h: ph-fisher-landfall-parametric pays 40%, ph-typhoon-rice-parametric pays 50%.

## The finding that matters: divergence detected from the encoding, not the payout table

Read the table above carefully. On these four events the two products behave almost
identically, and the one difference is a tier ratio. That is not the interesting result,
and pretending otherwise would be the exact overclaim this standard exists to catch.

The real finding is structural, and the validator extracts it without any event data at all:

- `ph-fisher-landfall-parametric`: threshold 118 km/h >=, measured at **storm centre at landfall, national bulletin value**, settlement promise 14 days, encoding confidence *reconstructed*.
- `ph-typhoon-rice-parametric`: threshold 118 km/h >=, measured at **insured parcel, georeferenced, from remote-sensed wind field**, settlement promise 5 days, encoding confidence *reconstructed*.

Two products, the same advertised 118 km/h headline, and two different promises. One pays
on where the storm centre crossed the coast; the other on what happened over the insured
parcel. One promises settlement in 5 days, the other in 14. On any brochure or national
product register these are the same product. In the field they are not.

### Why the payout table cannot show this, and what would

This replay feeds landfall wind to both products because per-parcel gridded wind fields
are not in this repository. So the table understates the divergence by construction. The
arithmetic below is an ILLUSTRATION with an assumed parcel wind, not an observation, and
is included only to show the mechanism the structural check is pointing at:

> Take Rai (Odette), landfall wind 195 km/h. Assume a fisher household roughly 200 km from the landfall
> point experiences 95 km/h over its own location, below typhoon
> strength, while losing gear to storm surge and swell.
>
> - `ph-fisher-landfall-parametric` settles on 195 km/h and pays 100% of sum insured.
> - `ph-typhoon-rice-parametric` settles on 95 km/h and pays nothing.
>
> Same storm, same household, opposite outcomes, decided entirely by a field that most
> product documentation does not state. That is basis risk, and it is why a farmer who
> was not paid concludes the product is a fraud rather than that the index missed.

## Limits of this replay

- Four events. This is a demonstration set, not a full historical ingest. Extending to the
  complete IBTrACS and PAGASA record is month-one work under the FIRST Fund plan.
- Landfall-point wind is used as the observed value for both products, because gridded
  per-parcel wind fields are not in this repository. That means the divergence shown here
  is a *lower bound* on real spatial basis risk.
- Tier values in the reconstructed rice product are PAGASA class boundaries used as
  stand-ins. No issuer's published payout table is reproduced anywhere in this repository.
- No claim is made here about any named issuer's actual payout behaviour.
