#!/usr/bin/env python3
"""Rebuild the reviewed NRB sample and authored research protocols, offline."""
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
REF = REPO / 'skills/dharma-os/references/nepal-tech-intelligence'
sys.path.insert(0, str(REPO / 'skills/dharma-os/scripts'))
import research

SOURCE = 'NP-BIZ-NRB-PAYMENTS-BHADRA2083'
CHECKED = '2026-11-12'
# Values transcribed from NRB page 1, visually cross-checked on CHECKED.
# Columns are the five printed reference periods, not consecutive monthly observations.
PERIODS = [('2082 Ashad', 'Mid-July 2025', 'Mid Jun 2025–Mid Jul 2025', 202507),
           ('2082 Bhadra', 'Mid-Sept 2025', 'Mid Aug 2025–Mid Sept 2025', 202509),
           ('2083 Ashad', 'Mid-July 2026', 'Mid Jun 2026–Mid Jul 2026', 202607),
           ('2083 Shrawan', 'Mid-Aug 2026', 'Mid Jul 2026–Mid Aug 2026', 202608),
           ('2083 Bhadra', 'Mid-Sept 2026', 'Mid Aug 2026–Mid Sept 2026', 202609)]
SERIES = [
    ('wallet-accounts', 'Wallet accounts', 'number', 'stock', 'A4', [26765660, 24684836, 27698918, 28033039, 28150508], 'Wallet access counts reported by NRB; not unique persons or active customers.'),
    ('mobile-banking', 'Mobile banking access', 'number', 'stock', 'A9', [27741284, 28240106, 30099932, 30317575, 30473251], 'Mobile banking access counts; not unique persons or active customers.'),
    ('internet-banking', 'Internet banking access', 'number', 'stock', 'A10', [2219341, 2278262, 2498583, 2462060, 2515803], 'Internet banking access counts; not unique persons.'),
    ('atm-machines', 'ATM machines', 'number', 'stock', 'A5', [5263, 5292, 5115, 5108, 5098], 'ATM terminals at the reference point; no availability or utilization measure.'),
    ('qr-volume', 'QR-based payments', 'transactions', 'flow', 'B13 volume', [40236413, 41087808, 69589977, 72438302, 75581982], 'Monthly QR-based payment transactions as classified by NRB.'),
    ('qr-amount', 'QR-based payment amount', 'NPR million', 'flow', 'B13 amount', [113196, 101239, 189906, 164427, 167933], 'Monthly nominal QR-based payment amount; NPR million, not NPR.'),
    ('wallet-volume', 'Wallet payments', 'transactions', 'flow', 'B12 volume', [40190678, 37902235, 57040563, 53006769, 51494949], 'Monthly wallet payment transactions as classified by NRB.'),
    ('wallet-amount', 'Wallet payment amount', 'NPR million', 'flow', 'B12 amount', [48441, 43340, 58045, 48594, 49095], 'Monthly nominal wallet payment amount; NPR million, not NPR.'),
    ('card-ecommerce-volume', 'Card e-commerce', 'transactions', 'flow', 'B15 volume', [196326, 185301, 323833, 350224, 244488], 'Online payment using cards only; excludes other e-commerce payment forms.'),
    ('card-ecommerce-amount', 'Card e-commerce amount', 'NPR million', 'flow', 'B15 amount', [1466, 1578, 1951, 2302, 2485], 'Nominal online card payment amount only; not all e-commerce sales.')
]


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def evidence(locator, period, source=SOURCE, geography='Nepal national', relation='supports'):
    return dict(source_id=source, locator=locator, checked_on=CHECKED, reference_period=period,
                geography=geography, relation=relation)


def claim(key, text, kind='fact', evidence_list=None, basis=None, limitations='National descriptive evidence only; no locality or causal inference.'):
    result = dict(id=key, text=text, kind=kind, limitations=limitations)
    if evidence_list is not None:
        result['evidence'] = evidence_list
    if basis:
        result['basis'] = basis
    return result


def study(key, title, question, domains, claims, limitations, actions):
    return dict(schema_version='1.0', id=key, title=title, question=question,
                audience='Students, Nepal ICT businesses and research reviewers', domain_ids=domains,
                geography=dict(country='Nepal', level='national', name='Nepal national'),
                reference_period='Source-specific periods stated with each claim', status='desk_review',
                claims=claims, limitations=limitations, next_actions=actions)


def templates():
    return [
        dict(id='student-thesis', title='Student research protocol / विद्यार्थी अनुसन्धान', audience='Students and supervisors', domain_ids=['D02', 'D26', 'D59'],
             questions=['What is the research question and unit of analysis?', 'What gap does the literature establish?', 'Which population, sampling frame and inclusion rules apply?', 'What outcome, comparison and confounders will be measured?'],
             steps=['Define one answerable question and review owning-source literature.', 'Choose descriptive, qualitative, comparative or causal design appropriate to the question.', 'Predefine measures, sample selection, missing-data treatment and analysis before observing results.', 'Obtain institutional ethics/participant consent where required; collect minimal non-identifying data.', 'Record instruments, source editions, transformations and contradictory findings.', 'Report limitations, reproducibility steps and supervisor review.'],
             deliverables=['Research protocol and literature evidence matrix', 'Sampling and analysis plan', 'Consent/ethics requirements and anonymization plan', 'Results separated from interpretation']),
        dict(id='ict-market', title='ICT market decision / प्रविधि बजार', audience='Founders, suppliers and business students', domain_ids=['D15', 'D12', 'D18', 'D58'],
             questions=['Who experiences the problem and who pays?', 'What observed behaviour establishes need?', 'What alternatives, procurement timing and support radius constrain purchase?', 'Which price/cost assumptions are still unverified?'],
             steps=['Choose one customer segment, locality and decision.', 'Establish institution/enterprise counts with dates and definitions.', 'Use public procurement/operating records and consent-based interviews to triangulate needs.', 'Separate total institutions from eligible, reachable and currently funded buyers.', 'Build cost and support scenarios using explicitly labelled assumptions.', 'Test a small offer and record actual objections and outcomes.'],
             deliverables=['Source-backed segment brief', 'Assumptions and contradictory evidence ledger', 'Reachable-market scenario with denominators', 'Next validation action']),
        dict(id='tender-review', title='Tender evidence review / बोलपत्र समीक्षा', audience='ICT suppliers and procurement researchers', domain_ids=['D07', 'D22', 'D57'],
             questions=['Which issuing entity, notice/version and procurement method apply?', 'What are the exact deadline, timezone, security and eligibility requirements?', 'Which BOQ clauses need exact-model OEM evidence?', 'Which amendments or clarifications supersede earlier text?'],
             steps=['Retrieve the official notice, full bid document and all amendments.', 'Preserve original BS/AD dates; verify conversion and submission timezone separately.', 'Extract eligibility, financial, documentary and technical requirements by page/clause.', 'Map each requirement to the offered exact model and authoritative OEM evidence.', 'Mark unknown/partial/non-compliant items and prepare clarification questions.', 'Have the authorized human reviewer decide bid/no-bid and approve any submission.'],
             deliverables=['Clause-to-evidence compliance matrix', 'Deadline and document checklist', 'Open questions and amendment register', 'Human bid/no-bid review']),
        dict(id='school-readiness', title='Smart-classroom readiness / स्मार्ट कक्षा', audience='Schools, municipal researchers and integrators', domain_ids=['D39', 'D43', 'D37', 'D58'],
             questions=['Which teaching problem requires a change?', 'Are room, power, acoustics, connectivity and accessibility suitable?', 'What training, content rights and support are available?', 'Is there a verified funding/procurement record, or only a proposal?'],
             steps=['Identify the actual school, class, users and existing equipment.', 'Obtain institution permission before any site observation or interview.', 'Measure room, power, mounting and connectivity conditions using competent personnel.', 'Map teacher workflow, accessible content, licensing and maintenance responsibilities.', 'Check official budget and procurement stage independently from need.', 'Define acceptance tests and later usage measures before choosing equipment.'],
             deliverables=['Site-readiness and teaching-workflow checklist', 'Evidence of funding stage or explicit UNKNOWN', 'Lifecycle cost assumptions', 'Installation, training, acceptance and support plan']),
        dict(id='engineering-review', title='Engineering design review / इन्जिनियरिङ', audience='Engineers, integrators and technical students', domain_ids=['D21', 'D22', 'D28', 'D58'],
             questions=['What measurable functional and operating constraints apply?', 'Which standards, OEM versions and compatibility evidence are applicable?', 'How will failure, recovery, accessibility and maintenance be tested?', 'Who can accept the delivered system?'],
             steps=['Define requirements, environment, users and measurable acceptance criteria.', 'Compare architectures against current OEM/standards evidence and exact versions.', 'Trace power, connectivity, data, physical installation and support dependencies.', 'Document security/privacy and failure modes specific to this system.', 'Prototype or bench-test uncertain interfaces in an isolated environment.', 'Retain test results, limitations, rollback/recovery and handover responsibilities.'],
             deliverables=['Requirements-to-design-to-test traceability matrix', 'Versioned evidence and test log', 'Risk and recovery plan', 'Acceptance and maintenance record']),
        dict(id='media-verification', title='Technology news verification / समाचार जाँच', audience='Researchers, journalists and students', domain_ids=['D55', 'D56', 'D59'],
             questions=['What exact claim is being made and by whom?', 'Where and when did the event happen?', 'Is ICT substantive and is the Nepal business mechanism explicit?', 'Are multiple reports independent or syndicated?'],
             steps=['Retain original publisher, URL, title, publication/event date and attributed claim.', 'Separate registration/activity checks from evidence about this article.', 'Resolve institution/locality from primary records rather than publisher location.', 'Corroborate budget, procurement, award or deployment with the responsible owner.', 'Cluster duplicates and preserve contradictions and inaccessible sources.', 'Classify reported plan, verified event or unresolved lead with a next check.'],
             deliverables=['Claim and corroboration ledger', 'Syndication/duplicate notes', 'Technology/locality relevance decision', 'Correction and follow-up record'])
    ]


def main():
    observations = []
    for sid, indicator, unit, basis, row, values, definition in SERIES:
        for i, (bs, stock, flow, order) in enumerate(PERIODS):
            observations.append(dict(id=f'NRB-{sid}-{order}', series_id=sid, indicator=indicator,
                                     value=values[i], unit=unit, period_type=basis,
                                     reference_period=stock if basis == 'stock' else flow,
                                     period_bs=bs, period_order=order, geography='Nepal national',
                                     source_id=SOURCE, locator=f'Page 1, {row}, {bs}',
                                     checked_on=CHECKED, definition=definition,
                                     domain_ids=['D02', 'D49']))
    qr_change = (75581982 / 41087808 - 1) * 100
    amount_change = (167933 / 101239 - 1) * 100
    avg = 167933 * 1_000_000 / 75581982
    studies = [
        study('qr-growth', 'QR payments: volume growth is not customer growth',
              'How did reported monthly QR volume and nominal amount change between Bhadra 2082 and 2083?', ['D02', 'D49'], [
                  claim('Q1', 'NRB reports 41,087,808 QR transactions in Bhadra 2082 and 75,581,982 in Bhadra 2083.', evidence_list=[evidence('Page 1, B13, transaction columns for 2082 and 2083 Bhadra', 'Mid Aug–Mid Sept 2025 and Mid Aug–Mid Sept 2026')]),
                  claim('Q2', 'The corresponding nominal amounts are NPR 101,239 million and NPR 167,933 million.', evidence_list=[evidence('Page 1, B13, amount columns for 2082 and 2083 Bhadra', 'Mid Aug–Mid Sept 2025 and Mid Aug–Mid Sept 2026')]),
                  claim('Q3', f'Volume increased {qr_change:.2f}% and nominal amount {amount_change:.2f}%. Formula: (later/earlier − 1) × 100. This is descriptive year-on-year change in the printed monthly totals.', 'inference', basis=['Q1', 'Q2']),
                  claim('Q4', 'Investigate merchant workflow, settlement and support requirements in a defined segment before inferring an opportunity from these national totals.', 'recommendation', basis=['Q1', 'Q2'], limitations='No merchant sample, unique-user count, profitability or local adoption evidence is supplied.')],
              ['No causal attribution, inflation adjustment, seasonal model or forecast.', 'Five selected printed periods are not a continuous monthly series.', 'Statistics can be revised; use the named edition.'],
              ['Reproduce the comparison with the CLI.', 'Collect a consent-based local merchant sample and document its selection.', 'Seek current settlement/support evidence before a business recommendation.']),
        study('wallet-interpretation', 'Wallet access counts cannot measure unique-person adoption',
              'What can NRB wallet counts establish, and what remains unknown?', ['D02', 'D15', 'D49'], [
                  claim('W1', 'The wallet access row reports 28,150,508 at mid-Sept 2026.', evidence_list=[evidence('Page 1, A4, 2083 Bhadra', 'Mid-Sept 2026')], limitations='An access/account count; the source does not establish unique persons or activity.'),
                  claim('W2', 'The wallet usage row reports 51,494,949 monthly transactions for Bhadra 2083.', evidence_list=[evidence('Page 1, B12, transaction column, 2083 Bhadra', 'Mid Aug 2026–Mid Sept 2026')]),
                  claim('W3', 'Access counts and monthly transaction counts measure different units and time bases. Neither establishes the number of distinct active people in a municipality.', 'inference', basis=['W1', 'W2'], limitations='No deduplicated user or geographic breakdown is present.'),
                  claim('W4', 'Use a separately sourced, defined active-user measure for adoption research; preserve its population, period and deduplication method.', 'recommendation', basis=['W1', 'W2'])],
              ['No person-level data or local inference.', 'Do not divide access counts by population and label the result unique-person adoption.'],
              ['Define active user before selecting a denominator.', 'Request public aggregate methodology rather than private customer records.']),
        study('qr-ticket', 'Reproduce a national QR average transaction amount',
              'What was the aggregate mean QR amount per transaction in Bhadra 2083?', ['D02', 'D12', 'D49'], [
                  claim('A1', 'NRB B13 reports NPR 167,933 million and 75,581,982 transactions for the same monthly period.', evidence_list=[evidence('Page 1, B13, amount and transaction columns, 2083 Bhadra', 'Mid Aug 2026–Mid Sept 2026')]),
                  claim('A2', f'The aggregate mean is approximately NPR {avg:,.2f}: 167933 × 1000000 / 75581982. Convert NPR million before dividing.', 'inference', basis=['A1'], limitations='A ratio of national aggregates, not the median, a typical merchant ticket, or profitability.'),
                  claim('A3', 'Use a sector/locality-specific transaction distribution and actual fee schedule before pricing a payment service.', 'recommendation', basis=['A1', 'A2'], limitations='No merchant-specific mix, fees, costs or margins are supplied.')],
              ['The published amount is rounded in NPR million, so the derived mean is approximate.', 'The mean can conceal a skewed distribution and cannot establish a causal effect.'],
              ['Check matching period, category and unit before any ratio.', 'Collect lawful aggregate sector evidence for a local business decision.']),
        study('classroom-evidence-audit', 'Smart classrooms: what the source routes establish',
              'Do the bundled school/procurement source routes establish a funded smartboard buyer?', ['D07', 'D39', 'D43'], [
                  claim('S1', 'The bundled D39 route points to PPMO goods bidding documents, CTEVT school requirements and IEMIS. Their recorded checks concern different source roles.', evidence_list=[
                      evidence('Source registry record NP-BIZ-PPMO-GOODS; goods-document index check', 'Snapshot 2026-11-11', 'NP-BIZ-PPMO-GOODS'),
                      evidence('Source registry record eng-ctevt-school-minimums; requirements-page check', 'Snapshot 2026-11-11', 'eng-ctevt-school-minimums'),
                      evidence('Source registry record eng-iemis; search discovery with direct-page timeout', 'Snapshot 2026-11-11', 'eng-iemis')], limitations='This is an audit of bundled annotations, not a fresh validation of each linked underlying document.'),
                  claim('S2', 'These routes do not, by themselves, identify a school with an approved allocation, released funds or an active purchase.', 'inference', basis=['S1'], limitations='Absence from this sample does not prove absence of a real opportunity.'),
                  claim('S3', 'Select a real institution, verify its identity and obtain the current need, readiness, budget/procurement evidence and support plan before qualifying a lead.', 'recommendation', basis=['S1', 'S2'])],
              ['No site visit, local demand measurement, budget approval or buyer commitment.', 'IEMIS accessibility and public fields remain unresolved in the inherited source snapshot.'],
              ['Create a school-readiness study for a defined institution.', 'Attach official documents by page/clause and retain amendment versions.'])
    ]
    data = dict(schema_version='1.0', release='0.2.0', checked_on=CHECKED,
                scope='Selected national payment evidence and authored desk studies/protocols; not nationwide completed research.',
                observations=observations, studies=studies, templates=templates(),
                provenance=dict(source_id=SOURCE, downloaded_sha256='0a3257c1b116ec42eb756600cc483b93afaa1951af54bb8d6372ff74e8cbbee1',
                                extraction='Selected 10 series × 5 printed periods, manually transcribed and visually cross-checked on page 1.',
                                review='Maintainer desk review; no independent academic peer-review claim.',
                                omitted='Other NRB rows, other months, provincial/local payment statistics and private data.'))
    dump(REF / 'research-library.json', data)
    # Validate before generating user-facing reports.
    for s in studies:
        check = research.validate(s, today=__import__('datetime').date(2026, 11, 12))
        if check['errors']:
            raise ValueError(check)
        (REPO / 'docs/studies').mkdir(parents=True, exist_ok=True)
        (REPO / 'docs/studies' / (s['id'] + '.md')).write_text(research.report(s, as_of=__import__('datetime').date(2026, 11, 12)), encoding='utf-8')
    (REPO / 'data').mkdir(exist_ok=True)
    (REPO / 'data/payment-observations.csv').write_text(research.dataset_csv(), encoding='utf-8')
    registry = json.loads((REF / 'source-registry.json').read_text())
    for source in registry:
        if source['id'] == SOURCE:
            source['supported_evidence_levels'] = ['national']
            source['verification_date'] = CHECKED
            source['evidence'] = 'Selected ten series across five printed periods checked against the rendered one-page table on 2026-11-12; original periods, units and definitions retained.'
            source['extraction_status'] = '50 selected observations; not every row or a complete monthly series'
    dump(REF / 'source-registry.json', registry)
    coverage = research.read('coverage.json')
    coverage['release'] = '0.2.0'
    coverage['packaged']['statistical_observations'] = 52
    coverage['workbench'] = dict(payment_observations=50, legacy_observations=10, overlapping_observations=8,
                                 distinct_measurements=52, desk_studies=len(studies), protocols=len(data['templates']),
                                 domains_with_linked_desk_study=len({d for s in studies for d in s['domain_ids']}),
                                 observation_source_check=CHECKED, independent_academic_peer_review=False)
    coverage['organization_assessment'] = dict(scale_profiles=6, organization_types=12, requirement_areas=16, status='AUTHORED_GUIDANCE_NOT_ORGANIZATION_AUDITS')
    coverage['sector_working_packs'] = dict(packs=4, decision_workflows=24, blank_csv_templates=16, status='AUTHORED_PLAYBOOKS_NOT_COMPLETED_AUDITS')
    dump(REF / 'coverage.json', coverage)
    provenance = json.loads((REPO / 'sources/provenance.json').read_text())
    provenance['workbench'] = data['provenance']
    for item in provenance['sources']:
        if item['id'] == SOURCE:
            item['verification_date'] = CHECKED
    dump(REPO / 'sources/provenance.json', provenance)
    # One generated browser catalog; script tags escaped for safe local rendering.
    catalog = dict(data, organization_needs=research.read('organization-needs.json'), domains=research.read('domains.json'), sources=registry,
                   methods=research.read('principles-and-methods.json')['methods'], aliases=research.ALIASES,
                   coverage=coverage)
    (REPO / 'web').mkdir(exist_ok=True)
    payload = json.dumps(catalog, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    (REPO / 'web/catalog.js').write_text('/* Generated by scripts/build_library.py; do not edit. */\nwindow.DHARMA_DATA = ' + payload + ';\n', encoding='utf-8')
    out = io.StringIO(newline='')
    writer = csv.writer(out); writer.writerow(['domain_id', 'domain', 'topics', 'bundled_studies', 'observation_records', 'status'])
    for d in catalog['domains']:
        count = sum(d['id'] in s['domain_ids'] for s in studies)
        writer.writerow([d['id'], d['name'], len(d['leaves']), count,
                         sum(d['id'] in o['domain_ids'] for o in observations),
                         'SELECTED_DESK_EVIDENCE' if count else 'RESEARCH_REQUIREMENTS_ONLY'])
    (REPO / 'data/domain-coverage.csv').write_text(out.getvalue(), encoding='utf-8')
    digest = hashlib.sha256((REF / 'research-library.json').read_bytes()).hexdigest()
    print(json.dumps(dict(observations=len(observations), studies=len(studies), templates=len(data['templates']), library_sha256=digest)))


if __name__ == '__main__':
    main()
