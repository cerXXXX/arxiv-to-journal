"""Network acquisition; the default analysis never imports this module."""
import concurrent.futures
import hashlib
from html.parser import HTMLParser
import json
import re
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
ACTA_DOI = '10.5506/aphyspolb.54.6-a2'


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


class ParagraphParser(HTMLParser):
    """Extract publisher paragraphs without a browser or remote rendering service."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.paragraphs = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.current = []

    def handle_endtag(self, tag):
        if tag == 'p' and self.current is not None:
            value = ' '.join(' '.join(self.current).split())
            if value:
                self.paragraphs.append(value)
            self.current = None

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)


def acta_publication_date():
    """Fetch and validate the exact Acta date absent from Crossref/INSPIRE."""
    path = RAW / ('crossref/doi_' + hashlib.sha256(ACTA_DOI.encode()).hexdigest()[:20] + '.json')
    message = json.loads(path.read_text(encoding='utf-8'))['message']
    if message.get('DOI', '').lower() != ACTA_DOI:
        raise ValueError('Unexpected Crossref DOI for Acta date lookup')
    url = message.get('resource', {}).get('primary', {}).get('URL')
    if not url:
        raise ValueError('Crossref record has no primary publisher URL')
    body = fetch('publisher/acta_54_6-A2.html', url)
    text = body.decode('utf-8', errors='replace')
    parser = ParagraphParser()
    parser.feed(text)
    doi_confirmed = ACTA_DOI in text.lower()
    article_ref = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('aid', [''])[0]
    if not doi_confirmed or article_ref != '6-A2':
        raise ValueError('Acta primary page does not confirm DOI and article identifier')
    matches = [re.search(r'\barticle\s+6-A2\b.*?published online\s+(\d{4}-\d{2}-\d{2})', p, re.I)
               for p in parser.paragraphs]
    dates = sorted({m.group(1) for m in matches if m})
    if len(dates) != 1:
        raise ValueError(f'Expected one explicit date for Acta article 6-A2, found {dates}')
    meta = json.loads((RAW / 'publisher/acta_54_6-A2.html.meta.json').read_text(encoding='utf-8'))
    result = {'doi': ACTA_DOI, 'article_ref': article_ref, 'date': dates[0],
              'source_url': meta['url'],
              'status': meta['status'], 'sha256': meta['sha256'],
              'retrieved_utc': meta['retrieved_utc'],
              'evidence': 'publisher HTML paragraph naming article 6-A2 and explicit published online date'}
    result_path = RAW / 'publisher_dates/acta_54_6-A2.json'
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


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
