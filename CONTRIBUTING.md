# Contributing

Keep contributions focused on Nepal technology-business decisions and evidence quality.

- For a source, include its publisher, exact URL, geographic scope, reference period where relevant, check date, verification method and limitations. An HTTP response is not a content audit.
- For a numerical observation, preserve original units, stock/flow basis, time period, geography, table/page and caveats. Explain transformations.
- For a topic or method, distinguish research requirements and analytical guidance from measured findings.
- For a news signal, establish a Nepal technology connection and separate reported claims from official confirmation. Cluster syndicated stories.
- Use institutional/public information only. Do not submit private chats, credentials, personal contact lists, employee/client files, internal system paths or confidential business records.
- Preserve attribution and verify redistribution rights for any added third-party content. Prefer links and original annotations when rights are unclear.
- Update coverage counts when packaged resources change. Do not count unbundled or unreviewed material as verified coverage.

Run `python3 -m unittest discover -s tests -v` before proposing changes. Include what changed, how it was checked and any unresolved gaps. Do not add a live crawler or recurring job as an incidental documentation change.

For study/data changes, read the [study format and workbench guide](skills/dharma-os/references/nepal-tech-intelligence/workbench.md). Add sources before citing their IDs. Preserve facts, inferences, hypotheses and recommendations separately, including contradictions and incomplete local evidence. Do not attach national-only NRB measurements to a local geography by relabelling the evidence.

`scripts/build_library.py` maintains the selected NRB transcription and authored protocols/studies. Update its reviewed inputs rather than editing generated JSON/CSV/Markdown/catalog copies. Revisit the original source before changing a check date, record its checksum/locator, explain revisions, and regenerate. The builder makes no network requests and cannot refresh evidence by itself.

For browser changes run `node --check web/app.js` and `node tests/browser_core.cjs` with Node.js 20+. Open `web/index.html` and exercise the changed user flow. Browser and Python checks should preserve the same important evidence states. Exported reports must retain material review warnings. CI regenerates the library and rejects committed/generated drift.

Use the study contribution issue form for a scoped new case. A passed structural checker or AI-agent evaluation must not be presented as academic peer review, legal compliance, field validation or a verified customer outcome.
