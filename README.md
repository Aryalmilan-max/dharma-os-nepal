# Dharma OS Nepal

A portable AI-agent skill for evidence-based research into Nepal's technology-business sector.

Dharma OS connects technology with statistics, markets, management, entrepreneurship, HR, procurement, institutions, infrastructure and the external conditions affecting business in Nepal. It is a research framework and source-discovery collection. It is not a complete market database or a running media monitor.

## What is included

| Resource | Count | Meaning |
| --- | ---: | --- |
| Knowledge domains | 60 | Organized business, technical and external-environment branches |
| Core research topics | 600 | Questions to investigate, not 600 verified findings |
| Engineering specialization topics | 164 | Finer prompts; overlap with core topics is possible |
| Analytical principles and methods | 30 | Nepal applications, evidence requirements and failure modes |
| Source records | 119 | 117 distinct URLs, with individual verification limits |
| Statistical observations | 10 | Attributed NRB payment figures with periods, units and caveats |
| Checked publisher records | 37 | Historical checks; no continuous monitoring claim |

Source-check snapshot: **2026-11-11**. Public edition prepared: **2026-11-12**. Recheck current facts before consequential use.

## Explore

Python 3.10 or newer is sufficient. The helper uses only the standard library, reads bundled files, and makes no network requests.

```bash
python3 skills/dharma-os/scripts/nepal.py coverage
python3 skills/dharma-os/scripts/nepal.py find smartboard
python3 skills/dharma-os/scripts/nepal.py domain D39
python3 skills/dharma-os/scripts/nepal.py sources labour
python3 skills/dharma-os/scripts/nepal.py methods sampling
python3 skills/dharma-os/scripts/nepal.py observations
python3 skills/dharma-os/scripts/nepal.py brief --domain D39 --locality "Banganga Municipality"
```

The example brief treats its locality as an unverified research target. It does not assert a budget, tender, demand or official geographic-code match.

Start with the [knowledge-tree index](skills/dharma-os/references/nepal-tech-intelligence/INDEX.md), [methodology](skills/dharma-os/references/nepal-tech-intelligence/methodology.md), and [coverage notes](docs/coverage-and-limitations.md).

## Use as an agent skill

The portable skill is in `skills/dharma-os/`. Copy that complete folder into a skill directory supported by your agent. Check for an existing `dharma-os` skill first and preserve any private customized edition. This repository does not install or overwrite skills automatically. Host-specific discovery and execution requirements should be checked in that host's documentation.

Example request:

> Use Dharma OS to investigate smart-classroom needs in this Nepal locality. Identify the relevant institutions, official sources, procurement stage, operating constraints and evidence still missing.

Skill format and CLI behavior are checked locally; behavior in every agent product has not been certified. No accounts, browser sessions, remote tools or paid APIs are bundled.

## Data, privacy and provenance

This public edition contains authored workflow material and public-source metadata. Private company references, chats, client/employee records, credentials, local runtime configuration, private databases and bulk registration extracts are excluded.

The wider research examined locality and media registers. Those raw/extracted registers and original PDFs are not distributed here. Their research counts are explicitly separated from packaged resources. Obtain source material from the original publishers and check applicable terms before redistributing it.

See [source provenance](sources/provenance.json) and [third-party notices](THIRD_PARTY_NOTICES.md). The [MIT license](LICENSE) covers the project's original code and authored prose; it does not relicense referenced third-party publications or data.

## Develop and contribute

```bash
python3 -m unittest discover -s tests -v
```

Read [CONTRIBUTING.md](CONTRIBUTING.md). Useful contributions include source corrections, verified local evidence, better methods and clearer coverage limits. A new source or topic must not silently become a claim of nationwide coverage.
