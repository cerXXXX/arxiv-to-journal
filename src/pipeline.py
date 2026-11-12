"""Deterministic metadata matching and analysis of a fixed arXiv cohort."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import calendar
import csv
import html
import math
import statistics
import unicodedata
from urllib.parse import unquote
from datetime import date
from difflib import SequenceMatcher
from collections import Counter
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom',
      'o': 'http://a9.com/-/spec/opensearch/1.1/'}
SEED = 'hep-th-2021-publication-study-v1'
CUTOFF = date(2026, 11, 5)
NA = 'NA'


def json_read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def json_write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def csv_write(path, rows, fields=None):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields or list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def read_frame():
    all_entries = {}
    raw_count = 0
    total = None
    for path in sorted((ROOT / 'data/raw/arxiv').glob('frame_*.xml')):
        tree = ET.fromstring(path.read_bytes())
        n = int(tree.findtext('o:totalResults', namespaces=NS))
        if total is None:
            total = n
        if total != n:
            raise ValueError('arXiv pagination totals changed during download')
        for e in tree.findall('a:entry', NS):
            raw_count += 1
            ident = re.sub(r'v\d+$', '', e.findtext('a:id', namespaces=NS).split('/abs/')[-1])
            primary = e.find('x:primary_category', NS).attrib['term']
            created = e.findtext('a:published', namespaces=NS)
            row = {'arxiv_id': ident, 'title': ' '.join(e.findtext('a:title', namespaces=NS).split()),
                   'first_submitted': created, 'primary_category': primary,
                   'authors': [a.findtext('a:name', namespaces=NS) for a in e.findall('a:author', NS)],
                   'abstract': ' '.join(e.findtext('a:summary', namespaces=NS).split()),
                   'arxiv_doi': e.findtext('x:doi', '', NS), 'journal_ref': e.findtext('x:journal_ref', '', NS)}
            if ident in all_entries:
                raise ValueError('Duplicate frame identifier: ' + ident)
            all_entries[ident] = row
    if raw_count != total:
        raise ValueError(f'Incomplete frame: {raw_count} != {total}')
    return [x for x in all_entries.values() if x['primary_category'] == 'hep-th' and x['first_submitted'].startswith('2021-')]


def sample_frame(frame):
    def key(p):
        return hashlib.sha256((SEED + ':' + p['arxiv_id']).encode()).hexdigest(), p['arxiv_id']
    return sorted(sorted(frame, key=key)[:200], key=lambda x: x['arxiv_id'])


def add_first_titles(sample):
    tree = ET.parse(ROOT / 'data/raw/arxiv/sample_v1.xml').getroot()
    first = {}
    for e in tree.findall('a:entry', NS):
        ident = re.sub(r'v\d+$', '', e.findtext('a:id', namespaces=NS).split('/abs/')[-1])
        first[ident] = e
    if set(first) != {p['arxiv_id'] for p in sample}:
        raise ValueError('First-version metadata does not cover the sample exactly')
    for p in sample:
        e = first[p['arxiv_id']]
        if e.findtext('a:published', namespaces=NS) != p['first_submitted']:
            raise ValueError('Inconsistent first submission date')
        if e.find('x:primary_category', NS).attrib['term'] != 'hep-th':
            raise ValueError('Selected category was not primary in v1')
        p['latest_title'] = p['title']
        p['title'] = ' '.join(e.findtext('a:title', namespaces=NS).split())
        p['v1_authors'] = [a.findtext('a:name', namespaces=NS) for a in e.findall('a:author', NS)]
    return sample


def normalized(text):
    text = html.unescape(re.sub(r'<[^>]*>', '', text))
    greek = {'α':'alpha', 'β':'beta', 'γ':'gamma', 'δ':'delta', 'λ':'lambda', 'σ':'sigma',
             'φ':'phi', 'ϕ':'phi', 'ψ':'psi', 'ω':'omega', 'θ':'theta', 'τ':'tau', '×':' times '}
    text = ''.join(greek.get(c, c) for c in text)
    text = re.sub(r'\\(?:boldsymbol|mathcal|mathbb|mathrm|mathbf|mathfrak|text|ddot|dot|bar|hat|cal|rm)\s*', '', text)
    text = text.replace('\\varphi', 'phi').replace('\\times', ' times ')
    text = re.sub(r'[_{}$\\]', '', text)
    text = text.replace('&', ' and ')
    text = text.casefold().translate(str.maketrans({'ł': 'l', 'ø': 'o', 'đ': 'd', 'ð': 'd', 'þ': 'th', 'ß': 'ss', 'æ': 'ae', 'œ': 'oe'}))
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c)).casefold()
    return ' '.join(re.findall(r'[a-z0-9]+', text))


def title_key(text):
    return normalized(text).replace(' ', '')


def title_similarity(a, b):
    a, b = normalized(a), normalized(b)
    if not a or not b:
        return 0.0
    x, y = set(a.split()), set(b.split())
    dice = 2 * len(x & y) / (len(x) + len(y))
    return .65 * dice + .35 * SequenceMatcher(None, a, b, autojunk=False).ratio()


def surname(name):
    name = name.split(',')[0] if ',' in name else name.split()[-1]
    return normalized(name).replace(' ', '')


def author_overlap(p, m):
    a = {surname(x) for x in p['authors']}
    b = {surname(x.get('family') or x.get('name', '')) for x in m.get('author', []) if x.get('family') or x.get('name')}
    return len(a & b) / min(len(a), len(b)) if a and b else 0.0


def date_interval(parts):
    """Preserve precision; never invent a day for a year-only/month-only value."""
    if not 1 <= len(parts) <= 3:
        raise ValueError('Unsupported date parts')
    y = int(parts[0])
    m = int(parts[1]) if len(parts) > 1 else 1
    d = int(parts[2]) if len(parts) > 2 else 1
    lo = date(y, m, d)
    hi = lo if len(parts) == 3 else date(y, m, calendar.monthrange(y, m)[1]) if len(parts) == 2 else date(y, 12, 31)
    return lo, hi, ['year', 'month', 'day'][len(parts) - 1]


@lru_cache(maxsize=1)
def publisher_blocks():
    blocks = []
    for path in sorted((ROOT / 'data/raw/pages').glob('publisher_*.json')):
        if not path.name.endswith('.meta.json'):
            meta = path.with_suffix('.json.meta.json')
            if meta.exists() and json_read(meta).get('status') != 200:
                continue
            doc = json_read(path)
            requested_url = json_read(meta)['url'] if meta.exists() else doc.get('url', '')
            blocks.extend((unquote(requested_url).lower(), block) for block in doc.get('markdown', '').split('* * *'))
    return blocks


def publication_date(m, inspire):
    if m.get('_original_publisher_imprint'):
        exact = sorted(x['date'] for x in inspire.get('imprints', []) if len(x.get('date', '')) == 10)
        if exact:
            return list(map(int, exact[0].split('-'))), 'inspire:original_publisher_imprint'
    doi = m.get('DOI', '').lower()
    direct_path = ROOT / 'data/raw/publisher_dates/acta_54_6-A2.json'
    if doi == '10.5506/aphyspolb.54.6-a2' and direct_path.exists():
        evidence = json_read(direct_path)
        if (evidence.get('doi') == doi and evidence.get('article_ref') == '6-A2'
                and evidence.get('status') == 200
                and 'aid=6-A2' in evidence.get('source_url', '')
                and re.fullmatch(r'[0-9a-f]{64}', evidence.get('sha256', ''))
                and re.fullmatch(r'\d{4}-\d{2}-\d{2}', evidence.get('date', ''))):
            return list(map(int, evidence['date'].split('-'))), 'publisher:explicit_online_date'
    # The Acta page labels the online date explicitly and separates articles
    # with horizontal rules. Only the block containing this DOI is eligible.
    for requested_url, block in publisher_blocks():
        if doi and doi in requested_url and doi in block.lower():
            hit = re.search(r'published online\s+(\d{4}-\d{2}-\d{2})', block, re.I)
            if hit:
                return list(map(int, hit.group(1).split('-'))), 'publisher:explicit_online_date'
    online = m.get('published-online', {}).get('date-parts', [[]])[0]
    if online:
        return online, 'crossref:published-online'
    imprints = [x['date'] for x in inspire.get('imprints', []) if re.fullmatch(r'\d{4}(?:-\d{2}){0,2}', x.get('date', ''))]
    exact = sorted(x for x in imprints if len(x) == 10)
    if exact:
        return list(map(int, exact[0].split('-'))), 'inspire:imprint'
    for field in ['published', 'published-print', 'issued']:
        parts = m.get(field, {}).get('date-parts', [[]])[0]
        if parts:
            return parts, 'crossref:' + field
    if imprints:
        return list(map(int, sorted(imprints)[0].split('-'))), 'inspire:imprint'
    return [], 'missing'


def crossref_records():
    records = {}
    for path in sorted((ROOT / 'data/raw/crossref').glob('doi_*.json')):
        if path.name.endswith('.meta.json'):
            continue
        meta = json_read(path.with_suffix('.json.meta.json'))
        if meta['status'] != 200:
            continue
        m = json_read(path)['message']
        records[m['DOI'].lower()] = m
    return records


def inspire_record(p):
    hits = json_read(ROOT / f"data/raw/inspire/{p['arxiv_id']}.json")['hits']['hits']
    hits = [h for h in hits if any(e['value'] == p['arxiv_id'] for e in h['metadata'].get('arxiv_eprints', []))]
    if len(hits) > 1:
        raise ValueError('Multiple exact INSPIRE identities: ' + p['arxiv_id'])
    return hits[0]['metadata'] if hits else {}


@lru_cache(maxsize=1)
def referee_flags():
    flags = {}
    for path in sorted((ROOT/'data/raw/refereed').glob('batch_*.json')):
        if path.name.endswith('.meta.json'):
            continue
        for hit in json_read(path)['hits']['hits']:
            for e in hit['metadata'].get('arxiv_eprints', []):
                flags[e['value']] = hit['metadata'].get('refereed')
    return flags


def journal_record(url):
    path = ROOT / ('data/raw/journals/' + url.rsplit('/', 1)[-1] + '.json')
    return json_read(path).get('metadata', {}) if path.exists() else {}


def candidates(p, crossref):
    ins = inspire_record(p)
    sources = {}
    for doi in p['arxiv_doi'].split():
        sources.setdefault(doi.lower(), set()).add('arxiv_doi')
    for d in ins.get('dois', []):
        if d.get('material') != 'erratum':
            sources.setdefault(d['value'].lower(), set()).add('inspire_arxiv')
    aliases = json_read(ROOT / 'data/reference/doi_aliases.json')
    for old, details in aliases.items():
        if old in sources:
            sources.setdefault(details['canonical_doi'], set()).update(sources.pop(old) | {'publisher_doi_alias'})
    result = []
    for doi, route in sorted(sources.items()):
        m = crossref.get(doi)
        if m and any(doi == x['canonical_doi'] and x.get('date_policy') == 'original_publisher_imprint' for x in aliases.values()):
            m = dict(m, _original_publisher_imprint=True)
        if not m and not doi.startswith(('10.5281/', '10.48550/')):
            pub = [x for x in ins.get('publication_info', []) if x.get('journal_title') and x.get('year')]
            if pub:
                j = journal_record(pub[0].get('journal_record', {}).get('$ref', ''))
                issns = [x['value'] for x in j.get('issns', [])]
                m = {'DOI': doi, 'title': [ins['titles'][0]['title']], 'type': 'journal-article',
                     'container-title': [j.get('journal_title', {}).get('title') or pub[0]['journal_title']],
                     'ISSN': issns, 'author': [{'family': a['full_name'].split(',')[0]} for a in ins.get('authors', [])],
                     '_metadata_source': 'inspire_publisher_metadata'}
        if m:
            result.append((m, route))
    present = {m['DOI'].lower() for m, _ in result}
    for prefix in ['search', 'first_title']:
        search_path = ROOT / f"data/raw/crossref/{prefix}_{p['arxiv_id']}.json"
        if search_path.exists():
            for m in json_read(search_path)['message']['items']:
                if m['DOI'].lower() not in present:
                    result.append((m, {'title_search'}))
                    present.add(m['DOI'].lower())
    # OpenAlex supplies discovery candidates, but publication dates and article type
    # must still be verified against a cached DOI registration record.
    for prefix in ['search', 'first_title']:
        oa_path = ROOT / f"data/raw/openalex/{prefix}_{p['arxiv_id']}.json"
        if oa_path.exists():
            for work in json_read(oa_path).get('results', []):
                doi = (work.get('doi') or '').removeprefix('https://doi.org/').lower()
                if doi in crossref and doi not in present:
                    result.append((crossref[doi], {'openalex_title_search'}))
                    present.add(doi)
    return ins, result


def match(p, crossref):
    ins, options = candidates(p, crossref)
    audit, accepted = [], []
    for m, route in options:
        title = ' '.join(html.unescape(re.sub(r'<[^>]*>', '', ' '.join(m.get('title', [])))).split())
        t = max(title_similarity(p['title'], title), title_similarity(p['latest_title'], title))
        a = author_overlap(p, m)
        direct = bool(route & {'arxiv_doi', 'inspire_arxiv'})
        score = .75 * t + .25 * a
        parts, field = publication_date(m, ins if direct else {})
        reason = 'accepted'
        if m.get('type') != 'journal-article':
            reason = 'excluded_nonjournal'
        elif referee_flags().get(p['arxiv_id']) is False:
            reason = 'explicitly_not_refereed'
        elif re.match(r'(?i)\s*(erratum|corrigendum|correction|retraction)\b', title):
            reason = 'excluded_correction'
        elif not parts:
            reason = 'missing_publication_date'
        elif date_interval(parts)[1] > CUTOFF:
            reason = 'after_cutoff_or_uncertain'
        elif direct and (a < .5 or (t < .45 and 'inspire_arxiv' not in route)):
            reason = 'identity_conflict'
        elif not direct and not (t >= .88 and a >= .5 and score >= .85):
            reason = 'weak_title_or_authors'
        item = {'arxiv_id': p['arxiv_id'], 'doi': m['DOI'].lower(), 'title': title, 'type': m.get('type'),
                'venue': ' '.join(m.get('container-title', [])),
                'route': sorted(route), 'title_similarity': round(t, 6), 'author_overlap': round(a, 6),
                'score': round(score, 6), 'reason': reason}
        audit.append(item)
        if reason == 'accepted':
            accepted.append((direct, score, m['DOI'].lower(), m, route, parts, field, item))
    accepted.sort(key=lambda x: (-x[0], -x[1], x[2]))
    runners = [x['score'] for x in audit if accepted and x['doi'] != accepted[0][2]
               and x['type'] == 'journal-article' and x['author_overlap'] >= .5
               and x['reason'] in ['accepted', 'weak_title_or_authors']]
    if accepted and not accepted[0][0] and runners and accepted[0][1] - max(runners) < .05:
        for item in audit:
            if item['reason'] == 'accepted':
                item['reason'] = 'ambiguous_title_candidates'
        return None, audit
    return (accepted[0] if accepted else None), audit


def load_sjr():
    with (ROOT / 'data/raw/sjr/sjr_2025.csv').open(encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream, delimiter=';'))


def quartile(m, sjr):
    ids = {re.sub(r'[^0-9X]', '', x.upper()) for x in m.get('ISSN', [])}
    rows = [r for r in sjr if ids & {x.strip() for x in r['Issn'].split(',')}]
    if not rows:
        title = normalized(' '.join(m.get('container-title', [])))
        rows = [r for r in sjr if normalized(r['Title']) == title]
    if len(rows) != 1:
        return NA, NA, NA, 'unranked_or_ambiguous'
    r = rows[0]
    return r['SJR Best Quartile'] if r['SJR Best Quartile'] in ['Q1','Q2','Q3','Q4'] else NA, r['Sourceid'], r['Title'], r['Categories']


def make_row(p, found, sjr):
    row = {'preprint_title': p['title'], 'arxiv_id': p['arxiv_id'], 'first_version_date': p['first_submitted'][:10],
           'published': 'нет', 'venue': NA, 'publication_doi': NA, 'sjr_quartile': NA,
           'publication_date': NA, 'delay_days': NA, 'title_changed': NA, 'match_confidence': 'низкая',
           'publication_title': NA, 'date_precision': NA, 'date_source': NA,
           'delay_lower_days': NA, 'delay_upper_days': NA, 'match_route': 'no_accepted_match',
           'sjr_source_id': NA, 'sjr_title': NA, 'sjr_categories': NA,
           'latest_arxiv_title': p['latest_title'], 'arxiv_doi_present': 'да' if p['arxiv_doi'] else 'нет',
           'status_reason': 'no_journal_match_found_by_cutoff'}
    row['inspire_refereed'] = {True: 'да', False: 'нет', None: NA}[referee_flags().get(p['arxiv_id'])]
    if not found:
        return row
    direct, score, doi, m, routes, parts, field, item = found
    lo, hi, precision = date_interval(parts)
    start = date.fromisoformat(row['first_version_date'])
    low, high = (lo - start).days, (hi - start).days
    q, sid, stitle, cats = quartile(m, sjr)
    # A real pre-arXiv publication is retained as published, with its signed
    # chronology in diagnostics; it cannot enter a forward waiting-time mean.
    delay = low if precision == 'day' and low >= 0 else NA
    row.update(published='да', venue=' '.join(m.get('container-title', [])), publication_doi=doi,
               sjr_quartile=q, publication_date='-'.join(str(v).zfill(4 if i == 0 else 2) for i, v in enumerate(parts)),
               delay_days=delay, title_changed='да' if title_key(p['title']) != title_key(item['title']) else 'нет',
               match_confidence='высокая' if direct else 'средняя', publication_title=item['title'],
               date_precision=precision, date_source=field, delay_lower_days=max(0, low) if high >= 0 else NA,
               delay_upper_days=high if high >= 0 else NA, match_route='+'.join(sorted(routes)),
               sjr_source_id=sid, sjr_title=stitle, sjr_categories=cats,
               status_reason='journal_publication' if low >= 0 else 'published_before_v1_or_overlapping_interval')
    return row


def verify_rows(rows):
    if len(rows) != 200 or len({r['arxiv_id'] for r in rows}) != 200:
        raise ValueError('Expected exactly 200 distinct preprints')
    for r in rows:
        if any(v is None or str(v).strip() == '' for v in r.values()):
            raise ValueError('Empty field: ' + r['arxiv_id'])
        if not r['first_version_date'].startswith('2021-'):
            raise ValueError('Wrong cohort year')
        if r['published'] == 'да':
            if any(r[k] == NA for k in ['venue', 'publication_doi', 'publication_date', 'publication_title']):
                raise ValueError('Missing publication metadata')
        if r['delay_days'] != NA and (not isinstance(r['delay_days'], int) or r['delay_days'] < 0):
            raise ValueError('Invalid exact delay')
    dois = [r['publication_doi'] for r in rows if r['published'] == 'да']
    if len(dois) != len(set(dois)):
        raise ValueError('One publication was assigned to multiple preprints')


def evaluate_gold(rows):
    path = ROOT / 'data/review/gold.json'
    if not path.exists():
        return {'status': 'not_created'}
    by_id = {r['arxiv_id']: r for r in rows}
    results = []
    for case in json_read(path)['cases']:
        prediction = by_id[case['arxiv_id']]
        actual = prediction['published'] == 'да'
        status_error = actual != case['expected_published']
        doi_error = case['expected_published'] and prediction['publication_doi'] not in case['accepted_dois']
        date_error = bool(case.get('expected_publication_date') and prediction['publication_date'] != case['expected_publication_date'])
        delay_error = 'expected_delay_days' in case and str(prediction['delay_days']) != str(case['expected_delay_days'])
        baseline_error = 'baseline_published' in case and case['baseline_published'] != case['expected_published']
        results.append({'arxiv_id': case['arxiv_id'], 'groups': case['groups'],
                        'status_error': status_error, 'doi_error': bool(doi_error),
                        'date_error': date_error, 'delay_error': delay_error, 'baseline_error': baseline_error,
                        'error': status_error or bool(doi_error) or date_error or delay_error, 'predicted_published': actual})
    group_summary = {}
    for group in sorted({g for r in results for g in r['groups']}):
        cases = [r for r in results if group in r['groups']]
        group_summary[group] = {'n': len(cases), 'errors': sum(r['error'] for r in cases),
                               'status_errors': sum(r['status_error'] for r in cases), 'doi_errors': sum(r['doi_error'] for r in cases),
                               'date_errors': sum(r['date_error'] for r in cases), 'delay_errors': sum(r['delay_error'] for r in cases),
                               'baseline_errors': sum(r['baseline_error'] for r in cases)}
    return {'status': 'evaluated', 'groups': group_summary, 'cases': results,
            'total_unique_cases': len(results), 'total_errors': sum(r['error'] for r in results)}


def analyze(rows, frame):
    pub = [r for r in rows if r['published'] == 'да']
    delays = [r['delay_days'] for r in pub if r['delay_days'] != NA]
    q1 = sum(r['sjr_quartile'] == 'Q1' for r in pub)
    n, phat, z = len(rows), len(pub) / len(rows), 1.959963984540054
    center = (phat + z*z/(2*n))/(1+z*z/n)
    half = z * math.sqrt(phat*(1-phat)/n + z*z/(4*n*n))/(1+z*z/n)
    all_count = int(ET.parse(sorted((ROOT/'data/raw/arxiv').glob('frame_*.xml'))[0]).getroot().findtext('o:totalResults', namespaces=NS))
    return {'category': 'hep-th', 'cohort_year': 2021, 'cutoff': CUTOFF.isoformat(), 'seed': SEED,
            'frame_including_crosslists': all_count,
            'frame_primary': len(frame), 'sample_n': len(rows), 'published_n': len(pub),
            'not_found_n': len(rows)-len(pub), 'published_fraction': phat,
            'wilson95': [center-half, center+half], 'exact_delay_n': len(delays),
            'partial_date_n': sum(r['date_precision'] != 'day' for r in pub),
            'mean_delay_days': statistics.mean(delays), 'median_delay_days': statistics.median(delays),
            'min_delay_days': min(delays), 'max_delay_days': max(delays),
            'mean_delay_lower_bound': statistics.mean(r['delay_lower_days'] for r in pub if r['delay_lower_days'] != NA),
            'mean_delay_upper_bound': statistics.mean(r['delay_upper_days'] for r in pub if r['delay_upper_days'] != NA),
            'q1_n': q1, 'q1_fraction_published': q1/len(pub), 'q1_fraction_sample': q1/len(rows),
            'unranked_n': sum(r['sjr_quartile'] == NA for r in pub),
            'renamed_n': sum(r['title_changed'] == 'да' for r in pub),
            'published_without_arxiv_doi_n': sum(r['arxiv_doi_present'] == 'нет' for r in pub),
            'published_refereed_true_n': sum(r['inspire_refereed'] == 'да' for r in pub),
            'published_refereed_unset_n': sum(r['inspire_refereed'] == NA for r in pub),
            'confidence': dict(Counter(r['match_confidence'] for r in rows)),
            'quartiles': dict(sorted(Counter(r['sjr_quartile'] for r in pub).items())),
            'venues': dict(Counter(r['venue'] for r in pub).most_common()),
            'negative_exact_delay_n': sum(r['delay_days'] != NA and r['delay_days'] < 0 for r in rows),
            'publication_before_v1_n': sum(r['status_reason'] == 'published_before_v1_or_overlapping_interval' for r in pub),
            'publication_years': dict(sorted(Counter(r['publication_date'][:4] for r in pub).items())),
            'followup_min_days': min((CUTOFF-date.fromisoformat(r['first_version_date'])).days for r in rows),
            'followup_max_days': max((CUTOFF-date.fromisoformat(r['first_version_date'])).days for r in rows)}


def run(output=None):
    output = Path(output or ROOT / 'results')
    output.mkdir(parents=True, exist_ok=True)
    frame = read_frame()
    sample = add_first_titles(sample_frame(frame))
    crossref, sjr = crossref_records(), load_sjr()
    rows, diagnostics = [], []
    for p in sample:
        found, trace = match(p, crossref)
        diagnostics.extend(trace)
        row = make_row(p, found, sjr)
        excluded = [x for x in trace if x['reason'] == 'excluded_nonjournal' and x['type'] == 'proceedings-article'
                    and set(x['route']) & {'arxiv_doi', 'inspire_arxiv'}]
        row.update(excluded_proceedings_doi=excluded[0]['doi'] if excluded else NA,
                   excluded_proceedings_venue=excluded[0]['venue'] if excluded else NA)
        if not found and excluded:
            row['status_reason'] = 'conference_proceedings_excluded_by_definition'
        rows.append(row)
    verify_rows(rows)
    metrics = analyze(rows, frame)
    metrics['conference_only_n'] = sum(r['published'] == 'нет' and r['excluded_proceedings_doi'] != NA for r in rows)
    metrics['published_with_known_proceedings_n'] = metrics['published_n'] + metrics['conference_only_n']
    evaluation = evaluate_gold(rows)
    csv_write(output / 'preprints.csv', rows)
    csv_write(output / 'sample.csv', [{'arxiv_id': p['arxiv_id'], 'selection_hash': hashlib.sha256((SEED+':'+p['arxiv_id']).encode()).hexdigest(),
                                     'primary_category': p['primary_category'], 'first_submitted': p['first_submitted']} for p in sample])
    json_write(output / 'metrics.json', metrics)
    json_write(output / 'match_audit.json', diagnostics)
    json_write(output / 'validation.json', evaluation)
    funnel = [{'stage': 'arxiv_category_including_crosslists', 'n': metrics['frame_including_crosslists']},
              {'stage': 'primary_category_2021', 'n': len(frame)}, {'stage': 'random_sample', 'n': 200},
              {'stage': 'inspire_exact_arxiv_identity', 'n': sum(bool(inspire_record(p)) for p in sample)},
              {'stage': 'doi_in_arxiv_or_inspire', 'n': sum(bool(p['arxiv_doi'] or inspire_record(p).get('dois')) for p in sample)},
              {'stage': 'journal_publication_accepted', 'n': metrics['published_n']},
              {'stage': 'exact_day_delay', 'n': metrics['exact_delay_n']}, {'stage': 'sjr_q1', 'n': metrics['q1_n']}]
    csv_write(output / 'funnel.csv', funnel)
    json_write(output / 'funnel.json', funnel)
    csv_write(output / 'discovery_branches.csv', [{'arxiv_doi_present': doi, 'published': pub,
              'n': sum(r['arxiv_doi_present'] == doi and r['published'] == pub for r in rows)} for doi in ['да','нет'] for pub in ['да','нет']])
    chronology = [{'arxiv_id': r['arxiv_id'], 'first_version_date': r['first_version_date'],
                   'publication_date': r['publication_date'], 'date_precision': r['date_precision'],
                   'signed_exact_difference_days': (date.fromisoformat(r['publication_date'])-date.fromisoformat(r['first_version_date'])).days
                       if r['date_precision'] == 'day' else NA,
                   'included_in_forward_mean': r['delay_days'] != NA} for r in rows if r['published'] == 'да']
    csv_write(output / 'chronology.csv', chronology)
    russian = ['Название препринта','Идентификатор arXiv','Дата первой версии','Опубликован',
               'Журнал или конференция','DOI публикации','Квартиль SJR 2025','Дата публикации',
               'Задержка в днях','Изменилось ли название','Уверенность в сопоставлении']
    english = list(rows[0])[:11]
    csv_write(output/'preprints_ru.csv',[dict(zip(russian,[r[k] for k in english])) for r in rows])
    json_write(output/'quality.json',{'rows':len(rows),'unique_arxiv_ids':len({r['arxiv_id'] for r in rows}),
        'empty_cells':sum(str(v).strip()=='' for r in rows for v in r.values()),
        'negative_forward_delays':metrics['negative_exact_delay_n'],
        'unresolved_month_dates':metrics['partial_date_n'],'publications_before_v1':metrics['publication_before_v1_n'],
        'unique_publication_dois':len({r['publication_doi'] for r in rows if r['published']=='да'}),
        'gold_errors':evaluation.get('total_errors',NA)})
    print(f"Sample: {len(rows)}; journal publications: {metrics['published_n']}; exact delays: {metrics['exact_delay_n']}; Q1: {metrics['q1_n']}")
    return rows, metrics, evaluation


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Analyze a saved metadata snapshot.')
    parser.add_argument('--data-root', type=Path, help='Snapshot root containing data/raw and snapshot.json')
    parser.add_argument('--output', type=Path, help='Directory for generated results')
    args = parser.parse_args()
    if args.data_root:
        ROOT = args.data_root.resolve()
        snapshot = ROOT / 'snapshot.json'
        if not (ROOT / 'data/raw').is_dir() or not snapshot.is_file():
            parser.error('--data-root must be a completed snapshot with data/raw and snapshot.json')
        CUTOFF = date.fromisoformat(json_read(snapshot)['cutoff'])
        publisher_blocks.cache_clear()
        referee_flags.cache_clear()
    run(args.output or ROOT / 'results')
