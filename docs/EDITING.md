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
| `series:` | Kanonická URL ukazuje na hub, odznak „Součást pravidelné série", seznam „Nejbližší termíny série" na hubu |

## Časté chyby

- **Mezery nebo diakritika v `slug:`** — slug musí být ASCII s pomlčkami. Špatně: `Milonga u Mamuta`. Správně: `milonga-u-mamuta`.
- **Nastavený `series:` u jednorázové akce** — `series:` použijte jen tehdy, když existuje hub stránka s tímto slugem v `content/pages/`.
- **Chybějící `event-end`** — JSON-LD vyžaduje začátek i konec; build neselže, ale Google rich-result se nespustí.
- **Vymýšlení pole `og_image`** — takové pole neexistuje. Použijte `preview_image`.
- **Příliš dlouhý `description`** — držte se pod cca 200 znaky; delší hodnoty se ořežou.

## Související dokumenty

- [README.md](../README.md) — hlavní průvodce pro editory (česky): pracovní postup, struktura souboru akce, widgety, obrázky.
- [SEO.md](SEO.md) — *proč* to celé funguje takto (anglicky, technický popis): kanonická strategie, `<base href>`, mechanika hubů.
- [WIDGETS.md](WIDGETS.md) — tagy `<widget-*>` v těle článku.
- [content/pages/milonga-u-draka.md](../content/pages/milonga-u-draka.md) — reálný příklad hub stránky.
- [content/events/2026/05/2026-05-16-milonga-u-draka.md](../content/events/2026/05/2026-05-16-milonga-u-draka.md) — reálný příklad instance v sérii.
