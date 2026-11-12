# Подробная перекрестная проверка

Первичные 10 положительных и 10 отрицательных предсказаний выбраны по первым SHA256(audit-v1:arxiv_id) внутри каждого исходного слоя. Дополнительные 3+2 и 5 спорных случаев выбраны целенаправленно.

Эталон использован для исправления нормализации фамилий; текущая оценка не является независимым тестом. Отрицательные вердикты ограничены доступными источниками.

## 2101.05879 — журнальная версия не установлена

Группы: audit20, audit_initial_not_found.

Для Anna Karlsson сохранены arXiv, INSPIRE и поиски двух агрегаторов. Родственные статьи Replica wormholes ... написаны другими авторами; их нельзя подставлять вместо данного критического препринта. Журнальная версия не установлена.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2101.05879) — `data/raw/pages/arxiv_2101.05879.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2101.05879&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2101.05879.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Concerns+about+the+replica+wormhole+derivation+of+the+island+conjecture&rows=5) — `data/raw/crossref/search_2101.05879.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Concerns+about+the+replica+wormhole+derivation+of+the+island+conjecture&per-page=5) — `data/raw/openalex/search_2101.05879.json`

## 2101.10978 — журнальная версия подтверждена

Группы: audit20, audit_initial_published.

Метаданные APS, переданные в Crossref, указывают Riccardo D’Auria и Lucrezia Ravera, Phys. Rev. D 104, 084034, 04.10.2021. Удаление Super из названия подтверждается историей названий INSPIRE; это та же работа.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2101.10978) — `data/raw/pages/arxiv_2101.10978.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2101.10978&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2101.10978.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1103/physrevd.104.084034) — `data/raw/crossref/doi_958baa71b7632df77485.json`

## 2102.02253 — журнальная версия подтверждена

Группы: disputed5.

Авторы Alexey Sharapov / Evgeny Skvortsov, название Higher Spin Gravities and Presymplectic AKSZ Models, NPB 972, 115551 и DOI согласуются между arXiv, INSPIRE и Crossref. Дата только 2021-11; в таблице сохранен месяц и интервал задержки, точное среднее не получает выдуманный день.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2102.02253) — `data/raw/pages/arxiv_2102.02253.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2102.02253&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2102.02253.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1016/j.nuclphysb.2021.115551) — `data/raw/crossref/doi_2f45e8461bef2ac278c0.json`

## 2103.08231 — журнальная версия подтверждена

Группы: audit20, audit_initial_published.

Четверка Buchbinder / Krykhtin / Tsulaia / Weissman и формула N=1 подтверждают тождество. В издательском Crossref есть том 967 и статья 115427, но дата только июнь 2021. Точный день не восстанавливается искусственно.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2103.08231) — `data/raw/pages/arxiv_2103.08231.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2103.08231&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2103.08231.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1016/j.nuclphysb.2021.115427) — `data/raw/crossref/doi_60939c38ca51b96dbf70.json`

## 2104.00281 — журнальная версия подтверждена

Группы: audit20, audit_initial_published.

Страница Springer, DOI и авторы Shouvik Datta / Yunfeng Jiang совпадают с arXiv. Проверен раздел дат публикации: 22.07.2021, а не дата получения рукописи.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2104.00281) — `data/raw/pages/arxiv_2104.00281.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2104.00281&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2104.00281.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1007/jhep07(2021)162) — `data/raw/crossref/doi_3b0dffc3ec1d6f8d362c.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://doi.org/10.1007/jhep07(2021)162) — `data/raw/pages/publisher_2104.00281.json`

## 2104.03350 — журнальная версия не установлена

Группы: disputed5.

Страница PoS подтверждает доклад P. Sułkowski в ICHEP2020, DOI 10.22323/1.390.0042. Это proceedings-article; из журнальной метрики исключен по заранее выбранному правилу, хотя существование публикации в сборнике подтверждено. В отдельной чувствительности конференции учитываются.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2104.03350) — `data/raw/pages/arxiv_2104.03350.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2104.03350&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2104.03350.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Quantum+fields%2C+strings%2C+and+physical+mathematics&rows=5) — `data/raw/crossref/search_2104.03350.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Quantum+fields%2C+strings%2C+and+physical+mathematics&per-page=5) — `data/raw/openalex/search_2104.03350.json`

## 2104.06587 — журнальная версия подтверждена

Группы: audit20, audit_initial_published.

Страница IOP прямо перечисляет Goodhew / Jazayeri / Lee / Pajer и Published 2 August 2021. Журнальная версия JCAP 08 (2021) 003 совпадает с arXiv, индекс в названии не используется для вывода о публикации.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2104.06587) — `data/raw/pages/arxiv_2104.06587.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2104.06587&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2104.06587.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1088/1475-7516/2021/08/003) — `data/raw/crossref/doi_36529b455019c2d21d4a.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://doi.org/10.1088/1475-7516/2021/08/003) — `data/raw/pages/publisher_2104.06587.json`

## 2104.11336 — журнальная версия подтверждена

Группы: control_published.

В arXiv нет прямого DOI, но точная запись INSPIRE связывает препринт с 10.21468/SciPostPhysCore.4.3.020. Сверены автор Benjamin Knorr, длинное название о derivative expansion, журнальные данные SciPost Physics Core и метаданные издателя в Crossref; 09.09.2021.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2104.11336) — `data/raw/pages/arxiv_2104.11336.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2104.11336&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2104.11336.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.21468/scipostphyscore.4.3.020) — `data/raw/crossref/doi_38f0d914a832485da7e9.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://scipost.org/SciPostPhysCore.4.3.020) — `data/raw/pages/publisher_scipost_2104.11336.json`

## 2104.14434 — журнальная версия не установлена

Группы: control_difficult.

Название между v1 Is quantum time the classical time? и последней версией Quantum f(R) gravity and AdS/CFT резко изменилось. В обеих версиях указан M. Bousder. Проверены оба названия; точная запись INSPIRE и результаты Crossref/OpenAlex не дают журнальной версии. Это пример предела поиска по старому названию.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2104.14434) — `data/raw/pages/arxiv_2104.14434.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2104.14434&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2104.14434.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Quantum+f%28R%29+gravity+and+AdS%2FCFT&rows=5) — `data/raw/crossref/search_2104.14434.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Is+quantum+time+the+classical+time%3F&rows=5) — `data/raw/crossref/first_title_2104.14434.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Quantum+f%28R%29+gravity+and+AdS%2FCFT&per-page=5) — `data/raw/openalex/search_2104.14434.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Is+quantum+time+the+classical+time%3F&per-page=5) — `data/raw/openalex/first_title_2104.14434.json`

## 2105.01130 — журнальная версия подтверждена

Группы: control_published.

Название v1 Double Holography as a Model for Black Hole Complementarity полностью сменилось на Homology conditions for RT surfaces in double holography. Точная связь по arXiv в INSPIRE и DOI IOP, тот же состав авторов и тема; 03.03.2022, задержка 304 дня. Издательская страница временами возвращает CAPTCHA; основа проверки — переданные издателем DOI-метаданные и история версий.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2105.01130) — `data/raw/pages/arxiv_2105.01130.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2105.01130&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2105.01130.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1088/1361-6382/ac51e7) — `data/raw/crossref/doi_7ed4eb2548f87cdb2428.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://iopscience.iop.org/article/10.1088/1361-6382/ac51e7) — `data/raw/pages/publisher_iop_2105.01130.json`

## 2105.11374 — журнальная версия не установлена

Группы: audit20, audit_initial_not_found.

Для J.S. Dowker нет journal_ref/DOI в двух профильных записях. Поиск Crossref/OpenAlex возвращает другие работы о Casimir effect, отличающиеся названием и авторами. Вердикт означает отсутствие найденной версии на дату среза.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2105.11374) — `data/raw/pages/arxiv_2105.11374.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2105.11374&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2105.11374.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Casimir+Domains+on+a+sphere&rows=5) — `data/raw/crossref/search_2105.11374.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Casimir+Domains+on+a+sphere&per-page=5) — `data/raw/openalex/search_2105.11374.json`

## 2105.11684 — журнальная версия не установлена

Группы: audit20, audit_initial_not_found.

Четверка Alonzo-Artiles / Avilez-López / Díaz-Cruz / Larios-López и подробная аннотация о Higgs-graviton couplings отличают работу от статей Stieberger/Taylor и Draper et al. Поиск не выявил журнальную версию именно этого текста.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2105.11684) — `data/raw/pages/arxiv_2105.11684.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2105.11684&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2105.11684.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=The+Higgs-Graviton+Couplings%3A+from+Amplitudes+to+the+Action&rows=5) — `data/raw/crossref/search_2105.11684.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=The+Higgs-Graviton+Couplings%3A+from+Amplitudes+to+the+Action&per-page=5) — `data/raw/openalex/search_2105.11684.json`

## 2106.15706 — журнальная версия подтверждена

Группы: audit20, audit_initial_published.

Страница Springer содержит Altaisky / Kaputkina / Raj и опубликованное название Multiresolution Quantum Field Theory in Light-Front Coordinates. В v1 было infinite-momentum frame; история названий INSPIRE подтверждает связь. Published 22.02.2022.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2106.15706) — `data/raw/pages/arxiv_2106.15706.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2106.15706&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2106.15706.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1007/s10773-022-05029-6) — `data/raw/crossref/doi_4b9b3ff56ecc6cb59eb5.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://doi.org/10.1007/s10773-022-05029-6) — `data/raw/pages/publisher_2106.15706.json`

## 2107.01371 — журнальная версия не установлена

Группы: control_difficult.

Сопоставление с похожими On unimodular quantum gravity (Astrid Eichhorn, 2013) и Geometrical trinity ... отклонено. Другая статья BRST quantization ... имеет трех авторов Kugo / Nakayama / Ohta и другой arXiv. Один общий автор и близкая тема недостаточны; самостоятельная журнальная версия 2107.01371 не установлена.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2107.01371) — `data/raw/pages/arxiv_2107.01371.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2107.01371&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2107.01371.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=On+Unimodular+Gauge+of+Quantum+Gravity&rows=5) — `data/raw/crossref/search_2107.01371.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=On+Unimodular+Gauge+of+Quantum+Gravity&per-page=5) — `data/raw/openalex/search_2107.01371.json`

## 2107.01954 — журнальная версия не установлена

Группы: audit20, audit_initial_not_found.

В INSPIRE document_type=thesis, а в OpenAlex type=dissertation. Это диссертация Javier Gómez Subils. Публикации отдельных глав не означают, что вся диссертация стала одной журнальной статьей; соответствующая версия не найдена.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2107.01954) — `data/raw/pages/arxiv_2107.01954.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2107.01954&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2107.01954.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Non-perturbative+Aspects+of+Quantum+Field+Theories+from+Holography&rows=5) — `data/raw/crossref/search_2107.01954.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Non-perturbative+Aspects+of+Quantum+Field+Theories+from+Holography&per-page=5) — `data/raw/openalex/search_2107.01954.json`

## 2107.03401 — журнальная версия подтверждена

Группы: audit20, audit_initial_published.

На странице Springer совпадают Fröb / Imbimbo / Risso, название и DOI JHEP12(2021)009; публикация 02.12.2021. Умлауты и акценты фамилий не обозначают разных авторов.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2107.03401) — `data/raw/pages/arxiv_2107.03401.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2107.03401&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2107.03401.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1007/jhep12(2021)009) — `data/raw/crossref/doi_b9aa4907883cd37eb499.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://doi.org/10.1007/jhep12(2021)009) — `data/raw/pages/publisher_2107.03401.json`

## 2107.05662 — журнальная версия подтверждена

Группы: audit20, audit_initial_published.

Springer указывает ту же тройку авторов Buoninfante / Di Filippo / Mukohyama, ту же тему и DOI; дата Published 11.10.2021. Запись является Regular Article, а не материалом конференции.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2107.05662) — `data/raw/pages/arxiv_2107.05662.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2107.05662&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2107.05662.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1007/jhep10(2021)081) — `data/raw/crossref/doi_0cabbb9d9fd85add82d6.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://doi.org/10.1007/jhep10(2021)081) — `data/raw/pages/publisher_2107.05662.json`

## 2107.09020 — журнальная версия подтверждена

Группы: audit20, audit_initial_published.

Единственный автор Zhijin Li совпадает; издательские метаданные связывают название Conformality and self-duality ... с тем же препринтом. В Crossref формула Nf местами теряет индекс f. Дата 10.08.2022 подтверждается imprint INSPIRE; название v1 начинается с On.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2107.09020) — `data/raw/pages/arxiv_2107.09020.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2107.09020&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2107.09020.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1016/j.physletb.2022.137192) — `data/raw/crossref/doi_c4b4b347f4074da0f0b8.json`

## 2109.03271 — журнальная версия подтверждена

Группы: disputed5.

На странице MDPI полностью совпадают авторы Murygin / Kirillov / Nikulin, название и DOI; статья датирована 02.08.2021. arXiv v1 загружена 07.09.2021. Разность -36 дней реальна и не вызвана заполнением неполной даты. Статус опубликована сохранен, delay_days=NA: обратная последовательность не входит в среднюю длительность пути вперед.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2109.03271) — `data/raw/pages/arxiv_2109.03271.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2109.03271&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2109.03271.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.3390/physics3030035) — `data/raw/crossref/doi_bd2691a3e0c1e8b926d7.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://www.mdpi.com/2624-8174/3/3/35) — `data/raw/pages/publisher_2109.03271.json`

## 2109.08551 — журнальная версия подтверждена

Группы: audit20, audit_initial_published.

Проверена исходная статья Varun Gupta JHEP12(2021)032. В INSPIRE также указан erratum JHEP02(2023)026; исправление не является первой публикацией и не заменяет основной DOI.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2109.08551) — `data/raw/pages/arxiv_2109.08551.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2109.08551&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2109.08551.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1007/jhep12(2021)032) — `data/raw/crossref/doi_83a48509c0f6c7efdbc7.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://doi.org/10.1007/jhep12(2021)032) — `data/raw/pages/publisher_2109.08551.json`

## 2109.10401 — журнальная версия не установлена

Группы: audit20, audit_initial_not_found.

Совпадающий препринт имеет четырех авторов Lize / Lyu / Siegel / Wang. В arXiv, INSPIRE и поисках нет подтвержденной журнальной версии; общие книги о струнах и частицах отвергнуты по типу и авторам.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2109.10401) — `data/raw/pages/arxiv_2109.10401.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2109.10401&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2109.10401.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Chiral+string+theories+as+an+interpolation+between+strings+and+particles&rows=5) — `data/raw/crossref/search_2109.10401.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Chiral+string+theories+as+an+interpolation+between+strings+and+particles&per-page=5) — `data/raw/openalex/search_2109.10401.json`

## 2110.04303 — журнальная версия не установлена

Группы: audit20, audit_initial_not_found.

Cameron V. Cogburn указан единственным автором; arXiv и INSPIRE не содержат журнальной версии. Поиск возвращает общие работы о bulk reconstruction с другими авторами. Сходство короткого названия CFT2 не является подтверждением.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2110.04303) — `data/raw/pages/arxiv_2110.04303.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2110.04303&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2110.04303.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=CFT%24_2%24+in+the+Bulk&rows=5) — `data/raw/crossref/search_2110.04303.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=CFT%24_2%24+in+the+Bulk&per-page=5) — `data/raw/openalex/search_2110.04303.json`

## 2110.14616 — журнальная версия не установлена

Группы: audit20, audit_initial_not_found.

Costello / Williams: нет DOI/journal_ref в arXiv/INSPIRE. Авторская страница Brian Williams (Research) связывает название именно с arXiv, без журнальной ссылки. Совпадающие слова в старых работах о heterotic/type I duality не подтверждают публикацию этой работы.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2110.14616) — `data/raw/pages/arxiv_2110.14616.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2110.14616&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2110.14616.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Twisted+heterotic%2Ftype+I+duality&rows=5) — `data/raw/crossref/search_2110.14616.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Twisted+heterotic%2Ftype+I+duality&per-page=5) — `data/raw/openalex/search_2110.14616.json`
- [Авторская страница связывает работу с arXiv, журнальная ссылка отсутствует.](https://sites.google.com/view/brianrwilliams/research) — `data/raw/pages/author_williams_research.json`

## 2111.04800 — журнальная версия не установлена

Группы: audit20, audit_initial_not_found.

В arXiv и INSPIRE перечислены Ccuiro / Choque / Valdivia-Mera; DOI и journal_ref отсутствуют. Проверены оба названия v1 и последней версии в Crossref и OpenAlex. Найденные статьи о hairy black holes имеют другие составы авторов и не приняты.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2111.04800) — `data/raw/pages/arxiv_2111.04800.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2111.04800&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2111.04800.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Anomalous+changing+of+geodesics+in+hairy+black+holes&rows=5) — `data/raw/crossref/search_2111.04800.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Anomalous+changing+angular+momentum+of+geodesic+of+hairy+black+holes&rows=5) — `data/raw/crossref/first_title_2111.04800.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Anomalous+changing+of+geodesics+in+hairy+black+holes&per-page=5) — `data/raw/openalex/search_2111.04800.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Anomalous+changing+angular+momentum+of+geodesic+of+hairy+black+holes&per-page=5) — `data/raw/openalex/first_title_2111.04800.json`

## 2111.05295 — журнальная версия подтверждена

Группы: disputed5.

Издатель TÜBİTAK перенаправляет старый DOI 10.3906/fiz-2111-13 на ту же статью с DOI 10.55730/1300-0101.1000. Совпадают Guo / Hughes / Mathur / Mehta, том 45(6), 281–365. Новая запись Crossref содержит 01.01.2021, исходные метаданные издателя в INSPIRE — 28.12.2021. Для задержки взят исходный publisher imprint; обе версии DOI сохранены, решение о конфликте даты отмечено явно.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2111.05295) — `data/raw/pages/arxiv_2111.05295.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2111.05295&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2111.05295.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.55730/1300-0101.1000) — `data/raw/crossref/doi_6a028d8466911692e878.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://doi.org/10.3906/fiz-2111-13) — `data/raw/pages/publisher_2111.05295.json`

## 2111.07453 — журнальная версия подтверждена

Группы: audit20, audit_initial_not_found, disputed5.

Jacek Pawelczyk в arXiv и J. Pawełczyk в издательских метаданных WSP — один автор: совпадают Варшавский университет, название и идентификатор arXiv в INSPIRE. Ошибка исходного сопоставления возникла из-за буквы ł; исправлена транслитерация. Журнал IJMPA, DOI 10.1142/S0217751X22500622.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2111.07453) — `data/raw/pages/arxiv_2111.07453.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2111.07453&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2111.07453.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1142/s0217751x22500622) — `data/raw/crossref/doi_b5dc38bd7b48b489776d.json`

## 2111.09330 — журнальная версия подтверждена

Группы: audit20, audit_initial_published.

На странице Springer совпадают Felipe Rosso и Gustavo Turiaci, название, JHEP02(2022)187 и дата публикации 23.02.2022.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2111.09330) — `data/raw/pages/arxiv_2111.09330.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2111.09330&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2111.09330.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.1007/jhep02(2022)187) — `data/raw/crossref/doi_c8930959188f031c63d6.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://doi.org/10.1007/jhep02(2022)187) — `data/raw/pages/publisher_2111.09330.json`

## 2112.05333 — журнальная версия не установлена

Группы: audit20, audit_initial_not_found.

Han / Rinaldi: INSPIRE помечает материал как conference paper и связывает с мероприятием C21-12-06.2. Отдельной журнальной версии и DOI не обнаружено. Само участие в семинаре/конференции не удовлетворяет выбранному журнальному определению.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2112.05333) — `data/raw/pages/arxiv_2112.05333.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2112.05333&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2112.05333.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.crossref.org/works?query.bibliographic=Neural+quantum+states+for+supersymmetric+quantum+gauge+theories&rows=5) — `data/raw/crossref/search_2112.05333.json`
- [Сохраненный поисковый ответ; просмотрены кандидаты и причины отказа.](https://api.openalex.org/works?search=Neural+quantum+states+for+supersymmetric+quantum+gauge+theories&per-page=5) — `data/raw/openalex/search_2112.05333.json`

## 2112.15592 — журнальная версия подтверждена

Группы: control_published.

Сверены история названий INSPIRE, arXiv v1 Shadow Extra Dimensions & Fuzzy Branes ... и опубликованный текст Florian Nortier. На первой странице полного текста и на странице издателя стоит published online 11 July 2023, тогда как Crossref хранит только 2023. Это Regular Series, не Proceedings Supplement. Точная задержка 557 дней.

- [История версий, название, авторы, DOI/journal_ref или их отсутствие.](https://arxiv.org/abs/2112.15592) — `data/raw/pages/arxiv_2112.15592.json`
- [Точная связь arXiv, альтернативные названия, публикационные сведения, тип документа.](https://inspirehep.net/api/literature?q=arxiv%3A2112.15592&size=5&fields=titles%2Cauthors%2Cdois%2Cpublication_info%2Carxiv_eprints%2Cdocument_type%2Cpreprint_date%2Cimprints%2Cabstracts%2Curls) — `data/raw/inspire/2112.15592.json`
- [Издательские регистрационные метаданные: авторы, DOI, журнал, даты.](https://api.crossref.org/works/10.5506/aphyspolb.54.6-a2) — `data/raw/crossref/doi_7b142cd56fe4c73ee0ac.json`
- [Страница издателя: авторы, публикационный статус, DOI и/или дата.](https://doi.org/10.5506/aphyspolb.54.6-a2) — `data/raw/pages/publisher_2112.15592.json`
- [Прочитан опубликованный текст: автор, аннотация, дата 11.07.2023.](https://www.actaphys.uj.edu.pl/R/54/6-A2/pdf) — `data/raw/texts/acta_2112.15592.pdf`
