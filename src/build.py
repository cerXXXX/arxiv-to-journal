"""Single offline build entry point."""
import os

os.environ['SOURCE_DATE_EPOCH'] = '946684800'
from bootstrap import bootstrap
bootstrap()

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pipeline import ROOT, run
from charts import export_figures
from report import render


def build(output=None):
    pdfmetrics.registerFont(TTFont('Study',str(ROOT/'vendor/fonts/DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('StudyBold',str(ROOT/'vendor/fonts/DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFontFamily('Study',normal='Study',bold='StudyBold',italic='Study',boldItalic='StudyBold')
    rows,metrics,evaluation=run(output)
    output=ROOT/'results' if output is None else output
    export_figures(output,rows,metrics)
    from algorithm import export
    export(output)
    render(output,rows,metrics,evaluation)
    from presentation import render_presentation
    render_presentation(output,metrics,rows)
    print('Built CSV, statistics, figures, report.pdf, report.md and presentation')


if __name__=='__main__':
    build()
