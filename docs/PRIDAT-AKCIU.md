# Přidat akci za 5 minut

Nejčastější úkol: přidat milongu, workshop nebo lekci do kalendáře. Tenhle návod tě provede od kopírování po commit. Postupuj shora dolů.

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

## Související

- [Pole v hlavičce](EDITING.md) — referenční přehled všech metadat a co se kde zobrazí.
- [Série](SERIE.md) — jak přidat akci do pravidelné série (Milonga u Draka, Tango & Pizza).
- [Anglická verze](ANGLICKA-VERZIA.md) — `.en.md` sourozenec stránky.
- [Widgety](WIDGETS.md) — tagy `<widget-*>` v těle (kalendář, seznam akcí).
