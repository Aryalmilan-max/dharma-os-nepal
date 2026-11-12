#!/usr/bin/env python3
"""Explicit bounded HTTP availability sample; not content or catalog-wide validation."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

def run():
    sources = json.loads((ROOT / 'catalog/source-records.json').read_text())
    groups = {}
    for s in sources:
        if s.get('discovery_index'): groups.setdefault(s['discovery_index'], []).append(s['url'])
    urls = set()
    for group in groups.values():
        for offset in (0, len(group)//2, len(group)-1): urls.add(group[offset])
    for refs in json.loads((ROOT / 'catalog/task-reference-map.json').read_text()).values():
        urls.update(s['url'] for s in refs)
    if len(urls) > 60: raise ValueError('Sample exceeds bounded limit')
    def check(url):
        result = dict(url=url, checked_at=datetime.now(timezone.utc).isoformat(), content_reviewed=False)
        try:
            with urlopen(Request(url, headers={'User-Agent':'DharmaOSResearch/0.4 (bounded reference availability sample)'}), timeout=12) as response:
                response.read(1024)
                result.update(http_status=response.status, final_url=response.url, state='HTTP_RESPONDED_NOT_CONTENT_VALIDATED')
        except HTTPError as exc: result.update(http_status=exc.code, state='HTTP_ERROR_REVIEW_REQUIRED')
        except (URLError, TimeoutError, OSError): result.update(http_status=None, state='FETCH_FAILED_REVIEW_REQUIRED')
        return result
    with ThreadPoolExecutor(max_workers=4) as pool: rows = list(pool.map(check, sorted(urls)))
    result = dict(method='First, middle and last URL per selected publisher index, plus curated task links; bounded GET reads at most 1024 response bytes.',
                  limitations='Nonrandom convenience sample. Availability is not content validation, statistical coverage or proof of applicability. Unchecked records remain index discoveries.', records=rows)
    (ROOT / 'catalog/availability-sample.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(checked=len(rows), responded=sum(r['state']=='HTTP_RESPONDED_NOT_CONTENT_VALIDATED' for r in rows), review_required=sum(r['state']!='HTTP_RESPONDED_NOT_CONTENT_VALIDATED' for r in rows))))

if __name__ == '__main__': run()
