# Série a huby — milongy s více termíny

Některé akce se opakují, ale každá instance je vlastní datovaný soubor (Milonga u Draka, Tango & Pizza). Bez seskupení by každé hledání jména série v Googlu rozdělovalo pozornost mezi N téměř identických stránek. Pole `series:` říká webu „všechny tyhle akce jsou jedna a ta samá věc, pošli vyhledávače na jednu hlavní stránku".

Běžnou akci bez série řeší [Přidat akci](PRIDAT-AKCIU.md). Tenhle návod je navíc, jen když akce patří do opakující se série.

## Série vs. hub — jaký je rozdíl?

Lidé tyhle dva pojmy často míchají, protože spolu úzce souvisí, ale dělají dvě jiné věci:

- **Série** je **koncept** — „Milonga u Draka", logická skupina opakujících se akcí, které mají stejné jméno, atmosféru a obvykle i místo. Sérii reprezentuje **slug** (např. `milonga-u-draka`), nic víc; nemá vlastní soubor, neexistuje samostatně. Žije jen jako hodnota v poli `series:` v hlavičkách instancí.
- **Hub** je **konkrétní stránka v `content/pages/series/`**, která sérii reprezentuje navenek — má vlastní URL (`brnosaires.com/<slug-série>/`), titulek, popis, preview obrázek a tělo, které vysvětluje co je série zač. Hub je „domovská stránka" série; sem Google posílá uživatele místo na jednotlivé instance.

Vztah: **série = skupina, hub = stránka té skupiny**. Hub poznáte podle toho, že má `slug:` a `series:` se stejnou hodnotou (odkazuje sám na sebe). Instance mají vlastní `slug:` (s datem), ale jejich `series:` ukazuje na slug hubu.

Jednoduchá analogie: série je název kapely, hub je oficiální web kapely, jednotlivé instance jsou koncerty.

## Co potřebuje editor udělat

**Přidat novou instanci do existující série:**

1. Vytvořte soubor akce normálně podle [Přidat akci](PRIDAT-AKCIU.md), v [content/events/](../content/events/)`RRRR/MM/`.
2. Přidejte jeden řádek: `series: <slug-existujícího-hubu>` (např. `series: milonga-u-draka`).
3. Hotovo. Web automaticky:
   - Přepne kanonickou URL stránky na `/{series}/`.
   - Zobrazí pod nadpisem odznak „Součást pravidelné série: …" odkazující na hub.
   - Přidá tento termín do seznamu „Nejbližší termíny série" na hubu (pokud je v budoucnu).

**Vytvořit zcela novou sérii:**

1. Vytvořte hub stránku: [content/pages/series/](../content/pages/series/)`<slug-série>.md`. Nastavte `series: <slug-série>` v jejím frontmatteru a do těla napište obecný popis série (atmosféra, místo, co očekávat).
2. Přidejte `series: <slug-série>` do každé existující instance v [content/events/](../content/events/).
3. Budoucí instance pak stačí, aby měly stejný řádek `series:`.

## Kdy `series:` **nepoužívat**

- Jednorázové akce, které se nebudou opakovat — nechte pole vynechané, stránka bude kanonická sama na sebe (což je správné chování).
- Opakující se **lekce/praktiky** psané přes `recurrence:` (jeden zdrojový soubor, jeden URL) — `series:` nepotřebují, už mají jednu kanonickou stránku.

## Hub stránka (`content/pages/series/<slug-série>.md`)

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

## Související

- [Přidat akci](PRIDAT-AKCIU.md) — základní postup pro instanci akce.
- [Pole v hlavičce](EDITING.md) — referenční přehled všech metadat.
- [content/pages/series/milonga-u-draka.md](../content/pages/series/milonga-u-draka.md) — reálný příklad hub stránky.
- [content/events/2026/05/2026-05-16-milonga-u-draka.md](../content/events/2026/05/2026-05-16-milonga-u-draka.md) — reálný příklad instance v sérii.
- [SEO](SEO.md) — *proč* huby fungují takto (kanonická strategie).
