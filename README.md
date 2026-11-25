# NYC compost lever audit

Pre-registered tests of whether New York City's compost levers (fines, repeat enforcement, school collection)
move household compost tonnage, using NYC Open Data only.

- `prereg/` — each test's design and decision line, committed before the test is run.
- `audit/core.py` — pure estimation functions; `audit/run_did_placebo.py` — data loading and output.
- `results/` — outputs, committed after the run.

Run tests: `python3 -m unittest discover -s tests -t .` · Run: `python3 -m audit.run_did_placebo data`

Data: NYC Open Data (DSNY monthly tonnage, OATH hearings aggregated to block-month, PLUTO). Provided as is, no warranty.
