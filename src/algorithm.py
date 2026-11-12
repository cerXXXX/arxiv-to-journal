"""One vector algorithm diagram shared by the report and editable slides."""
WIDTH, HEIGHT = 848, 350


def draw(rect, text, line):
    def box(x, y, w, title, body, h=100):
        rect(x,y,w,h,'EEF4F5')
        text(x+12,y+10,w-24,title,18,True)
        text(x+12,y+39,w-24,body,15)

    def arrow(x1,y1,x2,y2):
        line(x1,y1,x2,y2,color='23527A')
        if x1 == x2:
            line(x2-4,y2+(-6 if y2>y1 else 6),x2,y2,color='23527A')
            line(x2+4,y2+(-6 if y2>y1 else 6),x2,y2,color='23527A')
        else:
            line(x2-6,y2-4,x2,y2,color='23527A')
            line(x2-6,y2+4,x2,y2,color='23527A')

    box(0,0,258,'1 · Данные и выборка','arXiv 2021: 7 127 → 3 770\nОсновная hep-th → 200\nОтбор по SHA256; версия v1')
    box(295,0,258,'2 · Кандидаты','DOI arXiv + INSPIRE\nЕсли не найдено: поиск\nCrossref / OpenAlex, top-5')
    box(590,0,258,'3 · Совпадение?','Журнал; дата ≤ среза\nИдентификаторы + авторы\nИли название + авторы')
    arrow(258,50,295,50); arrow(553,50,590,50)
    line(719,100,719,120,color='23527A')
    line(424,120,719,120,color='23527A')
    arrow(424,120,424,150);arrow(719,120,719,150)
    text(435,123,180,'нет / неоднозначно',13)
    text(730,123,100,'да',13)
    box(295,150,258,'4б · Не найдено: 19','Статус сохраняется\nПоля публикации: NA\nНе означает «никогда»')
    box(590,150,258,'4а · Найдено: 181','Дата статьи − дата v1\nТочные ≥ 0 дней: 176\nЖурнал → SJR 2025 → Q')
    box(0,150,258,'5 · Проверка','Ручная сверка 10 + 10\nИсправить правило,\nповторить сопоставление')
    line(129,150,129,120,color='23527A');line(129,120,277,120,color='23527A')
    line(277,120,277,50,color='23527A');arrow(277,50,295,50)
    for x in [424,719]: arrow(x,250,x,285)
    arrow(129,285,129,250)
    box(0,285,848,'6 · Итог: таблица 200 работ → статистика → отчёт и презентация',
        'Доля журналов: 181/200 · среднее и медиана: n = 176 · доля Q1: 69/181',65)


def export(output):
    from charts import SVG, PDF
    from reportlab.pdfgen.canvas import Canvas
    def paint(renderer):
        def text(x,y,w,value,size=18,bold=False):
            for i,s in enumerate(value.split('\n')):
                renderer.text(x,y+size+i*size*1.27,s,size=size,bold=bold)
        draw(lambda x,y,w,h,c: renderer.rect(x,y,w,h,'#'+c),text,
             lambda x,y,xx,yy,color: renderer.line(x,y,xx,yy,'#'+color))
    svg=SVG(WIDTH,HEIGHT);paint(svg);svg.save(output/'figures/algorithm.svg')
    c=Canvas(str(output/'figures/algorithm.pdf'),pagesize=(WIDTH,HEIGHT),invariant=1)
    paint(PDF(c,HEIGHT));c.showPage();c.save()
