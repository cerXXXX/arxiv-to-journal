"""Acquire a new live snapshot without overwriting the frozen submission."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import urllib.parse

import collect
import pipeline

SOURCE = Path(__file__).resolve().parents[1]


def optional_acta_publication_date():
    """Return verified publisher date, or an error for precision-aware fallback."""
    try:
        return collect.acta_publication_date(), None
    except (OSError, KeyError, ValueError) as error:
        return None, str(error)


def refresh(destination):
    destination.mkdir(parents=True,exist_ok=True)
    (destination/'data/reference').mkdir(parents=True,exist_ok=True)
    shutil.copyfile(SOURCE/'data/reference/doi_aliases.json',destination/'data/reference/doi_aliases.json')
    pipeline.ROOT=collect.ROOT=destination
    collect.RAW=destination/'data/raw'
    pipeline.CUTOFF=datetime.now(timezone.utc).date()
    pipeline.publisher_blocks.cache_clear()
    pipeline.referee_flags.cache_clear()
    print('Live snapshot:',destination,flush=True)
    collect.frame()
    sample=pipeline.sample_frame(pipeline.read_frame())
    collect.download_v1(sample)
    sample=pipeline.add_first_titles(sample)
    collect.run_parallel(collect.inspire_one,sample)
    records=[pipeline.inspire_record(p) for p in sample]
    dois={d['value'] for m in records for d in m.get('dois',[]) if d.get('material')!='erratum'}
    dois.update(d for p in sample for d in p['arxiv_doi'].split())
    aliases=pipeline.json_read(destination/'data/reference/doi_aliases.json')
    for old,entry in aliases.items():
        if old.lower() in {d.lower() for d in dois}:dois.add(entry['canonical_doi'])
    collect.run_parallel(collect.crossref_one,sorted(dois))
    urls=sorted({x['journal_record']['$ref'] for m in records for x in m.get('publication_info',[]) if x.get('journal_record')})
    collect.run_parallel(lambda u:collect.fetch('journals/'+u.rsplit('/',1)[-1]+'.json',u),urls)
    def flags(k):
        q=urllib.parse.urlencode({'q':' OR '.join('arxiv:'+p['arxiv_id'] for p in sample[k:k+20]),'size':100,
                                 'fields':'arxiv_eprints,refereed,document_type,publication_info'})
        return collect.fetch(f'refereed/batch_{k:03}.json','https://inspirehep.net/api/literature?'+q)
    collect.run_parallel(flags,list(range(0,len(sample),20)))
    repositories=[('P-M-Ferreira/ranking','sjr_2025'),('bastianaravenaulagos/DATOS_SCIMAGO_REVISTAS','sjr_mirror')]
    for repo,label in repositories:
        path='scimagojr 2025.csv'
        q=urllib.parse.urlencode({'path':path,'per_page':1})
        body=collect.fetch('sjr/'+label+'_commit.json','https://api.github.com/repos/'+repo+'/commits?'+q)
        commit=json.loads(body)[0]['sha']
        collect.fetch('sjr/'+label+'.csv','https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+urllib.parse.quote(path))
    a=collect.RAW/'sjr/sjr_2025.csv';b=collect.RAW/'sjr/sjr_mirror.csv'
    if a.read_bytes()!=b.read_bytes() or b'Total Docs. (2025)' not in a.read_bytes().splitlines()[0]:
        raise RuntimeError('SJR mirror mismatch or wrong metric year; snapshot retained for inspection')
    crossref=pipeline.crossref_records()
    unmatched=[p for p in sample if pipeline.match(p,crossref)[0] is None]
    collect.run_parallel(collect.search_one,unmatched,workers=3)
    # DOI registration records also verify plausible OpenAlex discoveries.
    extra=set()
    for path in (collect.RAW/'openalex').glob('*.json'):
        if path.name.endswith('.meta.json'):continue
        for work in json.loads(path.read_text()).get('results',[]):
            doi=(work.get('doi') or '').removeprefix('https://doi.org/')
            if doi and work.get('type') in ['article','review']:
                extra.add(doi)
    collect.run_parallel(collect.crossref_one,sorted(extra))
    direct_date, direct_date_error = optional_acta_publication_date()
    pipeline.run(destination/'results')
    now=datetime.now(timezone.utc).isoformat()
    summary={'completed_utc':now,'cutoff':pipeline.CUTOFF.isoformat(),'sample_n':len(sample),
             'searched_unmatched_n':len(unmatched),
             'direct_publisher_date_n':int(direct_date is not None),
             'direct_publisher_date':direct_date['date'] if direct_date else None,
             'direct_publisher_date_error':direct_date_error,
             'status':'core_api_snapshot_complete','gold_validation':'Not transferred: the frozen gold is dated and snapshot-specific.'}
    pipeline.json_write(destination/'snapshot.json',summary)
    files=sorted(p for p in (destination/'data').rglob('*') if p.is_file())
    (destination/'INPUTS.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(destination).as_posix()+'\n' for p in files))
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,default=None,help='Resume/reuse this live snapshot directory')
    args=parser.parse_args()
    destination=args.destination or SOURCE/'data/live'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    if not args.destination and destination.exists():
        raise FileExistsError('Fresh snapshot destination already exists: ' + str(destination))
    refresh(destination.resolve())
