# Widget systém — technická dokumentace

Tahle dokumentace popisuje, jak widget systém funguje uvnitř Pelicanu — od detekce tagů v Markdownu po renderování komponent.

## Obsah

1. [Přehled](#přehled)
2. [Architektura](#architektura)
3. [Widget procesor](#widget-procesor)
4. [Pravidla pro standardizaci](#pravidla-pro-standardizaci)
5. [Podporované typy widgetů](#podporované-typy-widgetů)
6. [Referenční přehled atributů](#referenční-přehled-atributů)
7. [Standard pro metadata akcí](#standard-pro-metadata-akcí)
8. [Přidání nového widgetu](#přidání-nového-widgetu)
9. [Technické detaily](#technické-detaily)
10. [Troubleshooting](#troubleshooting)
11. [Migrační průvodce](#migrační-průvodce)
12. [Výkonnostní úvahy](#výkonnostní-úvahy)
13. [Související dokumenty](#související-dokumenty)

## Přehled

Widget systém umožňuje vkládat dynamické komponenty do Markdown obsahu pomocí vlastních HTML tagů. Widgety se zpracovávají na straně serveru během renderování šablon v Pelicanu.

## Architektura

### Tok zpracování

1. **Vstupní obsah**: Markdown soubory obsahují vlastní HTML tagy (`<widget-calendar>`, `<widget-articles>`)
2. **Zpracování Markdownu**: Pelicanův Markdown procesor zachová HTML elementy
3. **Zpracování šablony**: Šablona `page.html` volá makro `process_widgets()`
4. **Detekce widgetů**: Makro detekuje widget tagy a vytáhne název tagu + surový řetězec atributů
5. **Routing**: Makro nasměruje na příslušnou šablonu komponenty podle názvu tagu
6. **Parsování atributů**: Každá komponenta si parsuje atributy sama z obsahu tagu
7. **Renderování komponenty**: Komponenta filtruje, řadí, omezuje a renderuje obsah
8. **Výstup**: Vyrenderované HTML nahradí původní widget tag

### Struktura souborů

```
theme/templates/
├── page.html                          # Uses widget processor
└── components/
    ├── widget_processor.html          # Simplified: detection + routing only
    ├── widget_calendar.html           # Events: parses filter_by_type, days, start, end, limit, sort, group_by
    └── widget_articles.html           # Articles: unified widget for announcements, curiosities, people

plugins/
├── calendarium/                        # Calendar filtering and grouping (package)
│   ├── __init__.py                    # Plugin registration
│   ├── config.py                      # Constants and defaults
│   ├── attrs.py                       # Widget attribute parsing
│   ├── dates.py                       # Date utilities
│   ├── filter.py                      # Event filtering
│   ├── grouping.py                    # Event grouping
│   ├── feed_links.py                  # Calendar link/feed discovery
│   └── ics.py                         # ICS file generation
└── article_filter.py                  # Article filtering by category, slugs, sort, limit
```

## Widget procesor

### Umístění

`theme/templates/components/widget_processor.html`

### Makro: `process_widgets(content)`

Rekurzivně prochází obsah stránky a nahrazuje widget tagy.

**Parametry:**
- `content` (string): HTML/Markdown obsah stránky

**Vrací:**
- Vyrenderované HTML, kde jsou widgety nahrazené komponentami

**Co dělá:**
- Detekuje widget tagy (`<widget-calendar />`, `<widget-articles />`, atd.)
- Vytáhne název tagu a surový obsah tagu (řetězec atributů)
- Nasměruje na příslušnou šablonu komponenty
- Předá komponentě proměnnou `tag_content` (obsahuje surový řetězec atributů)
- Řeší rekurzivní zpracování pro vnořené widgety

**Algoritmus:**
1. Rozdělí obsah podle vzoru `<widget-`
2. Pro každý nalezený widget:
   - Vytáhne název tagu z obsahu tagu
   - Vytáhne surový obsah tagu (včetně všech atributů jako string)
   - Nasměruje na komponentu podle názvu tagu (`calendar`, `articles`)
   - Předá komponentě proměnnou `tag_content`
   - Komponenta si parsuje atributy sama
   - Rekurzivně zpracuje zbytek obsahu

**Klíčový princip:**
- Procesor atributy NEparsuje (parsování si řeší komponenty)
- Procesor jen detekuje a routuje widgety
- Každá komponenta je samostatná a nezávislá

## Pravidla pro standardizaci

### Pojmenování typů widgetů

- Všechny widget tagy používají **kebab-case** (malá písmena s pomlčkami)
- Názvy tagů: `widget-calendar`, `widget-articles`
- Interní typy widgetů: `calendar` (widget_calendar.html), `articles` (widget_articles.html)

### Pojmenování atributů

- **Všechny atributy mají standardní HTML formát (bez prefixu `data-`)**
- **Všechny atributy používají kebab-case**
- Příklady: `type="milonga"`, `days="365"`, `limit="3"`, `category="announcement"`

### Mapování tagu na komponentu

- `<widget-calendar>` → `widget_calendar.html`
- `<widget-articles>` → `widget_articles.html`

## Podporované typy widgetů

### 1. Widget akcí (`<widget-calendar>`)

Zobrazuje filtrované seznamy akcí z [`content/events/`](../content/events/).

**Atributy:**
- `filter_by_type="milonga|workshop|class|..."` (volitelné) - Filtr typu akce. Jeden typ nebo seznam oddělený mezerami pro OR logiku (např. `filter_by_type="milonga neolonga pocoloco"`).
- `days="7"` (volitelné) - Dnů od dneška (kladné = budoucnost, záporné = minulost)
- `start="2026-06-01"` (volitelné) - Začátek časového okna. Lze použít samostatně (od startu dál) nebo s `end`. Hodnoty: `YYYY-MM-DD` nebo tokeny `today`, `this-week` (pondělí aktuálního týdne), `this-month` (1. dne měsíce), `this-year` (1. ledna).
- `end="2026-08-31"` (volitelné) - Konec časového okna. Stejný formát jako `start`. Pokud je nastaven jen `start`, končí se na start + 365 dnů.
- `month="6"` (volitelné) - Omezí widget na **jeden kalendářní měsíc** — celý měsíc 6 (červen) v *upcoming-framing* roce (letos, nebo příští rok, pokud už červen proběhl). Přijímá číslo `1`–`12` nebo název měsíce, česky (včetně tvarů v 6. pádě — `cerven`, `červnu`, `leden`, `prosinci`…) nebo anglicky (`June`). **Přepisuje `days`/`start`/`end`** (pokud je `month` neparsovatelný, widget spadne zpět na běžnou logiku `days`/`start`/`end`). Tohle pohání 12 evergreen měsíčních stránek (`/milongy-brno-<měsíc>/` — viz [SEO + sociální kartičky](SEO.md)); rozhodování o ročníku kopíruje Jinja filtr `tango_year_for_month`.
- `limit="3"` (volitelné) - Omezí počet zobrazených položek (`"3"`, `"all"`, `"last 3"`)
- `sort="newest|oldest"` (volitelné) - Řazení (výchozí: **nejstarší první**, tj. chronologicky)
- `group_by="day|week|month|week day"` (volitelné) - Seskupí akce do řádků s nadpisem pro každou skupinu. Jedna hodnota (např. `"week"`) = ploché seskupení. Tokeny oddělené mezerou (např. `"week day"`) = vnořené seskupení s 7sloupcovým gridem (první token = vnější/řádky, druhý token = vnitřní/sloupce). Když je nastaveno, zobrazí se jen neprázdné skupiny; řazení je chronologické (nejdřív nejstarší) mezi skupinami i uvnitř nich.
- `headers="week|day|week day"` (volitelné) - Zobrazí hlavičky skupin. Výchozí: hlavičky skryté. Hodnoty: `"week"` (jen týdenní hlavičky), `"day"` (jen denní hlavičky), `"week day"` (obojí). Funguje jen když je nastaveno `group_by`.
- `hide_empty_days="true"` (volitelné) - Skryje prázdné denní sloupce v gridu week-day. Výchozí: false (všech 7 dnů se vykreslí). Funguje jen když je `group_by="week day"`.
- `card_size="xs|s|m|l"` (volitelné) - Velikost kartiček akcí. Výchozí: `s` (malá). Hodnoty: `xs` (extra malá), `s` (malá), `m` (střední), `l` (velká).

**Filtrování podle data:**
- `days="7"` = příštích 7 dnů od dneška
- `days="-7"` = posledních 7 dnů od dneška
- `days="365"` nebo `days="-365"` = roční okno od dneška
- `start` (volitelné) = začátek okna; použij s `end` nebo bez. S `end` = rozsah dat; bez `end` = od startu do start+365 dnů. Vzájemně se vylučuje s `days`.
- `start` i `end` přijímají tokeny `today`, `this-week`, `this-month`, `this-year` nebo `YYYY-MM-DD`
- `month="6"` / `month="cerven"` = přesně tenhle kalendářní měsíc v upcoming-framing roce; přepisuje `days`/`start`/`end`

**Příklady:**
```html
<!-- Next 7 days of milongas -->
<widget-calendar filter_by_type="milonga" days="7"></widget-calendar>

<!-- All workshops in next year -->
<widget-calendar filter_by_type="workshop" days="365"></widget-calendar>

<!-- Milongas in date range -->
<widget-calendar filter_by_type="milonga" start="2026-06-01" end="2026-08-31"></widget-calendar>

<!-- Just June's milongas/praktikas (the evergreen-month-page widget) -->
<widget-calendar filter_by_type="milonga praktika neolonga" month="6"></widget-calendar>

<!-- Last 3 milongas -->
<widget-calendar filter_by_type="milonga" days="-7" limit="3"></widget-calendar>

<!-- Milongas from today (default sort is oldest first) -->
<widget-calendar filter_by_type="milonga" start="today"></widget-calendar>

<!-- Multiple event types (OR): milonga or neolonga or pocoloco -->
<widget-calendar filter_by_type="milonga neolonga pocoloco" days="7"></widget-calendar>

<!-- Events grouped by week (rows per week with headline) -->
<widget-calendar days="365" group_by="week"></widget-calendar>

<!-- Events in week-day grid (7 columns, no headers) -->
<widget-calendar start="this-week" group_by="week day" days="14"></widget-calendar>

<!-- Events in week-day grid with week headers only -->
<widget-calendar start="this-week" group_by="week day" days="14" headers="week"></widget-calendar>

<!-- Events in week-day grid with both headers -->
<widget-calendar start="this-week" group_by="week day" days="14" headers="week day"></widget-calendar>

<!-- Events in week-day grid, hiding empty days -->
<widget-calendar start="this-week" group_by="week day" days="14" headers="day" hide_empty_days="true"></widget-calendar>

<!-- Events with medium-sized cards -->
<widget-calendar filter_by_type="milonga" days="7" card_size="m"></widget-calendar>

<!-- Events with large-sized cards -->
<widget-calendar filter_by_type="workshop" days="30" card_size="l"></widget-calendar>
```

**Seskupení (`group_by`):**
- **Ploché seskupení:** Jedna hodnota (`day`, `week`, `month`). Akce v řádcích po skupinách; každý řádek má nadpis (datum dne, rozsah dat týdne nebo název měsíce + rok).
- **Vnořené seskupení:** Tokeny oddělené mezerou (např. `"week day"`). První token = vnější seskupení (řádky), druhý token = vnitřní seskupení (sloupce). Při `"week day"` vznikne 7sloupcový grid.
- **Týden:** Pondělí–neděle; nadpis = rozsah dat „Týden od 3.2. do 9.2. 2026" česky, „Week from 3 Feb to 9 Feb 2026" anglicky.
- **Den (vnořený):** Krátký formát se zkratkou dne v týdnu: „Po 3.2." (česky), „Mon 3 Feb" (anglicky).
- **Prázdné skupiny:** Řádky s nulou akcí se nevykreslují (ploché seskupení). U vnořeného seskupení `"week day"` se ve výchozím stavu vykreslí všech 7 denních sloupců (i prázdných), aby se zachovala struktura gridu. Použij `hide_empty_days="true"`, aby se prázdné sloupce skryly.
- **Řazení:** Chronologické (nejdřív nejstarší) mezi skupinami i uvnitř každé skupiny. Atribut `sort` widgetu se při nastaveném `group_by` neuplatní.
- **Hlavičky:** Hlavičky skupin jsou ve výchozím stavu skryté. Pro zobrazení použij atribut `headers` (např. `headers="week"`, `headers="day"`, `headers="week day"`).
- **Layout:** Vnořené seskupení používá responzivní grid denních sloupců (`.calendar-days-grid`), který drží všechny viditelné dny v jednom řádku. Sloupce se automaticky rozšíří podle počtu viditelných dní. Při `hide_empty_days="true"` se zobrazí jen dny s akcemi a každý má stejnou šířku. Akce uvnitř každého dne se stackují vertikálně přes `.el-stack`.
- **Locale:** Nadpisy a formáty dat se řídí podle `DEFAULT_LANG` (např. `cs`, `en`). Čeština funguje hned; angličtinu lze přidat nastavením `DEFAULT_LANG = "en"` a tím, že ji theme používá.

**Implementace:**
- Komponenta: [`theme/templates/components/widget_calendar.html`](../theme/templates/components/widget_calendar.html) parsuje atributy z `tag_content` a volá Jinja filtr `calendarium` (z pluginu [`plugins/calendarium/filter.py`](../plugins/calendarium/filter.py)) pro veškeré filtrování, datové okno, řazení a limit.
- Filtrování (filter_by_type, datové okno, sort, limit) je implementované v pluginu calendarium; šablona jen parsuje atributy a renderuje výsledek. Typ akce používá metadata `event-type`; více typů ve `filter_by_type="a b c"` jsou OR. Kategorie `announcement` a `curiosity` jsou vyloučené.
- Seskupení: Při nastaveném `group_by` filtr `group_events` z pluginu calendarium seskupí akce po dnech/týdnech/měsících a vrátí dvojice `(headline, events)`; šablona renderuje sekci na skupinu s nadpisem + grid kartiček.
- Výchozí řazení: nejstarší první (chronologicky). Pro opačné použij `sort="newest"`.

### 2. Odběr kalendáře (`<widget-calendar-link>`)

Vygeneruje nadpis a tři odkazy pro odběr iCal (.ics) feedu na třech platformách: webcal (Apple / výchozí kalendářové aplikace), Google Calendar a obyčejný HTTPS odkaz (např. pro Outlook „Subscribe from web"). Plugin najde tyhle widgety, pro každou unikátní konfiguraci feedu vytvoří jeden `.ics` soubor a vyrenderuje jeden nadpis plus jeden prostý `<a>` na platformu. Žádné třídy se neaplikují.

**Atributy:**
- `cal_file_name="all|marathon|..."` (volitelné) - Název výstupního souboru feedu: `/calendars/{cal_file_name}.ics`. Když není uvedený, odvodí se stabilní ID z filtru (hash). Pro čitelné URL používej explicitní `cal_file_name` (např. `/calendars/marathon.ics`).
- `filter_by_type="milonga|workshop|..."` (volitelné) - Filtr typu akce (stejně jako u `widget-calendar`)
- `days="7"` (volitelné) - Dnů od dneška (kladné = budoucnost, záporné = minulost)
- `start="2026-06-01"` (volitelné) - Začátek časového okna (stejně jako u `widget-calendar`)
- `end="2026-08-31"` (volitelné) - Konec časového okna
- `filter_by_path="events/2026-marathon"` (volitelné) - Filtruje podle source path článku obsahujícího tenhle podřetězec
- `category="events"` (volitelné) - Filtruje podle názvu Pelican kategorie (např. `events`, `classes`)
- `tags="tango workshop"` (volitelné) - Tagy oddělené mezerou (OR logika)
- `label="Subscribe"` (volitelné) - Text nadpisu nad odkazy (výchozí: „Subscribe to calendar")
- `label_webcal="Apple"` (volitelné) - Text odkazu pro webcal (výchozí: „Apple / default calendar")
- `label_google="Google"` (volitelné) - Text odkazu pro Google Calendar (výchozí: „Google Calendar")
- `label_outlook="Ostatní"` (volitelné) - Text odkazu pro HTTPS/copy link (výchozí: „Copy link")

**Generování feedu:**
- Plugin při buildu projde všechny stránky a články a najde tagy `<widget-calendar-link>`
- Pro každou unikátní konfiguraci feedu (stejné `feed_id` nebo stejný filtr) vznikne jeden `.ics` soubor v `output/calendars/`
- Akce s metadaty `recurrence` vygenerují v iCal feedu RRULE
- Widget se vyrenderuje jako: jeden `<div>` s `<p>` (nadpis z `label`) a jeden prostý `<a>` na platformu (webcal, Google, https).

**Vyrenderuje se jako (příklad):**
```html
<div>
  <p>📆 Odebírej akce do svého kalendáře</p>
  <a href="webcal://example.com/calendars/events.ics">Apple</a>
  <a href="https://www.google.com/calendar/render?cid=https%3A%2F%2Fexample.com%2Fcalendars%2Fevents.ics">Google</a>
  <a href="https://example.com/calendars/events.ics">Ostatní</a>
</div>
```

**Příklady:**
```html
<!-- All events (no filter) -->
<widget-calendar-link cal_file_name="all" label="Přidat do kalendáře"></widget-calendar-link>

<!-- Headline and custom link labels -->
<widget-calendar-link
  cal_file_name="events"
  filter_by_path="events"
  label="📆 Odebírej akce do svého kalendáře"
  label_webcal="Apple"
  label_google="Google"
  label_outlook="Ostatní"
></widget-calendar-link>

<!-- Marathon events only -->
<widget-calendar-link cal_file_name="marathon" filter_by_path="events/2026-marathon" label="Marathon 2026"></widget-calendar-link>

<!-- Milongas in next 30 days -->
<widget-calendar-link cal_file_name="milongas" filter_by_type="milonga" days="30" label="Upcoming milongas"></widget-calendar-link>
```

**Konfigurace (volitelná):**
V `pelicanconf.py`:
```python
CALENDAR_ICS_OUTPUT_DIR = "calendars"  # Default: "calendars"
CALENDAR_ICS_EXCLUDED_CATEGORIES = ["announcement", "curiosity"]  # Default: same as EXCLUDED_CATEGORIES
```

**Implementace:**
- Kompletní dokumentaci pluginu najdeš v [`plugins/calendarium/README.md`](../plugins/calendarium/README.md): discovery feedů, generování ICS, filter pipeline, typy URL a přehled modulů.
- Komponenta: [`theme/templates/components/widget_calendar_link.html`](../theme/templates/components/widget_calendar_link.html) renderuje jeden nadpis a tři odkazy (bez tříd)

### 3. Widget článků (`<widget-articles>`)

Sjednocený widget pro zobrazení článků filtrovaných podle kategorie. Nahrazuje staré widgety `widget-announcements`, `widget-curiosities`, `widget-classes` a `widget-people`.

**Atributy:**
- `category="announcement|curiosity|people"` (povinné) - Kategorie, podle které se filtruje
- `slugs="slug1 slug2"` (volitelné) - Seznam slugů článků oddělený mezerou k zobrazení v daném pořadí. Přepisuje `sort` a `limit`.
- `sort="newest|oldest|title"` (volitelné) - Řazení (výchozí: nejstarší první)
- `limit="3"` (volitelné) - Omezí počet položek (`"3"`, `"all"`, `"last 3"`)
- `columns="3"` (volitelné) - Počet sloupců gridu (používá `.el-grid-N`)
- `metadata="description location"` (volitelné) - Seznam dalších metadat k zobrazení, oddělený mezerou

**Příklady:**
```html
<!-- Last 3 announcements -->
<widget-articles category="announcement" limit="3"></widget-articles>

<!-- All curiosities -->
<widget-articles category="curiosity" limit="all"></widget-articles>

<!-- People with descriptions -->
<widget-articles category="people" metadata="description"></widget-articles>

<!-- Specific people in specific order -->
<widget-articles category="people" slugs="filip-paldia lenka-platenikova" metadata="description"></widget-articles>

<!-- Announcements sorted newest first -->
<widget-articles category="announcement" limit="12" sort="newest"></widget-articles>
```

**Implementace:**
- Komponenta: [`theme/templates/components/widget_articles.html`](../theme/templates/components/widget_articles.html)
- Plugin: [`plugins/article_filter.py`](../plugins/article_filter.py) poskytuje Jinja filtry `parse_article_attrs` a `article_filter`
- Filtruje články podle `article.category.name`
- Vrací seznam dictů `{article, extra_metadata}`
- Šablona renderuje kartičky s titulem, popisem (pokud je), náhledovým obrázkem a jakýmikoli dalšími metadaty

**Stránkovaný archiv (vzor dvou úrovní):** Pro náhledovou stránku s omezeným počtem položek + odkazem na plný archiv použij `limit="12"` a doplň odkaz na stránku kategorie: `[Všechny oznamy →](/category/announcement/)`. Plný stránkovaný seznam je na `/category/announcement/` přes Pelican šablonu kategorie s 12 položkami na stránku.

## Referenční přehled atributů

### Atributy widget-calendar

| Atribut | Typ | Povinný | Hodnoty | Popis |
|-----------|------|----------|--------|-------------|
| `filter_by_type` | string | Ne | `milonga`, `workshop`, `class` nebo oddělené mezerou pro OR | Filtr typu akce |
| `days` | integer | Ne | `7`, `365`, `-7` | Dnů od dneška (kladné = budoucnost, záporné = minulost) |
| `start` | date/token | Ne | `YYYY-MM-DD`, `today`, `this-week`, `this-month`, `this-year` | Začátek datového okna |
| `end` | date/token | Ne | Stejné jako `start` | Konec datového okna (volitelné, pokud je nastaven `start`) |
| `limit` | string/integer | Ne | `"3"`, `"all"`, `"last 3"` | Omezení počtu položek |
| `sort` | string | Ne | `newest`, `oldest` | Řazení (výchozí: oldest) |
| `group_by` | string | Ne | `day`, `week`, `month`, `week day` | Seskupit akce do řádků |
| `headers` | string | Ne | `week`, `day`, `week day` | Zobrazit hlavičky skupin (výchozí: skryté) |
| `hide_empty_days` | boolean | Ne | `true`, `false` | Skrýt prázdné denní sloupce v gridu week-day |
| `card_size` | string | Ne | `xs`, `s`, `m`, `l` | Velikost kartičky (výchozí: `s`) |

### Atributy widget-articles

| Atribut | Typ | Povinný | Hodnoty | Popis |
|-----------|------|----------|--------|-------------|
| `category` | string | Ano | `announcement`, `curiosity`, `people`, atd. | Kategorie pro filtrování |
| `slugs` | string | Ne | `"slug1 slug2 slug3"` | Slugy oddělené mezerou, zobrazí se v daném pořadí (přepíše sort/limit) |
| `sort` | string | Ne | `newest`, `oldest`, `title` | Řazení (výchozí: oldest) |
| `limit` | string/integer | Ne | `"3"`, `"all"`, `"last 3"` | Omezení počtu položek |
| `columns` | string/integer | Ne | `"3"` | Sloupce gridu |
| `metadata` | string | Ne | `"title description image location"` | Pole k zobrazení, oddělená mezerou (výchozí: `title description`) |
| `card_size` | string | Ne | `s`, `m`, `l` | Velikost kartičky: malá, střední (výchozí), velká |
| `link` | string | Ne | `true`, `false`, `yes`, `no`, `0` | Jestli každá kartička linkuje na článek; výchozí je linkování. `false`/`no`/`0` vyrenderují kartičky bez prokliku. |

**Pravidla:**
- `days` a `start`/`end` se u `widget-calendar` vzájemně vylučují
- `group_by` funguje jen u `widget-calendar`; když je nastaveno, řazení je vždy chronologické
- `slugs` přepisuje `sort` a `limit` u `widget-articles`
- Výchozí řazení: `oldest` (chronologicky)

## Standard pro metadata akcí

Widgety očekávají, že akce použijí standardizovaný formát metadat:

### Povinná pole

- `date`: Datum článku (požadavek Pelicanu, formát: `YYYY-MM-DD HH:MM:SS`)
- `event-start`: Datum a čas začátku akce (formát: `YYYY-MM-DD HH:MM:SS`)
- `slug`: Identifikátor pro URL

### Volitelná pole

- `event-end`: Datum a čas konce akce (formát: `YYYY-MM-DD HH:MM:SS`)
- `recurrence`: Opakující se akce se ve widgetu kalendáře rozbalí na více instancí. Použij jednoduchou frázi: `recurrence: weekly sunday` (každou neděli), `recurrence: monthly 1 saturday` (první sobota v měsíci). Pro pokročilé použití je podporované i syrové RRULE přes volitelný `event-rrule`.

### Vzor přístupu v šabloně

Šablony používají metadata jen pro event start/end:

```jinja2
{% set event_start = event.metadata.get('event-start') if event.metadata else none %}
{% set event_end = event.metadata.get('event-end') if event.metadata else none %}
```

Šablony nepoužívají `event.date` ani `event.metadata.get('end_date')`.

## Přidání nového widgetu

### Krok 1: Vytvoř šablonu komponenty

Vytvoř `theme/templates/components/your-widget.html`:

```jinja2
{% set your_param = none %}

{% if tag_content %}
  {% set tag_name_parts = tag_content.split(' ') %}
  {% set tag_name = tag_name_parts[0] %}
  {% if tag_name_parts | length > 1 %}
    {% set attrs_str = tag_content[tag_name | length:] | trim %}
    {% if attrs_str %}
      {% set attrs_list = attrs_str.split('" ') %}
      {% for attr in attrs_list %}
        {% if 'your-attr="' in attr %}
          {% set your_param = attr.split('your-attr="')[1] %}
        {% endif %}
      {% endfor %}
    {% endif %}
  {% endif %}
{% endif %}

<div class="your-widget">
  <!-- Your widget HTML -->
</div>
```

**Klíčové body:**
- Komponenta dostane od procesoru proměnnou `tag_content`
- Komponenta si parsuje vlastní atributy z `tag_content`
- Použij standardní vzor parsování atributů (split podle `" `)

### Krok 2: Uprav widget procesor

Přidej routing do `widget_processor.html`:

```jinja2
{% elif tag_name == 'your-widget' %}
  {% include 'components/your_widget.html' with context %}
```

**Klíčové body:**
- Procesor routuje jen podle `tag_name`
- Proměnnou `tag_content` předává automaticky
- Žádné parsování atributů v procesoru

### Krok 3: Zdokumentuj použití

Doplň do téhle dokumentace syntax a příklady widgetu.

## Technické detaily

### Detekce widget tagů

Procesor používá rozdělení stringu pro detekci widget tagů:

```jinja2
{% set parts = content.split('<widget-') %}
{% for part in parts[1:] %}
  {% set tag_parts = part.split('>', 1) %}
  {% set tag_content = tag_parts[0] %}
  {% set tag_name_parts = tag_content.split(' ') %}
  {% set tag_name = tag_name_parts[0] %}
  <!-- Route to component, pass tag_content -->
{% endfor %}
```

### Parsování atributů (v komponentách)

Každá komponenta si parsuje vlastní atributy z `tag_content`:

```jinja2
{% set tag_name_parts = tag_content.split(' ') %}
{% set tag_name = tag_name_parts[0] %}
{% if tag_name_parts | length > 1 %}
  {% set attrs_str = tag_content[tag_name | length:] | trim %}
  {% if attrs_str %}
    {% set attrs_list = attrs_str.split('" ') %}
    {% for attr in attrs_list %}
      {% if 'your-attr="' in attr %}
        {% set your_param = attr.split('your-attr="')[1] %}
      {% endif %}
    {% endfor %}
  {% endif %}
{% endif %}
```

**Vlastnosti:**
- Podporuje samouzavírací (`<widget-calendar />`) i párové tagy (`<widget-calendar></widget-calendar>`)
- Zvládá whitespace a nové řádky v tagech
- Atributy musí být oddělené `" ` (uvozovka + mezera)
- Hodnoty atributů nesmí obsahovat mezery (použij raději samostatné atributy)
- Vnořené widgety jsou podporované přes rekurzi
- Každá komponenta je samostatná a parsuje si atributy sama

### Kontextové proměnné

Widgety mají přístup k plnému Pelican kontextu šablon:

- `articles`: Všechny články (akce se z toho filtrují)
- `pages`: Všechny stránky
- `SITEURL`: Základní URL webu
- `SITENAME`: Název webu
- `NOW`: Aktuální datetime objekt (automaticky vystavený z `pelicanconf.py`)
- Všechny ostatní kontextové proměnné Pelicanu

### Filtrování obsahu

**widget-calendar:** Používá plugin `calendarium`, který filtruje podle event metadat a vylučuje kategorie `announcement` a `curiosity`.

**widget-articles:** Používá plugin `article_filter`, který filtruje podle `article.category.name`:

```python
def _filter_by_category(articles, category):
    category_lower = category.strip().lower()
    out = []
    for a in articles or []:
        cat = getattr(a, "category", None)
        if cat and getattr(cat, "name", "").lower() == category_lower:
            out.append(a)
    return out
```

Tohle navazuje na Pelican konfiguraci `ARTICLE_PATHS = ["announcements", "events", "classes", "curiosities", "people"]`, kde se každý podadresář stává kategorií.

### Práce s daty

Widgety používají metadata pro data akcí:

```jinja2
{% set event_start = event.metadata.get('event-start') if event.metadata else none %}
```

**Důležité:**
- Hodnota může být string (pro výpočty potřebuje parsování)
- Pro zobrazení: větvi podle `event_start is string` a buď ořež, nebo použij `strftime`
- Pro filtrování: před porovnáním normalizuj na date/datetime

## Troubleshooting

### Widget se nerenderuje

**Zkontroluj:**
1. Syntax widgetu sedí přesně (zkopíruj z příkladů výše)
2. Název widget tagu má správný formát (`widget-calendar`, ne `widget_calendar`)
3. Všechny atributy mají standardní HTML formát (bez prefixu `data-`)
4. Stránka používá šablonu `page.html` (ne vlastní šablonu)
5. V šabloně se volá makro `process_widgets()`
6. V HTML widgetu nejsou syntaktické chyby

**Debug:**
- Mrkni do build outputu Pelicanu na template errors
- Ověř, že widget tag je v obsahu stránky (a markdown ho neshodil)
- Otestuj nejdřív jednoduchý widget

### Akce se nezobrazují

**Zkontroluj:**
1. Akce existují ve správném adresáři ([`content/events/`](../content/events/), [`content/announcements/`](../content/announcements/), atd.)
2. Akce mají platné metadatum `event-start`
3. Filtr odpovídá titulům akcí (case-insensitive)
4. Akce jsou v datovém rozsahu (pokud je nastaveno `days` nebo `start`/`end`)

**Debug:**
- Zkontroluj, že `article.source_path` obsahuje očekávanou cestu
- Ověř, že formát metadat akce sedí se standardem
- Otestuj přístup k akci: `{{ event.metadata.get('event-start') }}`

### Problémy se zobrazením data

**Zkontroluj:**
1. Akce má `event-start` ve frontmatteru
2. Formát je `YYYY-MM-DD HH:MM:SS`

**Debug:**
- Zkontroluj metadata: `{{ event.metadata }}`
- Ověř datetime objekt: `{{ event_start }}`
- Otestuj strftime: `{{ event_start.strftime('%d. %m. %Y') }}`

## Migrační průvodce

### Ze starých widgetů na widget-articles

Následující widgety byly nahrazeny sjednoceným `widget-articles`:

| Starý widget | Nový widget |
|------------|------------|
| `<widget-announcements limit="3">` | `<widget-articles category="announcement" limit="3">` |
| `<widget-curiosities limit="3">` | `<widget-articles category="curiosity" limit="3">` |
| `<widget-classes limit="3">` | `<widget-articles category="class" limit="3">` |
| `<widget-people>` | `<widget-articles category="people" metadata="description">` |
| `<widget-people slugs="...">` | `<widget-articles category="people" slugs="..." metadata="description">` |

**Klíčové změny:**
- Všechny widgety založené na článcích teď používají `<widget-articles>` s atributem `category`
- Atribut `metadata` umožňuje určit, která další pole se mají zobrazit (např. `description`)
- Atribut `slugs` funguje stejně — vybírá konkrétní články v daném pořadí
- Atribut `pagination` nikdy nebyl implementovaný a je odstraněný

## Výkonnostní úvahy

### Zpracování widgetů

- Widgety se zpracovávají během renderování šablon (server-side)
- Žádný JavaScript na straně klienta není potřeba
- Zpracování je rekurzivní (podporuje vnořené widgety)
- Každý widget projde všechny články (u velkých webů zvaž cache)

### Filtrování akcí

- Filtrování probíhá v Jinja2 šablonách (žádné databázové dotazy)
- Všechny články jsou v paměti
- Filtrování je O(n), kde n = počet článků
- U velkých seznamů akcí zvaž stránkování

## Související dokumenty

- [Brnos Aires — web](../README.md) — hlavní průvodce: pracovní postup, struktura souboru akce, widgety, obrázky.
- [Úprava obsahu](EDITING.md) — průvodce pro editory: metadata v hlavičce souboru a co dělají na živém webu.
- [SEO + sociální kartičky](SEO.md) — *proč* to celé funguje takto: kanonická strategie, `<base href>`, mechanika hubů, anglická verze a `hreflang`.
- [Discoverability pro LLM](LLMS.md) — soubory pro AI asistenty (`content/llm/`) a `.md` zrcadla stránek.
- [Lokální testování](local-testing.md) — lokální testování widgetů a celého webu.
- [Nasazení](publishing.md) — deployment a publikace.
- [Nastavení vývojového prostředí](setup.md) — nastavení vývojového prostředí.
- [GitHub Issues](https://github.com/filipaldi/brnosaires/issues) - co je v plánu.
