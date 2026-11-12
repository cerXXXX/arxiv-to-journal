"""Publication figures generated from the exported numeric tables."""
import csv
import html
import math
from pathlib import Path

PALETTE = ['#237d8d', '#86b8bd', '#b6cbd0', '#d0b38e', '#b6b9c0']
INK, MUTED, GRID = '#18343d', '#546a73', '#dce5e8'


class SVG:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                      '<rect width="100%" height="100%" fill="white"/>']

    def rect(self, x, y, w, h, fill):
        self.parts.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{fill}"/>')

    def line(self, x1, y1, x2, y2, color=GRID):
        self.parts.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}"/>')

    def text(self, x, y, text, size=12, color=INK, anchor='start', bold=False):
        self.parts.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="DejaVu Sans, sans-serif" font-size="{size}" '
                          f'font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{html.escape(str(text))}</text>')

    def save(self, path):
        path.write_text('\n'.join(self.parts + ['</svg>']) + '\n', encoding='utf-8')


class PDF:
    def __init__(self, canvas, height):
        self.c, self.h = canvas, height

    def rect(self, x, y, w, h, fill):
        from reportlab.lib.colors import HexColor
        self.c.setFillColor(HexColor(fill))
        self.c.rect(x, self.h-y-h, w, h, fill=1, stroke=0)

    def line(self, x1, y1, x2, y2, color=GRID):
        from reportlab.lib.colors import HexColor
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(.6)
        self.c.line(x1, self.h-y1, x2, self.h-y2)

    def text(self, x, y, text, size=12, color=INK, anchor='start', bold=False):
        from reportlab.lib.colors import HexColor
        self.c.setFillColor(HexColor(color))
        self.c.setFont('StudyBold' if bold else 'Study', size)
        draw = self.c.drawCentredString if anchor == 'middle' else self.c.drawRightString if anchor == 'end' else self.c.drawString
        draw(x, self.h-y, str(text))


def bars(p, labels, values, title, subtitle, width=700, height=250):
    p.text(24, 25, title, 16, bold=True)
    p.text(24, 45, subtitle, 10, color=MUTED)
    x0, y0, bottom, span = 45, 70, height-40, width-70
    max_v = max(values) or 1
    tick = 20 if max_v <= 80 else 25
    limit = math.ceil(max_v * 1.12 / tick) * tick
    for value in range(0, limit + 1, tick):
        y = bottom-(bottom-y0)*value/limit
        p.line(x0, y, width-18, y)
        p.text(x0-8, y+3, value, 11, MUTED, anchor='end')
    step = span/len(labels)
    for i, (label, value) in enumerate(zip(labels, values)):
        h = (bottom-y0)*value/limit
        x = x0+step*i+step*.2
        p.rect(x, bottom-h, step*.6, h, ('#a7b5bd' if label in ('NA', 'Нет в SJR', 'Нет данных') else '#237d8d'))
        p.text(x+step*.3, bottom-h-6, value, 12, anchor='middle', bold=True)
        p.text(x+step*.3, bottom+18, label, 12, anchor='middle')


def funnel(p, metrics, width=700, height=320):
    p.text(24, 25, 'Отбор выборки и результаты поиска', 16, bold=True)
    stages = [
        ('Выгрузка arXiv с hep-th, включая cross-list', str(metrics['frame_including_crosslists'])),
        ('Основная категория hep-th · исключены 3 357 cross-list', str(metrics['frame_primary'])),
        ('Отобраны по хешу · остальные 3 570 не изучаются', str(metrics['sample_n'])),
    ]
    for i,(label,n) in enumerate(stages):
        y=43+i*43
        p.rect(24,y,652,34,'#eef4f5')
        p.text(36,y+22,label,11)
        p.text(664,y+23,n,16,anchor='end',bold=True)
        p.text(350,y+41,'↓',10,MUTED,anchor='middle')
    p.rect(24,178,315,46,'#dcebed')
    p.rect(355,178,321,46,'#f1e9dd')
    p.text(36,198,'Журнальная версия: 181 / 200',13,bold=True)
    p.text(36,215,'90,5% выборки',10)
    p.text(367,198,'Не установлена: 19 / 200',13,bold=True)
    p.text(367,215,'В том числе 2 сборника',10)
    p.line(180,224,180,242)
    p.line(180,242,508,242)
    p.line(508,242,508,251)
    p.line(180,242,180,251)
    p.rect(24,252,315,43,'#eef4f5')
    p.rect(355,252,321,43,'#eef4f5')
    p.text(36,271,'Анализ задержки: 176 точных',12,bold=True)
    p.text(36,287,'4 даты до месяца + 1 выход до arXiv',10)
    p.text(367,271,'Анализ квартилей: 69 Q1 / 181',12,bold=True)
    p.text(367,287,'Отдельный показатель; не следующий фильтр',10)


def figure_data(rows, metrics):
    delays = [int(r['delay_days']) for r in rows if r['delay_days'] != 'NA']
    edges = [(0, 90), (90, 180), (180, 365), (365, 730), (730, 100000)]
    bins = [sum(lo <= x < hi for x in delays) for lo, hi in edges]
    qs = [metrics['quartiles'].get(q, 0) for q in ['Q1','Q2','Q3','Q4','NA']]
    return bins, qs


def export_figures(output, rows, metrics):
    from reportlab.pdfgen.canvas import Canvas
    output = Path(output)
    folder = output/'figures'
    folder.mkdir(exist_ok=True)
    bins, qs = figure_data(rows, metrics)
    specs = [('delay_histogram', ['0–89','90–179','180–364','365–729','730+'], bins,
              'Задержка до журнальной публикации', f"{metrics['exact_delay_n']} работ с точными датами; интервалы — в днях"),
             ('quartiles', ['Q1','Q2','Q3','Q4','Нет в SJR'], qs,
              'Квартили журналов SJR 2025', f"{metrics['published_n']} публикация; лучший квартиль журнала")]
    for name, labels, values, title, subtitle in specs:
        svg = SVG(700, 250)
        bars(svg, labels, values, title, subtitle)
        svg.save(folder/(name+'.svg'))
        canvas = Canvas(str(folder/(name+'.pdf')), pagesize=(700,250), invariant=1, pageCompression=1)
        canvas.setTitle(title)
        bars(PDF(canvas,250), labels, values, title, subtitle)
        canvas.save()
        with (output/(name+'_data.csv')).open('w',encoding='utf-8',newline='') as f:
            writer=csv.writer(f,lineterminator='\n');writer.writerow(['group','n']);writer.writerows(zip(labels,values))
    svg=SVG(700,320);funnel(svg,metrics);svg.save(folder/'publication_funnel.svg')
    canvas=Canvas(str(folder/'publication_funnel.pdf'),pagesize=(700,320),invariant=1,pageCompression=1)
    canvas.setTitle('Publication study funnel');funnel(PDF(canvas,320),metrics);canvas.save()
