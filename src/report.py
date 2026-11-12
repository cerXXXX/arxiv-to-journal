"""A short report, an extended report and review notes, compiled from calculated statistics."""
import html
import re
from pathlib import Path

from pipeline import ROOT, json_read


def pct(value):
    return f'{100*value:.1f}'.replace('.', ',') + '%'


def text_blocks(metrics, evaluation, rows):
    m = metrics
    a = evaluation['groups']['audit20']
    controls = [
        ['Смена названия', '<a href="https://arxiv.org/abs/2105.01130">Препринт 2105.01130</a> → <a href="https://doi.org/10.1088/1361-6382/ac51e7">статья в Classical and Quantum Gravity</a>, 03.03.2022. Название изменилось; связь подтверждена по arXiv ID.'],
        ['Смена названия и проверка даты', '<a href="https://arxiv.org/abs/2112.15592">Препринт 2112.15592</a> → <a href="https://www.actaphys.uj.edu.pl/R/54/6-A2">статья в Acta Physica Polonica B</a>, 11.07.2023. Название изменилось; дата проверена в тексте статьи.'],
        ['Нет DOI в arXiv', '<a href="https://arxiv.org/abs/2104.11336">Препринт 2104.11336</a> → <a href="https://scipost.org/SciPostPhysCore.4.3.020">статья в SciPost Physics Core</a>, 09.09.2021. DOI найден в INSPIRE по arXiv ID.'],
        ['Похожие работы', '<a href="https://arxiv.org/abs/2107.01371">Препринт 2107.01371</a>. У похожих работ другие авторы или arXiv ID. Совпадения отклонены; журнальная версия не найдена.'],
        ['Два названия, нет статьи', '<a href="https://arxiv.org/abs/2104.14434">Препринт 2104.14434</a>. Is quantum time the classical time? сменилось на Quantum f(R) gravity and AdS/CFT. Проверены оба названия и INSPIRE; журнальная версия не найдена.'],
    ]
    return [
        ('title', 'Путь статьи: от препринта к журналу'),
        ('subtitle', 'Теоретическая физика высоких энергий (hep-th) · первые версии за 2021 год · данные на 05.11.2026'),
        ('p', 'Для 200 случайных препринтов оценены доля журнальных публикаций, срок выхода и доля Q1.'),
        ('h', 'Главные результаты'),
        ('summary', [
            ['Вышли в журналах', f'{m["published_n"]} из {m["sample_n"]} · {pct(m["published_fraction"])}'],
            ['Время до публикации', f'В среднем {m["mean_delay_days"]:.2f} дня; медиана {m["median_delay_days"]:.0f} дней'.replace('.', ',')],
            ['Вышли в журналах Q1', f'{m["q1_n"]} из {m["published_n"]} · {pct(m["q1_fraction_published"])}'],
        ]),
        ('p', 'Среднее и медиана — по 176 точным задержкам. Q1 — верхняя четверть журналов SJR; доля Q1 среди всех 200 работ — 34,5%, среди опубликованных — 38,1%.'),
        ('h', 'Как проведено исследование'),
        ('algorithm', None),
        ('p', '<b>Отбор.</b> Сортировать arXiv ID основной hep-th за 2021 год по SHA256("hep-th-2021-publication-study-v1:" + ID); взять первые 200. Сохранить дату UTC, авторов и название v1, а также последнее название. Для ненайденных версий взять top-5 Crossref и OpenAlex по каждому из двух названий; DOI раскрыть через Crossref (при отсутствии записи — метаданные INSPIRE).'),
        ('p', '<b>Правило совпадения.</b> Нормализовать регистр, диакритику (включая ł → l), формулы и пунктуацию. A = общие фамилии / число фамилий меньшего множества. Dice = 2|X ∩ Y|/(|X| + |Y|) для множеств слов. T = 0,65 × Dice + 0,35 × SequenceMatcher строк (autojunk=False); взять максимум для v1 и последнего названия. S = 0,75T + 0,25A. Прямая связь: A ≥ 0,5; для DOI arXiv также T ≥ 0,45, для связи INSPIRE по arXiv ID порога T нет. Поиск по названию: T ≥ 0,88, A ≥ 0,5, S ≥ 0,85; отрыв от следующего журнального кандидата с A ≥ 0,5 — не менее 0,05. Приоритет: прямая связь, затем S, затем DOI по алфавиту.'),
        ('p', '<b>Фильтры и расчёт.</b> Только journal-article; исключить исправления, ретракции, сборники и refereed=false. Дата должна быть известна и весь её интервал — не позже 05.11.2026. Приоритет даты: исходный imprint при смене DOI; явная online-дата издателя; online Crossref; точный imprint INSPIRE; published / published-print / issued Crossref; неполный imprint. created/deposited не использовать. Задержка — дата статьи минус дата v1: 4 неполные даты дают интервалы, 1 отрицательная разность хранится отдельно; в среднем только 176 точных неотрицательных значений. SJR 2025: ISSN/eISSN, иначе точное нормализованное название; лучший квартиль, при отсутствии — NA.'),
        ('pagebreak', None),
        ('h', 'Что показала ручная проверка'),
        ('p', f'Отдельно выбраны и проверены 10 работ, для которых программа нашла статью, и 10, для которых не нашла. Сверены arXiv, INSPIRE и данные издателей. Найдена <b>{a["baseline_errors"]} ошибка из 20</b>: фамилии Pawelczyk и Pawełczyk программа приняла за разные и пропустила статью. После исправления обработки буквы ł осталось <b>{a["errors"]} ошибок на тех же 20 работах</b>. Это повторная проверка после исправления, поэтому она не доказывает отсутствие ошибок во всей выборке.'),
        ('h', 'Контрольные примеры: три найденные статьи и два трудных случая'),
        ('table', controls),
        ('h', 'Пять спорных случаев: что решено и почему'),
        ('p', '<b>1. Изменился DOI — <a href="https://arxiv.org/abs/2111.05295">2111.05295</a>.</b> У статьи появился новый DOI. В новой записи Crossref указано 01.01.2021, а в исходных данных издателя, сохранённых в INSPIRE, — 28.12.2021. Принята дата 28 декабря; новый DOI сохранён. Для расчёта использована исходная дата выхода.'),
        ('p', '<b>2. Статья вышла до arXiv — <a href="https://arxiv.org/abs/2109.03271">2109.03271</a>.</b> <a href="https://www.mdpi.com/2624-8174/3/3/35">Издатель</a> указывает 02.08.2021, первая версия arXiv подана 07.09.2021. Статья учтена как опубликованная. Разность −36 дней сохранена отдельно, но исключена из среднего времени ожидания после препринта.'),
        ('p', '<b>3. Найден сборник, а не журнал — <a href="https://arxiv.org/abs/2104.03350">2104.03350</a>.</b> Доклад вышел в <a href="https://pos.sissa.it/390/042/">PoS ICHEP2020</a>. В Crossref он отмечен как материал конференции. По выбранному правилу в долю журнальных публикаций он не входит; в расчёте со сборниками учитывается.'),
        ('p', '<b>4. Известен только месяц — <a href="https://arxiv.org/abs/2102.02253">2102.02253</a>.</b> Статья вышла в Nuclear Physics B в ноябре 2021 года. Задержка составляет 271–300 дней. Точное значение не указано: подстановка первого числа месяца создала бы ложную точность.'),
        ('p', '<b>5. Разное написание фамилии — <a href="https://arxiv.org/abs/2111.07453">2111.07453</a>.</b> У Pawelczyk и Pawełczyk совпадают название статьи, университет и DOI. Это один автор. После исправления сравнения фамилий статья найдена: она вышла 03.06.2022, через 201 день. Именно этот пропуск обнаружен при проверке 20 работ.'),
        ('h', 'Вывод и границы результата'),
        ('p', 'К дате сбора журнальная статья найдена примерно у девяти из десяти препринтов этой выборки. «Не найдено» не значит «никогда не опубликовано»: оставшиеся работы могут выйти позже или отсутствовать в изученных базах. Метод также может пропустить статью, если название сильно изменилось и нет связи по идентификаторам, либо один препринт разделился на несколько статей.'),
        ('p', 'Средняя задержка описывает только найденные публикации с точными датами; это не время рецензирования. Квартиль характеризует журнал и не даёт оценки качества отдельной статьи. Журналы добавляют экспертную проверку, редакционную ответственность и официальную версию для цитирования.'),
        ('small', 'Источники: <a href="https://arxiv.org">arXiv</a>, <a href="https://inspirehep.net">INSPIRE-HEP</a>, <a href="https://www.crossref.org">Crossref</a>, <a href="https://openalex.org">OpenAlex</a>, издатели; SJR 2025 — сохранённые копии справочника SCImago. Таблица: results/preprints_ru.csv. Пересчёт: make reproduce в корне проекта (Python 3.12, Linux x86_64, make; без сети). Подробная методика и проверки — в полном отчёте results/report.pdf (приложения А–Е) и коде.'),
    ]


def to_markdown(blocks):
    def md_links(s):
        s = re.sub(r'<a href="([^"]+)">([^<]+)</a>', r'[\2](\1)', s)
        return s.replace('<b>','**').replace('</b>','**')
    output=[]
    heading_index = 0
    for kind, value in blocks:
        if kind in ('title', 'h', 'atitle'):
            output.append(f'<a id="section-{heading_index}"></a>')
            heading_index += 1
        if kind == 'title': output.append('# '+value)
        elif kind in ['h','ah']: output.append('## '+value)
        elif kind == 'atitle': output.append('# '+value)
        elif kind in ['p','small','subtitle','ap']: output.append(md_links(value))
        elif kind == 'algorithm': output.append('![Алгоритм исследования](figures/algorithm.svg)')
        elif kind == 'pagebreak': output.append('<!-- pagebreak -->')
        elif kind == 'charts':
            output.extend(['![Задержка](figures/delay_histogram.svg)', '![Квартили SJR 2025](figures/quartiles.svg)'])
        elif kind == 'funnel': output.append('![Отбор и исходы](figures/publication_funnel.svg)')
        elif kind == 'large_delay': output.append('![Распределение задержек](figures/delay_histogram.svg)')
        elif kind == 'large_quartiles': output.append('![Квартили](figures/quartiles.svg)')
        elif kind in ['table','atable','summary']:
            header = ['Особенность случая', 'Результат и подтверждение'] if kind == 'table' else ['Показатель', 'Результат'] if kind == 'summary' else value[0]
            data = value[1:] if kind == 'atable' else value
            output.append('| '+' | '.join(header)+' |\n|'+'|'.join('---' for _ in header)+'|\n'+'\n'.join('| '+' | '.join(md_links(x) for x in row)+' |' for row in data))
    return '\n\n'.join(output)+'\n'


def make_pdf(path, blocks, rows, metrics):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen.canvas import Canvas
    from charts import bars, PDF, figure_data
    styles={
        'title':ParagraphStyle('title',fontName='StudyBold',fontSize=17,leading=21,spaceAfter=7,textColor=HexColor('#18343d')),
        'subtitle':ParagraphStyle('subtitle',fontName='Study',fontSize=8,leading=10,spaceAfter=9,textColor=HexColor('#546a73')),
        'h':ParagraphStyle('heading',fontName='StudyBold',fontSize=10.3,leading=13,spaceBefore=8,spaceAfter=4,textColor=HexColor('#237d8d'),keepWithNext=True),
        'p':ParagraphStyle('body',fontName='Study',fontSize=9.7,leading=13.1,spaceAfter=6),
        'small':ParagraphStyle('small',fontName='Study',fontSize=8,leading=10.5,spaceBefore=5),
        'atitle':ParagraphStyle('appendix_title',fontName='StudyBold',fontSize=17,leading=22,spaceAfter=14,textColor=HexColor('#18343d')),
        'ah':ParagraphStyle('appendix_heading',fontName='StudyBold',fontSize=12,leading=16,spaceBefore=12,spaceAfter=7,textColor=HexColor('#237d8d'),keepWithNext=True),
        'ap':ParagraphStyle('appendix_body',fontName='Study',fontSize=10,leading=14.3,spaceAfter=9),
        'acell':ParagraphStyle('appendix_cell',fontName='Study',fontSize=9,leading=12),
        'cell':ParagraphStyle('cell',fontName='Study',fontSize=9,leading=11.6)
    }
    # Use one embedded font family for body, links and bold spans.
    class Algorithm(Flowable):
        def __init__(self):
            super().__init__()
            self.width, self.height = 508, 218
        def draw(self):
            from algorithm import draw
            from charts import PDF
            self.canv.saveState(); self.canv.scale(508/848,508/848)
            renderer=PDF(self.canv,350)
            def text(x,y,w,value,size=18,bold=False):
                for i,s in enumerate(value.split('\n')):
                    renderer.text(x,y+size+i*size*1.27,s,size=size,bold=bold)
            draw(lambda x,y,w,h,c: renderer.rect(x,y,w,h,'#'+c), text,
                 lambda x,y,xx,yy,color: renderer.line(x,y,xx,yy,'#'+color))
            self.canv.restoreState()

    class PairCharts(Flowable):
        def __init__(self):
            super().__init__()
            self.width, self.height = 508, 100
        def draw(self):
            bins,qs=figure_data(rows,metrics)
            self.canv.saveState();self.canv.scale(.36,.36)
            bars(PDF(self.canv,250),['0–89','90–179','180–364','365–729','730+'],bins,'Задержка, дни','176 точных прямых задержек')
            self.canv.translate(710,0)
            bars(PDF(self.canv,250),['Q1','Q2','Q3','Q4','Нет данных'],qs,'SJR 2025','181 журнальная публикация')
            self.canv.restoreState()
    class LargeFigure(Flowable):
        def __init__(self, kind):
            super().__init__()
            self.kind = kind
            self.width = 508
            self.height = 230 if kind == 'funnel' else 188
        def draw(self):
            from charts import funnel
            self.canv.saveState()
            self.canv.scale(508/700,508/700)
            bins,qs=figure_data(rows,metrics)
            if self.kind == 'funnel':
                funnel(PDF(self.canv,320),metrics)
            elif self.kind == 'large_delay':
                bars(PDF(self.canv,250),['0–89','90–179','180–364','365–729','730+'],bins,
                     'От первой версии до выхода статьи','176 работ с точными датами; интервалы — в днях')
            else:
                bars(PDF(self.canv,250),['Q1','Q2','Q3','Q4','Нет данных'],qs,
                     'Квартили журналов · SJR 2025','Число работ; все 181 журнальная публикация')
            self.canv.restoreState()
    def paragraph(text, style):
        # A visible link treatment remains identifiable in grayscale printouts.
        text = re.sub(r'<a href="([^"]+)">(.*?)</a>',
                      r'<a href="\1" color="#186b83"><u>\2</u></a>', text)
        for token in ('journal_ref', 'refereed=false', 'refereed=true', 'normalized',
                      'autojunk=False', 'difflib.SequenceMatcher', 'delay_days',
                      'published-online', 'published-print', 'primary_category',
                      'created', 'deposited', 'imprint', 'issued', 'family'):
            text = re.sub(r'(?<![\w/])' + re.escape(token) + r'(?![\w/])',
                          lambda match: '<font name="Courier">' + match[0] + '</font>', text)
        return Paragraph(text, style)

    class ReportDocument(SimpleDocTemplate):
        def afterFlowable(self, flowable):
            if isinstance(flowable, Paragraph) and flowable.style.name in ('title', 'heading', 'appendix_title'):
                key = getattr(flowable, 'navigation_key', None)
                if key:
                    self.canv.bookmarkPage(key)
                    self.canv.addOutlineEntry(flowable.getPlainText(), key, level=0)

    story=[]
    heading_index = 0
    for kind, value in blocks:
        if kind in styles and kind not in ['cell','acell']:
            item = paragraph(value, styles[kind])
            if kind in ('title', 'h', 'atitle'):
                item.navigation_key = f'section-{heading_index}'
                heading_index += 1
            story.append(item)
        elif kind == 'pagebreak':story.append(PageBreak())
        elif kind == 'algorithm':story.append(Algorithm())
        elif kind == 'charts':story.append(PairCharts())
        elif kind in ['funnel','large_delay','large_quartiles']:story.append(LargeFigure(kind))
        elif kind == 'atable':
            widths = [220,288] if len(value[0]) == 2 else [240,140,128] if len(value[0]) == 3 else [235,91,91,91]
            table=Table([[Paragraph(html.escape(x),styles['acell']) for x in row] for row in value],colWidths=widths,hAlign='LEFT',repeatRows=1)
            table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),HexColor('#dcebed')),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#f1f5f5'),HexColor('#ffffff')]),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
            story.append(table)
        elif kind == 'summary':
            values = [pct(metrics['published_fraction']),
                      f"{metrics['mean_delay_days']:.2f}".replace('.', ',') + ' дня',
                      pct(metrics['q1_fraction_published'])]
            details = [f"{metrics['published_n']} из {metrics['sample_n']} препринтов",
                       f"Медиана — {metrics['median_delay_days']:.0f} дней",
                       f"{metrics['q1_n']} из {metrics['published_n']} публикации"]
            card_style = ParagraphStyle('metric', fontName='Study', fontSize=9,
                                        leading=14, textColor=HexColor('#18343d'))
            number_style = ParagraphStyle('metric_number', fontName='StudyBold', fontSize=22,
                                          leading=29, textColor=HexColor('#18343d'))
            cells = [[paragraph(row[0], card_style), paragraph(number, number_style),
                      paragraph(detail, card_style)]
                     for row, number, detail in zip(value, values, details)]
            table = Table([cells], colWidths=[169,170,169], hAlign='LEFT')
            table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                ('BACKGROUND',(0,0),(-1,-1),HexColor('#eef4f5')),
                ('LINEBEFORE',(1,0),(-1,-1),3,HexColor('#ffffff')),
                ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),8),
                ('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12)]))
            story.extend([table, Spacer(1,9)])
        elif kind == 'table':
            cells=[[paragraph(x,styles['cell']) for x in row] for row in value]
            table=Table(cells,colWidths=[104,404],hAlign='LEFT')
            table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),
                                      ('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),
                                      ('BOTTOMPADDING',(0,0),(-1,-1),4),('ROWBACKGROUNDS',(0,0),(-1,-1),[HexColor('#eef4f5'),HexColor('#ffffff')])]))
            story.append(table)
    def footer(c,doc):
        c.setStrokeColor(HexColor('#237d8d'));c.setLineWidth(2);c.line(43,823,552,823)
        c.setFont('Study',7);c.setFillColor(HexColor('#546a73'))
        c.drawString(43,23,'hep-th · первая версия 2021 · срез 05.11.2026')
        c.drawRightString(552,23,str(doc.page))
    doc=ReportDocument(str(path),pagesize=(595.276,841.89),leftMargin=43,rightMargin=43,topMargin=30,bottomMargin=35,
                          title='Путь статьи: от препринта к журналу',author='Publication Study',creator='Publication Study 1.0')
    def canvas_maker(*args, **kwargs):
        kwargs.update(invariant=1, pageCompression=1)
        return Canvas(*args, **kwargs)
    doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=canvas_maker)


def make_review_markdown(output):
    gold=json_read(ROOT/'data/review/gold.json')
    text=['# Подробная перекрестная проверка',gold['selection'],gold['independence']]
    for case in gold['cases']:
        text.append('## '+case['arxiv_id']+' — '+('журнальная версия подтверждена' if case['expected_published'] else 'журнальная версия не установлена'))
        text.extend(['Группы: '+', '.join(case['groups'])+'.',case['assessment']])
        text.append('\n'.join('- ['+s['supports']+']('+s['url']+') — `'+s['cache']+'`' for s in case['sources']))
    (output/'review_cases.md').write_text('\n\n'.join(text)+'\n',encoding='utf-8')


def render(output,rows,metrics,evaluation):
    blocks=text_blocks(metrics,evaluation,rows)
    (output/'report.md').write_text(to_markdown(blocks),encoding='utf-8')
    make_pdf(output/'report_short.pdf',blocks,rows,metrics)
    (output/'report_short.md').write_text(to_markdown(blocks),encoding='utf-8')
    from report_appendix import appendix_blocks
    extended=blocks+appendix_blocks(metrics)
    (output/'report.md').write_text(to_markdown(extended),encoding='utf-8')
    make_pdf(output/'report.pdf',extended,rows,metrics)
    make_review_markdown(output)
