# Discoverability pro LLM

O LLM-friendly výstupy Brnos Aires se stará jediný custom plugin - [`llm_ally.py`](../plugins/llm_ally.py). Je to **hloupý renderer**: žádné znalosti o konkrétním webu v sobě nemá. Všechna editorská rozhodnutí (co vystavit, co vynechat, jak oslovit které publikum) leží v souborech, které editují editoři.

## Obsah

- [Dvě zodpovědnosti](#dvě-zodpovědnosti)
- [Textové šablony widgetů](#textové-šablony-widgetů)
- [Proč hloupý renderer](#proč-hloupý-renderer)
- [Reference souborů](#reference-souborů)
- [Související dokumenty](#související-dokumenty)

## Dvě zodpovědnosti

### 1. Editorsky kurátorované `*.txt` soubory

Pro každý `*.md` soubor v [`content/llm/`](../content/llm/) plugin vygeneruje odpovídající `.txt` do rootu webu **a** do `/.well-known/`. Mapování názvů je jedna ku jedné:

| Zdroj | Výstup (kanonický) | Výstup (well-known alias) |
|---|---|---|
| `content/llm/llms.md` | `output/llms.txt` | `output/.well-known/llms.txt` |
| `content/llm/llms-full.md` | `output/llms-full.txt` | `output/.well-known/llms-full.txt` |
| `content/llm/<cokoli>.md` | `output/<cokoli>.txt` | `output/.well-known/<cokoli>.txt` |

Přidat nové publikum znamená `cp` plus editaci:

```bash
cp content/llm/llms.md content/llm/androids.md
# uprav nadpisy, widget filtry a text pro android publikum
pelican content -s pelicanconf.py
# /androids.txt a /.well-known/androids.txt jsou na světě
```

Žádná změna v kódu. Žádná registrace. Plugin při buildu projde adresář a vyrobí, co tam najde.

[`content/llm/`](../content/llm/) **není zaregistrované u Pelicanu** - soubory v něm se nestanou samostatnými HTML stránkami. Plugin si je čte přímo během signálu `finalized`, ořeže YAML frontmatter, rozbalí každý tag `<widget-*>` přes `widget_processor.render_widgets_in_text()` a výsledek zapíše.

### 2. Markdown zrcadla jednotlivých stránek

Pro každý veřejný článek a stránku zapíše `llm_ally` soubor `index.md` vedle vygenerovaného `index.html`:

```
output/tango-pizza-sesamo-2026-04-29/index.html   ← vyrenderované HTML
output/tango-pizza-sesamo-2026-04-29/index.md     ← čisté Markdown zrcadlo
```

Každý `.md` obsahuje:

1. **Discovery marker ve stylu Mintlify** - `> For a complete page index, fetch {SITEURL}/llms.txt`. Říká LLM, který přistál na jediné stránce, kde najde index celého korpusu.
2. **YAML frontmatter** - `title`, `date`, `url`, a u akcí navíc `event-type`, `event-start`, `event-end`, `event-venue`, `event-street`, `event-locality`, `event-organiser`, `instructor`, `recurrence`, `series`, `event-url` (pokud jsou vyplněné). `instructor` je jediný klíč, který v žádném souboru není: akce si lektory drží slugem v `instructor_slugs:` a zrcadlo místo něj vypíše jména z profilů. Slug by tu nikam nevedl - profil každého lektora má `llm_mirror: false`, takže se nezrcadlí.
3. **Tělo** - syrový Markdown ze `source_path`, kde se `<widget-*>` tagy vykreslí jako prosté textové bullety přes stejné Jinja šablony, co pohánějí HTML web (textoví sourozenci: `widget_calendar.txt.j2`, `widget_articles.txt.j2`, atd.).

### Jak vyřadit konkrétní obsah

Libovolný článek nebo stránka se dá ze zrcadlení vyřadit jedním řádkem ve frontmatteru:

```yaml
---
title: Smutné období drogových dealerů
slug: smutne-obdobi-drogovych-dealeru
date: 2026-04-12 18:00:00
llm_mirror: false
---
```

Na Brnos Aires nese tento řádek každý soubor pod [`content/curiosities/`](../content/curiosities/) a profily lektorů v [`content/people/`](../content/people/) (píkošky jsou editorské zabarvení, profily lidí jsou bio - ani jedno není to, co uživatelé hledají). Profily DJů maratonu vlajku nemají a zrcadlí se. Jiné weby si vlajku nastaví, kde dává smysl jim.

Vlajka nemá žádný centrální protějšek v kódu ani v konfiguraci. Vyřazení editor značí přímo u zdroje.

## Textové šablony widgetů

[`theme/templates/components/widget_*.txt.j2`](../theme/templates/components/) jsou textové protějšky HTML šablon. Widget processor poskytuje `render_widgets_in_text(text, env, context)`, kterou plugin volá; helper si při renderu sám přemapuje `widget_calendar.html` → `widget_calendar.txt.j2`.

Chybějící `.txt.j2` šablona vykreslí widget jako prázdný řetězec - záměrně, aby se do Markdownu nedostalo `<div>`.

### Deduplikace pravidelných lekcí

V textovém režimu má `<widget-calendar>` defaultně `dedupe-recurring="true"`. Každý opakující se zdroj se objeví jednou jako `- weekly Sunday 18:00 — Title — Location (URL)`, ne jako N řádků s konkrétními daty. Vypnout to lze per-tag přes `dedupe-recurring="false"`. Deduplikace je implementovaná v textové šabloně, ne v pluginu - plugin o konceptu „opakující se" vůbec neví.

## Proč hloupý renderer

Dřívější verze tohohle řešení měly natvrdo v Pythonu seznam kurátorovaných sekcí, okno opakujících se akcí v týdnech, název kategorie oznámení, zdrojovou cestu k akcím a vyloučení píkošek a lidí. Každé editorské rozhodnutí znamenalo zásah do kódu a plugin byl přilepený na Brnos Aires.

Model hloupého rendereru posouvá všechna editorská rozhodnutí do souborů, které vlastní editor: `content/llm/*.md` určuje, jaké `*.txt` výstupy web vystavuje a co je v každém z nich; `llm_mirror: false` na úrovni obsahu určuje, co se zrcadlí. Plugin je teď přenositelný na libovolný Pelican web, který má `widget_processor`.

## Reference souborů

- [`plugins/llm_ally.py`](../plugins/llm_ally.py) - samotný plugin (~165 řádků, žádné stringy specifické pro web).
- [`plugins/widget_processor.py`](../plugins/widget_processor.py) - poskytuje `render_widgets_in_text`.
- [`theme/templates/components/widget_*.txt.j2`](../theme/templates/components/) - textové šablony widgetů.
- [`content/llm/*.md`](../content/llm/) - soubory pro jednotlivá publika, editované editorem.

Statický soubor `marathon/llms.txt` pod [`content/extra/marathon/`](../content/extra/marathon/) zůstává tak, jak je; je to fixture pro samostatný sub-web maratonu, mimo působnost tohohle pluginu.

## Související dokumenty

- [Úprava obsahu](EDITING.md) - průvodce metadaty pro editory.
- [SEO + sociální kartičky](SEO.md) - kanonická strategie, hreflang, mechanika hubů.
- [Widget systém](WIDGETS.md) - tagy `<widget-*>` v těle článku.
- [Lokální testování](local-testing.md) - lokální vývoj a testování.
- [Nasazení](publishing.md) - publikační workflow.
- [Nastavení vývojového prostředí](setup.md) - počáteční nastavení projektu.
- [GitHub Issues](https://github.com/filipaldi/brnosaires/issues) - plán rozvoje, nápady, bugy.
- [Brnos Aires — web](../README.md) - hlavní průvodce pro editory.
