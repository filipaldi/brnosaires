# Plán rozvoje

Plánované funkce, známé problémy a úklidové úkoly pro web Brnos Aires. Položky jsou seskupeny podle typu; každá odkazuje zpět na zdroj, ze kterého vychází.

## Obsah

1. [Plánované funkce](#plánované-funkce)
2. [Známé problémy](#známé-problémy)
3. [Úklid](#úklid)
4. [Hotovo](#hotovo)
5. [Související](#související)

---

## Plánované funkce

- **Překlad obsahu pod `/en/` — akce, oznámení, pikošky, lidé.** Anglická verze webu (`/en/`) běží — stránky ([content/pages/](../content/pages/)) jsou přeložené, navigace, datumy, meta tagy a přepínač jazyka taky (viz [Anglická lokalizace celého webu](#hotovo) v sekci *Hotovo*). Co zatím **fallbackuje na češtinu**: jednotlivé akce ([content/events/](../content/events/)), oznámení ([content/announcements/](../content/announcements/)), pikošky ([content/curiosities/](../content/curiosities/)) a profily lidí ([content/people/](../content/people/)) — na `/en/<slug>/` se zobrazí české tělo v anglickém obalu. Postupně doplnit anglické varianty (`*.en.md`, stejný `Slug`, `Lang: en`) tam, kde to dává smysl (priorita: nejnavštěvovanější / nadčasový obsah). Marathon je výjimka — je anglicky od začátku, žádný překlad nepotřebuje (`translate: false`).

- **YAML pole `entry` (vstupné) u akcí.** Frontmatter akcí (např. [content/events/2026/05/2026-05-milonga-v-adrinele.md](../content/events/2026/05/2026-05-milonga-v-adrinele.md)) dnes obsahuje pole `event-type`, `event-start`, `event-end`, `event-location`, `event-organiser` — ale informace o vstupném je různě roztroušená v těle markdownu (viz [vikend-2026-sobota-milonga-ziva-hudba.md](../content/events/2026/05/vikend-2026-sobota-milonga-ziva-hudba.md) *„Vstupné 390,- Kč / 16Eur"* nebo workshopy *„PLNÁ CENA: jedna lekce 270 Kč…"*). Zavést jednotné YAML pole `entry` (volně formátovaný řetězec, např. `entry: "150 Kč / 6 €"` nebo `entry: "zdarma"`). Pole musí být zobrazeno jak na kartě akce ([theme/templates/components/event_card.html](../theme/templates/components/event_card.html)), tak na stránce události ([theme/templates/article.html](../theme/templates/article.html)), a doplnit ho i do JSON-LD jako `offers.price` / `offers.priceCurrency` kde to dává smysl. Pole nechat volitelné — chybějící hodnota se nezobrazí.

- **Automatické kontroly před publikací.** [Nasazení](publishing.md) definuje ruční checklist před nasazením (widgety se renderují, metadata akcí jsou validní, odkazy fungují atd.). Nahradit CI jobem, který poběží při každém pushi: sestaví web s [publishconf.py](../publishconf.py), ověří frontmatter akcí (povinná a parsovatelná pole `date` a `event-start`) a zkontroluje odkazy ve složce `output/`.

---

## Známé problémy

- **Web neni plne optimalizovan pro čtečky.**

- **Zastaralá syntaxe widgetů v dokumentaci lokálního testování.** Vyřešeno během sjednocení dokumentace — viz [Lokální testování](local-testing.md). *(Zachováno pro historii.)*

- **Průvodce publikací popisuje špatný způsob nasazení.** Vyřešeno — [Nasazení](publishing.md) byla přepsána tak, aby popisovala skutečné nasazení přes GitHub Actions → GitHub Pages podle [.github/workflows/deploy.yml](../.github/workflows/deploy.yml). *(Zachováno pro historii.)*

- **README a docs byly v různých jazycích.** Vyřešeno — všechna dokumentace je nyní v češtině; [Brnos Aires — web](../README.md) slouží jako rozcestník odkazující do [docs/](.). *(Zachováno pro historii.)*

- **Nepřesný strom obsahu v setup dokumentaci.** Vyřešeno — [Nastavení vývojového prostředí](setup.md) má teď správný strom (`classes/` pod `events/`). *(Zachováno pro historii.)*

---

## Úklid

- **Prázdné adresáře `migration-scripts/converters/` a `migration-scripts/utils/`.** Vyřešeno — adresáře na disku neexistují a [.gitignore](../.gitignore) celý `migration-scripts/` ignoruje. *(Zachováno pro historii.)*

- **Dočasné soubory v kořeni projektu.** Vyřešeno — `test_workshop.html`, `event-detail.png`, `.playwright-mcp/` jsou v [.gitignore](../.gitignore).

- **Úklid `.DS_Store`.** `.DS_Store` je v [.gitignore](../.gitignore), ale dva soubory (`theme/static/.DS_Store`, `theme/static/fonts/.DS_Store`) zůstaly v repu z historie a je třeba je odtrackovat příkazem `git rm --cached`.

## Hotovo

- **Sjednocení dokumentace + převod do češtiny.** Všechny dokumenty v [docs/](.) jsou v češtině, [Brnos Aires — web](../README.md) je rozcestník místo 645řádkového manuálu pro editory (obsah se přesunul do [Úprava obsahu](EDITING.md)). Každý dokument má TOC, „Související" navigační blok dole a interní odkazy používají *názvy dokumentů* místo holých jmen souborů. [Nasazení](publishing.md) byla přepsána ke skutečnému toku GitHub Actions → Pages, [Lokální testování](local-testing.md) opraveno (správná syntaxe widgetů), [Nastavení vývojového prostředí](setup.md) opraveno (strom `content/`).

- **Přepracovaná patička (sekundární navigace + SEO).** Patička je teď řízená daty z [content/navigation/footer.md](../content/navigation/footer.md) (+ `footer.en.md`) přes plugin [nav_from_docs.py](../plugins/nav_from_docs.py) — stejný mechanismus jako hlavní navigace, takže má **per-jazyk varianty** a na `/en/` stránkách je celá anglicky (předtím byla hardcoded česky). Kromě odkazů na všechny klíčové stránky + huby sérií + „milongy tento týden" obsahuje pásek měsíčních stránek („Milongy po měsících:"), odkazy na `.ics` kalendáře (milongy / lekce / vše) a sitewide `Organization` JSON-LD (`name`, `description` per-jazyk, `areaServed` → City „Brno"). Kontakt / sociální sítě / logo se nedoplňovaly — pro web žádné neexistují. Šablona: [theme/templates/components/footer.html](../theme/templates/components/footer.html).

- **Měsíční stránky milong (`/milongy-brno-<měsíc>/`).** Dvanáct evergreen stránek, jedna na každý měsíc (`/milongy-brno-leden/` … `/milongy-brno-prosinec/`, + `.en.md` dvojčata na `/en/…`), cílených na hledání „milonga Brno [měsíc]" / „milonga Brno [měsíc] [rok]". Stránka je tenká skořápka: `month: N` ve frontmatteru, úvodní odstavec bez ročníku, `<widget-calendar month="N">`, `.ics` odběr. `<title>`/`<h1>` i zobrazený rok vyrábí šablona ([theme/templates/page.html](../theme/templates/page.html)) z `month:` přes build-time filtr `tango_year_for_month` — žádný roční úklid. Šablona navíc vykresluje `ItemList` JSON-LD pro daný měsíc, `noindex,follow` u prázdného měsíce, prev/next prstenec a pásek všech měsíců; vstupní odkazy „Milongy po měsících:" jsou na [milongy.md](../content/pages/milongy.md) a [kalendar.md](../content/pages/kalendar.md) (CS+EN). **Zvažovaná, zamítnutá alternativa:** plugin, který stránky generuje sám — moc kódu na údržbu za malý přínos; dvanáct ručních souborů je triviálních a editovatelných. (Architektura: [SEO + sociální kartičky](SEO.md), editorský postup: [Úprava obsahu](EDITING.md), `month=` parametr widgetu: [Widget systém](WIDGETS.md).)

- **Anglická lokalizace celého webu (`/en/`).** Web má anglickou verzi pod prefixem `/en/`: české URL (`/<slug>/`) zůstávají beze změny, anglické se renderují na `/en/<slug>/`. Hotovo: lehký i18n engine (Pelican `Lang:`/`Slug:` propojení + per-jazyk řetězcové tabulky [theme/i18n/cs.py](../theme/i18n/cs.py) a [theme/i18n/en.py](../theme/i18n/en.py) + `t()` filtr + plugin [plugins/i18n_fallback.py](../plugins/i18n_fallback.py), který synthetizuje český fallback pro nepřeložený obsah — bez `i18n_subsites`, bez `gettext`); lokalizovaná hlavička v [theme/templates/base.html](../theme/templates/base.html) (`<html lang>`, `og:locale`, meta description, `hreflang`, `x-default`, localStorage zapamatování + redirect z `/` na `/en/`); přepínač jazyka jako chip dole na liště ([theme/templates/components/lang_switcher.html](../theme/templates/components/lang_switcher.html)); per-jazyk hlavní navigace ([content/navigation/main.en.md](../content/navigation/main.en.md)); lang-aware datumy; anglické překlady všech ~13 stránek (`content/pages/*.en.md`); jednojazyčný obsah deklaruje `translate: false` (marathon — bez `/en/` zrcadla, bez přepínače). Architektura v [SEO + sociální kartičky](SEO.md), editorský postup v [Úprava obsahu](EDITING.md). Zbývající práce (překlad akcí/oznámení/pikošek/lidí) je vedena jako samostatná položka v *Plánovaných funkcích*. Tato položka pohltila i dřívější samostatný úkol *„Anglická lokalizace nadpisů ve widgetech"*.

- **Nadpisy v kartách akcí se nezalamují.** `h3` v [theme/templates/components/event_card.html](../theme/templates/components/event_card.html) u delších názvů akcí nezalamoval na další řádek — text přetékal šířku karty a byl oříznutý/nezobrazený. Přidat v [theme/static/css/components.css](../theme/static/css/components.css) k pravidlu `[class*="card-"] > * > h3` zalamování (`overflow-wrap: anywhere;` nebo `word-break: break-word;`, případně `hyphens: auto;` s `lang="cs"`), aby dlouhé nadpisy korektně zalomily a zůstaly celé čitelné.

- **Maximální šířka karty akce na desktopu.** Když v řadě kalendáře (např. týdenní skupina) je jen jedna akce, karta `aesthetic-card` (viz [theme/templates/components/event_card.html](../theme/templates/components/event_card.html) a [theme/static/css/components.css](../theme/static/css/components.css)) se na desktopu roztahovala přes celou šířku flex/grid kontejneru a působila nepřiměřeně velká. Nastaveno `max-width: 45vw` (případně `max-width: min(45vw, …)`) na desktopových breakpointech tak, aby karta neměla nikdy víc než 45 % šířky viewportu. Mobilní layout zachován beze změny.

- **UX karet kalendáře na mobilu.** Aktuální horizontální scrollovací řádek karet akcí nahrazen „tinder-like" swipe zážitkem: jedna karta na viewport s drobným náznakem následující karty po straně, snap-scroll, vertikální orientace karty.

- **Apple kalendář – odběr nefunguje.** Na [brnosaires.com](https://brnosaires.com/) v sekci *„📆 Odebírej akce do svého kalendáře"* odkaz **Apple** na macOS (kterýkoli prohlížeč) neotevíral Kalendář ani nespouštěl odběr. Opraveno URL/scheme.

- **Tlačítka pro odběr kalendáře jsou plain links.** Odkazy *Apple*, *Google*, *Kopíruj pro ostatní* upraveny na tři plnohodnotná tlačítka ve stylu hlavního menu (stejné velikosti, tap target ≥ 44 px, odsazení).

## Související

- [Brnos Aires — web](../README.md) — hlavní rozcestník.
- [Úprava obsahu](EDITING.md) — frontmatter a metadata (pro editory).
- [Widget systém](WIDGETS.md) — tagy `<widget-*>` v markdownu.
- [SEO + sociální kartičky](SEO.md) — architektura a SEO (pro vývojáře).
- [Discoverability pro LLM](LLMS.md) — `/llms.txt` a `.md` zrcadla.
- [Nastavení vývojového prostředí](setup.md) — lokální prostředí.
- [Lokální testování](local-testing.md) — lokální server, ladění.
- [Nasazení](publishing.md) — GitHub Actions → Pages.
