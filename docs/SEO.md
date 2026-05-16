# SEO + sociální kartičky

Tento dokument popisuje, jak web vystavuje metadata vyhledávačům a konzumentům sociálních kartiček, a fixuje rozhodnutí, která ze samotných šablon nejsou zřejmá.

> **Pro editory:** Tento dokument je technický. Editorský průvodce metadaty s vysvětlením, jaká pole nastavovat ve frontmatteru a co každé dělá v náhledech na sociálních sítích, je v [Úprava obsahu](EDITING.md). Tady jde o architekturu, která pod tím vším běží.

## Obsah

1. [Strategie odkazů: relativní URL + `<base href>`](#strategie-odkazů-relativní-url--base-href)
2. [Kanonická URL](#kanonická-url)
3. [Vícejazyčnost: zrcadlo `/en/`](#vícejazyčnost-zrcadlo-en)
4. [Opakující se akce: hub stránky](#opakující-se-akce-hub-stránky)
5. [Evergreen měsíční stránky (`/milongy-brno-<měsíc>/`)](#evergreen-měsíční-stránky-milongy-brno-měsíc)
6. [Open Graph + Twitter Card](#open-graph--twitter-card)
7. [Discoverabilita llms.txt](#discoverabilita-llmstxt)
8. [Strukturovaná data (JSON-LD)](#strukturovaná-data-json-ld)
9. [Související shipnuté kousky](#související-shipnuté-kousky)
10. [Související dokumenty](#související-dokumenty)

## Strategie odkazů: relativní URL + `<base href>`

Všechny šablony emitují **relativní** URL:

- `href="{{ x.slug }}/"` pro navigaci
- `src="{{ x.preview_image.lstrip('/') }}"` pro obrázky
- `href="{{ nav_page.url }}"` pro boční menu

Jediný `<base href="{{ SITEURL }}/">` v [theme/templates/base.html](../theme/templates/base.html) je všechny dořeší. **Nikdy `<base href>` neodstraňuj ani neobcházej** — boční menu a každá kartička v listingu na něm závisí. Pokud se v šabloně přistihneš, jak píšeš `{{ SITEURL }}/{{ x.url }}`, jdeš proti zavedené strategii. Zastav se a použij relativní formu.

Trade-off: `<base href>` taky přepíše `<a href="#section">` na `https://brnosaires.com/#section` místo aby zůstal na aktuální stránce. Dnes žádné on-page fragment odkazy nemáme; kdyby se to změnilo, použij raději JS-driven scrolling nebo absolutní `href="{current_url}#section"`, ne shazování `<base>`.

## Kanonická URL

Každá stránka emituje `<link rel="canonical" href="{{ SITEURL }}/{{ url }}">`. Říká to vyhledávačům jedinou pravou URL stránky a brání tomu, aby `RELATIVE_URLS` artefakty (`/x/`, `/x/index.html`, …) vyvolaly penalizaci za duplicitní obsah.

U **opakujících se akcí** (Milonga u Draka, Tango & Pizza, opakující se lekce) kanonická URL každé instance ukazuje na **hub stránku** v [content/pages/](../content/pages/), ne na instanci samotnou. Viz „Opakující se akce: hub stránky" níže.

> **Známé omezení (fallback `/en/` stránky):** fallback stránka `/en/<event-instance>/` (taková, která nemá skutečný anglický překlad) si kanonickou počítá proti *českému* hubu (`/<hub-slug>/`), ne anglickému. To je obhajitelné — tělo fallbacku *je* česká stránka — ale když někdy hub přeložíš, přelož i instance, nebo akceptuj cross-language kanonickou.

## Vícejazyčnost: zrcadlo `/en/`

Web má anglickou verzi pod prefixem `/en/`. Čeština (výchozí jazyk, `DEFAULT_LANG = "cs"`) si ponechává původní root-level URL beze změny — **nulové riziko pro stávající SEO** — a obsah v jiném než výchozím jazyce routuje pod `/en/` přes `PAGE_LANG_URL` / `PAGE_LANG_SAVE_AS` / `ARTICLE_LANG_*` / `CATEGORY_LANG_*` v [pelicanconf.py](../pelicanconf.py).

**Jak stránka dostane anglickou verzi:** přidej sourozenecký soubor s `Lang: en` a *stejným* `Slug` (Pelican propojuje překlady podle slugu, přes `ARTICLE_TRANSLATION_ID` / `PAGE_TRANSLATION_ID`, oba `"slug"`). Např. `o-nas.md` (`Lang: cs`, `Slug: o-nas`) + `o-nas.en.md` (`Lang: en`, `Slug: o-nas`) → druhý se vyrenderuje na `/en/o-nas/`.

**Český fallback** je jediný vlastní kousek — Pelican v jádře dá `/en/<slug>/` jen tehdy, když existuje skutečný `.en.md`. [plugins/i18n_fallback.py](../plugins/i18n_fallback.py) tu díru zaplňuje: v `page_generator_finalized` / `article_generator_finalized` (po `process_translations`, před zápisem výstupu) syntetizuje `en` translation objekt pro každou českou stránku, která žádný nemá — stejný slug, `Lang: en`, znovu používá *už vyrenderovaný* `_content` (proto je plugin registrován v `PLUGINS` **až za** `widget_processor`em, aby byly widgety v těle už rozbalené). Klon se napojí do `.translations` na obě strany a přidá do `generator.translations` (writer iteruje právě to). Výsledek: `/en/<slug>/` zrcadlí celý web od startu, s anglickým „obalem" (nav, datumy, meta, hreflang, `<html lang="en">`) obalujícím české tělo, dokud nedorazí skutečný překlad. Marathon stránky jsou přeskočené — to je English-first sub-web bez českého zrcadla, takže nesmí dostat duplicitu `/en/marathon-…`.

**`page_lang`** se počítá jednou nahoře v [base.html](../theme/templates/base.html) (před `<html>`): marathon sekce → `en`, jinak `Lang:` content objektu (výchozí `cs`). Řídí `<html lang>`, `<meta og:locale>` (`cs_CZ` / `en_GB`), meta description (`SITEDESCRIPTION` / `SITEDESCRIPTION_EN`), `hreflang`, aria-labely v navigaci a guard přepínače jazyka. UI stringy chrome se berou z per-jazykových tabulek v [theme/i18n/](../theme/i18n/) přes `t(key, page_lang)` Jinja filtr; datumy z `DATE_FORMATS = {"cs": "%d. %m. %Y", "en": "%-d %B %Y"}`.

**`hreflang`:** každá stránka (s nastaveným `SITEURL`) emituje `<link rel="alternate" hreflang="…">` pro sebe + pro každý ze svých `.translations`, plus `hreflang="x-default"` ukazující na českou (default-language) verzi. Marathon stránky nemají překlad → žádný `hreflang` blok, což je správně (jednojazyčný sub-web). Sitemap zahrnuje `/en/` stránky automaticky.

**Přepínač jazyka** ([theme/templates/components/lang_switcher.html](../theme/templates/components/lang_switcher.html)): `CS · EN` v hlavičce; aktuální jazyk je inertní, druhý odkazuje na překladový protějšek této stránky (nebo `/` ↔ `/en/` pro homepage). Na marathon stránkách se úplně vynechává. Malý progressive-enhancement skript v `base.html` si zvolený jazyk pamatuje v `localStorage` a na holém root pathu redirectuje na `/en/`, pokud bylo dřív zvoleno `en` — odkazy fungují fajn i bez JS.

Editorská verze tohoto všeho (pojmenování `.en.md`, co kam psát): [Úprava obsahu → Jazykové verze](EDITING.md).

## Opakující se akce: hub stránky

Některé akce se opakují, ale každý termín je autorovaný jako vlastní datovaný soubor (např. `2026-04-18-milonga-u-draka.md`, `2026-05-16-milonga-u-draka.md`). Bez zásahu vyhledávače vidí N téměř identických URL soutěžících o stejný dotaz a roztříští link equity. Konvence `series:` to řeší.

### Jak to funguje

1. **Vytvoř hub stránku** v [content/pages/series/](../content/pages/series/) se stabilním slugem, např. [content/pages/series/milonga-u-draka.md](../content/pages/series/milonga-u-draka.md). Ve frontmatteru nastav `series: <slug>`, čímž ji označíš jako hub. Tělo popisuje opakující se akci obecně (místo, atmosféra, hudební styl, organizátoři). (Podsložka `series/` je čistě organizační — Pelican routuje podle `Slug:`, ne podle cesty; huby jednorázových / vícedenních akcí jako Tango Weekend žijí v [content/pages/events/](../content/pages/events/).)

2. **Otaguj každou instanci** stejným polem `series: <slug>` v jejím frontmatteru. Žádné změny v těle.

3. **Šablony udělají zbytek:**
   - [theme/templates/base.html](../theme/templates/base.html) detekuje `series:` na článku a přepíše `<link rel="canonical">` a `<meta property="og:url">` tak, aby ukazovaly na URL hubu (`/<series>/`) místo na sebe. Totéž platí pro samotný hub, který triviálně kanonicalizuje sám na sebe.
   - [theme/templates/article.html](../theme/templates/article.html) vyrenderuje pod hlavičkou akce malý odkaz „Součást pravidelné série: [Hub Title]", aby čtenáři i crawler měli cestu instance → hub.
   - [theme/templates/page.html](../theme/templates/page.html) detekuje `series:` na stránce a vyrenderuje sekci „Nejbližší termíny" se všemi budoucími instancemi série (filtrované podle `event-start >= today`, řazené chronologicky). Používá existující `calendarium` Jinja filtr, aby se metadata akcí parsovala konzistentně se zbytkem webu.

### Přidání nové série

1. Vytvoř `content/pages/<series-slug>.md` s `series: <series-slug>` ve frontmatteru a popisným tělem.
2. Přidej `series: <series-slug>` ke každému existujícímu souboru instance v [content/events/](../content/events/).
3. Budoucí instance potřebují jen stejný řádek `series:` a samy se na hubu objeví.

### Co hub **nepotřebuje**

- Jednorázové akce (jediná milonga, která se nebude opakovat) — self-canonical je správně.
- Opakující se lekce/praktiky autorované přes pole `recurrence:` v [plugins/recurring_events.py](../plugins/recurring_events.py) — ty jsou jediný zdrojový soubor rozbalený do N termínů sdílejících jednu URL, takže už mají jednu kanonickou plochu.

## Evergreen měsíční stránky (`/milongy-brno-<měsíc>/`)

Dvanáct ručně psaných stránek, jedna pro každý český název měsíce (`/milongy-brno-leden/` … `/milongy-brno-prosinec/`), v [content/pages/events/](../content/pages/events/). Cílí na dotazovací vzor *„milonga Brno [měsíc]"* / *„milonga Brno [měsíc] [rok]"* — na který nic jiného na webu titulem ani strukturou necílí. Každý `.md` je tenká schránka: evergreen úvodní odstavec (bez roku, s větou per-měsíc atmosféry), `<widget-calendar month="<N>" filter_by_type="milonga praktika neolonga">`, widget odběru `.ics` — a **záměrně bez `#` H1 a bez roku kdekoliv v souboru**. Jsou **year-agnostic** — URL se používá každý rok, mění se jen zobrazený rok, a tiskne ho *šablona* (viz níže). Vstupní body: pásek odkazů „Milongy po měsících:" stylu `<widget-calendar>` na [milongy.md](../content/pages/milongy.md) a [kalendar.md](../content/pages/kalendar.md) (CS + `.en.md`), plus inter-page prev/next prstenec + pásek všech měsíců, který emituje šablona.

### Pohyblivé části

- **`month: <N>` ve frontmatteru** stránky (číslo 1–12) je vlajka, která v [theme/templates/page.html](../theme/templates/page.html) zapne větev pro měsíční stránku. Taky šabloně říká, akce kterého měsíce vypsat do JSON-LD.
- **`tango_year_for_month(month)`** — Jinja filtr ([pelicanconf.py](../pelicanconf.py)). `page.html` ho používá (společně s `month_name(N, lang, 'locative')`) k sestavení `<title>` *i* `<h1>` měsíční stránky — `Milongy v Brně v <6. pádu> <rok>` (CS) / `Milongas in Brno in <Month> <year>` (EN) — takže se rok počítá v době buildu: aktuální rok, nebo příští rok, pokud už ten měsíc tento rok proběhl. Takže v listopadu titulek `/milongy-brno-leden/` čte „…leden 2027". **Žádná roční editorská povinnost a v `.md` se nic neaktualizuje.** (Lang pro ten titulek se čte z `page.lang`, ne z obvyklého `page_lang` — `page_lang` nastavuje `base.html` *až po* top-level statementech child šablony, takže nahoře ještě není vidět.) Společné helpery, taky v `pelicanconf.py` + zaregistrované v `JINJA_FILTERS`: `month_name(n, lang, form)` — display name, `form="locative"` dává české „v lednu"; `month_page_slug(n)` / `month_page_url(n, lang)`; `month_wrap(n, ±1)` — měsíční aritmetika, která omotává 12↔1. Calendarium plugin si v [dates.py](../plugins/calendarium/dates.py) drží vlastní drobné `year_for_month` zrcadlo — plugin nesmí importovat site config.
- **`<widget-calendar month="<N>">`** — parametr `month=` (viz [Widget systém](WIDGETS.md)) omezí widget přesně na ten kalendářní měsíc v roce vyřešeném `tango_year_for_month`, přepisuje `days`/`start`/`end`.
- **Větev `page.html` pro měsíční stránku** (gate na `month:`):
  - emituje JSON-LD **`ItemList`** milong/praktik/neolong toho měsíce (`itemListElement` → `ListItem` → `Event` s `startDate`/`endDate`/`location`/`url`) — postavený ze *stejného* `calendarium(month=…)` dotazu, jaký používá widget, takže nemůže driftovat od toho, co je vyrenderované;
  - pokud měsíc aktuálně **nemá žádné akce**, emituje `<meta name="robots" content="noindex,follow">` (přes `head` blok) plus empty-state řádek — drží tenkou stránku crawlovatelnou, ale mimo index, dokud akce nepřibyde; `noindex` se sám vypne při dalším buildu po přidání odpovídající akce;
  - renderuje **prev/next-month prstencové odkazy** (`← květen` / `červenec →`) a **pásek všech měsíců** — crawl cesty mezi 12, lang-aware (`/milongy-brno-<m>/` v CS, `/en/milongy-brno-<m>/` v EN).
- **Anglická dvojčata** jsou `.en.md` sourozenci se *stejným* slugem + `Lang: en` (jako každé jiné `.en.md`) → routováno na `/en/milongy-brno-<m>/`. Liší se jen text a zobrazený měsíc/rok; parametr `month=` a year filter jsou jazykově neutrální.
- **Canonical/sitemap**: každá měsíční stránka je self-canonical a sitemap plugin si ji vezme automaticky; `noindex` (jen prázdné měsíce) drží ty tenké mimo index, aniž by je odstranil.

Editorská verze (jak měsíční stránku autorovat/editovat, čeho se nedotýkat): [Úprava obsahu → Měsíční stránky milong](EDITING.md).

## Open Graph + Twitter Card

`<head>` obsahuje:

- Open Graph — `og:site_name / locale / title / description / type / url / image`. Používá Facebook, LinkedIn, Slack, Discord, WhatsApp, iMessage, Google pro renderování náhledů odkazů.
- Twitter Card — `twitter:card=summary_large_image` plus title/description/image. Twitter/X ignoruje samotný OG a čte vlastní namespace. `summary_large_image` ukazuje preview obrázek od kraje ke kraji nad titulkem.

### Jeden obrázek pohání všechno: `preview_image`

Články a stránky už deklarují `preview_image:` ve frontmatteru pro renderování kartičky na webu ([components/event_card.html](../theme/templates/components/event_card.html), [components/widget_articles.html](../theme/templates/components/widget_articles.html), [article.html](../theme/templates/article.html), [page.html](../theme/templates/page.html)). Totéž pole pohání `og:image` i `twitter:image` — záměrně **neexistují samostatná pole `og_image` / `twitter_image` ve frontmatteru**.

Důvody:

- Jeden obrázek na content item, ne tři.
- Garantovaná parita mezi kartičkami na webu a externími náhledy odkazů.
- Nulová autorská zátěž — každý autor už `preview_image` plní.

Pokud stránka `preview_image` nemá, `og:image` / `twitter:image` se neemituje (graceful degradation). Sociální náhledy se pořád vyrenderují s titulkem + popisem, jen bez obrázku.

### Fallback řetězec pro description

`<meta name="description">`, `og:description`, `twitter:description` se všechny resolvují v tomto pořadí:

1. `article.description` / `page.description` (explicitní frontmatter, když je nastaven)
2. `article.summary` (auto-generovaný Pelicanem z prvních ~50 slov)
3. `_site_desc` — `SITEDESCRIPTION` (cs) / `SITEDESCRIPTION_EN` (en)

Oříznuté na 200 znaků a zbavené HTML — to je proměnná `_desc` v [base.html](../theme/templates/base.html). Všechny tři tagy ji používají. (Do T1 byl `<meta name="description">` hardcodovaný na sitewide `{{ SITENAME }} - {{ SITEDESCRIPTION }}` a jen `og:`/`twitter:` ctily `_desc` — takže každá stránka shipovala stejný search snippet. Opraveno: tag `<meta description>` teď sedí pod přiřazením `_desc` a používá ho.)

## Discoverabilita llms.txt

`<head>` taky obsahuje:

```html
<link rel="alternate" type="text/plain" title="llms.txt" href=".../llms.txt">
<link rel="alternate" type="text/plain" title="llms-full.txt" href=".../llms-full.txt">
```

Ty ukazují na LLM-readable endpointy generované [plugins/llms_index.py](../plugins/llms_index.py). LLM crawleri a chatboti, kteří se řídí [konvencí llms.txt](https://llmstxt.org), objeví endpointy přes tyto hinty. Struktura pluginu a co která sekce obsahuje viz [Discoverability pro LLM](LLMS.md).

## Strukturovaná data (JSON-LD)

Schema.org JSON-LD se emituje server-side (je to statický web — není tu JS, který by ho injektoval). Kde každý blok žije:

| `@type` | Kde | Poznámky |
|---|---|---|
| `Event` | [article.html](../theme/templates/article.html), gated na `event-start` | `name`, `description`, `startDate`/`endDate` (ISO8601 přes filtr `event_iso8601`), `eventStatus`, `eventAttendanceMode` (offline), `location` (viz `event_address` níže), `organizer`, `performer`, `image`, `url`, `@id` (`<canonical>#event`). Pro instanci se `series:`: `superEvent` → `EventSeries` ukazující na hub, a `url`/`@id` se resolvujou na hub (stejné pravidlo jako `<link rel=canonical>`). `offers` (`@type` Offer, `price`/`priceCurrency` CZK/`availability`) je **gated na pole `entry:` ve frontmatteru** — žádná akce ho ještě nemá (vedeno jako [issue](https://github.com/filipaldi/brnosaires/issues)), takže blok je dormantní; `isAccessibleForFree: true` když je `entry` „zdarma"/„free"/„0"/„dobrovolné". |
| `EventSeries` | [page.html](../theme/templates/page.html), na hub stránce se `series:` | `name`, `description`, `url`, `image`, `location` (Brno) a `subEvent` — každá budoucí instance jako minimální `Event`. Dělá z hubu jedinou strukturovanou plochu pro „všechny budoucí termíny série \<series\>". |
| `ItemList` | [page.html](../theme/templates/page.html), na `/tango-kalendar-brno/` (matchováno podle `page.slug`) a na každé měsíční stránce (vlajka `month:`) | `itemListElement` → `ListItem` → `Event`. Kalendářní list je dalších ≤50 nadcházejících akcí; měsíční list jsou milongy/praktiky/neolongy daného měsíce. Oba postavené ze stejného `calendarium(...)` dotazu, jaký používá viditelný widget, takže data nemohou driftovat od toho, co je vyrenderované. |
| `FAQPage` | [page.html](../theme/templates/page.html), na `/tango-pro-zacatecniky-brno/` (stránka [E2 glossary](EDITING.md)) | `mainEntity` → `Question`/`acceptedAnswer`, parsované z Markdownu stránky ve formátu `**Otázka?**` + odstavec odpovědi přes Jinja filtr `faq_pairs` (jen `<p><strong>…?</strong> …</p>` bloky, jejichž tučný text končí `?` — běžný tučný text v těle se ignoruje). FAQ se přidává/edituje editováním sekce „Časté otázky" té stránky; nic jiného není potřeba. |
| `Organization` | [components/footer.html](../theme/templates/components/footer.html), jednou na stránku (patička je na každé stránce) | `@id` `<siteurl>/#organization`, `name`, `description` (per jazyk), `areaServed` → `City` „Brno". Základní entity signál; žádné `sameAs`/`email`/`logo` (pro web žádné neexistuje — nevymýšlej). |

Filtr `event_address(loc)` ([pelicanconf.py](../pelicanconf.py)) ze stringu `event-location` v kanonickém tvaru `"Venue, Street, Brno-District"` udělá `Place` (`name`) obalující `PostalAddress` (`streetAddress`/`addressLocality`/`addressCountry: "CZ"`), s bezpečným degradováním: `"Venue, Brno"` → `Place` + `PostalAddress` jen s `addressLocality`; samotné `"Brno"` / `"Brno-District"` → jen locality v `PostalAddress`, bez `name`; samotný název venue (bez čárky) → jen `Place` `name`, bez adresy; prázdné → `{}` (šablona spadne zpět na surový string). **Nikdy neemituje napůl postavenou `PostalAddress`** — každá úroveň graceful degradationem padá na další. Spoléhá na to, že je `event-location` v kanonickém 3-/2-dílném tvaru ([E3 hygiene pass](EDITING.md) ho normalizoval). `"Brno"` v `addressLocality` je literální city signál pro `milonga Brno`.

Malý řádek „Poprvé na milonze? [Mrkni, jak na to.](…)" pod hlavičkou akce na `milonga`/`praktika`/`neolonga` stránkách odkazuje na beginner stránku (stringy `first_milonga_prompt` / `first_milonga_link` v [theme/i18n/](../theme/i18n/)) — site-wide interní odkazy na glossary stránku.

## Související shipnuté kousky

- **`sitemap.xml`** generovaný komunitním pluginem `pelican.plugins.sitemap`; konfigurace v `SITEMAP` v [pelicanconf.py](../pelicanconf.py). Inzerováno v [content/extra/robots.txt](../content/extra/robots.txt).
- **Per-page Markdown zrcadla** generovaná [plugins/md_mirror.py](../plugins/md_mirror.py). Zdokumentováno v [Discoverability pro LLM](LLMS.md).

## Související dokumenty

- [EDITING.md](EDITING.md) — editorský průvodce metadaty ve frontmatteru.
- [LLMS.md](LLMS.md) — `llms.txt` / `llms-full.txt` endpointy a per-page `.md` zrcadla.
- [WIDGETS.md](WIDGETS.md) — tagy `<widget-*>` v těle článku.
- [local-testing.md](local-testing.md) — lokální dev server, port 41234, phone preview.
- [publishing.md](publishing.md) — deploy přes GitHub Actions na GitHub Pages.
- [setup.md](setup.md) — first-time setup repozitáře a venv.
- [ROADMAP.md](ROADMAP.md) - rozcestník na GitHub Issues.
- [../README.md](../README.md) — hlavní průvodce pro editory: pracovní postup, struktura souboru akce, widgety, obrázky.
