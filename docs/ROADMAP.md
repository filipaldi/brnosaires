# Plán rozvoje

Plánované funkce, známé problémy a úklidové úkoly pro web Brnos Aires. Položky jsou seskupeny podle typu; každá odkazuje zpět na zdroj, ze kterého vychází.

---

## Plánované funkce

- **Překlad obsahu pod `/en/` — akce, oznámení, pikošky, lidé.** Anglická verze webu (`/en/`) běží — stránky (`content/pages/`) jsou přeložené, navigace, datumy, meta tagy a přepínač jazyka taky (viz „Anglická lokalizace celého webu" v sekci *Hotovo*). Co zatím **fallbackuje na češtinu**: jednotlivé akce (`content/events/`), oznámení (`content/announcements/`), pikošky (`content/curiosities/`) a profily lidí (`content/people/`) — na `/en/<slug>/` se zobrazí české tělo v anglickém obalu. Postupně doplnit anglické varianty (`*.en.md`, stejný `Slug`, `Lang: en`) tam, kde to dává smysl (priorita: nejnavštěvovanější / nadčasový obsah). Marathon je výjimka — je anglicky od začátku, žádný překlad nepotřebuje (`translate: false`).

- **YAML pole `entry` (vstupné) u akcí.** Frontmatter akcí (např. `content/events/2026/05/2026-05-milonga-v-adrinele.md`) dnes obsahuje pole `event-type`, `event-start`, `event-end`, `event-location`, `event-organiser` — ale informace o vstupném je různě roztroušená v těle markdownu (viz `vikend-2026-sobota-milonga-ziva-hudba.md` *„Vstupné 390,- Kč / 16Eur"* nebo workshopy *„PLNÁ CENA: jedna lekce 270 Kč…"*). Zavést jednotné YAML pole `entry` (volně formátovaný řetězec, např. `entry: "150 Kč / 6 €"` nebo `entry: "zdarma"`). Pole musí být zobrazeno jak na kartě akce (`theme/templates/components/event_card.html`), tak na stránce události (`theme/templates/article.html`), a doplnit ho i do JSON-LD jako `offers.price` / `offers.priceCurrency` kde to dává smysl. Pole nechat volitelné — chybějící hodnota se nezobrazí.

- **Automatické kontroly před publikací.** [docs/publishing.md:8-18](publishing.md#L8-L18) definuje ruční checklist před nasazením (widgety se renderují, metadata akcí jsou validní, odkazy fungují atd.). Nahradit CI jobem, který poběží při každém pushi: sestaví web s `publishconf.py`, ověří frontmatter akcí (povinná a parsovatelná pole `date` a `event-start`) a zkontroluje odkazy ve složce `output/`.

---

## Známé problémy

- **Web neni plne optimalizovan pro čtečky.** 

- **Footer postrádá SEO a UX best practices.** Současná patička je velmi strohá a pravděpodobně ignoruje SEO i UX standardy (chybí např. navigační odkazy, kontakt, sociální sítě, odkaz na zdroj kalendáře, structured data, odkazy na klíčové stránky). Přepracovat patičku tak, aby plnila funkci sekundární navigace a zlepšila SEO signály. **Součástí tohoto přepracování musí být i anglická varianta patičky** — při anglické lokalizaci webu (`/en/`) byla patička záměrně ponechána česky i na anglických stránkách jako dočasný stav; oprava se sloučí sem, ať se patička nedělá nadvakrát. Odkazy patičky by ideálně měly vznikat přes stejný mechanismus jako hlavní navigace (`content/navigation/`, plugin `nav_from_docs.py`), aby měly per-jazyk varianty (`footer.md` + `footer.en.md`) bez hardcodu v `theme/templates/components/footer.html`.

- **Zastaralá syntaxe widgetů v dokumentaci lokálního testování.** [docs/local-testing.md:94](local-testing.md#L94) stále uvádí `<div data-widget="calendar" data-filter="milonga">`, ale [docs/WIDGETS.md:93](WIDGETS.md#L93) uvádí, že widgety používají formu tagu `<widget-*>` bez prefixu `data-`. Uvedený příklad se nevyrenderuje.

- **Průvodce publikací popisuje špatný způsob nasazení.** [docs/publishing.md](publishing.md) popisuje postupy přes FTP/SFTP, rsync a Netlify. Skutečné produkční nasazení probíhá přes GitHub Actions → GitHub Pages pomocí `.github/workflows/deploy.yml`. Dokumentaci přepsat tak, aby odpovídala realitě.

- **README.md je pouze česky, `docs/*.md` pouze anglicky.** Rozhodnout jazykovou politiku (dvojjazyčná dokumentace? angličtina pro vývojáře, čeština pro editory?) a sjednotit ji.

- **Nepřesný strom obsahu v setup dokumentaci.** [docs/setup.md:63](setup.md#L63) uvádí `classes/` jako složku na nejvyšší úrovni `content/`, ale lekce jsou ve skutečnosti v `content/events/classes/` (viz `pelicanconf.py` a `.claude/CLAUDE.md`).

---

## Úklid

- **Prázdné adresáře `migration-scripts/converters/` a `migration-scripts/utils/`.** Zbytky po migraci z Notionu. Buď skripty obnovit, přidat README vysvětlující, proč jsou prázdné, nebo adresáře smazat.

- **Dočasné soubory v kořeni projektu.** `test_workshop.html`, `event-detail.png` a složka `.playwright-mcp/` se objevují v `git status`. Přidat do `.gitignore` nebo odstranit.

- **Úklid `.DS_Store`.** Smazání `theme/static/.DS_Store` a `theme/static/fonts/.DS_Store` leží v pracovním stromu nestagované. Odstranění commitnout a přidat `.DS_Store` do `.gitignore`, pokud tam ještě není.

## Hotovo

- **Měsíční stránky milong (`/milongy-brno-<měsíc>/`).** Dvanáct evergreen stránek, jedna na každý měsíc (`/milongy-brno-leden/` … `/milongy-brno-prosinec/`, + `.en.md` dvojčata na `/en/…`), cílených na hledání „milonga Brno [měsíc]" / „milonga Brno [měsíc] [rok]". Stránka je tenká skořápka: `month: N` ve frontmatteru, úvodní odstavec bez ročníku, `<widget-calendar month="N">`, `.ics` odběr. `<title>`/`<h1>` i zobrazený rok vyrábí šablona ([page.html](../theme/templates/page.html)) z `month:` přes build-time filtr `tango_year_for_month` — žádný roční úklid. Šablona navíc vykresluje `ItemList` JSON-LD pro daný měsíc, `noindex,follow` u prázdného měsíce, prev/next prstenec a pásek všech měsíců; vstupní odkazy „Milongy po měsících:" jsou na `milongy.md` a `kalendar.md` (CS+EN). **Zvažovaná, zamítnutá alternativa:** plugin, který stránky generuje sám — moc kódu na údržbu za malý přínos; dvanáct ručních souborů je triviálních a editovatelných. (Architektura: [SEO.md → Evergreen month pages](SEO.md), editorský postup: [EDITING.md → Měsíční stránky milong](EDITING.md), `month=` parametr widgetu: [WIDGETS.md](WIDGETS.md).)

- **Anglická lokalizace celého webu (`/en/`).** Web má anglickou verzi pod prefixem `/en/`: české URL (`/<slug>/`) zůstávají beze změny, anglické se renderují na `/en/<slug>/`. Hotovo: lehký i18n engine (Pelican `Lang:`/`Slug:` propojení + per-jazyk řetězcové tabulky `theme/i18n/{cs,en}.py` + `t()` filtr + plugin `plugins/i18n_fallback.py`, který synthetizuje český fallback pro nepřeložený obsah — bez `i18n_subsites`, bez `gettext`); lokalizovaná hlavička v `base.html` (`<html lang>`, `og:locale`, meta description, `hreflang`, `x-default`, localStorage zapamatování + redirect z `/` na `/en/`); přepínač jazyka jako chip dole na liště (`components/lang_switcher.html`); per-jazyk hlavní navigace (`content/navigation/main.en.md`); lang-aware datumy; anglické překlady všech ~13 stránek (`content/pages/*.en.md`); jednojazyčný obsah deklaruje `translate: false` (marathon — bez `/en/` zrcadla, bez přepínače). Architektura v [SEO.md](SEO.md) („Multilingual: the /en/ mirror"), editorský postup v [EDITING.md](EDITING.md) („Jazykové verze"). Zbývající práce (překlad akcí/oznámení/pikošek/lidí) je vedena jako samostatná položka v *Plánovaných funkcích*. Tato položka pohltila i dřívější samostatný úkol *„Anglická lokalizace nadpisů ve widgetech"*.

- **Nadpisy v kartách akcí se nezalamují.** `h3` v `theme/templates/components/event_card.html` u delších názvů akcí nezalamuje na další řádek — text přeteče šířku karty a je oříznutý/nezobrazený. Přidat v `theme/static/css/components.css` k pravidlu `[class*="card-"] > * > h3` zalamování (`overflow-wrap: anywhere;` nebo `word-break: break-word;`, případně `hyphens: auto;` s `lang="cs"`), aby dlouhé nadpisy korektně zalomily a zůstaly celé čitelné.

- **Maximální šířka karty akce na desktopu.** Když v řadě kalendáře (např. týdenní skupina) je jen jedna akce, karta `aesthetic-card` (viz `theme/templates/components/event_card.html` a `theme/static/css/components.css`) se na desktopu roztáhne přes celou šířku flex/grid kontejneru a působí nepřiměřeně velká. Nastavit `max-width: 45vw` (případně `max-width: min(45vw, …)`) na desktopových breakpointech tak, aby karta neměla nikdy víc než 45 % šířky viewportu. Mobilní layout zachovat beze změny.

- **UX karet kalendáře na mobilu.** Aktuální horizontální scrollovací řádek karet akcí nahradit „tinder-like" swipe zážitkem: jedna karta na viewport s drobným náznakem následující karty po straně, snap-scroll, vertikální orientace karty. Cílem je výrazně zlepšit čitelnost a ovladatelnost na mobilních zařízeních.

- **Apple kalendář – odběr nefunguje.** Na [brnosaires.com](https://brnosaires.com/) v sekci *„📆 Odebírej akce do svého kalendáře"* odkaz **Apple** na macOS (kterýkoli prohlížeč) neotevře Kalendář ani nespustí odběr. Na mobilu se Kalendář sice otevře, ale odběr se nepřidá. Opravit URL/scheme (`webcal://` vs `https://`, případně správné MIME typu `text/calendar`) tak, aby fungoval jak desktop, tak mobil.

- **Tlačítka pro odběr kalendáře jsou plain links.** Odkazy *Apple*, *Google*, *Kopíruj pro ostatní* jsou v současnosti nenápadné textové odkazy a špatně se na ně klepe na mobilu. Upravit jako tři plnohodnotná tlačítka ve stylu hlavního menu (stejné velikosti, tap target ≥ 44 px, odsazení).
