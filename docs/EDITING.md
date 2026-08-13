# Pole v hlavičce — referenční přehled

Referenční přehled metadat (frontmatteru) Markdown souborů. **Když jen přidáváš nebo upravuješ akci, jdi na [Akce: přidat a upravit](AKCE.md)** — provede tě postupem za 5 minut. Tenhle dokument je slovník všech polí pro případy, kdy potřebuješ detail.

Související: série → [Série](SERIE.md), měsíční stránky milong → [Měsíční stránky](MESACNE-STRANKY.md), anglická verze → [Anglická verze](ANGLICKA-VERZIA.md), *proč* to funguje → [SEO](SEO.md), widgety → [Widgety](WIDGETS.md).

## 🗂️ Kam co patří — rychlé odkazy do repa

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

## 🖼️ Obrázky — nahrajte cokoli

Nahrajte obrázek v tom formátu, který máte (`.jpg` z mobilu, `.png` ze screenshotu, `.heic` z iPhonu). Do `preview_image:` napište přesně tu příponu, kterou nahráváte.

Velké fotky se zmenšují do `.avif` (zhruba čtvrtinová velikost), ale **až když to někdo spustí** — Actions → „Convert dropped images" → „Run workflow". Postup i s tím, co ten robotí commit udělá, je v [Akce: zmenšení obrázků](AKCE.md#zmenšení-obrázků-do-avif). Dokud to nikdo nespustí, web funguje dál a servíruje původní soubor.

Sociální náhledy (Facebook, LinkedIn, WhatsApp) AVIF přečíst neumí. **Řešit to nemusíte** — web si při každém buildu vyrobí JPEG kopii jen pro ně, do `/og/`. V repu ani v hlavičce ji nikde neuvidíte.

### Kam obrázek uložit — dvě možnosti

| Kam | Jak se na něj odkážete | Kdy to použít |
|---|---|---|
| [content/images/](../content/images/) | absolutní cesta: `preview_image: /images/curiosities/foto.avif` | **Výchozí volba.** Vždy, když obrázek používá (nebo může použít) víc než jeden článek. |
| **Vedle `.md` souboru** | jen jméno souboru: `preview_image: foto.avif` | Jednorázový článek, jehož obrázek nikdo jiný nepoužije — píkoška, jednotlivé oznámení. |

Druhá varianta je pohodlnější: obrázek nahrajete do stejné složky jako článek a nevymýšlíte cestu. Příklad v repu: [content/curiosities/dvacet-let-s-blancou.md](../content/curiosities/dvacet-let-s-blancou.md).

**Nefunguje to** u akcí s `recurrence:` nebo `series:` — jeden soubor se tam rozpadá na víc stránek a obrázek by u většiny z nich chyběl. Když to zkusíte, build vás na to upozorní v logu a obrázek se nezobrazí; přesuňte ho do `content/images/` a použijte absolutní cestu.

Vedle `.md` funguje **jen `preview_image:`**, nic jiného. Obrázek, který chcete i v **těle** článku (`![](...)`), patří do [content/images/](../content/images/) a odkazuje se absolutně `/images/…` — na soubor ležící vedle `.md` se z těla nedostanete.

## 📋 Šablona hlavičky — všechna pole

Zkopírujte celý blok do nového souboru, smažte řádky, které pro daný typ obsahu nepotřebujete, a vyplňte hodnoty. Komentář na konci řádku říká, **pro který typ dokumentu řádek platí**.

```yaml
---
# ─── POVINNÉ VŽDY (akce, stránka, hub, oznámení, píkoška, osoba) ───
title: Název dokumentu
slug: nazev-dokumentu              # zobrazí se v URL: brnosaires.com/<slug>/
date: 2026-04-10 18:00:00          # datum PUBLIKACE souboru, NE datum akce
author: Jméno autora

# ─── SILNĚ DOPORUČENO VŽDY ───
description: Krátký popis (cca 160-200 znaků) pro Google a sociální kartičky.
preview_image: /images/.../nahled.jpg   # 1200×630; OG, Twitter, kalendář

# ─── JEN PRO AKCE (content/events/RRRR/MM/) ───
event-type: milonga                # milonga | workshop | class | praktika | neolonga
event-start: 2026-05-16 19:00:00
event-end: 2026-05-16 22:30:00     # půlnoc = další den 00:00:00, NIKDY 24:00:00
event-location: Stará radnice, Radnická 8, Brno

# ─── VOLITELNÉ PRO AKCE ───
event-organiser: Brno Tango Club   # kdo akci pořádá
entry: 150 Kč                      # vstupné; "zdarma" / "dobrovolné" → isAccessibleForFree
event-url: https://...             # externí odkaz: vstupenky / registrace; zobrazí se jako "Více info a vstupenky"
series: milonga-u-draka            # jen pokud akce patří do série (slug hubu) — viz SERIE.md
instructor: Jana Nováková          # více lektorů → každé jméno na vlastní řádek, odsazené (viz níže)
recurrence: weekly friday          # jen šablonové opakující se akce; u milong NEPOUŽÍVAT
                                   # omezení série: "until RRRR-MM-DD", "count N", "from RRRR-MM-DD" — viz AKCE.md

# ─── JEN PRO HUB PRAVIDELNÉ SÉRIE (content/pages/series/) — viz SERIE.md ───
series: milonga-u-draka            # MUSÍ být stejné jako slug — tím se soubor pozná jako hub

# ─── JEN PRO MĚSÍČNÍ PŘEHLED MILONG (milongy-brno-<měsíc>) — viz MESACNE-STRANKY.md ───
month: 5                           # 1-12; řídí zobrazený rok, noindex, navigaci

# ─── VOLITELNÉ VŽDY ───
llm_mirror: false                  # skrýt před AI asistenty (vynechte = mirror se vytvoří)
translate: false                   # obsah bez anglické verze (marathon sub-web) — viz ANGLICKA-VERZIA.md
---
```

### Více lektorů na jedné akci

Každé jméno na vlastní řádek, druhé a další **odsazené** (4 mezery). Žádné hranaté závorky, žádné uvozovky:

```yaml
instructor: Šteky Yaku
    Filip Šterc
    Albert Mikó
    Jana Popelková
```

Zobrazí se oddělené čárkou: „Šteky Yaku, Filip Šterc, Albert Mikó, Jana Popelková". Jeden lektor = jeden řádek. (Jména píšte tak, jak mají vypadat — do budoucna se z nich budou moct stát odkazy na profil lektora, pokud profil existuje.)

## 👀 Co se zobrazí kde, když publikujete

| Když nastavíte… | …zobrazí se v |
|---|---|
| `title` | Záložce prohlížeče, výsledku Googlu, nadpisu náhledu na sociálních sítích, kartičce na webu |
| `description` | Snippetu ve výsledku Googlu, popisu náhledu na sociálních sítích (pokud nenastavíte, použije se prvních ~50 slov těla) |
| `preview_image` | Kartičce akce/článku na webu, náhledu na Facebooku/iMessage/Slacku, velké kartičce na Twitteru/X |
| `event-start` + `event-end` | Kalendáři (`/kalendar/`), hlavičce detailu akce, Google Event rich-result snippetu, `.ics` feedu |
| `event-location` | Hlavičce detailu akce, Google Event rich-result `location.address` |
| `entry` | Hlavičce detailu akce („Vstupné: …"), kartě akce v kalendáři, Google Event rich-result `offers.price`/`isAccessibleForFree` |
| `series:` | Kanonická URL ukazuje na hub, odznak „Součást pravidelné série", seznam „Nejbližší termíny série" na hubu |

## Samostatné stránky

Pro hub-stránky a běžné stránky (o nás, FAQ, marathon sub-site) stačí společná pole nahoře. Bez polí pro akce. Bez `series`, pokud to není hub.

### Roční úklid: rok v titulcích landing stránek

Titulky a nadpisy přehledových stránek (`tango-kalendar-brno`, `tango-milongy-brno`, `tango-lekce-brno` a jejich `.en.md` varianty) obsahují aktuální rok kvůli vyhledávání (lidé hledají „milonga Brno 2026"). **Jednou ročně** (typicky začátkem ledna) v nich přepište rok na nový — je to ~6 souborů + 6 anglických dvojčat, jen pole `title`, `description` a první `<h1>`/odstavec. Měsíční stránky (`milongy-brno-<měsíc>`, viz [Měsíční stránky](MESACNE-STRANKY.md)) rok řeší samy přes build-time filtr, ty se nedotýkáte.

## 📢 Oznámení / píkoška / osoba

Použijte společná pole. Aktuálně:

- Oznámení se zobrazují na `/lenka-pise-oznamy/` (chronologicky).
- Píkošky se zobrazují na `/pikosky/`.
- Osoby se zobrazují na marathonové stránce DJs/teamu, když jsou tam odkazované.

Žádný z těchto typů nevkládá JSON-LD Event strukturu (správně — nejsou to akce).

## 🤖 Soubory pro AI asistenty (`content/llm/`)

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

## 🔗 Související dokumenty

- [Akce: přidat a upravit](AKCE.md) — postup za 5 minut pro nejčastější úkol.
- [Série](SERIE.md) — série vs hub, přidat instanci, založit sérii.
- [Měsíční stránky](MESACNE-STRANKY.md) — měsíční přehledy milong.
- [Anglická verze](ANGLICKA-VERZIA.md) — `.en.md` sourozenci, navigace, `translate: false`.
- [SEO + sociální kartičky](SEO.md) — *proč* to celé funguje takto (kanonická strategie, `<base href>`, mechanika hubů, `hreflang`).
- [Widgety](WIDGETS.md) — tagy `<widget-*>` v těle článku.
