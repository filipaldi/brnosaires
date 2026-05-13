# Úprava obsahu — přehled metadat

Tento dokument je **průvodce pro editory**, kteří publikují obsah na webu brnosaires.com. Říká, co napsat do hlavičky (frontmatteru) Markdown souboru a co každé pole skutečně dělá na živém webu.

Pokud chcete vědět *proč* je některé pole takto zařízené nebo jak je technicky propojené, čtěte [SEO.md](SEO.md). Pokud chcete porozumět tagům `<widget-*>` v těle článku, čtěte [WIDGETS.md](WIDGETS.md). Vše níže je jen: *co napsat na začátek souboru?*

> Tento dokument doplňuje hlavní [README.md](../README.md), který je rovněž průvodcem pro editory. README pokrývá celkový pracovní postup (jak vytvořit soubor akce, jak používat widgety, jak nahrávat obrázky); tento dokument se zaměřuje výhradně na **metadata v hlavičce souboru** a na to, jak se promítnou do náhledů ve vyhledávačích a na sociálních sítích.

## Kde soubory leží

| Typ obsahu | Složka | URL |
|---|---|---|
| Akce (jednorázová nebo instance série) | `content/events/RRRR/MM/` | `/<slug>/` |
| Hlavní stránka („hub") pravidelné série | `content/pages/` | `/<slug>/` |
| Samostatná stránka (o nás, FAQ…) | `content/pages/` | `/<slug>/` |
| Oznámení | `content/announcements/` | `/<slug>/` |
| Píkoška (článek) | `content/curiosities/` | `/<slug>/` |
| Osoba (DJ, lektor) | `content/people/` | `/<slug>/` |

## Společná pole (všechny typy obsahu)

| Pole | Povinné? | Co ovlivňuje |
|---|---|---|
| `title` | Ano | `<title>` stránky, nadpis v náhledu na sociálních sítích, drobečková navigace, nadpisy na kartičkách na webu. |
| `slug` | Ano | URL — `/{slug}/`. Používejte malá písmena, pomlčky, **bez diakritiky a bez mezer**. Po publikaci by se neměl měnit (rozbil by odkazy). |
| `date` | Ano | Datum publikace článku (kdy soubor vznikl). Pelican ho používá pro řazení. **Není totéž co `event-start`.** |
| `author` | Doporučeno | Zobrazuje se na detailu, slouží k atribuci. |
| `description` | Doporučeno | Jednovětné shrnutí. Použito jako `<meta description>`, `og:description`, `twitter:description`. **Pokud nenastavíte**, Pelican automaticky vytáhne prvních ~50 slov těla článku. Lépe ho ale nastavit explicitně — řídí, co se zobrazí ve výsledcích Googlu a v náhledech v iMessage / Slacku / Facebooku. Maximum cca 200 znaků. |
| `preview_image` | Doporučeno | Cesta pod `/images/...`. Najednou napájí tři místa: (1) kartičku akce/článku na webu, (2) náhled na Facebooku / LinkedIn / iMessage / WhatsApp / Slacku (`og:image`), (3) velkou kartičku na Twitteru/X (`twitter:image`). **Jeden obrázek, tři použití** — záměrně neexistují samostatná pole `og_image` / `twitter_image`. Pokud nenastavíte, náhledy na sociálních sítích pořád fungují, jen bez obrázku (jen titul + popis). |

## Specifická pole pro akce

| Pole | Povinné? | Co ovlivňuje |
|---|---|---|
| `event-type` | Ano | Jedna z hodnot: `milonga`, `workshop`, `class`, `praktika`. Ovlivňuje styl, filtrování v `/kalendar/` a typ JSON-LD struktury, kterou web vygeneruje. |
| `event-start` | Ano (pro akce) | Datum a čas začátku, např. `2026-05-16 19:00:00`. Použito v kalendáři, v JSON-LD bloku Event (kvalifikace pro Google rich-results) a v `.ics` feedu. |
| `event-end` | Ano (pro akce) | Datum a čas konce. Stejná použití jako `event-start`. |
| `event-location` | Ano (pro akce) | Volný text místa, např. `Stará radnice, Radnická 8, Brno`. Zobrazí se na stránce a vloží do JSON-LD pod `location.address`. |
| `event-organiser` | Doporučeno | Kdo akci pořádá. |
| `entry` | Volitelné | Vstupné — volně formátovaný řetězec (např. `entry: 150 Kč`, `entry: 390 Kč / 16 €`, `entry: zdarma`, `entry: dobrovolné`). Zobrazí se v hlavičce stránky akce i na kartě v kalendáři (česky „Vstupné: …", anglicky „Entry: …"). Pole je zároveň napojené na JSON-LD: hodnota jde do `offers.price` + `priceCurrency: CZK`; pokud napíšete `zdarma` / `free` / `0` / `dobrovolné`, šablona navíc nastaví `isAccessibleForFree: true`. Pole vynechejte, pokud vstupné neznáte / není relevantní — řádek se prostě nezobrazí. |
| `instructor` | Pro lekce/workshopy | Lektor/lektoři. Pro jednoho napište jméno přímo. Pro více: `"['Jméno Jedna', 'Jméno Dva']"` (viz README pro detail). |
| `recurrence` | Volitelné | Pro **šablonové** opakující se akce (typicky lekce/praktiky). Příklad: `recurrence: weekly sunday`. Plugin [recurring_events.py](../plugins/recurring_events.py) ji rozbalí na N instancí sdílejících jeden URL. **Nepoužívejte pro milongy** — milongy se píší jako oddělené souborové instance, viz „Pravidelná série (`series:`)" níže. |
| `series` | Volitelné | Označuje tuto instanci jako součást skupiny pod hlavní stránkou („hubem"). Viz „Pravidelná série" níže. |

### Minimální příklad akce

```yaml
---
title: Milonga u Brněnského draka
slug: milonga-u-draka-2026-05-16
date: 2026-04-10 18:00:00
event-type: milonga
event-start: 2026-05-16 19:00:00
event-end: 2026-05-16 22:30:00
event-location: Stará radnice, Radnická 8, Brno
series: milonga-u-draka
preview_image: /images/events/2026/milonga-u-draka-kveten.jpg
description: Květnová milonga u Brněnského draka.
author: Lenka Pláteníková
---
```

## Pravidelná série (`series:`) — milongy s více datovanými instancemi

Některé akce se opakují, ale každá instance je vlastní datovaný soubor (Milonga u Draka, Tango & Pizza). Bez seskupení by každé hledání jména série v Googlu rozdělovalo pozornost mezi N téměř identických stránek. Pole `series:` říká webu „všechny tyhle akce jsou jedna a ta samá věc, pošli vyhledávače na jednu hlavní stránku".

### Co potřebuje editor udělat

**Přidat novou instanci do existující série:**

1. Vytvořte soubor akce normálně v `content/events/RRRR/MM/`.
2. Přidejte jeden řádek: `series: <slug-existujícího-hubu>` (např. `series: milonga-u-draka`).
3. Hotovo. Web automaticky:
   - Přepne kanonickou URL stránky na `/{series}/`.
   - Zobrazí pod nadpisem odznak „Součást pravidelné série: …" odkazující na hub.
   - Přidá tento termín do seznamu „Nejbližší termíny série" na hubu (pokud je v budoucnu).

**Vytvořit zcela novou sérii:**

1. Vytvořte hub stránku: `content/pages/<slug-série>.md`. Nastavte `series: <slug-série>` v jejím frontmatteru a do těla napište obecný popis série (atmosféra, místo, co očekávat).
2. Přidejte `series: <slug-série>` do každé existující instance v `content/events/`.
3. Budoucí instance pak stačí, aby měly stejný řádek `series:`.

### Kdy `series:` **nepoužívat**

- Jednorázové akce, které se nebudou opakovat — nechte pole vynechané, stránka bude kanonická sama na sebe (což je správné chování).
- Opakující se **lekce/praktiky** psané přes `recurrence:` (jeden zdrojový soubor, jeden URL) — `series:` nepotřebují, už mají jednu kanonickou stránku.

## Hub stránka (`content/pages/<slug-série>.md`)

Hub stránka vypadá jako běžná stránka, jen má dva specifické požadavky ve frontmatteru:

| Pole | Proč na něm záleží |
|---|---|
| `slug: <slug-série>` | Musí odpovídat hodnotě, kterou ostatní instance zapíšou do svého pole `series:`. |
| `series: <slug-série>` | Ano, hub *také* má `series` — odkazuje sám na sebe. Logika přepisu kanonické URL to správně pozná jako „jsem hub" a smyčka se neuzavře. |

Tělo hubu by mělo popisovat **sérii obecně**, ne konkrétní termín. Sekce „Nejbližší termíny série" se vykreslí automaticky pod tělem — tu nepíšete vy.

## Samostatné stránky

Pro hub-stránky a běžné stránky (o nás, FAQ, marathon sub-site) stačí společná pole nahoře. Bez polí pro akce. Bez `series`, pokud to není hub.

### Roční úklid: rok v titulcích landing stránek

Titulky a nadpisy přehledových stránek (`tango-kalendar-brno`, `tango-milongy-brno`, `tango-lekce-brno` a jejich `.en.md` varianty) obsahují aktuální rok kvůli vyhledávání (lidé hledají „milonga Brno 2026"). **Jednou ročně** (typicky začátkem ledna) v nich přepište rok na nový — je to ~6 souborů + 6 anglických dvojčat, jen pole `title`, `description` a první `<h1>`/odstavec. Měsíční stránky (`milongy-brno-<měsíc>`, viz níže) rok řeší samy přes build-time filtr, ty se nedotýkáte.

## Měsíční stránky milong (`content/pages/events/milongy-brno-<měsíc>.md`)

Dvanáct stránek, jedna pro každý měsíc (`/milongy-brno-leden/` … `/milongy-brno-prosinec/`), aby web uměl odpovědět na hledání „milonga Brno červen", „milonga Brno květen 2026" apod. Jsou **bez ročníku** — stejná URL platí každý rok, mění se jen zobrazený rok.

**Co je v souboru a co (ne)měnit:**

| Pole / prvek | Co s tím |
|---|---|
| `month: N` ve frontmatteru (číslo 1–12) | **Nech být.** Tohle je přepínač, který stránce zapne měsíční režim: nadpis i `<title>` se z něj vyrobí (`Milongy v Brně v <6. pádu> <rok>`), vykreslí se seznam akcí v JSON-LD, `noindex` u prázdného měsíce, odkazy na sousední měsíce. |
| `title:` ve frontmatteru | Záložní — skutečný `<title>` a `<h1>` na stránce vyrábí šablona z `month:` (včetně roku přes `tango_year_for_month`). `title:` ponech jak je; **rok do něj nepiš**, nemá smysl ho udržovat. |
| nadpis `#` v těle | **Žádný nepřidávej.** `<h1>` dodává šablona. Soubor má jen úvodní odstavec + widgety. |
| úvodní odstavec | Bez ročníku. Text klidně uprav (úvodní věty, „atmosféra měsíce"), ať to není mdlé — jen tam **nepiš konkrétní rok**, ať stránka zůstane evergreen. |
| `<widget-calendar month="N" ...>` v těle | Vykreslí milongy/praktiky/neolongy v daném měsíci. `month` musí odpovídat `month:` z frontmatteru. |
| widget odběru `.ics` | Standardní, nech být. |
| prázdný měsíc | Když na ten měsíc zatím nic není, stránka se sama označí `noindex` (zůstane dostupná, ale Google ji nenabízí) a ukáže hlášku „Na tenhle měsíc zatím žádné milongy vypsané nejsou." Jakmile přidáš akci v tom měsíci, při příštím buildu se `noindex` sám zruší. **Nic neděláš.** |

**Přidat akci do měsíční stránky** = nic navíc. Stačí normálně vytvořit soubor akce v `content/events/RRRR/MM/` s `event-type: milonga` (nebo `praktika`/`neolonga`) a `event-start` v daném měsíci — objeví se na příslušné měsíční stránce automaticky.

**Odkazy na měsíční stránky** najdeš ve spodku stránek `tango-milongy-brno` a `tango-kalendar-brno` (řádek „Milongy po měsících: leden · únor · …") — to je obyčejný seznam odkazů v Markdownu, klidně ho uprav nebo přesuň. Mezi sebou se měsíční stránky prolinkují samy (předchozí/další měsíc + pásek všech měsíců dodává šablona).

**Anglické verze** jsou `.en.md` dvojčata se stejným `slug` a `Lang: en` (jako u ostatních stránek) — běží na `/en/milongy-brno-<měsíc>/`. Mění se jen text; `month:` a vše ostatní je stejné.

## Oznámení / píkoška / osoba

Použijte společná pole. Aktuálně:

- Oznámení se zobrazují na `/lenka-pise-oznamy/` (chronologicky).
- Píkošky se zobrazují na `/pikosky/`.
- Osoby se zobrazují na marathonové stránce DJs/teamu, když jsou tam odkazované.

Žádný z těchto typů nevkládá JSON-LD Event strukturu (správně — nejsou to akce).

## Co se zobrazí kde, když publikujete

| Když nastavíte… | …zobrazí se v |
|---|---|
| `title` | Záložce prohlížeče, výsledku Googlu, nadpisu náhledu na sociálních sítích, kartičce na webu |
| `description` | Snippetu ve výsledku Googlu, popisu náhledu na sociálních sítích (pokud nenastavíte, použije se prvních ~50 slov těla) |
| `preview_image` | Kartičce akce/článku na webu, náhledu na Facebooku/iMessage/Slacku, velké kartičce na Twitteru/X |
| `event-start` + `event-end` | Kalendáři (`/kalendar/`), hlavičce detailu akce, Google Event rich-result snippetu, `.ics` feedu |
| `event-location` | Hlavičce detailu akce, Google Event rich-result `location.address` |
| `entry` | Hlavičce detailu akce („Vstupné: …"), kartě akce v kalendáři, Google Event rich-result `offers.price`/`isAccessibleForFree` |
| `series:` | Kanonická URL ukazuje na hub, odznak „Součást pravidelné série", seznam „Nejbližší termíny série" na hubu |

## Časté chyby

- **Mezery nebo diakritika v `slug:`** — slug musí být ASCII s pomlčkami. Špatně: `Milonga u Mamuta`. Správně: `milonga-u-mamuta`.
- **Nastavený `series:` u jednorázové akce** — `series:` použijte jen tehdy, když existuje hub stránka s tímto slugem v `content/pages/`.
- **Chybějící `event-end`** — JSON-LD vyžaduje začátek i konec; build neselže, ale Google rich-result se nespustí.
- **Vymýšlení pole `og_image`** — takové pole neexistuje. Použijte `preview_image`.
- **Příliš dlouhý `description`** — držte se pod cca 200 znaky; delší hodnoty se ořežou.

## Soubory pro AI asistenty (`content/llm/`)

Adresář [content/llm/](../content/llm/) obsahuje soubory, které řídí to, co web nabízí LLM asistentům (ChatGPT, Claude, Perplexity, …) k textovému stažení. **Jeden soubor → jeden výstup:** každý `*.md` v `content/llm/` se při buildu promítne do stejně pojmenovaného `*.txt` na rootu webu (a do `.well-known/`).

Aktuálně:

| Soubor | Výstup |
|---|---|
| [content/llm/llms.md](../content/llm/llms.md) | `/llms.txt` (krátký kurátorský rozcestník) |
| [content/llm/llms-full.md](../content/llm/llms-full.md) | `/llms-full.txt` (širší výpis) |

Chcete přidat další cílové publikum (např. zvlášť pro robota, který indexuje jen milongy)? Vytvořte nový soubor:

```bash
cp content/llm/llms.md content/llm/milongas.md
# upravte hlavičky, widget filtry, popisky pro to publikum
# build → /milongas.txt a /.well-known/milongas.txt vzniknou samy
```

Editujete je stejně jako homepage: Markdown plus tagy `<widget-*>`. Při buildu se widgety rozbalí do bulletů. Detaily v [LLMS.md](LLMS.md).

## Vyloučení stránky z `.md` zrcadla (`llm_mirror: false`)

Plugin standardně generuje `.md` zrcadlo (čistý Markdown bez HTML/CSS) ke každé stránce a článku — LLM asistent si tak může stáhnout obsah ve strojově dobře zpracovatelné podobě. Pokud nějaký soubor **nemá** být zrcadlen (např. interní píkošky, profily lidí), stačí do jeho frontmatteru přidat jeden řádek:

```yaml
---
title: …
slug: …
date: …
llm_mirror: false
---
```

Aktuálně tento řádek nesou všechny soubory v [content/curiosities/](../content/curiosities/) a [content/people/](../content/people/). Editor jednotlivých souborů to může kdykoli vrátit zpět odebráním řádku — `.md` zrcadlo se začne znovu generovat při dalším buildu. HTML stránka tím dotčená není.

## Jazykové verze — anglická verze webu (`/en/`)

Web má anglickou verzi pod prefixem `/en/`. České stránky si ponechávají původní URL (`/<slug>/`) beze změny. V hlavičce webu je přepínač `CS · EN`.

**Jak to funguje editorsky:**

- **Každá stránka má anglický klon „zdarma".** I když anglickou verzi nenapíšete, `/en/<slug>/` přesto existuje — zobrazí *české tělo* článku, ale s anglickým „obalem": navigace, datumy, meta tagy, přepínač jazyka, `<html lang="en">`, `hreflang`. Web tak má od začátku plné pokrytí; překlady přibývají postupně.
- **Chcete napsat skutečnou anglickou verzi stránky?** Vytvořte vedle původního souboru sourozenec s příponou `.en.md` a **stejným `slug`em**:

  ```
  content/pages/o-nas.md        →  Lang: cs  (nepovinné — výchozí),  Slug: o-nas
  content/pages/o-nas.en.md     →  Lang: en,                          Slug: o-nas   (stejný slug!)
  ```

  Pelican je propojí podle `slug`u. Anglický soubor se vyrenderuje na `/en/o-nas/`, přepínač jazyka mezi nimi pak skáče správně. `Lang: en` do hlavičky napište explicitně, i když přípona `.en.` ho nastavuje sama (kvůli čitelnosti).

  **Postup krok za krokem:** zkopírujte `content/pages/foo.md` → `content/pages/foo.en.md`; do hlavičky přidejte `Lang: en` a ponechte **stejný `Slug:`** jako v českém souboru; přeložte `Title:`, `Description:` a tělo (anglicky podle [voice skillu](../.claude/skills/voice/SKILL.md) — britská angličtina, bez pomlček „—"); widgety (`<widget-*>`) nechte tak, jen u nich přeložte texty v atributech `label=` / `label_webcal=` / `label_google=` / `label_outlook=`. Hotovo — stránka se objeví na `/en/<slug>/` místo dosavadního českého fallbacku.
- **Domovská stránka:** anglický `content/pages/index.en.md` má zvláštnost — musí mít `Slug: index` (web má `SLUGIFY_SOURCE = "basename"`, takže slug českého `index.md` je `index`, ne `brnos-aires` z titulku — sourozenec se propojí jen při shodě slugu) **a** `save_as: en/index.html` / `url: en/` (český `index.md` má vlastní `save_as`, který by se jinak zdědil).
- **Datumy** se vykreslují podle jazyka stránky: česky `16. 05. 2026`, anglicky `16 May 2026`. Nic nenastavujete — je to automatické.
- **Navigace v hlavičce i patičce:** odkazy se berou ze souborů v [content/navigation/](../content/navigation/) — formát `Popisek, slug` (jeden na řádek; `slug` je slug stránky nebo absolutní URL; řádky `#…` jsou komentář). Hlavní navigace: `main.md` (česky) + `main.en.md` (anglické popisky, stejné slugy). Patička: `footer.md` + `footer.en.md` — patička je **per-jazyk** (na `/en/` stránkách je celá anglicky), kromě odkazů obsahuje ještě automaticky pásek měsíčních stránek („Milongy po měsících:") a odkazy na `.ics` kalendáře — ty se z `footer.md` neberou, jsou v šabloně [components/footer.html](../theme/templates/components/footer.html). Pořadí v navigaci = pořadí řádků v souboru; změna se projeví na celém webu.
- **Jednojazyčný obsah — `translate: false`.** Obsah, který **nemá a nikdy mít nebude** překlad (typicky anglicky psaný microsite), může v hlavičce deklarovat `translate: false`. Pak se pro něj negeneruje žádný `/en/` klon, nezobrazuje se přepínač jazyka a `<html lang>` je `en`. Pro **Tango Marathon** je tahle vlajka nastavena hromadně pro všechny tři jeho složky — `content/pages/marathon/`, `content/events/2026-marathon/` a `content/people/marathon-djs/` — přes `EXTRA_PATH_METADATA` v `pelicanconf.py`. Marathon je tedy anglicky od začátku, bez české verze; jeho stránky, akce ani DJ profily žádný český sourozenec nedostávají a `<html lang>` je tam vždy `en`. Výchozí stav (bez vlajky) = obsah je „přeložitelný" a dostává český fallback pod `/en/`.

Architektura toho všeho (jak přesně se klony generují, jak funguje `hreflang`, proč jsou české URL beze změny) je popsaná v [SEO.md](SEO.md).

## Související dokumenty

- [README.md](../README.md) — hlavní průvodce pro editory (česky): pracovní postup, struktura souboru akce, widgety, obrázky.
- [SEO.md](SEO.md) — *proč* to celé funguje takto (anglicky, technický popis): kanonická strategie, `<base href>`, mechanika hubů, anglická verze a `hreflang`.
- [WIDGETS.md](WIDGETS.md) — tagy `<widget-*>` v těle článku.
- [content/pages/series/milonga-u-draka.md](../content/pages/series/milonga-u-draka.md) — reálný příklad hub stránky pravidelné série. Organizace složek v `content/pages/`: `series/` = huby pravidelných sérií (`series: <slug>`); `events/` = stránky konkrétních akcí a časově vymezené přehledy milong (Tango víkend, Tango léto, „milongy tento týden" a budoucí měsíční přehledy); `marathon/` = sub-web maratonu. URL se přesunem **nemění** — Pelican routuje podle `Slug:`, ne podle cesty.
- [content/events/2026/05/2026-05-16-milonga-u-draka.md](../content/events/2026/05/2026-05-16-milonga-u-draka.md) — reálný příklad instance v sérii.
- [content/navigation/](../content/navigation/) — odkazy v navigaci: `main.md`/`main.en.md` (hlavička), `footer.md`/`footer.en.md` (patička), `marathon.md` (sub-web maratonu).
