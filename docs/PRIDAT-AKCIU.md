# Přidat a upravit akci

Nejčastější úkoly v kostce:

- **Přidat jednorázovou akci** (milonga, workshop) → kroky 1-5 níže.
- **Přidat pravidelnou lekci** (každý týden / měsíc) → [Pravidelná lekce přes `recurrence:`](#pravidelná-lekce-přes-recurrence).
- **Upravit už existující akci/lekci** (datum, čas, cena) → [Upravit existující akci](#upravit-existující-akci).

Detail všech polí hlavičky → [Pole v hlavičce](EDITING.md). Série (Milonga u Draka apod.) → [Série](SERIE.md). Anglická verze → [Anglická verze](ANGLICKA-VERZIA.md).

---

## 1. Vytvoř soubor a zkopíruj do něj tuhle hlavičku

Nový soubor patří do [content/events/](../content/events/) → podsložka `RRRR/MM/` podle měsíce akce (např. akce v květnu 2026 → `content/events/2026/05/`).

Zkopíruj celý blok, smaž řádky, které nepotřebuješ, vyplň hodnoty:

```yaml
title: Milonga u Draka
slug: 2026-05-16-milonga-u-draka       # v URL: brnosaires.com/<slug>/
date: 2026-04-10 18:00:00              # datum PUBLIKACE, NE datum akce
author: Tvé jméno
description: Krátký popis (do ~200 znaků) pro Google a náhled na sítích.
preview_image: /images/events/2026/milonga.jpg   # 1200×630
event-type: milonga                    # milonga | workshop | class | praktika | neolonga
event-start: 2026-05-16 19:00:00
event-end: 2026-05-16 22:30:00         # půlnoc = 00:00:00 dalšího dne, NIKDY 24:00:00
event-location: Stará radnice, Radnická 8, Brno
entry: 150 Kč                          # vstupné; "zdarma" / "dobrovolné" → akce zdarma
```

Volitelně: `event-organiser`, `instructor`, `series` (jen u série, viz [Série](SERIE.md)). Bez `---` ohraničení nahoře/dole — Pelican je nepoužívá.

---

## 2. Pojmenuj soubor správně

Hlavička výše tohle neřeší — název souboru si musíš ohlídat sám. **Tři pravidla, jinak se akce nepublikuje nebo spadne celý web:**

| Pravidlo | Špatně | Správně |
|---|---|---|
| Datum vepředu jako `RRRR-MM-DD` | `16-05-2026-milonga.md` | `2026-05-16-milonga.md` |
| Bez mezer | `milonga u draka.md` | `milonga-u-draka.md` |
| Bez diakritiky | `Únorová neolonga.md` | `2026-02-neolonga.md` |

Špatné pořadí data (`DD-MM-RRRR`) **shodí build celému webu** — Pelican čeká rok první. Mezery a diakritika někdy projdou, ale nespoléhej na to; piš malými písmeny s pomlčkami.

---

## 3. Zkontroluj tyhle čtyři řádky — tady se chybuje nejčastěji

| Řádek | Na co si dát pozor |
|---|---|
| `date:` | Datum, kdy soubor **publikuješ**, ne kdy je akce. Datum akce patří jen do `event-start`. Formát `RRRR-MM-DD HH:MM:SS`. Datum v budoucnu = stránka se nezobrazí ve správném pořadí. |
| `slug:` | Unikátní, bez diakritiky, malými písmeny s pomlčkami. Dva soubory se stejným slugem se při buildu přepíšou — jeden tiše zmizí. |
| `event-end:` | Vždy vyplněné. Půlnoc piš jako `00:00:00` **dalšího dne** (`2026-05-17 00:00:00`), nikdy `24:00:00` — to Python neumí a akce se nepublikuje. |
| `event-type:` | Musí sedět druh akce — viz krok 4. |

---

## 4. Vyber správný `event-type`

Špatný typ build **nerozbije**, ale zařadí akci do jiné kategorie — v kalendáři a filtrech se zobrazí jinde, než má.

| Typ | Pro co |
|---|---|
| `milonga` | Tančírna |
| `neolonga` | Neo milonga (chová se jako milonga) |
| `workshop` | Jednorázová intenzivní akce, víkendovka |
| `class` | Pravidelná týdenní lekce |
| `praktika` | Praktika |

Klasická past: víkendový workshop omylem jako `class` se schová mezi pravidelné lekce. Pravidlo: **jednorázové = `workshop`, pravidelné týdenní = `class`.** Když nevíš, najdi v repu stejnou akci z minula a vezmi stejný typ.

---

## 5. Commitni

Soubor uložíš jedním ze dvou způsobů:

- **GitHub web UI** — otevři repo v prohlížeči, najdi složku, „Add file" → „Create new file" (nebo tužku ✏️ u existujícího), vlož obsah, dole „Commit changes". Stačí prohlížeč a GitHub účet. Vhodné pro text.
- **GitHub Desktop** — naklonuj repo, edituj v textovém editoru, commitni a „Push origin". Vhodné pro obrázky a víc souborů najednou.

Web se sestaví **automaticky dvakrát denně** (06:00 a 18:00 UTC). Potřebuješ rychleji? Vyžádej si ruční build u vývojáře.

---

## Akce se neobjevila? Pět nejčastějších důvodů

Soubor je commitnutý, build proběhl, ale akci na webu nevidíš. Skoro vždy je to jedno z těchto — a žádné z nich nehlásí chybu:

1. **Akce je v jiné kategorii** — špatný `event-type` (krok 4). Workshop jako `class` najdeš mezi lekcemi, ne mezi workshopy.
2. **Akce se vůbec nepublikovala** — `event-end` má `24:00:00` místo `00:00:00` dalšího dne, nebo chybí úplně.
3. **Akce se přepsala jinou** — dva soubory mají stejný `slug:`. Při buildu vyhraje poslední, druhý zmizí. Zkontroluj slug hledáním přes `content/`.
4. **Akce je „v budoucnu"** — `date:` (datum publikace) je nastavené dopředu, takže se řadí až za vším ostatním. Pozor: `date` ≠ `event-start`.
5. **Náhled je prázdný / kartička rozbitá** — `preview_image:` ukazuje na neexistující soubor, nebo cesta začíná `content` (má začínat lomítkem: `/images/...`). Pole se jmenuje `preview_image`, ne `og_image`.

Stále nic? Build mohl spadnout úplně (typicky špatné pořadí data v názvu souboru, krok 2). Napiš vývojáři, ať se podívá do logu GitHub Actions.

---

## Pravidelná lekce přes `recurrence:`

Lekce, která se opakuje každý týden nebo měsíc, je **jeden soubor**, ne dvanáct. Pole `recurrence:` ho při buildu rozbalí na všechny termíny. Soubory pravidelných lekcí leží v [content/events/classes/](../content/events/classes/) a v názvu **nemají datum** (datum dodá `event-start` + `recurrence`).

Vezmi existující lekci ze složky jako předlohu. Hlavička vypadá takhle:

```yaml
title: Tango II.
slug: stolarna-tango-ii-monday          # bez data; unikátní
event-start: 2026-06-01 17:45:00         # PRVNÍ termín (datum + čas začátku)
event-end: 2026-06-01 19:00:00           # konec prvního termínu
recurrence: weekly monday                # rozbalí na každé pondělí
event-type: class                        # pravidelná lekce = class (NE workshop)
event-location: Taneční studio Stolárna, Olomoucká 14, Brno
instructor: "['Jana Habalová', 'Petr Truhlář']"
preview_image: /images/classes/class-stolarna.avif
description: …
author: Tvé jméno
```

**Hodnoty `recurrence:`** — fungují jen tyhle dvě formy (jiné se tiše ignorují a zůstane jen jeden termín):

| Zápis | Význam |
|---|---|
| `weekly <den>` | každý týden: `weekly monday`, `weekly friday` … `weekly sunday` |
| `monthly <pořadí> <den>` | N-tý den v měsíci: `monthly 2 sunday` = každá 2. neděle; `monthly -1 friday` = poslední pátek (pořadí `1`-`4` nebo `-1`) |

Dny **anglicky** a malými písmeny (`monday`…`sunday`). Den v `recurrence:` musí sedět se dnem, na který padá `event-start` — jinak se termíny rozjedou. Čas se bere z `event-start`/`event-end` a platí pro všechny termíny.

## Upravit existující akci

Soubor už existuje, jen měníš hodnotu. Otevři ho ([content/events/](../content/events/) pro jednorázové, [content/events/classes/](../content/events/classes/) pro pravidelné lekce) a uprav jen ten řádek:

| Co měníš | Řádek | Pozor |
|---|---|---|
| Datum / čas jednorázové akce | `event-start`, `event-end` | `date:` **neměň** — to je datum publikace, ne akce. Půlnoc v `event-end` = `00:00:00` dalšího dne, nikdy `24:00:00`. |
| Cenu | `entry` | „zdarma" / „dobrovolné" → akce se označí jako bezplatná. |
| Místo | `event-location` | Tvar `Místo, Ulice, Brno` (kvůli mapě/SEO). |
| Čas pravidelné lekce | `event-start`, `event-end` | Změní se na **všech** termínech. |
| Den pravidelné lekce | `event-start` **i** `recurrence` | Musíš změnit **oba** — datum v `event-start` posuň na nový den a uprav `recurrence: weekly <den>`. Změna jen jednoho je nejčastější chyba. |

Co **neměnit**, pokud nechceš změnit URL: `slug:`. Změna slugu = nová URL, stará přestane fungovat (rozbité odkazy, ztracené SEO).

Po úpravě commitni stejně jako u nové akce (krok 5). Pokud se změna neprojeví, projdi [Akce se neobjevila?](#akce-se-neobjevila-pět-nejčastějších-důvodů) výše.

---

## Související

- [Pole v hlavičce](EDITING.md) — referenční přehled všech metadat a co se kde zobrazí.
- [Série](SERIE.md) — jak přidat akci do pravidelné série (Milonga u Draka, Tango & Pizza).
- [Anglická verze](ANGLICKA-VERZIA.md) — `.en.md` sourozenec stránky.
- [Widgety](WIDGETS.md) — tagy `<widget-*>` v těle (kalendář, seznam akcí).
