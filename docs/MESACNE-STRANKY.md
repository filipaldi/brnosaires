# Měsíční stránky milong

Dvanáct stránek, jedna pro každý měsíc (`/milongy-brno-leden/` … `/milongy-brno-prosinec/`), aby web uměl odpovědět na hledání „milonga Brno červen", „milonga Brno květen 2026" apod. Jsou **bez ročníku** — stejná URL platí každý rok, mění se jen zobrazený rok.

Soubory leží v [content/pages/events/](../content/pages/events/).

## Přidat akci do měsíční stránky = nic navíc

Stačí normálně vytvořit soubor akce podle [Přidat akci](PRIDAT-AKCIU.md), v [content/events/](../content/events/)`RRRR/MM/` s `event-type: milonga` (nebo `praktika`/`neolonga`) a `event-start` v daném měsíci — objeví se na příslušné měsíční stránce automaticky. Samotnou měsíční stránku neupravuješ.

## Co je v souboru a co (ne)měnit

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

## Odkazy a anglické verze

**Odkazy na měsíční stránky** najdeš ve spodku stránek `tango-milongy-brno` a `tango-kalendar-brno` (řádek „Milongy po měsících: leden · únor · …") — to je obyčejný seznam odkazů v Markdownu, klidně ho uprav nebo přesuň. Mezi sebou se měsíční stránky prolinkují samy (předchozí/další měsíc + pásek všech měsíců dodává šablona).

**Anglické verze** jsou `.en.md` dvojčata se stejným `slug` a `Lang: en` (jako u ostatních stránek) — běží na `/en/milongy-brno-<měsíc>/`. Mění se jen text; `month:` a vše ostatní je stejné. Viz [Anglická verze](ANGLICKA-VERZIA.md).

## Související

- [Přidat akci](PRIDAT-AKCIU.md) — jak vytvořit akci, která se na měsíční stránce objeví.
- [Pole v hlavičce](EDITING.md) — referenční přehled metadat (roční úklid titulků landing stránek).
- [Anglická verze](ANGLICKA-VERZIA.md) — `.en.md` dvojčata.
