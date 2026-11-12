# Start with a Nepal research question

These examples use the bundled snapshot. They do not browse live sources, validate a municipality code or assert a sales opportunity.

## Smart classrooms

```bash
python3 skills/dharma-os/scripts/nepal.py domain D39
python3 skills/dharma-os/scripts/nepal.py brief --domain D39 --locality "Banganga Municipality"
```

The domain covers interactive displays, projectors, acoustics, conferencing, teaching workflow, accessibility, installation, training, licensing and acceptance. Its candidate source IDs include `eng-iemis`, `eng-ctevt-school-minimums` and `NP-BIZ-PPMO-GOODS`.

The brief explicitly returns `RESEARCH_BRIEF_NOT_A_MARKET_FINDING` and `NOT_VERIFIED` for locality validation. Continue by checking the institution, current official sources, actual need, budget/procurement stage, room readiness and support requirements.

## HR and technical capacity

```bash
python3 skills/dharma-os/scripts/nepal.py domain D23
python3 skills/dharma-os/scripts/nepal.py domain D24
python3 skills/dharma-os/scripts/nepal.py sources labour
```

Separate the capability question from the employment-law question. Recheck current legal instruments and source availability before treating an employment policy as compliant.

## Payment figures and denominators

```bash
python3 skills/dharma-os/scripts/nepal.py observations
python3 skills/dharma-os/scripts/nepal.py methods denominator
```

The statistical sample retains Nepal Rastra Bank's periods and caveats. Wallet/account counts are not unique people; card e-commerce is not all e-commerce. National observations are not local-government estimates.

## Ask your agent

> Use Dharma OS to investigate this Nepal technology-business question. Select the relevant domain, establish the geography and period, retrieve the current owning sources, distinguish findings from assumptions, and list the evidence still missing.

The host must supply any live-search capability. See the coverage notes before interpreting source or topic counts.
