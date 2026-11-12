"""Regression checks for identity, dates, cohort selection and deliverables."""
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import pipeline as p
import refresh as r


class Matching(unittest.TestCase):
    def setUp(self):
        self.preprint={'arxiv_id':'test', 'title':'Quantum geometry of black holes',
                       'latest_title':'Quantum geometry of black holes','authors':['Alice Example']}
        self.article={'DOI':'10.1234/test', 'title':['Quantum geometry of black holes'],
                      'type':'journal-article','author':[{'family':'Example'}],
                      'published-online':{'date-parts':[[2022,2,2]]},'container-title':['Example Journal']}

    def matched(self, options, ins=None):
        with patch.object(p,'candidates',return_value=(ins or {}, options)):
            return p.match(self.preprint,{})

    def test_unicode_author_identity(self):
        self.assertEqual(p.surname('Jacek Pawelczyk'),p.surname('J. Pawełczyk'))
        self.assertEqual(p.surname('Markus Fröb'),p.surname('Fröb, Markus'))

    def test_identical_title_different_authors_rejected(self):
        self.article['author']=[{'family':'Different'}]
        found,audit=self.matched([(self.article,{'arxiv_doi'})])
        self.assertIsNone(found)
        self.assertEqual(audit[0]['reason'],'identity_conflict')

    def test_direct_identity_survives_complete_title_change(self):
        self.article['title']=['Entirely replaced scientific terminology']
        found,_=self.matched([(self.article,{'inspire_arxiv'})])
        self.assertIsNotNone(found)

    def test_conference_excluded_even_with_exact_identity(self):
        self.article['type']='proceedings-article'
        found,audit=self.matched([(self.article,{'inspire_arxiv'})])
        self.assertIsNone(found)
        self.assertEqual(audit[0]['reason'],'excluded_nonjournal')

    def test_preprint_doi_is_not_journal_publication(self):
        self.article['type']='posted-content'
        self.assertIsNone(self.matched([(self.article,{'title_search'})])[0])

    def test_text_fallback_can_accept_a_unique_same_author_article(self):
        found,_=self.matched([(self.article,{'title_search'})])
        self.assertIsNotNone(found)
        self.assertFalse(found[0])

    def test_tied_fuzzy_candidates_rejected(self):
        other=dict(self.article,DOI='10.1234/other')
        found,audit=self.matched([(self.article,{'title_search'}),(other,{'title_search'})])
        self.assertIsNone(found)
        self.assertTrue(all(x['reason']=='ambiguous_title_candidates' for x in audit))

    def test_near_threshold_runner_still_creates_ambiguity(self):
        other=dict(self.article,DOI='10.1234/other',title=['Quantum geometry of black hole'])
        with patch.object(p,'title_similarity',side_effect=[.9,.9,.879,.879]):
            found,audit=self.matched([(self.article,{'title_search'}),(other,{'title_search'})])
        self.assertIsNone(found)

    def test_future_publication_rejected(self):
        self.article['published-online']={'date-parts':[[2027,1,1]]}
        self.assertIsNone(self.matched([(self.article,{'inspire_arxiv'})])[0])

    def test_correction_cannot_replace_original(self):
        self.article['title']=['Erratum: Quantum geometry of black holes']
        self.assertIsNone(self.matched([(self.article,{'inspire_arxiv'})])[0])


class Dates(unittest.TestCase):
    def test_month_precision_is_interval(self):
        lo,hi,precision=p.date_interval([2021,11])
        self.assertEqual((lo,hi,precision),(date(2021,11,1),date(2021,11,30),'month'))

    def test_leap_year(self):
        self.assertEqual(p.date_interval([2024,2])[1],date(2024,2,29))
        with self.assertRaises(ValueError):p.date_interval([2021,2,29])

    def test_year_precision(self):
        self.assertEqual(p.date_interval([2023]),(date(2023,1,1),date(2023,12,31),'year'))

    def test_cited_doi_cannot_borrow_another_articles_date(self):
        article={'DOI':'10.1234/cited','published-online':{'date-parts':[[2022,2,2]]}}
        blocks=[('https://doi.org/10.1234/other','published online 2021-01-01; references: 10.1234/cited')]
        with patch.object(p,'publisher_blocks',return_value=blocks):
            self.assertEqual(p.publication_date(article,{})[0],[2022,2,2])

    def test_direct_acta_evidence_and_year_only_fallback(self):
        article={'DOI':'10.5506/aphyspolb.54.6-a2',
                 'published-online':{'date-parts':[[2023]]}}
        with tempfile.TemporaryDirectory() as directory, patch.object(p,'ROOT',Path(directory)):
            evidence=Path(directory)/'data/raw/publisher_dates/acta_54_6-A2.json'
            evidence.parent.mkdir(parents=True)
            evidence.write_text(json.dumps({'doi':article['DOI'],'article_ref':'6-A2',
                'date':'2023-07-11','status':200,
                'source_url':'https://publisher.example/findarticle?aid=6-A2',
                'sha256':'a'*64}),encoding='utf-8')
            date_parts,source=p.publication_date(article,{})
            self.assertEqual((date_parts,source),([2023,7,11],'publisher:explicit_online_date'))
            evidence.unlink()
            with patch.object(p,'publisher_blocks',return_value=[]):
                date_parts,source=p.publication_date(article,{})
            self.assertEqual((date_parts,source),([2023],'crossref:published-online'))

    def test_unavailable_acta_page_keeps_refresh_nonfatal(self):
        with patch.object(r.collect,'acta_publication_date',side_effect=OSError('publisher unavailable')):
            evidence,error=r.optional_acta_publication_date()
        self.assertIsNone(evidence)
        self.assertEqual(error,'publisher unavailable')


class FrozenStudy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (p.ROOT/'results/preprints.csv').open(encoding='utf-8') as stream:
            cls.rows=list(csv.DictReader(stream))
        cls.by_id={r['arxiv_id']:r for r in cls.rows}
        cls.metrics=p.json_read(p.ROOT/'results/metrics.json')

    def test_selection_independent_of_order(self):
        frame=p.read_frame()
        a=[r['arxiv_id'] for r in p.sample_frame(frame)]
        b=[r['arxiv_id'] for r in p.sample_frame(list(reversed(frame)))]
        self.assertEqual(a,b)
        self.assertEqual(a,list(self.by_id))

    def test_cohort_has_exactly_200_valid_first_versions(self):
        sample=p.add_first_titles(p.sample_frame(p.read_frame()))
        self.assertEqual(len(sample),200)
        self.assertTrue(all(x['first_submitted'].startswith('2021-') and x['primary_category']=='hep-th' for x in sample))

    def test_no_empty_cells_or_duplicate_publications(self):
        self.assertTrue(all(v.strip() for row in self.rows for v in row.values()))
        dois=[r['publication_doi'] for r in self.rows if r['published']=='да']
        self.assertEqual(len(dois),len(set(dois)))
        self.assertTrue(all(r['delay_days']=='NA' or int(r['delay_days'])>=0 for r in self.rows))

    def test_true_pre_arxiv_publication_is_preserved(self):
        row=self.by_id['2109.03271']
        self.assertEqual(row['published'],'да')
        self.assertEqual(row['delay_days'],'NA')
        with (p.ROOT/'results/chronology.csv').open() as stream:
            chron=list(csv.DictReader(stream))
        entry=next(x for x in chron if x['arxiv_id']=='2109.03271')
        self.assertEqual(entry['signed_exact_difference_days'],'-36')
        self.assertEqual(entry['included_in_forward_mean'],'False')

    def test_partial_dates_do_not_enter_exact_mean(self):
        row=self.by_id['2102.02253']
        self.assertEqual((row['publication_date'],row['delay_days'],row['delay_lower_days'],row['delay_upper_days']),('2021-11','NA','271','300'))
        delays=[int(r['delay_days']) for r in self.rows if r['delay_days']!='NA']
        self.assertEqual(len(delays),176)
        self.assertAlmostEqual(sum(delays)/len(delays),self.metrics['mean_delay_days'])

    def test_publisher_day_resolves_year_only_crossref(self):
        row=self.by_id['2112.15592']
        self.assertEqual((row['publication_date'],row['delay_days']),('2023-07-11','557'))
        self.assertEqual(row['date_source'],'publisher:explicit_online_date')

    def test_doi_migration_does_not_import_january_placeholder(self):
        row=self.by_id['2111.05295']
        self.assertEqual(row['publication_doi'],'10.55730/1300-0101.1000')
        self.assertEqual(row['publication_date'],'2021-12-28')

    def test_unranked_is_not_unpublished_or_q4(self):
        row=self.by_id['2101.01223']
        self.assertEqual(row['published'],'да')
        self.assertEqual(row['sjr_quartile'],'NA')

    def test_sjr_is_really_2025_and_mirrors_identical(self):
        a=(p.ROOT/'data/raw/sjr/sjr_2025.csv').read_bytes()
        b=(p.ROOT/'data/raw/sjr/sjr_mirror.csv').read_bytes()
        self.assertEqual(hashlib.sha256(a).digest(),hashlib.sha256(b).digest())
        self.assertIn(b'Total Docs. (2025)',a.splitlines()[0])
        jhep=next(x for x in p.load_sjr() if x['Title']=='Journal of High Energy Physics')
        self.assertEqual(jhep['SJR Best Quartile'],'Q2')

    def test_gold_and_initial_audit_are_accountable(self):
        result=p.evaluate_gold([{k:(int(v) if k in ['delay_days','delay_lower_days','delay_upper_days'] and v!='NA' else v) for k,v in r.items()} for r in self.rows])
        self.assertEqual(result['groups']['audit20']['n'],20)
        self.assertEqual(result['groups']['audit20']['baseline_errors'],1)
        self.assertEqual(result['groups']['audit20']['errors'],0)
        self.assertEqual(result['total_unique_cases'],29)
        self.assertEqual(result['total_errors'],0)
        baseline=p.json_read(p.ROOT/'data/review/baseline_audit.json')
        self.assertEqual(sum(x['published']=='да' for x in baseline),10)
        self.assertEqual(sum(x['published']=='нет' for x in baseline),10)

    def test_all_gold_citations_have_offline_evidence(self):
        for case in p.json_read(p.ROOT/'data/review/gold.json')['cases']:
            for source in case['sources']:
                self.assertTrue((p.ROOT/source['cache']).is_file(),source['cache'])
                self.assertTrue(source['url'].startswith('https://'))

    def test_submission_table_has_11_required_columns(self):
        with (p.ROOT/'results/preprints_ru.csv').open(encoding='utf-8') as f:
            rows=list(csv.reader(f))
        self.assertEqual(len(rows),201)
        self.assertTrue(all(len(r)==11 for r in rows))

    def test_short_report_and_extended_appendix(self):
        content=(p.ROOT/'results/report_short.pdf').read_bytes()
        self.assertEqual(len(re.findall(rb'/Type\s*/Page\b',content)),2)
        extended=(p.ROOT/'results/report.pdf').read_bytes()
        self.assertEqual(len(re.findall(rb'/Type\s*/Page\b',extended)),8)

    def test_summary_denominators(self):
        m=self.metrics
        self.assertEqual(m['published_n']+m['not_found_n'],200)
        self.assertEqual(sum(m['quartiles'].values()),m['published_n'])
        self.assertEqual(m['published_n'],181)
        self.assertEqual(m['conference_only_n'],2)
        self.assertEqual(m['published_with_known_proceedings_n'],183)
        self.assertAlmostEqual(m['q1_fraction_published'],69/181)
        self.assertEqual(m['exact_delay_n']+m['partial_date_n']+m['publication_before_v1_n'],181)


if __name__=='__main__':unittest.main()
