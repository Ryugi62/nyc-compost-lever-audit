# Pre-registration — clean-placebo difference-in-differences (written before any result of this test)

Written 2026-11-26 (KST), committed and pushed to this public repository **before** `audit/run_did_placebo.py` is run.
The push time on GitHub is the timestamp.

## Question
Did community districts that received more organics (compost) violations after fines resumed in April 2026
gain more household compost tonnage than their own pre-existing trend would predict?

## Why this test
An earlier simple comparison (59 districts, 2026-04..09 vs 2025-04..09) gave a negative slope (-0.65% per
1 violation / 1,000 units). A red-team check then found the same negative slope in a window with no fines at all
(2023 -> 2024, 21 districts: -1.03%, p 0.012). So the simple comparison mostly reflects *where* enforcement was
sent (targeting bias), not what fines did. This test removes each district's own pre-trend.

**Already known before this test (disclosed):** the 59-district post slope (-0.65%) and the 21-district
pre-trend slope (-1.03%). A naive difference across *different* samples suggested about +0.4%.
The post slope on the 21-district sample and the DiD itself have not been computed.

## Data (NYC Open Data, cached 2026-11-25, in `data/`)
- DSNY monthly tonnage by community district (`ebb7-mvp5`), field `resorganicstons`.
- OATH organics violations aggregated to borough-block-month (`jz4z-kudi`), no names or addresses.
- PLUTO block -> community district and residential units (`64uk-42ks`).

## Design
- Sample: districts with household compost tonnage > 0 in every month 2023-04..09, units > 0, data through 2026-09 (expected 21).
- Treatment intensity x: 2026-04..09 organics violations per 1,000 residential units.
- Outcome: d = [ln mean(2026-04..09) - ln mean(2025-04..09)] - [ln mean(2024-04..09) - ln mean(2023-04..09)].
- Estimator: within-borough centering of x and d, OLS slope beta_DiD.
- Inference: 10,000 permutations shuffling x inside borough, two-sided, seed 20261126.
- Robustness (pre-specified): same DiD with May..Sep windows (drops the April 2025 fine spike).
- Alternative specification (reported, not in the decision line): organics share of total residential tonnage.

## Decision line
- **PASS**: beta_DiD > 0 and p < 0.05 and the May..Sep beta_DiD > 0.
- **WEAK**: beta_DiD > 0 but the PASS line is not met.
- **NULL_OR_NEGATIVE**: beta_DiD <= 0.

## Forecast (before running)
PASS 25% · WEAK 40% · NULL_OR_NEGATIVE 35%.

## Known limits
21 districts, 14 of them in Queens (low power; one Bronx district has no within-borough contrast).
2023 was an early program year in several districts, so the pre-trend may include ramp-up.
District-level observational data: a null result means "not visible in this data", not "no effect".
