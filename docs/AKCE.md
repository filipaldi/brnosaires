# Přidat a upravit akci

## Nejjednodušší cesta: formulář na [/admin/](https://brnosaires.com/admin/) 🖱️

Otevři **[brnosaires.com/admin](https://brnosaires.com/admin/)** a klikni na **„Sign In Using Access Token"** — token si vygeneruješ podle odkazu přímo na přihlašovací obrazovce, stačí jednou. Celý postup i s tím, jak se editor přidává, je v [Přístup do /admin/](PRISTUP.md).

Rozhraní **je česky** — jazyk se bere z prohlížeče a dá se přepnout v nastavení (ikona účtu vpravo nahoře). Slovenština zatím není, tam se rozhraní vrátí k angličtině.

Dostaneš formulář: typ akce vybereš ze seznamu, datum a čas naklikáš, místo vybereš z nabídky, obrázek nahraješ přetažením. Slug, datum publikace a formát hlavičky za tebe pohlídá formulář — nic z toho, co je popsané níž, psát nemusíš.

Zbytek téhle stránky je **ruční cesta a je pro vývojáře**: psaní souborů přímo na GitHubu nebo v editoru. Jako editorka ji nepotřebuješ — formulář hlídá tvar hlavičky, jméno souboru i adresu stránky, ruční zápis nehlídá nic a chybu poznáš, až když akce nevyjde.

Obě cesty zapisují ty samé soubory, takže vývojář může kdykoli sáhnout do repozitáře, aniž by tím formulář rozbil.

---

Nejčastější úkoly v kostce:

- **Přidat jednorázovou akci** (milonga, workshop) → kroky 1-5 níže.
- **Přidat pravidelnou lekci** (každý týden / měsíc) → [Pravidelná lekce přes `recurrence:`](#pravidelná-lekce-přes-recurrence).
- **Upravit už existující akci/lekci** (datum, čas, cena) → [Upravit existující akci](#upravit-existující-akci).
- **Zmenšit nahrané fotky** (nedělá se samo) → [Zmenšení obrázků do AVIF](#zmenšení-obrázků-do-avif).

Detail všech polí hlavičky → [Pole v hlavičce](EDITING.md). Série (Milonga u Draka apod.) → [Série](SERIE.md). Anglická verze → [Anglická verze](ANGLICKA-VERZIA.md).

---

## 1️⃣ Vytvoř soubor a zkopíruj do něj tuhle hlavičku

Nový soubor patří do [content/events/](../content/events/) → podsložka `RRRR/MM/` podle měsíce akce (např. akce v květnu 2026 → `content/events/2026/05/`).

Zkopíruj celý blok, smaž řádky, které nepotřebuješ, vyplň hodnoty:

```yaml
---
title: Milonga u Draka
slug: 2026-05-16-milonga-u-draka       # NEPOVINNÉ — bez něj se adresa vezme
                                       # ze jména souboru
date: 2026-04-10 18:00:00              # datum PUBLIKACE, NE datum akce
author: Tvé jméno
description: Krátký popis (do ~200 znaků) pro Google a náhled na sítích.
preview_image: /images/events/2026/milonga.jpg   # 1200×630
event-type: milonga                    # milonga | workshop | class | praktika | neolonga
event-start: 2026-05-16 19:00:00
event-end: 2026-05-16 22:30:00         # půlnoc = 00:00:00 dalšího dne, NIKDY 24:00:00
event-venue: Stará radnice
event-street: Radnická 8
event-locality: Brno
entry: 150 Kč                          # vstupné; "zdarma" / "dobrovolné" → akce zdarma
---
```

Volitelně: `event-organiser`, `instructor_slugs` (slugy profilů z `content/people/`, viz [EDITING.md](EDITING.md)), `series` (jen u série, viz [Série](SERIE.md)).

⚠️ **Do hlavičky nepiš komentáře.** Řádek začínající `#` ukončí čtení hlavičky a **všechno pod ním se tiše zahodí** — pole tam zůstane napsané, ale web se chová, jako by ho tam nebylo. Poznámku napiš do těla článku, ne do hlavičky.

⚠️ **Hlavičku ohranič `---` nahoře i dole**, jak je v bloku výše. Pelicanu je to jedno, ale formuláři na [/admin/](https://brnosaires.com/admin/) ne: bez ohraničení přečte celý soubor jako text, hlavičku ti ukáže uprostřed článku a při uložení ji přepíše prázdnou. Deset souborů v repu tuhle chybu mělo.

---

## 2️⃣ Pojmenuj soubor správně ⚠️

Hlavička výše tohle neřeší — název souboru si musíš ohlídat sám. **Tři pravidla, jinak se akce nepublikuje nebo spadne celý web:**

| Pravidlo | Špatně | Správně |
|---|---|---|
| Datum vepředu jako `RRRR-MM-DD` | `16-05-2026-milonga.md` | `2026-05-16-milonga.md` |
| Bez mezer | `milonga u draka.md` | `milonga-u-draka.md` |
| Bez diakritiky | `Únorová neolonga.md` | `2026-02-neolonga.md` |

Špatné pořadí data (`DD-MM-RRRR`) **shodí build celému webu** — Pelican čeká rok první. Mezery a diakritika někdy projdou, ale nespoléhej na to; piš malými písmeny s pomlčkami.

---

## 3️⃣ Zkontroluj tyhle čtyři řádky — tady se chybuje nejčastěji ⚠️

| Řádek | Na co si dát pozor |
|---|---|
| `date:` | Datum, kdy soubor **publikuješ**, ne kdy je akce. Datum akce patří jen do `event-start`. Formát `RRRR-MM-DD HH:MM:SS`. Datum v budoucnu = stránka se nezobrazí ve správném pořadí. |
| `slug:` | **Nepovinné.** Bez něj se adresa vezme ze jména souboru, které formulář vyrobí z názvu — to je běžný případ. Když ho vyplníš: unikátní, bez diakritiky, malými písmeny s pomlčkami. Dva soubory se stejnou adresou se při buildu přepíšou, jeden tiše zmizí. |
| `event-end:` | Vždy vyplněné. Půlnoc piš jako `00:00:00` **dalšího dne** (`2026-05-17 00:00:00`), nikdy `24:00:00` — to Python neumí a akce se nepublikuje. |
| `event-type:` | Musí sedět druh akce — viz krok 4. |

---

## Adresa místa 📍

Místo se píše do **tří polí**, ne do jednoho řádku:

```yaml
event-venue: Adrinela Cafe          # podnik nebo sál
event-street: Životského 14         # ulice a číslo
event-locality: Brno-Židenice       # obec nebo čtvrť
```

Z nich se skládá adresa pro Google i mapa v hlavičce akce. Dřív to byl jeden
řádek dělený podle čárek a na pořadí částí záleželo; teď každá část ví, co je
zač, takže se nedá zaměnit ulice za název podniku.

Co pořád platí:

| Pole | Když chybí |
|---|---|
| `event-venue` | Nic se nerozbije, ale místo se ukáže jen jako adresa. Vhodné u „prostě v Brně". |
| `event-street` | Místo se vypíše, ale **neodkáže na mapu** — není kam navigovat. |
| `event-locality` | Google dostane podnik bez obce. Vyplň vždy; předvyplněné je `Brno`. |

Jeden podnik = **jeden zápis**. „Sesamo bakery" a „Sesamo Bakery" jsou pro web
dvě různá místa. Než vymyslíš nový, koukni, jak je napsaný u starších akcí:

```bash
grep -rh "^event-venue:" content/ | sort | uniq -c | sort -rn
```

Když akci píšeš i anglicky (`.en.md`), musí mít všechna tři pole **stejnou
hodnotu** — adresa se nepřekládá.

---

## 4️⃣ Vyber správný `event-type`

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

## 5️⃣ Commitni 💾

Soubor uložíš jedním ze dvou způsobů:

- **GitHub web UI** — otevři repo v prohlížeči, najdi složku, „Add file" → „Create new file" (nebo tužku ✏️ u existujícího), vlož obsah, dole „Commit changes". Stačí prohlížeč a GitHub účet. Vhodné pro text.
- **GitHub Desktop** — naklonuj repo, edituj v textovém editoru, commitni a „Push origin". Vhodné pro obrázky a víc souborů najednou.

Web se sestaví **automaticky dvakrát denně** (06:00 a 18:00 UTC). Potřebuješ rychleji? Vyžádej si ruční build u vývojáře.

**Obrázky nahrávej v jakémkoli formátu, který máš po ruce** — `.jpg` z mobilu, `.png` ze screenshotu, `.heic` z iPhonu. Do `preview_image:` napiš přesně tu příponu, kterou nahráváš. Web si s tím poradí: sociální náhledy pro Facebook a spol. si vyrobí sám při každém buildu.

Velké fotky se ale zmenšují **až na vyžádání**, ne samy — viz [Zmenšení obrázků](#zmenšení-obrázků-do-avif) níž. Do té doby se servíruje to, co jsi nahrál.

---

## Akce se neobjevila? Pět nejčastějších důvodů ❌

Soubor je commitnutý, build proběhl, ale akci na webu nevidíš. Skoro vždy je to jedno z těchto — a žádné z nich nehlásí chybu:

1. **Akce je v jiné kategorii** — špatný `event-type` (krok 4). Workshop jako `class` najdeš mezi lekcemi, ne mezi workshopy.
2. **Akce se vůbec nepublikovala** — `event-end` má `24:00:00` místo `00:00:00` dalšího dne, nebo chybí úplně.
3. **Akce se přepsala jinou** — dva soubory mají stejný `slug:`. Při buildu vyhraje poslední, druhý zmizí. Zkontroluj slug hledáním přes `content/`.
4. **Akce je „v budoucnu"** — `date:` (datum publikace) je nastavené dopředu, takže se řadí až za vším ostatním. Pozor: `date` ≠ `event-start`.
5. **Náhled je prázdný / kartička rozbitá** — `preview_image:` ukazuje na neexistující soubor, nebo cesta začíná `content` (má začínat lomítkem: `/images/...`). Pole se jmenuje `preview_image`, ne `og_image`.

Stále nic? Build mohl spadnout úplně (typicky špatné pořadí data v názvu souboru, krok 2). Napiš vývojáři, ať se podívá do logu GitHub Actions.

---

## Pravidelná lekce přes `recurrence:` 🔁

Lekce, která se opakuje každý týden nebo měsíc, je **jeden soubor**, ne dvanáct. Pole `recurrence:` ho při buildu rozbalí na všechny termíny.

Soubor leží tam, kde všechny ostatní akce: `content/events/RRRR/MM/` podle měsíce **prvního** termínu. Vlastní složku pravidelné lekce nemají — ve formuláři jsou to taky jen akce a v seznamu je vyfiltruješ přepínačem „Pravidelné".

Vezmi existující lekci jako předlohu. Hlavička vypadá takhle:

```yaml
title: Tango II.
event-start: 2026-06-01 17:45:00         # PRVNÍ termín (datum + čas začátku)
event-end: 2026-06-01 19:00:00           # konec prvního termínu
recurrence: weekly                       # každý týden ve stejný den jako Začátek
recurrence-until: 2026-12-14             # nepovinné; bez něj série běží dál
event-type: class                        # pravidelná lekce = class (NE workshop)
event-venue: Taneční studio Stolárna
event-street: Olomoucká 14
event-locality: Brno
instructor_slugs:
    - pavla-luzna
    - ondra-martinak
preview_image: /images/classes/class-stolarna.avif
description: …
author: Lenka Pláteníková
```

`instructor_slugs:` jsou slugy profilů z [content/people/](../content/people/) - název souboru bez `.md`, víc lektorů oddělených čárkou. Slug, ke kterému profil neexistuje, shodí build, takže jména z předlohy přepiš za svoje. Podrobnosti v [EDITING.md](EDITING.md).

**Hodnoty `recurrence:`** — jedna ze dvou, nic víc. Když se upíšeš, zůstane akci jen jeden termín a v logu GitHub Actions je varování:

| Zápis | Význam |
|---|---|
| `weekly` | každý týden ve stejný den, na jaký padá `event-start` |
| `monthly` | každý měsíc ve stejný den — třetí středa zůstane třetí středou |

**Den se nikam nepíše.** Vezme se z `event-start`, protože tam už jednou stojí. Dokud se psal dvakrát, rozešel se: `stolarna-tangomania.md` měla půl roku v pravidlu pondělí a v `event-start` čtvrtek, takže soubor tvrdil jedno a kalendář ukazoval druhé. Chceš lekci přesunout na jiný den? Změň `event-start` a nic dalšího.

Čas se bere z `event-start`/`event-end` a platí pro všechny termíny.

### Kdy má série začít a skončit ⏳

Bez dalšího údaje běží série **donekonečna**. Kurz o osmi lekcích tak slibuje hodiny, které se nekonají, a v kalendáři visí napořád.

```yaml
recurrence: weekly
recurrence-until: 2026-11-03      # poslední termín, včetně
```

Ve formuláři je to políčko „Opakovat do" hned pod „Opakování"; prázdné znamená bez konce. Datum, které se nedá přečíst, se zahodí a série běží dál — v logu GitHub Actions je pak varování, takže se to dá dohledat.

**Starší zápis** `weekly monday until 2026-12-16` (den i dovětky `until` / `count` / `from` uvnitř jednoho řádku) web pořád přečte, takže starý soubor nemusíš přepisovat. Psát ho ale nemusíš a formulář ho nenabízí.

## Zmenšení obrázků do AVIF

Fotka z mobilu má běžně 3-5 MB. Naservíruje se každému návštěvníkovi tak, jak je, takže se to vyplatí zmenšit — do `.avif` se vejde zhruba ve čtvrtině velikosti.

**Neděje se to samo.** Musí to někdo spustit:

1. GitHub → záložka **Actions** → vlevo **„Convert dropped images"**
2. vpravo **„Run workflow"** → tlačítko „Run workflow"
3. za pár minut se v repu objeví **commit od robota**

Ten commit převede každý obrázek v `content/`, přepíše na něj odkazy ve všech `.md` souborech a **původní soubor smaže**. Poprvé to zmate, ale je to správně — originál zůstává v historii gitu. Než robot doběhne, sáhne si na hotový web a ověří, že žádný odkaz nezůstal viset; když by měl, nic nepushne.

Spusť to, kdykoli se fotky nahromadí. Na prodlevě nezáleží — skript převede, co v `content/` zrovna leží. Když to nikdo nespustí, web funguje dál, jen se obrázky servírují v původní velikosti.

Sociální náhledy (Facebook, LinkedIn, WhatsApp) AVIF přečíst neumí. **Řešit to nemusíš** — web si při každém buildu vyrobí JPEG kopii jen pro ně. V repu ani v hlavičce ji nikde neuvidíš.

---

## Upravit existující akci ✏️

Soubor už existuje, jen měníš hodnotu. Otevři ho v [content/events/RRRR/MM/](../content/events/) podle měsíce konání (u pravidelné lekce podle **prvního** termínu) a uprav jen ten řádek:

| Co měníš | Řádek | Pozor |
|---|---|---|
| Datum / čas jednorázové akce | `event-start`, `event-end` | `date:` **neměň** — to je datum publikace, ne akce. Půlnoc v `event-end` = `00:00:00` dalšího dne, nikdy `24:00:00`. |
| Cenu | `entry` | „zdarma" / „dobrovolné" → akce se označí jako bezplatná. |
| Místo | `event-venue`, `event-street`, `event-locality` | Tři pole, ne jeden řádek — viz [Adresa místa](#adresa-místa-). |
| Čas pravidelné lekce | `event-start`, `event-end` | Změní se na **všech** termínech. |
| Den pravidelné lekce | jen `event-start` | Posuň datum na nový den. `recurrence: weekly` si den vezme odtamtud, takže se nedá rozejít. |

Co **neměnit**, pokud nechceš změnit URL: `slug:` a jméno souboru. Obojí určuje adresu — jméno souboru tehdy, když `slug:` chybí. Změna = nová URL, stará přestane fungovat (rozbité odkazy, ztracené SEO). Opravit název akce je bezpečné: adresu to nehne.

Po úpravě commitni stejně jako u nové akce (krok 5). Pokud se změna neprojeví, projdi [Akce se neobjevila?](#akce-se-neobjevila-pět-nejčastějších-důvodů) výše.

---

## Související 🔗

- [Pole v hlavičce](EDITING.md) — referenční přehled všech metadat a co se kde zobrazí.
- [Série](SERIE.md) — jak přidat akci do pravidelné série (Milonga u Draka, Tango & Pizza).
- [Anglická verze](ANGLICKA-VERZIA.md) — `.en.md` sourozenec stránky.
- [Widgety](WIDGETS.md) — tagy `<widget-*>` v těle (kalendář, seznam akcí).
