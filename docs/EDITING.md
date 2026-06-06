# Úprava obsahu — přehled metadat

Průvodce pro editory: co napsat do hlavičky (frontmatteru) Markdown souboru. Pracovní postup řeší [README](../README.md), *proč* to funguje [SEO](SEO.md), widgety [WIDGETS](WIDGETS.md).

## Kam co patří — rychlé odkazy do repa

Klikněte na složku, ve které soubor pro daný typ obsahu leží. Editovat budete vždy uvnitř `content/`.

| Co chcete přidat / upravit | Otevřete složku |
|---|---|
| Konkrétní akci (milongu, workshop, lekci) | [content/events/](../content/events/) → podsložka `RRRR/MM/` |
| Hub pravidelné série (Milonga u Draka, Tango & Pizza) | [content/pages/series/](../content/pages/series/) |
| Hub jednorázové / vícedenní akce (Tango víkend, Tango léto) | [content/pages/events/](../content/pages/events/) |
| Měsíční přehled milong (`milongy-brno-kveten` atd.) | [content/pages/events/](../content/pages/events/) |
| Samostatnou stránku (o nás, FAQ, školy a lektorství) | [content/pages/](../content/pages/) |
| Marathon sub-web (anglicky, bez české verze) | [content/pages/marathon/](../content/pages/marathon/) + [content/events/2026-marathon/](../content/events/2026-marathon/) |
| Oznámení | [content/announcements/](../content/announcements/) |
| Píkošku (článek) | [content/curiosities/](../content/curiosities/) |
| Profil osoby (DJ, lektor) | [content/people/](../content/people/) |
| Odkazy v navigaci (hlavička / patička) | [content/navigation/](../content/navigation/) |
| Obrázky | [content/images/](../content/images/) |

Detaily k jednotlivým typům (struktura hlaviček, povinná pole, šablony) najdete v sekcích níže.

## Šablona hlavičky — všechna pole

Zkopírujte celý blok do nového souboru, smažte řádky, které pro daný typ obsahu nepotřebujete, a vyplňte hodnoty. Komentář na konci řádku říká, **pro který typ dokumentu řádek platí**.

```yaml
---
# ─── POVINNÉ VŽDY (akce, stránka, hub, oznámení, píkoška, osoba) ───
title: Název dokumentu
slug: nazev-dokumentu              # zobrazí se v URL: brnosaires.com/<slug>/
date: 2026-04-10 18:00:00          # datum PUBLIKACE souboru, NE datum akce
author: Jméno autora

# ─── SILNĚ DOPORUČENO VŽDY ───
description: Krátký popis (cca 160–200 znaků) pro Google a sociální kartičky.
preview_image: /images/.../nahled.jpg   # 1200×630; OG, Twitter, kalendář

# ─── JEN PRO AKCE (content/events/RRRR/MM/) ───
event-type: milonga                # milonga | workshop | class | praktika | neolonga
event-start: 2026-05-16 19:00:00
event-end: 2026-05-16 22:30:00     # půlnoc = další den 00:00:00, NIKDY 24:00:00
event-location: Stará radnice, Radnická 8, Brno

# ─── VOLITELNÉ PRO AKCE ───
event-organiser: Brno Tango Club   # kdo akci pořádá
entry: 150 Kč                      # vstupné; "zdarma" / "dobrovolné" → isAccessibleForFree
series: milonga-u-draka            # jen pokud akce patří do série (slug hubu)
instructor: Jana Nováková          # více lektorů: ['Jana Nováková', 'Petr Novák']
recurrence: weekly friday          # jen šablonové opakující se akce; u milong NEPOUŽÍVAT

# ─── JEN PRO HUB PRAVIDELNÉ SÉRIE (content/pages/series/) ───
series: milonga-u-draka            # MUSÍ být stejné jako slug — tím se soubor pozná jako hub

# ─── JEN PRO MĚSÍČNÍ PŘEHLED MILONG (milongy-brno-<měsíc>) ───
month: 5                           # 1–12; řídí zobrazený rok, noindex, navigaci

# ─── VOLITELNÉ VŽDY ───
llm_mirror: false                  # skrýt před AI asistenty (vynechte = mirror se vytvoří)
translate: false                   # obsah bez anglické verze (marathon sub-web)
---
```

### Co se zobrazí kde, když publikujete

| Když nastavíte… | …zobrazí se v |
|---|---|
| `title` | Záložce prohlížeče, výsledku Googlu, nadpisu náhledu na sociálních sítích, kartičce na webu |
| `description` | Snippetu ve výsledku Googlu, popisu náhledu na sociálních sítích (pokud nenastavíte, použije se prvních ~50 slov těla) |
| `preview_image` | Kartičce akce/článku na webu, náhledu na Facebooku/iMessage/Slacku, velké kartičce na Twitteru/X |
| `event-start` + `event-end` | Kalendáři (`/kalendar/`), hlavičce detailu akce, Google Event rich-result snippetu, `.ics` feedu |
| `event-location` | Hlavičce detailu akce, Google Event rich-result `location.address` |
| `entry` | Hlavičce detailu akce („Vstupné: …"), kartě akce v kalendáři, Google Event rich-result `offers.price`/`isAccessibleForFree` |
| `series:` | Kanonická URL ukazuje na hub, odznak „Součást pravidelné série", seznam „Nejbližší termíny série" na hubu |

## Čeklist před publikací — časté chyby

Než stránku commitnete, projděte tyto body. Pokrývají chyby, které se v souborech objevují nejčastěji.

- [ ] **`date:` má formát `RRRR-MM-DD HH:MM:SS` a je to datum publikace, ne akce.** Časté přehození: `date: 10. 4. 2026` nebo `date: 2026-05-16` (datum akce). Správně: `date: 2026-04-10 18:00:00`. Datum akce patří výhradně do `event-start`. Pokud `date` nastavíte do budoucnosti, stránka se neobjeví ve správném pořadí.
- [ ] **`slug:` je unikátní a bez diakritiky.** Dva české soubory se stejným slugem se přepíší při buildu (vyhraje poslední); český a anglický sourozenec **musí** sdílet slug, ale jiný pár souborů ne. Slug musí být ASCII, malými písmeny, pomlčky místo mezer (`Milonga u Mamuta` ❌ → `milonga-u-mamuta` ✅). Zkontrolujte hledáním slugu přes `content/`.
- [ ] **Všechna povinná YAML pole jsou vyplněná.** Pro akce: `title`, `slug`, `date`, `author`, `event-type`, `event-start`, `event-end`, `event-location`. Silně doporučené: `description`, `preview_image`. Nezapomeňte na `entry:` u placených akcí (jinak schema.org neoznačí akci jako placenou). Šablonu viz [Šablona hlavičky](#šablona-hlavičky--všechna-pole).
- [ ] **`event-type:` odpovídá druhu akce.** Povolené hodnoty: `milonga` | `workshop` | `class` | `praktika` | `neolonga` (`neolonga` se chová jako milonga, jen se zatím v obsahu nepoužívá). Špatný typ akci nerozbije build, ale zařadí ji do nesprávné kategorie, takže se v kalendáři a filtrech zobrazí jinde, než má (víkendový workshop omylem jako `class` se schová mezi pravidelné lekce). Pravidlo: jednorázová intenzivní akce = `workshop`, pravidelná týdenní lekce = `class`. Porovnejte s existující stejnou akcí přes `grep`, ať máte stejný typ jako minule.
- [ ] **`event-end` je vyplněné a půlnoc je `00:00:00` dalšího dne, ne `24:00:00`.** Bez `event-end` se nespustí Google Event rich-result. Zápis `24:00:00` Python neumí — akce se nepublikuje. Půlnoc: `event-end: 2026-05-17 00:00:00`, ne `2026-05-16 24:00:00`.
- [ ] **`preview_image:` ukazuje na existující soubor.** Cesta začíná lomítkem, bez prefixu `content` (např. `/images/events/2026/milonga.jpg`). Pole se jmenuje `preview_image`, **ne** `og_image` (to neexistuje). Špatná cesta = rozbité OG kartičky a prázdný náhled v kalendáři.
- [ ] **`description:` má pod ~200 znaků.** Delší se ořeže ve snippetu Googlu i v OG kartičce.
- [ ] **`series:` jen pro skutečné série.** Použijte jen tehdy, když v `content/pages/series/` existuje hub stránka s tímto slugem. U jednorázových akcí pole vynechte.
- [ ] **Názvy souborů bez mezer a diakritiky.** Markdowny i obrázky pojmenovávejte malými písmeny, pomlčkami místo mezer, bez háčků a čárek. Místo `Únorová neolonga.md` → `2026-02-neolonga.md`, místo `brunch milonga.jpg` → `brunch-milonga.jpg`.
- [ ] **Datum v názvu souboru je `RRRR-MM-DD` nebo `RRRR-MM`, ne `DD-MM-RRRR`.** Pelican tahá datum z názvu přes regex `\d{4}-\d{2}-\d{2}` a kontroluje jen tvar, ne platnost — `2026-30-05-neolonga.jpg` projde regexem, ale spadne při parsování a **shodí celý build**. Pořadí vždy rok-měsíc-den.

## Pravidelná série (`series:`) — milongy s více datovanými instancemi

Některé akce se opakují, ale každá instance je vlastní datovaný soubor (Milonga u Draka, Tango & Pizza). Bez seskupení by každé hledání jména série v Googlu rozdělovalo pozornost mezi N téměř identických stránek. Pole `series:` říká webu „všechny tyhle akce jsou jedna a ta samá věc, pošli vyhledávače na jednu hlavní stránku".

### Série vs. hub — jaký je rozdíl?

Lidé tyhle dva pojmy často míchají, protože spolu úzce souvisí, ale dělají dvě jiné věci:

- **Série** je **koncept** — „Milonga u Draka", logická skupina opakujících se akcí, které mají stejné jméno, atmosféru a obvykle i místo. Sérii reprezentuje **slug** (např. `milonga-u-draka`), nic víc; nemá vlastní soubor, neexistuje samostatně. Žije jen jako hodnota v poli `series:` v hlavičkách instancí.
- **Hub** je **konkrétní stránka v `content/pages/`**, která sérii reprezentuje navenek — má vlastní URL (`brnosaires.com/<slug-série>/`), titulek, popis, preview obrázek a tělo, které vysvětluje co je série zač. Hub je „domovská stránka" série; sem Google posílá uživatele místo na jednotlivé instance.

Vztah: **série = skupina, hub = stránka té skupiny**. Hub poznáte podle toho, že má `slug:` a `series:` se stejnou hodnotou (odkazuje sám na sebe). Instance mají vlastní `slug:` (s datem), ale jejich `series:` ukazuje na slug hubu.

Jednoduchá analogie: série je název kapely, hub je oficiální web kapely, jednotlivé instance jsou koncerty.

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
