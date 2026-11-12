"""Network acquisition; the default analysis never imports this module."""
import concurrent.futures
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom',
      'o': 'http://a9.com/-/spec/opensearch/1.1/'}
FIELDS = 'titles,authors,dois,publication_info,arxiv_eprints,document_type,preprint_date,imprints,abstracts,urls'


def fetch(relative, url, attempts=5):
    path = RAW / relative
    if path.exists() and path.with_suffix(path.suffix + '.meta.json').exists():
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PreprintPublicationStudy/1.0 (academic metadata research)'})
            with urllib.request.urlopen(req, timeout=100) as r:
                body, status, headers = r.read(), r.status, dict(r.headers)
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                body, status, headers = e.read(), e.code, dict(e.headers)
                break
            if i + 1 == attempts:
                raise
            time.sleep(3 * (i + 1))
        except (OSError, TimeoutError):
            if i + 1 == attempts:
                raise
            time.sleep(3 * (i + 1))
    path.write_bytes(body)
    meta = {'url': url, 'status': status, 'retrieved_utc': datetime.now(timezone.utc).isoformat(),
            'sha256': hashlib.sha256(body).hexdigest(), 'headers': headers}
    path.with_suffix(path.suffix + '.meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    return body


def frame():
    start, total = 0, 1
    while start < total:
        query = urllib.parse.urlencode({'search_query': 'cat:hep-th AND submittedDate:[202101010000 TO 202112312359]',
                'start': start, 'max_results': 1000, 'sortBy': 'submittedDate', 'sortOrder': 'ascending'})
        body = fetch(f'arxiv/frame_{start:05}.xml', 'https://export.arxiv.org/api/query?' + query)
        tree = ET.fromstring(body)
        total = int(tree.findtext('o:totalResults', namespaces=NS))
        count = len(tree.findall('a:entry', NS))
        if not count:
            raise RuntimeError('Premature empty arXiv page')
        print('arxiv', start, count, total, flush=True)
        start += count
        time.sleep(3)


def selected():
    from pipeline import read_frame, sample_frame, add_first_titles
    return add_first_titles(sample_frame(read_frame()))


def download_v1(sample):
    q = urllib.parse.urlencode({'id_list': ','.join(p['arxiv_id']+'v1' for p in sample), 'max_results': len(sample)})
    return fetch('arxiv/sample_v1.xml', 'https://export.arxiv.org/api/query?' + q)


def inspire_one(p):
    ident = p['arxiv_id']
    q = urllib.parse.urlencode({'q': 'arxiv:' + ident, 'size': 5, 'fields': FIELDS})
    return fetch(f'inspire/{ident}.json', 'https://inspirehep.net/api/literature?' + q)


def crossref_one(doi):
    return fetch('crossref/doi_' + hashlib.sha256(doi.lower().encode()).hexdigest()[:20] + '.json',
                 'https://api.crossref.org/works/' + urllib.parse.quote(doi, safe=''))


def search_one(p):
    ident = p['arxiv_id']
    title = p.get('latest_title', p['title'])
    q = urllib.parse.urlencode({'query.bibliographic': title, 'rows': 5})
    fetch(f'crossref/search_{ident}.json', 'https://api.crossref.org/works?' + q)
    q = urllib.parse.urlencode({'search': title, 'per-page': 5})
    fetch(f'openalex/search_{ident}.json', 'https://api.openalex.org/works?' + q)
    if p['title'] != title:
        q = urllib.parse.urlencode({'query.bibliographic': p['title'], 'rows': 5})
        fetch(f'crossref/first_title_{ident}.json', 'https://api.crossref.org/works?' + q)
        q = urllib.parse.urlencode({'search': p['title'], 'per-page': 5})
        fetch(f'openalex/first_title_{ident}.json', 'https://api.openalex.org/works?' + q)


def run_parallel(func, things, workers=5):
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(func, x): x for x in things}
        failed = []
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            try:
                future.result()
            except Exception as e:
                failed.append((str(futures[future]), str(e)))
            if i % 20 == 0:
                print(func.__name__, i, '/', len(futures), flush=True)
        if failed:
            print('FAILED', json.dumps(failed), flush=True)
            raise RuntimeError(f'{len(failed)} requests failed; rerun resumes cached acquisition')


if __name__ == '__main__':
    import sys
    command = sys.argv[1]
    if command == 'frame':
        frame()
    elif command == 'inspire':
        run_parallel(inspire_one, selected())
    elif command == 'crossref':
        dois = set()
        for p in selected():
            if p['arxiv_doi']:
                dois.update(x.strip() for x in p['arxiv_doi'].split())
            for hit in json.loads((RAW / f"inspire/{p['arxiv_id']}.json").read_bytes())['hits']['hits']:
                if any(e['value'] == p['arxiv_id'] for e in hit['metadata'].get('arxiv_eprints', [])):
                    dois.update(d['value'] for d in hit['metadata'].get('dois', []) if d.get('material') != 'erratum')
        run_parallel(crossref_one, sorted(dois))
    elif command == 'search':
        candidates = []
        for p in selected():
            hits = json.loads((RAW / f"inspire/{p['arxiv_id']}.json").read_bytes())['hits']['hits']
            if not p['arxiv_doi'] and not any(h['metadata'].get('dois') for h in hits):
                candidates.append(p)
        run_parallel(search_one, candidates, workers=3)
