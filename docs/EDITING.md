# Úprava obsahu — přehled metadat

Tento dokument je **průvodce pro editory**, kteří publikují obsah na webu brnosaires.com. Říká, co napsat do hlavičky (frontmatteru) Markdown souboru a co každé pole skutečně dělá na živém webu.

Pokud chcete vědět *proč* je některé pole takto zařízené nebo jak je technicky propojené, čtěte [SEO + sociální kartičky](SEO.md). Pokud chcete porozumět tagům `<widget-*>` v těle článku, čtěte [Widget systém](WIDGETS.md). Vše níže je jen: *co napsat na začátek souboru?*

> Tento dokument doplňuje hlavní [Brnos Aires — web](../README.md), který je rovněž průvodcem pro editory. README pokrývá celkový pracovní postup (jak vytvořit soubor akce, jak používat widgety, jak nahrávat obrázky); tento dokument se zaměřuje výhradně na **metadata v hlavičce souboru** a na to, jak se promítnou do náhledů ve vyhledávačích a na sociálních sítích.

## Obsah

1. [Kde soubory leží](#kde-soubory-leží)
2. [Šablona akce — všechna pole](#šablona-akce--všechna-pole)
3. [Pravidelná série (`series:`)](#pravidelná-série-series-milongy-s-více-datovanými-instancemi)
4. [Hub stránka](#hub-stránka-contentpagesslug-sériemd)
5. [Samostatné stránky](#samostatné-stránky)
6. [Měsíční stránky milong](#měsíční-stránky-milong-contentpageseventsmilongy-brno-měsícmd)
7. [Oznámení / píkoška / osoba](#oznámení--píkoška--osoba)
8. [Co se zobrazí kde, když publikujete](#co-se-zobrazí-kde-když-publikujete)
9. [Časté chyby](#časté-chyby)
10. [Soubory pro AI asistenty](#soubory-pro-ai-asistenty-contentllm)
11. [Vyloučení stránky z `.md` zrcadla](#vyloučení-stránky-z-md-zrcadla-llm_mirror-false)
12. [Jazykové verze — anglická verze webu](#jazykové-verze--anglická-verze-webu-en)
13. [Související dokumenty](#související-dokumenty)

## Kde soubory leží

| Typ obsahu | Složka | URL |
|---|---|---|
| Akce (jednorázová nebo instance série) | `content/events/RRRR/MM/` | `/<slug>/` |
| Hlavní stránka („hub") pravidelné série | `content/pages/` | `/<slug>/` |
| Samostatná stránka (o nás, FAQ…) | `content/pages/` | `/<slug>/` |
| Oznámení | `content/announcements/` | `/<slug>/` |
| Píkoška (článek) | `content/curiosities/` | `/<slug>/` |
| Osoba (DJ, lektor) | `content/people/` | `/<slug>/` |

## Šablona akce — všechna pole

Zkopírujte, smažte řádky, které nepotřebujete, a upravte hodnoty.

```yaml
---
# POVINNÉ VŽDY
title: Milonga u Brněnského draka
slug: milonga-u-draka-2026-05-16
date: 2026-04-10 18:00:00         # datum PUBLIKACE (kdy soubor vznikl) — ne datum akce!
author: Lenka Pláteníková

# SILNĚ DOPORUČENO
description: Pravidelná páteční milonga u Brněnského draka v květnu 2026.
preview_image: /images/events/2026/milonga-u-draka-kveten.jpg

# POVINNÉ PRO AKCE
event-type: milonga                # milonga | workshop | class | praktika
event-start: 2026-05-16 19:00:00
event-end: 2026-05-16 22:30:00     # půlnoc = 2026-05-17 00:00:00  ← NIKDY nepište 24:00:00!
event-location: Stará radnice, Radnická 8, Brno

# VOLITELNÉ — smažte řádky, které nepotřebujete
event-organiser: Brno Tango Club   # kdo akci pořádá
entry: 150 Kč                      # vstupné; "zdarma" / "dobrovolné" nastaví isAccessibleForFree
series: milonga-u-draka            # jen pokud akce patří do série (viz sekce Pravidelná série níže)
instructor: Jana Nováková          # pro více lektorů: "['Jana Nováková', 'Petr Novák']"
recurrence: weekly friday          # jen pro šablonové opakující se akce — pro milongy NEPOUŽÍVAT
llm_mirror: false                  # vynechejte nebo nastavte false, chcete-li skrýt před AI asistenty
---
```

## Pravidelná série (`series:`) — milongy s více datovanými instancemi

Některé akce se opakují, ale každá instance je vlastní datovaný soubor (Milonga u Draka, Tango & Pizza). Bez seskupení by každé hledání jména série v Googlu rozdělovalo pozornost mezi N téměř identických stránek. Pole `series:` říká webu „všechny tyhle akce jsou jedna a ta samá věc, pošli vyhledávače na jednu hlavní stránku".

### Co potřebuje editor udělat

**Přidat novou instanci do existující série:**

1. Vytvořte soubor akce normálně v [content/events/](../content/events/)`RRRR/MM/`.
2. Přidejte jeden řádek: `series: <slug-existujícího-hubu>` (např. `series: milonga-u-draka`).
3. Hotovo. Web automaticky:
   - Přepne kanonickou URL stránky na `/{series}/`.
   - Zobrazí pod nadpisem odznak „Součást pravidelné série: …" odkazující na hub.
   - Přidá tento termín do seznamu „Nejbližší termíny série" na hubu (pokud je v budoucnu).

**Vytvořit zcela novou sérii:**

1. Vytvořte hub stránku: [content/pages/](../content/pages/)`<slug-série>.md`. Nastavte `series: <slug-série>` v jejím frontmatteru a do těla napište obecný popis série (atmosféra, místo, co očekávat).
2. Přidejte `series: <slug-série>` do každé existující instance v [content/events/](../content/events/).
3. Budoucí instance pak stačí, aby měly stejný řádek `series:`.

### Kdy `series:` **nepoužívat**

- Jednorázové akce, které se nebudou opakovat — nechte pole vynechané, stránka bude kanonická sama na sebe (což je správné chování).
- Opakující se **lekce/praktiky** psané přes `recurrence:` (jeden zdrojový soubor, jeden URL) — `series:` nepotřebují, už mají jednu kanonickou stránku.

## Hub stránka (`content/pages/<slug-série>.md`)

Hub stránka vypadá jako běžná stránka. Kritické jsou dva řádky: `slug` a `series` musí mít **stejnou hodnotu** — takto systém pozná, že je to hub a ne další instance.

```yaml
---
title: Milonga u brněnského draka
slug: milonga-u-draka                   # instance série píší series: milonga-u-draka
date: 2026-05-16 00:00:00
series: milonga-u-draka                 # hub odkazuje sám na sebe — slug = series
preview_image: /images/events/2026/milonga-u-draka.jpg
description: Pravidelná milonga ve Staré radnici v Brně.
author: Lenka Pláteníková
---
```

Tělo hubu popisuje **sérii obecně**, ne konkrétní termín. Sekce „Nejbližší termíny série" se vykreslí automaticky pod tělem — tu nepíšete vy.

## Samostatné stránky

Pro hub-stránky a běžné stránky (o nás, FAQ, marathon sub-site) stačí společná pole nahoře. Bez polí pro akce. Bez `series`, pokud to není hub.

### Roční úklid: rok v titulcích landing stránek

Titulky a nadpisy přehledových stránek (`tango-kalendar-brno`, `tango-milongy-brno`, `tango-lekce-brno` a jejich `.en.md` varianty) obsahují aktuální rok kvůli vyhledávání (lidé hledají „milonga Brno 2026"). **Jednou ročně** (typicky začátkem ledna) v nich přepište rok na nový — je to ~6 souborů + 6 anglických dvojčat, jen pole `title`, `description` a první `<h1>`/odstavec. Měsíční stránky (`milongy-brno-<měsíc>`, viz níže) rok řeší samy přes build-time filtr, ty se nedotýkáte.

## Měsíční stránky milong (`content/pages/events/milongy-brno-<měsíc>.md`)

Dvanáct stránek, jedna pro každý měsíc (`/milongy-brno-leden/` … `/milongy-brno-prosinec/`), aby web uměl odpovědět na hledání „milonga Brno červen", „milonga Brno květen 2026" apod. Jsou **bez ročníku** — stejná URL platí každý rok, mění se jen zobrazený rok.

**Co je v souboru a co (ne)měnit:**

```yaml
---
title: Milongy v Brně v květnu   # záložní; skutečný <h1> a <title> vyrábí šablona — ROK SEM NEPIŠ
slug: milongy-brno-kveten
date: 2026-01-01 00:00:00
month: 5                          # 1–12; NEDOTÝKEJ SE — řídí zobrazený rok, noindex, navigaci
---
```

- Nadpis `#` do těla **nepřidávej** — `<h1>` dodá šablona.
- Úvodní odstavec klidně uprav, ale **nepiš konkrétní rok** — stránka je evergreen.
- `<widget-calendar month="N" ...>` v těle musí mít stejné číslo jako `month:` ve frontmatteru.
- Prázdný měsíc se sám označí `noindex`; jakmile přibyde akce, při dalším buildu se `noindex` zruší. **Nic neděláš.**

**Přidat akci do měsíční stránky** = nic navíc. Stačí normálně vytvořit soubor akce v [content/events/](../content/events/)`RRRR/MM/` s `event-type: milonga` (nebo `praktika`/`neolonga`) a `event-start` v daném měsíci — objeví se na příslušné měsíční stránce automaticky.

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

- **Půlnoc jako `24:00:00`** — Python tento formát neumí zpracovat a akce se nepublikuje. Půlnoc pište jako začátek dalšího dne: `event-end: 2026-05-17 00:00:00` (ne `2026-05-16 24:00:00`).
- **`date:` nastavené na datum akce** — `date` je datum publikace souboru (kdy jste ho vytvořili), ne datum akce. Datum akce nastavujte pomocí `event-start`. Pokud `date` nastavíte do budoucnosti, stránka se nemusí objevit ve správném pořadí.
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

Editujete je stejně jako homepage: Markdown plus tagy `<widget-*>`. Při buildu se widgety rozbalí do bulletů. Detaily v [Discoverability pro LLM](LLMS.md).

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
- **Jednojazyčný obsah — `translate: false`.** Obsah, který **nemá a nikdy mít nebude** překlad (typicky anglicky psaný microsite), může v hlavičce deklarovat `translate: false`. Pak se pro něj negeneruje žádný `/en/` klon, nezobrazuje se přepínač jazyka a `<html lang>` je `en`. Pro **Tango Marathon** je tahle vlajka nastavena hromadně pro všechny tři jeho složky — [content/pages/marathon/](../content/pages/marathon/), [content/events/2026-marathon/](../content/events/2026-marathon/) a [content/people/marathon-djs/](../content/people/marathon-djs/) — přes `EXTRA_PATH_METADATA` v [pelicanconf.py](../pelicanconf.py). Marathon je tedy anglicky od začátku, bez české verze; jeho stránky, akce ani DJ profily žádný český sourozenec nedostávají a `<html lang>` je tam vždy `en`. Výchozí stav (bez vlajky) = obsah je „přeložitelný" a dostává český fallback pod `/en/`.

Architektura toho všeho (jak přesně se klony generují, jak funguje `hreflang`, proč jsou české URL beze změny) je popsaná v [SEO + sociální kartičky](SEO.md).

## Související dokumenty

- [Brnos Aires — web](../README.md) — hlavní průvodce pro editory (česky): pracovní postup, struktura souboru akce, widgety, obrázky.
- [SEO + sociální kartičky](SEO.md) — *proč* to celé funguje takto (anglicky, technický popis): kanonická strategie, `<base href>`, mechanika hubů, anglická verze a `hreflang`.
- [Widget systém](WIDGETS.md) — tagy `<widget-*>` v těle článku.
- [content/pages/series/milonga-u-draka.md](../content/pages/series/milonga-u-draka.md) — reálný příklad hub stránky pravidelné série. Organizace složek v `content/pages/`: `series/` = huby pravidelných sérií (`series: <slug>`); `events/` = stránky konkrétních akcí a časově vymezené přehledy milong (Tango víkend, Tango léto, „milongy tento týden" a budoucí měsíční přehledy); `marathon/` = sub-web maratonu. URL se přesunem **nemění** — Pelican routuje podle `Slug:`, ne podle cesty.
- [content/events/2026/05/2026-05-16-milonga-u-draka.md](../content/events/2026/05/2026-05-16-milonga-u-draka.md) — reálný příklad instance v sérii.
- [content/navigation/](../content/navigation/) — odkazy v navigaci: `main.md`/`main.en.md` (hlavička), `footer.md`/`footer.en.md` (patička), `marathon.md` (sub-web maratonu).
