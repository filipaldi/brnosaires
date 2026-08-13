# Anglická verze webu (`/en/`)

Web má anglickou verzi pod prefixem `/en/`. České stránky si ponechávají původní URL (`/<slug>/`) beze změny. V hlavičce webu je přepínač `CS · EN`.

## ⚙️ Jak to funguje

- **Každá stránka má anglický klon „zdarma".** I když anglickou verzi nenapíšete, `/en/<slug>/` přesto existuje — zobrazí *české tělo* článku, ale s anglickým „obalem": navigace, datumy, meta tagy, přepínač jazyka, `<html lang="en">`, `hreflang`. Web tak má od začátku plné pokrytí; překlady přibývají postupně.
- **Chcete napsat skutečnou anglickou verzi stránky?** Vytvořte vedle původního souboru sourozenec s příponou `.en.md` a **stejným `slug`em**:

  ```
  content/pages/o-nas.md        →  Lang: cs  (nepovinné — výchozí),  Slug: o-nas
  content/pages/o-nas.en.md     →  Lang: en,                          Slug: o-nas   (stejný slug!)
  ```

  Pelican je propojí podle `slug`u. Anglický soubor se vyrenderuje na `/en/o-nas/`, přepínač jazyka mezi nimi pak skáče správně. `Lang: en` do hlavičky napište explicitně, i když přípona `.en.` ho nastavuje sama (kvůli čitelnosti).

## 📝 Postup krok za krokem

Zkopírujte `content/pages/foo.md` → `content/pages/foo.en.md`; do hlavičky přidejte `Lang: en` a ponechte **stejný `Slug:`** jako v českém souboru; přeložte `Title:`, `Description:` a tělo (anglicky podle [voice skillu](../.claude/skills/voice/SKILL.md) — britská angličtina, bez pomlček „-"); widgety (`<widget-*>`) nechte tak, jen u nich přeložte texty v atributech `label=` / `label_webcal=` / `label_google=` / `label_outlook=`. Hotovo — stránka se objeví na `/en/<slug>/` místo dosavadního českého fallbacku.

**Domovská stránka** má zvláštnost — anglický `content/pages/index.en.md` musí mít `Slug: index` (web má `SLUGIFY_SOURCE = "basename"`, takže slug českého `index.md` je `index`, ne `brnos-aires` z titulku — sourozenec se propojí jen při shodě slugu) **a** `save_as: en/index.html` / `url: en/` (český `index.md` má vlastní `save_as`, který by se jinak zdědil).

## 🧭 Navigace, datumy, jednojazyčný obsah

- **Datumy** se vykreslují podle jazyka stránky: česky `16. 05. 2026`, anglicky `16 May 2026`. Nic nenastavujete — je to automatické.
- **Navigace v hlavičce i patičce:** odkazy se berou ze souborů v [content/navigation/](../content/navigation/) — formát `Popisek, slug` (jeden na řádek; `slug` je slug stránky nebo absolutní URL; řádky `#…` jsou komentář). Hlavní navigace: `main.md` (česky) + `main.en.md` (anglické popisky, stejné slugy). Patička: `footer.md` + `footer.en.md` — patička je **per-jazyk** (na `/en/` stránkách je celá anglicky), kromě odkazů obsahuje ještě automaticky pásek měsíčních stránek („Milongy po měsících:") a odkazy na `.ics` kalendáře — ty se z `footer.md` neberou, jsou v šabloně [components/footer.html](../theme/templates/components/footer.html). Pořadí v navigaci = pořadí řádků v souboru; změna se projeví na celém webu.
- **Jednojazyčný obsah — `translate: false`.** Obsah, který **nemá a nikdy mít nebude** překlad (typicky anglicky psaný microsite), může v hlavičce deklarovat `translate: false`. Pak se pro něj negeneruje žádný `/en/` klon, nezobrazuje se přepínač jazyka a `<html lang>` je `en`. Pro **Tango Marathon** je tahle vlajka nastavena hromadně pro všechny tři jeho složky — [content/pages/marathon/](../content/pages/marathon/), [content/events/2026-marathon/](../content/events/2026-marathon/) a profily DJů (ty vlajku nesou každý sám v hlavičce, viz níž) — přes `EXTRA_PATH_METADATA` v [pelicanconf.py](../pelicanconf.py). Marathon je tedy anglicky od začátku, bez české verze; jeho stránky, akce ani DJ profily žádný český sourozenec nedostávají a `<html lang>` je tam vždy `en`. Výchozí stav (bez vlajky) = obsah je „přeložitelný" a dostává český fallback pod `/en/`.

## 🔗 Související

- [SEO](SEO.md) — architektura: jak přesně se klony generují, jak funguje `hreflang`, proč jsou české URL beze změny.
- [Pole v hlavičce](EDITING.md) — referenční přehled metadat.
- [content/navigation/](../content/navigation/) — odkazy v navigaci: `main.md`/`main.en.md`, `footer.md`/`footer.en.md`, `marathon.md`.

### `translate: false` v hlavičce jednotlivého souboru

Vlajka funguje i mimo ty složky — napiš ji do hlavičky a soubor žádný `/en/`
klon nedostane. Tak ji nesou profily marathonových DJů: leží v jedné složce
[content/people/](../content/people/) spolu s ostatními lidmi, takže jim ji
cesta dát nemůže.

Pozor na jednu věc: **řádek s `#` v hlavičce zahodí všechno pod sebou**, takže
vlajka napsaná pod komentářem se tiše neuplatní. Komentáře do hlavičky nepatří.
