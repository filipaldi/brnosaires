# Brnos Aires Web - Průvodce pro editory

Tento průvodce je určen pro editory obsahu pracující s webem Brnos Aires. Popisuje, jak vytvářet a upravovat akce, používat widgety, spravovat obrázky a organizovat obsah.

---

## Obsah

1. [Než začnete](#než-začnete)
2. [Vysvětlení klíčových pojmů](#vysvětlení-klíčových-pojmů)
3. [Práce se soubory akcí](#práce-se-soubory-akcí)
4. [Metadata akcí – data a časy](#metadata-akcí--data-a-časy)
5. [Systém widgetů](#systém-widgetů)
6. [Práce s obrázky](#práce-s-obrázky)
7. [Organizace obsahu](#organizace-obsahu)
8. [Běžné úkoly](#běžné-úkoly)
9. [Rychlý přehled](#rychlý-přehled)
10. [Potřebujete pomoc?](#potřebujete-pomoc)

---

## Než začnete

### Jak úpravy fungují

Web upravujete pomocí textových souborů uložených v tomto repozitáři. Každý soubor představuje jeden obsah — akci, stránku nebo oznámení.

**Kdy se změny zveřejní:** Po uložení (commitnutí) změn se web automaticky sestaví v nejbližším naplánovaném čase — obvykle do 12 hodin. Pokud potřebujete aktualizaci zobrazit dříve, požádejte vývojáře o ruční sestavení.

**Formát souborů:** Všechny soubory s obsahem jsou prostý text s příponou `.md` (Markdown). Lze je otevřít v libovolném textovém editoru.

Soubory lze upravovat dvěma způsoby:

---

#### Možnost A: Upravit přímo na GitHubu (doporučeno pro malé změny)

Nevyžaduje instalaci žádného softwaru — stačí webový prohlížeč a GitHub účet.

1. Přejděte do repozitáře na GitHubu
2. Přejděte k souboru, který chcete upravit (např. otevřete `content/events/2026/02/` a klikněte na soubor)
3. Klikněte na **ikonu tužky** (✏️ „Edit this file") v pravém horním rohu zobrazení souboru
4. Proveďte změny v textovém editoru, který se zobrazí
5. Přejděte dolů na sekci **„Commit changes"**
6. Do prvního textového pole napište krátký popis změny (např. `Přidání milongy leden 2026`)
7. Klikněte na **„Commit changes"** — změna je uložena; web se aktualizuje při nejbližším naplánovaném sestavení

> **Tip:** Úpravy na GitHubu jsou ideální pro aktualizaci detailů akcí, opravy textu nebo přidání nového souboru akce. **Neumožňují** nahrávání obrázků — k tomu použijte GitHub Desktop.

---

#### Možnost B: Upravit lokálně pomocí GitHub Desktop (doporučeno pro nahrávání obrázků nebo více změn najednou)

GitHub Desktop je bezplatná aplikace, která vám umožňuje pracovat se soubory v počítači a synchronizovat změny s GitHubem.

**Jednorázové nastavení:**
1. Nainstalujte [GitHub Desktop](https://desktop.github.com/) a přihlaste se svým GitHub účtem
2. Naklonujte repozitář: **File → Clone Repository** → vyberte repozitář → klikněte na **Clone**
   - Tím se stáhnou všechny soubory webu do složky ve vašem počítači

**Úprava souborů:**
1. Otevřete naklonovanou složku v počítači a najděte soubor, který chcete upravit
2. Otevřete jej v libovolném textovém editoru (Poznámkový blok ve Windows, TextEdit na Macu)
3. Proveďte změny a **soubor uložte**

**Nahrávání obrázků:**
1. Zkopírujte soubor obrázku do podsložky `content/images/` uvnitř naklonované složky

**Uložení a zveřejnění změn:**
1. Otevřete GitHub Desktop — zobrazí všechny soubory, které jste změnili nebo přidali
2. Do pole **„Summary"** (vlevo dole) napište krátký popis (např. `Přidání milongy únor 2026`)
3. Klikněte na **„Commit to main"**
4. Klikněte na **„Push origin"** v horní liště — změny jsou odeslány na GitHub a web se aktualizuje při nejbližším naplánovaném sestavení

---

### Co je Markdown?

Markdown je jednoduchý způsob formátování textu pomocí symbolů. Například:
- `**tučně**` se zobrazí jako **tučně**
- `# Nadpis` se zobrazí jako velký nadpis
- `- položka` se zobrazí jako odrážka

Markdown nemusíte znát do hloubky — šablony v tomto průvodci pokrývají vše, co potřebujete.

---

## Vysvětlení klíčových pojmů

| Pojem | Co znamená |
|-------|-----------|
| **Frontmatter** | Blok na začátku každého souboru, ohraničený dvěma řádky `---`. Obsahuje strukturované informace jako název akce, datum a místo konání. |
| **Slug** | URL-přátelská verze názvu akce. Zobrazuje se v adrese webu: `brnosaires.cz/events/milonga-fuera-del-nido`. Používejte pouze malá písmena, číslice a pomlčky — žádné mezery ani speciální znaky. |
| **Markdown soubor (`.md`)** | Prostý textový soubor s jednoduchým formátováním. Web ho převede na stylizovanou webovou stránku. |
| **AVIF** | Formát obrázkových souborů (podobně jako JPG nebo PNG, ale efektivnější). Web používá obrázky `.avif`. |
| **Widget** | Speciální úryvek kódu, který vložíte na stránku a který automaticky zobrazí seznam akcí nebo článků. |
| **SEO popis** | Krátké shrnutí (1–2 věty) zobrazované ve výsledcích vyhledávačů a náhledech na sociálních sítích. |

---

## Práce se soubory akcí

### Kde jsou uloženy soubory akcí

Všechny soubory akcí jsou uloženy ve složce `content/events/`. Každá akce má vlastní Markdown soubor (`.md`).

### Vytvoření nového souboru akce

1. Vytvořte nový soubor v příslušné podsložce:
   - Pro jednorázovou akci: `content/events/YYYY/MM/` — např. `content/events/2026/03/` pro březen 2026
   - Pro opakující se lekci: `content/events/classes/`
2. Pojmenujte soubor pouze malými písmeny, pomlčkami a číslicemi — bez mezer, bez diakritiky (např. `milonga-fuera-del-nido.md`)
3. Název souboru se stane součástí webové adresy akce, proto ho pojmenujte výstižně

**Příklady pojmenování souborů:**

| Typ obsahu | Formát | Příklad |
|---|---|---|
| Jednorázová akce | `kratky-popis.md` | `milonga-fuera-del-nido.md` |
| Opakující se lekce | `studio-uroven.md` | `stolarna-tango-i.md` |
| Oznámení | `RRRR-MM-DD-popis.md` | `2026-03-15-jarni-oznameni.md` |

**Obecná pravidla:**
- Pouze malá písmena
- Pomlčky místo mezer (`milonga-brno`, ne `milonga brno`)
- Žádná podtržítka, žádná diakritika (`á`, `č`, `š` apod.)

### Základní struktura souboru akce

Každý soubor akce má dvě části:

1. **Frontmatter** (nahoře, mezi řádky `---`) — Obsahuje metadata o akci
2. **Obsah** (pod frontmatterem) — Popis a detaily akce

### Ideální metadata akce (šablona pro editory)

Akce se na webu zobrazují s metadaty (typ, časový rozsah, místo, pořadatel, lektoři). Vyplňte je ve frontmatteru, aby stránka akce a widgety zobrazovaly konzistentní informace.

| Pole | Povinné | Použití |
|------|---------|---------|
| `title` | Ano | Název akce. |
| `slug` | Ano | URL slug (malá písmena, pomlčky). Obvykle stejné jako název souboru bez `.md`. |
| `date` | Ano | Datum článku. Použijte stejnou hodnotu jako `event-start`, pokud článek nepublikujete jiný den. Formát: `RRRR-MM-DD HH:MM:SS`. |
| `event-type` | Doporučeno | Jedna z hodnot: `milonga`, `workshop`, `class`, `praktika`. Slouží k filtrování ve widgetech. |
| `event-start` | Ano | Datum a čas začátku. Formát: `RRRR-MM-DD HH:MM:SS`. |
| `event-end` | Doporučeno | Datum a čas konce. Stejný formát jako `event-start`. |
| `event-location` | Doporučeno | Název místa a adresa (např. `Taneční studio Stolárna, Olomoucká 14` nebo `Café Adrinela`). |
| `event-organiser` | Doporučeno | Kdo akci pořádá (např. `Taneční studio Stolárna`, `Lenka a Filip`). |
| `instructor` | Pro lekce/workshopy | Lektoři. Pro jednoho lektora: napište jméno přímo. Pro více: `"['Jméno Jedna', 'Jméno Dva']"` (viz poznámka níže). |
| `recurrence` | Pro opakující se akce | Např. `weekly sunday`, `weekly tuesday`. Viz sekce o opakování níže. |
| `description` | Doporučeno | Krátké shrnutí pro kartičky a výsledky vyhledávání (1–2 věty). |
| `preview_image` | Volitelné | Cesta k obrázku, např. `/images/akce.avif`. |
| `author` | Volitelné | Autor obsahu. |

> **Více lektorů:** Neobvyklý formát `"['Jméno Jedna', 'Jméno Dva']"` (s uvozovkami a hranatými závorkami) je vyžadován systémem webu. Zkopírujte jej přesně a vyměňte pouze jména. Pro jednoho lektora napište jméno přímo: `instructor: Filip Paldia`.

**Šablona – jednorázová akce (milonga nebo workshop):**

```markdown
---
title: Název akce
slug: nazev-akce
date: 2026-01-17 18:00:00
event-type: milonga
event-start: 2026-01-17 18:00:00
event-end: 2026-01-17 22:30:00
event-location: Název místa, adresa
event-organiser: Název pořadatele
description: Krátké shrnutí pro kartičky a vyhledávání.
preview_image: /images/vas-obrazek.avif
author: Vaše jméno
---

Text akce zde.
```

**Šablona – opakující se lekce:**

```markdown
---
title: Název lekce
slug: nazev-lekce
date: 2026-01-16 01:00:00
event-type: class
event-start: 2026-01-08 18:00:00
event-end: 2026-01-08 20:00:00
recurrence: weekly tuesday
event-organiser: Název studia
event-location: Adresa, Brno
instructor: "['Lektor Jedna', 'Lektor Dva']"
description: Krátké shrnutí.
preview_image: /images/lekce.avif
author: Vaše jméno
---

Text lekce zde.
```

---

## Metadata akcí – data a časy

Soubory akcí používají čtyři typy informací o datu a čase:

### 1. `date` – Datum článku (povinné)

Systém webu toto pole vyžaduje u každého článku. U akcí nastavte stejnou hodnotu jako `event-start`. Jiné datum použijte pouze tehdy, pokud článek píšete a publikujete v jiný den, než kdy se akce koná.

**Formát:** `RRRR-MM-DD HH:MM:SS`

**Příklad:**
```markdown
date: 2026-01-17 18:00:00
```

### 2. `event-start` – Čas začátku akce (povinné)

Toto je nejdůležitější pole. Říká, kdy akce začíná.

**Formát:** `RRRR-MM-DD HH:MM:SS`

**Příklady:**
```markdown
event-start: 2026-01-17 18:00:00
event-start: 2026-03-15 20:30:00
event-start: 2026-12-25 19:00:00
```

**Důležité:**
- Vždy uveďte datum i čas
- Používejte 24hodinový formát (18:00 místo 6:00 PM)
- Dodržujte přesně uvedený formát

### 3. `event-end` – Čas konce akce (volitelné)

Vyplňte, pokud má akce konkrétní čas konce. Pokud akce nemá pevný čas konce, toto pole vynechejte.

**Formát:** `RRRR-MM-DD HH:MM:SS`

**Příklady:**
```markdown
event-end: 2026-01-17 22:30:00
event-end: 2026-03-15 23:00:00
```

**Důležité:**
- Musí být ve stejný den nebo později než `event-start`
- Používejte stejný formát jako u `event-start`

### 4. `recurrence` – Opakující se akce (volitelné)

Toto pole slouží pro akce, které se pravidelně opakují (např. týdenní lekce). Většina akcí ho nepotřebuje. Pokud si nejste jistí, pole vynechejte.

**Kdy použít:**
- Týdenní lekce každé pondělí
- Měsíční akce, které se opakují
- Jiné pravidelně se opakující akce

**Formát:** Jednoduchá fráze. `event-start` označuje první výskyt; pravidlo se opakuje od tohoto data.

**Příklady:**
- Každou neděli: `recurrence: weekly sunday`
- První sobotu v měsíci: `recurrence: monthly 1 saturday`
- Každé pondělí: `recurrence: weekly monday`

### Kompletní příklad akce

```markdown
---
title: Milonga Fuera del Nido
date: 2026-01-17 18:00:00
event-start: 2026-01-17 18:00:00
event-end: 2026-01-17 22:30:00
slug: milonga-fuera-del-nido
---

Další Milonga tentokrát v úchvatných prostorách v parkovacím domě Domini Park.

Openclass od 18:00 (není nutné přijít s partnerem)
19.00-22.30 Milonga, DJ Kenan
```

### Časté chyby při zadávání data a času

1. **Špatný formát:** `17.1.2026 18:00` ❌
   - **Správně:** `2026-01-17 18:00:00` ✅

2. **Chybějící čas:** `2026-01-17` ❌
   - **Správně:** `2026-01-17 18:00:00` ✅

3. **Pouze `date` místo `event-start`:** jen `date: 2026-01-17 18:00:00` ❌
   - **Správně:** Uveďte jak `date`, tak `event-start` se stejnou hodnotou ✅

4. **Použití `end_date` místo `event-end`:** `end_date: 2026-01-17 22:30:00` ❌
   - **Správně:** `event-end: 2026-01-17 22:30:00` ✅

5. **Chybějící pole `date`:** Akce musí mít jak `date`, tak `event-start` ❌
   - **Správně:** Uveďte obě pole se stejnou hodnotou ✅

---

## Systém widgetů

Widgety jsou speciální komponenty, které automaticky zobrazují seznamy akcí na vašich stránkách. Lze je vložit kamkoliv do obsahu v Markdownu.

Úplnou dokumentaci widgetů — všechny atributy, příklady a technické detaily — najdete v **[docs/WIDGETS.md](docs/WIDGETS.md)**.

### Jak widgety fungují

Widgety se vkládají pomocí vlastních HTML tagů, které vložíte do souboru Markdown. Web tyto tagy automaticky nahradí skutečným seznamem akcí.

### Dostupné widgety

**`<widget-calendar>`** — zobrazuje kartičky akcí podle filtru:
```html
<widget-calendar filter_by_type="milonga" days="14"></widget-calendar>
```

**`<widget-calendar-link>`** — zobrazuje odkazy pro přihlášení k odběru kalendáře (Apple, Google, Outlook):
```html
<widget-calendar-link
    cal_file_name="milongas"
    filter_by_path="events"
    filter_by_type="milonga"
    label="📆 Odebírej milongy do svého kalendáře"
    label_webcal="Apple"
    label_google="Google"
    label_outlook="Ostatní">
</widget-calendar-link>
```

**`<widget-articles>`** — zobrazuje kartičky článků filtrované podle kategorie:
```html
<widget-articles category="announcement" limit="3"></widget-articles>
```

### Použití widgetů na stránkách

Widgety lze vložit kamkoliv v obsahu stránky. Zde je kompletní příklad:

```markdown
---
title: Tango milongy Brno
slug: tango-milongy-brno
---

Tangové tančírny neboli **milongy v Brně** - pravidelné i nepravidelné.

<widget-calendar filter_by_type="milonga" days="365"></widget-calendar>

## Upcoming Events

<widget-calendar filter_by_type="milonga" days="7"></widget-calendar>

## Announcements

<widget-articles category="announcement" limit="3"></widget-articles>
```

### Doporučené postupy pro widgety

1. **Přidejte před widget nadpis** — Pomozte čtenářům pochopit, co vidí
2. **Umísťujte widgety tam, kde to dává smysl** — Seznamy akcí dejte k relevantnímu obsahu
3. **Po přidání zkontrolujte** — Ověřte, že se akce zobrazují správně
4. **Widgety se zobrazí jen pokud existuje odpovídající obsah** — Pokud neexistuje žádný odpovídající obsah, widget se nezobrazí
5. **Používejte řazení pro lepší organizaci** — Od nejstarší pro historický obsah, od nejnovější pro aktuální aktualizace

### Řešení problémů s widgety

**Widget se nezobrazuje:**
- Zkontrolujte, zda existují akce se správným polem `event-type` (např. `event-type: milonga`)
- Ověřte, zda je syntaxe správná (viz [docs/WIDGETS.md](docs/WIDGETS.md))
- Ujistěte se, že upravujete soubor stránky, ne soubor akce

**Akce se nezobrazují:**
- Ověřte, že jsou akce ve složce `content/events/`
- Zkontrolujte, že každý soubor akce má správně nastavené pole `event-type` (např. `event-type: milonga`)
- Ujistěte se, že akce mají platná data `event-start` ve frontmatteru

**Články se nezobrazují:**
- Ověřte, že je obsah ve správné složce (`content/announcements/`, `content/curiosities/`, `content/people/` apod.)
- Zkontrolujte, zda atribut `category` odpovídá názvu složky
- Ujistěte se, že soubory s obsahem mají platná data

---

## Práce s obrázky

### Kde jsou uloženy obrázky

Všechny obrázky jsou ve složce `content/images/`. Web používá obrázky ve formátu `.avif` (moderní a efektivní formát). Pokud máte JPG nebo PNG, požádejte vývojáře o převod před nahráním.

### Přidání obrázku k akci

Pro přidání obrázku do obsahu akce použijte tento formát:

```markdown
![Popis obrázku]({static}/images/nazev-vaseho-obrazku.avif)
```

> **Poznámka:** `{static}` je speciální klíčové slovo používané systémem webu k nalezení složky s obrázky. Pište ho přesně tak, jak je uvedeno — neměňte ho. Nahraďte pouze `nazev-vaseho-obrazku.avif` skutečným názvem souboru.

> **Tip:** Vždy přidejte krátký popis do závorek `[ ]` (např. `![Plakát Milongy Fuera del Nido]`). Pomůže to návštěvníkům se zrakovým postižením používajícím čtečky obrazovky a zlepší viditelnost ve vyhledávačích.

**Příklad:**
```markdown
---
title: Milonga Fuera del Nido
event-start: 2026-01-17 18:00:00
slug: milonga-fuera-del-nido
---

![Plakát Milongy Fuera del Nido]({static}/images/milonga-fuera-del-nido.avif)

Popis akce zde...
```

### Doporučené postupy pro obrázky

1. **Používejte výstižné názvy souborů** — Usnadní pozdější vyhledávání (např. `milonga-leden-2026.avif` místo `IMG_4821.avif`)
2. **Používejte formát `.avif`** — V případě potřeby požádejte vývojáře o převod
3. **Udržujte názvy souborů jednoduché** — Pouze malá písmena, číslice a pomlčky; žádné mezery ani speciální znaky
4. **Vždy přidejte popis** — Vyplňte závorky `[ ]` krátkým popisem obrázku

### Vyhledávání obrázků

Dostupné obrázky zjistíte pohledem do složky `content/images/`. Název souboru, který tam vidíte, použijte ve svém Markdownu (bez cesty ke složce).

---

## Organizace obsahu

### Struktura složek

Obsah webu je organizován do složek:

- **`content/events/`** — Všechny soubory akcí, organizované podle roku a měsíce (např. `content/events/2026/03/`)
- **`content/events/classes/`** — Soubory opakujících se lekcí
- **`content/pages/`** — Běžné stránky (o nás, stránky kalendáře apod.)
- **`content/announcements/`** — Oznámení
- **`content/images/`** — Všechny obrázky používané na webu

### Typy obsahu

**Akce** (`content/events/YYYY/MM/`)
- Jednotlivé akce s daty a časy
- Musí mít pole `event-start`
- Zobrazují se v kalendářích a seznamech akcí
- Pojmenování souborů: `kratky-popis.md` (např. `milonga-fuera-del-nido.md`)

**Stránky** (`content/pages/`)
- Běžné webové stránky
- Mohou obsahovat widgety
- Příklady: stránky kalendáře, informační stránky

**Šablona – stránka:**

```markdown
---
title: Název stránky
slug: nazev-stranky
date: 2026-01-17 18:00:00
description: Krátký popis zobrazovaný ve výsledcích vyhledávání.
author: Vaše jméno
preview_image: /images/vas-obrazek.avif
---

Text stránky zde. Níže přidejte widgety pro automatické zobrazení obsahu.
```

**Oznámení** (`content/announcements/`)
- Novinky a aktualizace
- Nepotřebují datum akce
- Pojmenování souborů: `RRRR-MM-DD-popis.md` (např. `2026-03-15-jarni-oznameni.md`)

**Šablona – oznámení:**

```markdown
---
title: Název oznámení
date: 2026-03-15 09:00:00
category: announcement
description: Krátké shrnutí pro kartičky a výsledky vyhledávání.
preview_image: /images/announcements/vas-obrazek.avif
author: Vaše jméno
---

Text oznámení zde.
```

**Lekce** (`content/events/classes/`)
- Soubory opakujících se lekcí s polem `recurrence`
- Pojmenování souborů: `studio-uroven.md` (např. `stolarna-tango-i.md`)

---

## Běžné úkoly

### Přidání nové akce

1. Vytvořte nový soubor ve správné podsložce (např. `content/events/2026/03/` pro akci v březnu 2026)
2. Pojmenujte ho výstižně, malými písmeny a s pomlčkami (např. `milonga-fuera-del-nido.md`)
3. Přidejte frontmatter s povinnými poli:
   ```markdown
   ---
   title: Název vaší akce
   date: 2026-01-17 18:00:00
   event-start: 2026-01-17 18:00:00
   event-end: 2026-01-17 22:30:00
   slug: slug-vasi-akce
   ---
   ```
4. Pod frontmatter přidejte popis akce
5. Soubor uložte

### Aktualizace dat akce

1. Otevřete soubor akce ve složce `content/events/`
2. Najděte řádek `event-start` nebo `event-end` ve frontmatteru
3. Aktualizujte datum a čas ve formátu: `RRRR-MM-DD HH:MM:SS`
4. Soubor uložte

**Příklad — změna začátku z 18:00 na 19:00:**
```markdown
event-start: 2026-01-17 19:00:00
```

### Přidání widgetu na stránku

1. Otevřete soubor stránky ve složce `content/pages/`
2. Najděte místo, kde má widget být
3. Přidejte kód widgetu (zkopírujte z příkladů výše)
4. Soubor uložte

**Příklad:**
```markdown
## Nadcházející milongy

<widget-calendar filter_by_type="milonga" days="365"></widget-calendar>
```

### Vyhledávání a úprava existujícího obsahu

**Hledání akce:**
- Podívejte se do složky `content/events/`
- Hledejte podle názvu souboru nebo otevřete soubory a přečtěte si názvy

**Hledání stránky:**
- Podívejte se do složky `content/pages/`
- Názvy souborů obvykle odpovídají tématu stránky

**Úprava:**
- Otevřete soubor
- Proveďte změny
- Soubor uložte

### Přidání obrázku do obsahu

1. Umístěte soubor obrázku `.avif` do složky `content/images/`
2. V obsahu přidejte: `![Krátký popis]({static}/images/vas-soubor.avif)`
3. Nahraďte `vas-soubor.avif` skutečným názvem souboru a do závorek `[ ]` přidejte popis

---

## Rychlý přehled

### Povinná pole akce

- `title` — Název akce
- `date` — Datum článku (formát: `RRRR-MM-DD HH:MM:SS`, stejná hodnota jako `event-start`)
- `event-start` — Kdy akce začíná (formát: `RRRR-MM-DD HH:MM:SS`)
- `slug` — URL-přátelský identifikátor (malá písmena, pomlčky, bez mezer)

### Doporučená / volitelná pole akce

- `event-type` — `milonga`, `workshop`, `class` nebo `praktika`
- `event-end` — Kdy akce končí (stejný formát jako `event-start`)
- `event-location` — Místo konání a adresa
- `event-organiser` — Název pořadatele nebo studia
- `instructor` — Pro lekce/workshopy: `"['Jméno', 'Jméno']"` pro více lektorů, nebo pouze jméno pro jednoho
- `recurrence` — Pro opakující se akce, např. `weekly sunday`
- `description` — Krátké shrnutí pro kartičky a výsledky vyhledávání
- `preview_image` — Např. `/images/akce.avif`

### Rychlá syntaxe widgetů

**Akce:**
```html
<widget-calendar filter_by_type="milonga" days="365"></widget-calendar>
<widget-calendar filter_by_type="milonga" days="7"></widget-calendar>
<widget-calendar filter_by_type="milonga" days="-30"></widget-calendar>
<widget-calendar filter_by_type="milonga" start="2026-06-01" end="2026-08-31"></widget-calendar>
```

**Články (oznámení, pikanterie, lidé):**
```html
<widget-articles category="announcement" limit="3"></widget-articles>
<widget-articles category="curiosity" limit="all"></widget-articles>
<widget-articles category="people" metadata="description"></widget-articles>
<widget-articles category="people" slugs="filip-paldia lenka-platenikova" metadata="description"></widget-articles>
```

### Syntaxe obrázku

```markdown
![Krátký popis obrázku]({static}/images/soubor.avif)
```

---

## Potřebujete pomoc?

Pokud si nejste jistí:
- **Formáty dat** — Použijte příklady v tomto průvodci
- **Syntaxe widgetů** — Zkopírujte příklady přesně
- **Umístění souborů** — Podívejte se do sekce o struktuře složek
- **Použití obrázků** — Viz sekce o obrázcích

Pamatujte: V případě pochybností se podívejte do existujících souborů jako příkladů, jak se věci dělají.
