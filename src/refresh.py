"""Acquire a new live snapshot without overwriting the frozen submission."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import urllib.error
import urllib.parse
import urllib.request

import collect
import pipeline

SOURCE = Path(__file__).resolve().parents[1]


def page_fetch(task):
    label, url, destination = task
    path = destination/'data/raw/pages'/f'{label}.json'
    meta_path = path.with_suffix('.json.meta.json')
    if path.exists() and meta_path.exists():
        return json.loads(meta_path.read_text())['status'] == 200
    base = os.environ.get('CRAWL4AI_URL','http://asgard.local:11235').removesuffix('/mcp/sse').removesuffix('/mcp').rstrip('/')
    headers={'Content-Type':'application/json'}
    if os.environ.get('CRAWL4AI_TOKEN'):
        headers['Authorization']='Bearer '+os.environ['CRAWL4AI_TOKEN']
    req=urllib.request.Request(base+'/md',data=json.dumps({'url':url,'f':'raw'}).encode(),headers=headers)
    local=urllib.parse.urlparse(base).hostname in ['asgard.local','localhost','127.0.0.1']
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({})) if local else urllib.request.build_opener()
    try:
        with opener.open(req,timeout=100) as response:
            body,status=response.read(),response.status
    except urllib.error.HTTPError as e:
        body,status=e.read(),e.code
    except (OSError,TimeoutError) as e:
        body,status=json.dumps({'success':False,'error':str(e)}).encode(),0
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(body)
    meta_path.write_text(json.dumps({'url':url,'service':'crawl4ai/md','status':status,
       'retrieved_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(body).hexdigest()},indent=2)+'\n')
    return status==200


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
    # Re-fetch the documented page URLs. A failed page stays an explicit failed
    # response; it never substitutes for an API metadata record.
    page_tasks=[]
    for meta in sorted((SOURCE/'data/raw/pages').glob('*.json.meta.json')):
        info=json.loads(meta.read_text())
        page_tasks.append((meta.name.removesuffix('.json.meta.json'),info['url'],destination))
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(3) as executor:
        page_status=list(executor.map(page_fetch,page_tasks))
    pipeline.publisher_blocks.cache_clear()
    pipeline.referee_flags.cache_clear()
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
    pipeline.run(destination/'results')
    now=datetime.now(timezone.utc).isoformat()
    summary={'completed_utc':now,'cutoff':pipeline.CUTOFF.isoformat(),'sample_n':len(sample),
             'searched_unmatched_n':len(unmatched),'page_requests_n':len(page_tasks),
             'page_http_failures_n':sum(not ok for ok in page_status),
             'status':'core_api_snapshot_complete','gold_validation':'Not transferred: the frozen gold is dated and snapshot-specific.'}
    pipeline.json_write(destination/'snapshot.json',summary)
    files=sorted(p for p in (destination/'data').rglob('*') if p.is_file())
    (destination/'INPUTS.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(destination).as_posix()+'\n' for p in files))
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,default=None,help='Resume/reuse this live snapshot directory')
    args=parser.parse_args()
    destination=args.destination or SOURCE/'data/live'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    refresh(destination.resolve())
