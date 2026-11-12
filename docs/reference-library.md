# Task skills and reference library · 0.4

The repository packages **101 actual skills**: the Dharma OS router plus **100 focused task skills**. It also packages **16,884 distinct reference URLs**: **117 Nepal institutional/media references** and **16,767 international official technical references**. These are document/reference counts, not publisher counts or completed studies.

## Choose the task, not every skill

Open [the offline library](../web/library.html), search a task and open its instructions and working record. The seven families are banks (12), tech shops (12), schools (12), research (16), ICT procurement (12), engineering delivery (20) and technology-business operations (16). Each task has its own trigger, inputs, steps, CSV fields and acceptance condition. [Browse the complete list](task-skills.md).

For Codex, copy only a needed `skills/np-…` folder into your agent's skills directory. Keep the whole folder, including `assets/working-record.csv`. Restart or refresh your agent's skill discovery if needed. The root Dharma OS skill remains available separately; the task folders do not require it. This release does not install or synchronize files to a ChatGPT account. For ChatGPT, attach the selected instructions and template to your conversation or project and ask it to follow them; this is manual use, not a native skill installation.

No API key, database or paid service is needed to browse, search or export. Live research depends on the tools and permissions of the agent you use.

```bash
python3 scripts/library.py counts
python3 scripts/library.py skills restore --family engineering
python3 scripts/library.py sources --kind nepal_institutional_reference
python3 scripts/library.py sources authentication --topic identity --limit 10
python3 scripts/library.py export np-shop-repair-intake repair-intake.zip
```

Export writes one self-contained task folder to a new ZIP and refuses to overwrite an existing file. Keep client-filled templates outside the public repository.

## What a source record establishes

International references were discovered from seven selected official publisher indexes: MDN, Microsoft Learn, PostgreSQL and Kubernetes. The maintained collector selects specified English technical documentation sections, applies publisher robots rules and canonicalizes URLs. It excludes translated copies, selected older version collections and unrelated sections. The catalog includes low-level API and configuration references because they are useful when implementing the corresponding technology. It is not an endorsement of every product or a reason to deploy enterprise infrastructure at a small business.

**`PUBLISHER_INDEX_DISCOVERED_NOT_PAGE_REVIEWED` means only that the selected publisher index listed the URL.** It does not mean the page was opened, is still available, was read, is supported on a particular software version or supports a claim. Labels for these records come from URL paths, not retrieved page titles. Publisher last-modified fields are publisher metadata, not our review dates. No international record is Nepal market evidence.

The 117 Nepal references retain the earlier registry's verification state and limitations. Metadata/search checks are not promoted into content review. Duplicate canonical URLs retain their original aliases. These references do not constitute exhaustive coverage of all 753 local governments, all media or every organization. Existing selected payment statistics and four desk studies remain separate evidence collections; adding reference URLs does not create more measured findings.

A bounded availability sample is recorded separately where present. HTTP availability does not validate content, applicability or every URL in the catalog.

## Relevance and provenance

- `catalog/skill-definitions.json`: original task specifications, version and license.
- `catalog/task-reference-map.json`: curated starting points for specific tasks. Unmapped tasks explicitly have no preselected authority. Broad topic overlap is insufficient to attach a source to a task.
- `catalog/source-records.json`: unique reference metadata, conditional applicability, discovery index and verification state.
- `catalog/source-manifest.json`: counts, selection limits, publisher totals, original index byte lengths and SHA-256 hashes, and bundled data hashes.
- `scripts/collect_reference_indexes.py`: explicit bounded refresh; not a deployed crawler or monitor.
- `scripts/build_skill_library.py`: deterministic offline generation of skills, templates, navigation and web data.

The metadata snapshot was recorded on 2026-11-12. Cached index provenance does not claim a new retrieval date. The packaged hashes identify bytes; they do not prove publisher authenticity or content correctness. Original index files remain outside the release. To independently refresh, run the collector with a new cache directory, review the changed records and regenerate the skill library. CI uses bundled data and does not crawl publishers.

```bash
python3 scripts/collect_reference_indexes.py --cache-dir /tmp/dharma-reference-cache --refresh
python3 scripts/build_skill_library.py
python3 -m unittest discover -s tests -v
```

The new task workflows and navigation code are original MIT-licensed work. Underlying external documents retain their publishers' rights; no article or manual bodies are redistributed. Sources are references, not copied knowledge or a promise of complete Nepal coverage. Contribution proposals should demonstrate a distinct Nepal technology task and concrete artifact; arbitrary topic splitting and duplicate URLs do not count.
