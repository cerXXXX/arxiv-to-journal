"""Build a matching editable PowerPoint, vector PDF and submission slides."""
import io
import json
import sys
import zipfile
from datetime import datetime

from pipeline import ROOT

W, H = 960, 540
INK, ACCENT, MUTED, GREY, BG = '171717', '23527A', '606060', 'D8D8D8', 'FFFFFF'


def presentation_dependencies():
    # Separate optional wheels leave the original study runtime unchanged.
    dest = ROOT / '.deps' / 'presentation'
    dest.mkdir(exist_ok=True)
    for wheel in sorted((ROOT / 'vendor/presentation-wheels').glob('*.whl')):
        with zipfile.ZipFile(wheel) as archive:
            archive.extractall(dest)
    sys.path.insert(0, str(dest))


def render_presentation(output, metrics, rows):
    presentation_dependencies()
    from pptx import Presentation
    from pptx.util import Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
    from pptx.oxml.xmlchemy import OxmlElement
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase.pdfmetrics import stringWidth

    sections = json.loads((ROOT / 'docs/slides.json').read_text())
    deck = Presentation()
    deck.slide_width, deck.slide_height = Pt(W), Pt(H)
    deck.core_properties.title = 'Путь статьи: от препринта к журналу'
    deck.core_properties.subject = 'Исследование публикаций · hep-th, 2021'
    deck.core_properties.author = 'Publication Study'
    deck.core_properties.created = deck.core_properties.modified = datetime(2000, 1, 1)
    pdf = Canvas(str(output/'presentation.pdf'), pagesize=(W,H), invariant=1)
    pdf.setTitle(deck.core_properties.title)
    pdf.setAuthor('Publication Study')
    slide = None

    def rect(x,y,w,h,color):
        pdf.setFillColor(HexColor('#'+color)); pdf.rect(x,H-y-h,w,h,fill=1,stroke=0)
        shape=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Pt(x),Pt(y),Pt(w),Pt(h))
        shape.fill.solid(); shape.fill.fore_color.rgb=RGBColor.from_string(color)
        shape.line.fill.background()
        shape._element.spPr.append(OxmlElement("a:effectLst"))
        for effect in shape._element.xpath("./p:style/a:effectRef"):
            effect.set("idx", "0")

    def text(x,y,w,value,size=22,bold=False,color=INK,url=None):
        # Manual wrapping by the embedded PDF font gives identical line breaks in both exports.
        font='StudyBold' if bold else 'Study'
        lines=[]
        for para in str(value).split('\n'):
            line=''
            for word in para.split():
                candidate=(line+' '+word).strip()
                if stringWidth(candidate,font,size)>w and line:
                    lines.append(line); line=word
                else: line=candidate
            lines.append(line)
        lineheight=size*1.27
        box=slide.shapes.add_textbox(Pt(x),Pt(y),Pt(w+3),Pt(len(lines)*lineheight+5))
        tf=box.text_frame; tf.clear(); tf.word_wrap=False; tf.vertical_anchor=MSO_ANCHOR.TOP
        tf.auto_size=MSO_AUTO_SIZE.NONE
        tf._txBody.bodyPr.set("anchorCtr", "0")
        tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
        for i,line in enumerate(lines):
            pdf.setFillColor(HexColor('#'+color)); pdf.setFont(font,size)
            pdf.drawString(x,H-y-size-i*lineheight,line)
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
            p.alignment=PP_ALIGN.LEFT
            p.space_before=p.space_after=Pt(0); p.line_spacing=Pt(lineheight)
            run=p.add_run();run.text=line;run.font.name='DejaVu Sans';run.font.size=Pt(size)
            run.font.bold=bold;run.font.color.rgb=RGBColor.from_string(color)
            if url:
                run.hyperlink.address=url;run.font.underline=True
                width=stringWidth(line,font,size)
                pdf.linkURL(url,(x,H-y-size-i*lineheight-2,x+width,H-y-i*lineheight),relative=0)
                pdf.setStrokeColor(HexColor('#'+color));pdf.setLineWidth(.6)
                pdf.line(x,H-y-size-i*lineheight-2,x+width,H-y-size-i*lineheight-2)
        assert y+len(lines)*lineheight < H-10, (value, y, lines)

    def line(x1,y1,x2,y2,color=INK,width=1):
        pdf.setStrokeColor(HexColor('#'+color));pdf.setLineWidth(width)
        pdf.line(x1,H-y1,x2,H-y2)
        shape=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Pt(x1),Pt(y1),Pt(x2),Pt(y2))
        shape.line.color.rgb=RGBColor.from_string(color);shape.line.width=Pt(width)
        shape._element.spPr.append(OxmlElement("a:effectLst"))
        for effect in shape._element.xpath("./p:style/a:effectRef"):
            effect.set("idx", "0")

    exact = sorted(int(row['delay_days']) for row in rows if row['delay_days'] != 'NA')
    cases = {row['arxiv_id']: row for row in rows}
    n = metrics['sample_n']
    published = metrics['published_n']
    proceedings = metrics['conference_only_n']
    unresolved = n-published-proceedings
    q = metrics['quartiles']
    journal_n = metrics['venues']['Journal of High Energy Physics']
    with_doi = [row for row in rows if row['arxiv_doi_present'] == 'да']
    without_doi = [row for row in rows if row['arxiv_doi_present'] != 'да']
    def found(group): return sum(row['published']=='да' for row in group)

    for i,section in enumerate(sections):
        slide=deck.slides.add_slide(deck.slide_layouts[6])
        rect(0,0,W,H,BG)
        text(56,39,848,section['title'],26,True)
        if i==0:
            text(56,100,848,'200 препринтов hep-th · первые версии 2021 года',24)
            text(56,145,848,'Поиск журнальных версий на 5 ноября 2026 года',18,color=MUTED)
            outcomes=[('Журнал',published,f'{published/n*100:.1f}%'.replace('.',',')),
                      ('Только сборник конференции',proceedings,''),
                      ('Журнал или сборник не найдены',unresolved,'')]
            for j,(label,count,percentage) in enumerate(outcomes):
                y=235+j*70
                text(56,y,610,label,24)
                text(700,y,75,count,27,True)
                if percentage:text(795,y,115,percentage,24)
        elif i==1:
            from algorithm import draw
            draw(lambda x,y,w,h,c: rect(x+56,y+115,w,h,c),
                 lambda x,y,w,v,size=18,bold=False: text(x+56,y+115,w,v,size,bold),
                 lambda x,y,xx,yy,color: line(x+56,y+115,xx+56,yy+115,color=color))
        elif i==2:
            text(56,103,848,'Накопленная доля опубликованных работ с точными датами · n = '+str(len(exact)),18,color=MUTED)
            x0,xmax,top,bottom=105,890,167,414
            def xp(day): return x0+(xmax-x0)*day/1350
            def yp(fraction): return bottom-(bottom-top)*fraction
            for fraction,label in [(0,'0'),(.25,'25'),(.5,'50'),(.75,'75'),(1,'100%')]:
                y=yp(fraction)
                text(56,y-10,48,label,14,color=MUTED)
                line(x0-5,y,x0,y,color=MUTED,width=.7)
            line(x0,bottom,xmax,bottom,width=.8)
            line(x0,top,x0,bottom,width=.8)
            for day in [0,365,730,1095]:
                x=xp(day);line(x,bottom,x,bottom+5,width=.8)
                text(x-8,bottom+10,65,day,14,color=MUTED)
            text(853,437,60,'дни',14,color=MUTED)
            # Exact empirical CDF of completed, nonnegative delays; no survival estimate.
            previous=0
            for k,day in enumerate(exact):
                line(xp(previous),yp(k/len(exact)),xp(day),yp(k/len(exact)),width=1.6)
                line(xp(day),yp(k/len(exact)),xp(day),yp((k+1)/len(exact)),width=1.6)
                previous=day
            median=metrics['median_delay_days']
            line(x0,yp(.5),xp(median),yp(.5),color=INK,width=.8)
            line(xp(median),yp(.5),xp(median),bottom,color=INK,width=.8)
            text(xp(median)+13,yp(.5)+17,265,'Медиана — 140 дней',18,True,color=INK)
            text(530,238,355,'Среднее — 200,85 дня',21)
            text(660,192,230,'Максимум — 1 281 день',16,color=MUTED)
        elif i==3:
            text(56,105,848,'181 статья · лучший квартиль журнала · SJR 2025',20,color=MUTED)
            x0,scale=240,5.7
            for j,label in enumerate(['Q1','Q2','Q3','Q4','NA']):
                count=q[label];y=173+j*51
                text(56,y+3,175,'Не установлен' if label=='NA' else label,21)
                if label=='Q2':
                    rect(x0,y,scale*journal_n,30,'777777')
                    rect(x0+scale*journal_n,y,scale*(count-journal_n),30,GREY)
                    text(x0+12,y+3,420,f'JHEP: {journal_n}',18,color='FFFFFF')
                else:rect(x0,y,scale*count,30,INK if label=='Q1' else GREY)
                text(x0+scale*count+14,y,240,f'{count} · 38,1%' if label=='Q1' else count,23,True)
        elif i==4:
            case=cases['2111.07453']
            text(56,108,848,'Ручная проверка: 10 найденных + 10 ненайденных версий',20,color=MUTED)
            text(56,171,848,'Deforming integrable models of AdS3 strings',24,True)
            text(56,232,370,'arXiv',15,color=MUTED)
            text(493,232,370,'Издатель',15,color=MUTED)
            text(56,262,370,'Pawelczyk',30)
            text(493,262,370,'Pawełczyk',30)
            text(56,344,848,'Название, университет и DOI подтвердили совпадение.',21)
            text(56,387,848,'После нормализации ł → l: 0 ошибок на тех же 20 случаях.',21)
            text(56,435,380,'arXiv: 2111.07453',16,color=INK,url='https://arxiv.org/abs/2111.07453')
            text(493,435,410,'Статья · 03.06.2022',16,color=INK,url='https://doi.org/'+case['publication_doi'])
        else:
            text(56,120,848,'У 9 из 10 препринтов найдена журнальная версия.',28,True)
            text(56,183,848,'Половина статей с точными датами вышла за 140 дней.',22)
            limits=[('Область вывода','hep-th · первые версии 2021 года'),
                    ('Среднее время','176 точных дат выхода после arXiv'),
                    ('Ненайденные версии','Могут выйти позже или отсутствовать в базах')]
            for j,(label,detail) in enumerate(limits):
                y=285+j*52
                text(56,y,250,label,17,color=MUTED)
                text(320,y,584,detail,19)
        pdf.bookmarkPage(f'slide-{i+1}');pdf.addOutlineEntry(section['title'],f'slide-{i+1}')
        pdf.showPage()
    pdf.save()
    buffer=io.BytesIO();deck.save(buffer)
    # Zip metadata is fixed so make reproduce can verify bytes, including the PPTX.
    with zipfile.ZipFile(buffer) as source, zipfile.ZipFile(output/'presentation.pptx','w',zipfile.ZIP_DEFLATED) as target:
        for name in sorted(source.namelist()):
            info=zipfile.ZipInfo(name,date_time=(2000,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            target.writestr(info,source.read(name))

    print(f'Built presentation ({len(sections)} slides, PDF + PPTX)')
