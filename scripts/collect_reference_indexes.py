#!/usr/bin/env python3
"""Build a bounded primary-reference catalog from publisher indexes and local metadata.

Network access occurs only when explicitly running this collector with an empty
cache or --refresh. It is not a crawler, monitor, content audit or model training.
"""
import argparse
from collections import Counter
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit, unquote
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]
AGENT = 'DharmaOSResearch'
INDEXES = [
    ('Mozilla Contributors / MDN', 'https://developer.mozilla.org/sitemaps/en-us/sitemap.xml.gz'),
    ('Microsoft Learn', 'https://learn.microsoft.com/_sitemaps/entra_en-us_1.xml'),
    ('Microsoft Learn', 'https://learn.microsoft.com/_sitemaps/windows-server_en-us_1.xml'),
    ('Microsoft Learn', 'https://learn.microsoft.com/_sitemaps/security_en-us_1.xml'),
    ('Microsoft Learn', 'https://learn.microsoft.com/_sitemaps/azure_en-us_1.xml'),
    ('PostgreSQL Global Development Group', 'https://www.postgresql.org/sitemap.xml'),
    ('Kubernetes project', 'https://kubernetes.io/en/sitemap.xml'),
]
MDN_CORE_API = re.compile(r'^/en-US/docs/Web/API/(Abort|Attr|Blob|Cache|Cookie|Credential|Crypto|CustomEvent|DOM|Document|Element|Event|Fetch|File|FormData|Headers|History|HTML|IDB|IntersectionObserver|Location|MediaDevices|MediaStream|Message|MutationObserver|Navigator|Node|Performance|Permissions|Push|ReadableStream|Request|Response|Screen|Selection|ServiceWorker|Storage|SubtleCrypto|Text|URL|ValidityState|WebSocket|Window|Worker|XMLHttpRequest)')
EXCLUDE = re.compile(r'/(previous-versions|retired|deprecated|obsolete|releases|blog|community|events|training|answers|contribute|_static|_images|experiments)(/|$)|/(2003|2008|2012)(/|$)|[-/]deprecated[-/]', re.I)


def canonical(url):
    u = urlsplit(url)
    if u.scheme not in ('https', 'http') or not u.hostname or u.username is not None or u.password is not None:
        raise ValueError('Non-public-reference URL')
    path = u.path.rstrip('/') or '/'
    return urlunsplit((u.scheme.lower(), u.netloc.lower(), path, '', ''))


def topics_for(url):
    """Explicit section selection. No news, product marketing or translated copies."""
    u = urlsplit(url); p = u.path; lower = p.lower()
    if EXCLUDE.search(p):
        return []
    if u.hostname == 'developer.mozilla.org':
        if not (re.match(r'^/en-US/docs/Web/(Accessibility|CSS|HTML|HTTP|JavaScript|Security|Privacy|Performance|Progressive_web_apps|URI)(/|$)', p) or MDN_CORE_API.match(p)):
            return []
        result = ['web']
        if any(x in lower for x in ('security', 'privacy', 'credential', 'crypto', 'permission')):
            result += ['security', 'identity']
        if 'performance' in lower:
            result += ['performance']
        return result
    if u.hostname == 'learn.microsoft.com':
        if not p.startswith('/en-us/'):
            return []
        if re.match(r'^/en-us/entra/(identity|id-governance|architecture|fundamentals|standards|id-protection|backup)(/|$)', p):
            return ['identity', 'security']
        if p.startswith('/en-us/windows-server/'):
            return ['endpoint', 'operations', 'network']
        if p.startswith('/en-us/security/') and not any(x in lower for x in ('agentic', 'copilot', 'preview')):
            return ['security']
        if p.startswith('/en-us/azure/azure-sql/'):
            return ['data', 'cloud']
        if re.match(r'^/en-us/azure/(virtual-machines|virtual-desktop|container-instances|devops)(/|$)', p) and not any(x in lower for x in ('/sizes/', '/pricing', '/whats-new', '/troubleshoot/')):
            return ['cloud', 'architecture', 'operations']
        return []
    if u.hostname == 'www.postgresql.org' and p.startswith('/docs/current/') and p.endswith('.html') and not any(x in lower for x in ('release-', '/index', '/bookindex')):
        return ['data', 'continuity']
    if u.hostname == 'kubernetes.io' and p.startswith('/docs/') and not any(x in lower for x in ('/generated/', '/reference/kubectl/generated/')):
        return ['architecture', 'operations', 'continuity']
    return []


def fetch(url, cache, refresh):
    name = url.split('//', 1)[1].replace('/', '_')
    path = cache / name
    if path.exists() and not refresh:
        raw = path.read_bytes()
        # Inspection caches use the same bytes but do not imply today's fetch.
        return raw, 'cached_index_snapshot', None
    with urlopen(Request(url, headers={'User-Agent': AGENT + '/0.4 (public documentation metadata)'}), timeout=25) as response:
        raw = response.read(64_000_001)
        if len(raw) > 64_000_000:
            raise ValueError('Index exceeds the bounded 64 MB download limit')
    path.write_bytes(raw)
    return raw, 'publisher_index_retrieved', date.today().isoformat()


def label(url):
    # This is an original navigation label, never represented as the page's title.
    tail = urlsplit(url).path.rsplit('/', 1)[-1]
    return unquote(tail).removesuffix('.html').replace('-', ' ').replace('_', ' ') or 'Documentation section'


def nepal_topics(s):
    value = (s['id'] + ' ' + s.get('title', '')).lower()
    topics = ['nepal-reference']
    if any(x in value for x in ('nrb', 'payment', 'cyber')): topics += ['nepal-bank', 'governance', 'security']
    if any(x in value for x in ('ppmo', 'procurement', 'budget', 'fcgo')): topics += ['procurement']
    if any(x in value for x in ('ird', 'tariff', 'customs', 'trade', 'consumer')): topics += ['commercial', 'inventory']
    if any(x in value for x in ('ctevt', 'iemis', 'education', 'school')): topics += ['education']
    if any(x in value for x in ('nso', 'census', 'curriculum', 'nast')): topics += ['research', 'business']
    if any(x in value for x in ('labour', 'enterprise', 'moics', 'iids', 'ocr')): topics += ['business', 'governance']
    if any(x in value for x in ('electrical', 'solar', 'nea', 'nbsm')): topics += ['power']
    if 'nta' in value: topics += ['network']
    return sorted(set(topics))


def build(cache, refresh=False):
    cache.mkdir(parents=True, exist_ok=True)
    records, snapshots, rejected = {}, [], Counter()
    roots = {}
    for _, url in INDEXES:
        u = urlsplit(url); roots[u.scheme + '://' + u.netloc] = None
    for root in roots:
        url = root + '/robots.txt'
        old = cache / (urlsplit(root).hostname + '.robots.txt')
        if old.exists() and not refresh:
            raw = old.read_bytes(); method = 'cached_robots_snapshot'; retrieved = None
        else:
            raw, method, retrieved = fetch(url, cache, refresh)
        robot = RobotFileParser(); robot.parse(raw.decode('utf-8').splitlines()); roots[root] = robot
        snapshots.append(dict(url=url, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), method=method, retrieved_on=retrieved))
    for publisher, index in INDEXES:
        u = urlsplit(index); robot = roots[u.scheme + '://' + u.netloc]
        if not robot.can_fetch(AGENT, index):
            raise ValueError('Index disallowed by publisher robots: ' + index)
        raw, method, retrieved = fetch(index, cache, refresh)
        content = gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw
        if len(content) > 100_000_000:
            raise ValueError('Expanded index exceeds 100 MB')
        tree = ET.fromstring(content)
        if tree.tag.rsplit('}', 1)[-1] != 'urlset':
            raise ValueError('Expected a selected document urlset, not a sitemap index')
        count, retained = 0, 0
        index_id = 'INDEX-' + hashlib.sha256(index.encode()).hexdigest()[:16]
        for item in tree:
            values = {x.tag.rsplit('}', 1)[-1]: x.text for x in item}
            source = values.get('loc')
            if not source:
                continue
            count += 1
            try:
                url = canonical(source)
            except ValueError:
                rejected['invalid_url'] += 1; continue
            if urlsplit(url).hostname != u.hostname:
                rejected['unexpected_host'] += 1; continue
            topics = topics_for(url)
            if not topics:
                rejected['outside_selected_sections'] += 1; continue
            if not robot.can_fetch(AGENT, url):
                rejected['robots_disallowed'] += 1; continue
            if url in records:
                rejected['duplicate_canonical_url'] += 1; continue
            condition = 'Use only for the browser/web technology actually selected for the Nepal application.'
            if 'Microsoft' in publisher:
                condition = 'Use only when the relevant Microsoft product and supported version are in the actual Nepal organization architecture.'
            elif 'PostgreSQL' in publisher:
                condition = 'Use only for an actual PostgreSQL system; resolve the deployed version before applying current-document guidance.'
            elif 'Kubernetes' in publisher:
                condition = 'Use only for an actual Kubernetes deployment with the required operating capability; not a default recommendation for small organizations.'
            records[url] = dict(id='REF-' + hashlib.sha256(url.encode()).hexdigest()[:16], url=url,
                                label=label(url), label_basis='URL_DERIVED_NOT_RETRIEVED_PAGE_TITLE',
                                publisher=publisher, kind='international_technical_reference', topics=topics,
                                applicability=condition, nepal_market_evidence=False,
                                verification_state='PUBLISHER_INDEX_DISCOVERED_NOT_PAGE_REVIEWED',
                                discovery_index=index_id, publisher_lastmod=values.get('lastmod'),
                                page_reviewed_on=None, index_recorded_on='2026-11-12')
            retained += 1
        snapshots.append(dict(id=index_id, url=index, publisher=publisher, sha256=hashlib.sha256(raw).hexdigest(),
                              bytes=len(raw), method=method, retrieved_on=retrieved, indexed_urls=count, retained_urls=retained))
        print(json.dumps(dict(index=index, discovered=count, retained=retained)), flush=True)
    base = json.loads((REPO / 'skills/dharma-os/references/nepal-tech-intelligence/source-registry.json').read_text())
    for s in base:
        url = canonical(s['url'])
        if url in records:
            records[url].setdefault('legacy_ids', []).append(s['id']); continue
        records[url] = dict(id=s['id'], url=url, original_url=s['url'], label=s['title'], label_basis='INHERITED_SOURCE_METADATA',
                            publisher=s['publisher'], kind='nepal_institutional_reference', topics=nepal_topics(s),
                            applicability='Consult the original owning source for the stated Nepal question; preserve its geography, period and source-specific limits.',
                            nepal_market_evidence='Claim-dependent; a registered source is not an established market finding.',
                            verification_state=s.get('verification_status', s.get('verification_method', 'SOURCE_METADATA_ONLY')),
                            page_reviewed_on=None, metadata_checked_on=s.get('verification_date'),
                            legacy_verification_note=s.get('verification_method'), limitations=s.get('limitations', []))
    rows = sorted(records.values(), key=lambda r: r['url'])
    policy = dict(schema_version='1.0', prepared_on='2026-11-12', unique_reference_urls=len(rows),
                  kinds=dict(Counter(r['kind'] for r in rows)), publishers=dict(Counter(r['publisher'] for r in rows)),
                  rejected=dict(rejected), page_content_review='International entries are publisher-index discoveries. No claim that all pages responded, were read, or support a particular conclusion.',
                  count_basis='One canonical URL per record. Query/fragment variants, translated copies, old version collections and unrelated site sections are excluded by the maintained selection rules.',
                  geographic_boundary='Nepal is the market and institutional scope. International documents are conditional engineering references, not Nepal-published research or Nepal market measurements.',
                  rights='Only reference URLs, original navigation labels, publisher metadata and authored applicability notes are packaged. Underlying documents retain publisher rights; no article/manual bodies are redistributed.',
                  source_indexes=snapshots)
    target = REPO / 'catalog'; target.mkdir(exist_ok=True)
    (target / 'source-records.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (target / 'source-manifest.json').write_text(json.dumps(policy, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(unique_reference_urls=len(rows), kinds=policy['kinds'], rejected=policy['rejected'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache-dir', type=Path, required=True)
    parser.add_argument('--refresh', action='store_true', help='Re-fetch selected public indexes and robots; bounded requests only')
    args = parser.parse_args()
    build(args.cache_dir, args.refresh)
