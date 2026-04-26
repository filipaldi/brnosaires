# Plán rozvoje

Plánované funkce, známé problémy a úklidové úkoly pro web Brnos Aires. Položky jsou seskupeny podle typu; každá odkazuje zpět na zdroj, ze kterého vychází.

---

## Plánované funkce

- [ ] **Anglická lokalizace nadpisů ve widgetech.** Nadpisy skupin ve widgetech (např. *„Týden od 3.2. do 9.2. 2026"*) jsou dnes pouze česky. Podle [docs/WIDGETS.md:177](WIDGETS.md#L177) lze angličtinu doplnit nastavením `DEFAULT_LANG = "en"` a úpravou šablony, aby tuto hodnotu používala.

- [ ] **Automatické kontroly před publikací.** [docs/publishing.md:8-18](publishing.md#L8-L18) definuje ruční checklist před nasazením (widgety se renderují, metadata akcí jsou validní, odkazy fungují atd.). Nahradit CI jobem, který poběží při každém pushi: sestaví web s `publishconf.py`, ověří frontmatter akcí (povinná a parsovatelná pole `date` a `event-start`) a zkontroluje odkazy ve složce `output/`.

---

## Známé problémy

- [ ] **Zastaralá syntaxe widgetů v dokumentaci lokálního testování.** [docs/local-testing.md:94](local-testing.md#L94) stále uvádí `<div data-widget="calendar" data-filter="milonga">`, ale [docs/WIDGETS.md:93](WIDGETS.md#L93) uvádí, že widgety používají formu tagu `<widget-*>` bez prefixu `data-`. Uvedený příklad se nevyrenderuje.

- [ ] **Průvodce publikací popisuje špatný způsob nasazení.** [docs/publishing.md](publishing.md) popisuje postupy přes FTP/SFTP, rsync a Netlify. Skutečné produkční nasazení probíhá přes GitHub Actions → GitHub Pages pomocí `.github/workflows/deploy.yml`. Dokumentaci přepsat tak, aby odpovídala realitě.

- [ ] **README.md je pouze česky, `docs/*.md` pouze anglicky.** Rozhodnout jazykovou politiku (dvojjazyčná dokumentace? angličtina pro vývojáře, čeština pro editory?) a sjednotit ji.

- [ ] **Nepřesný strom obsahu v setup dokumentaci.** [docs/setup.md:63](setup.md#L63) uvádí `classes/` jako složku na nejvyšší úrovni `content/`, ale lekce jsou ve skutečnosti v `content/events/classes/` (viz `pelicanconf.py` a `.claude/CLAUDE.md`).

---

## Úklid

- [ ] **Prázdné adresáře `migration-scripts/converters/` a `migration-scripts/utils/`.** Zbytky po migraci z Notionu. Buď skripty obnovit, přidat README vysvětlující, proč jsou prázdné, nebo adresáře smazat.

- [ ] **Dočasné soubory v kořeni projektu.** `test_workshop.html`, `event-detail.png` a složka `.playwright-mcp/` se objevují v `git status`. Přidat do `.gitignore` nebo odstranit.

- [ ] **Úklid `.DS_Store`.** Smazání `theme/static/.DS_Store` a `theme/static/fonts/.DS_Store` leží v pracovním stromu nestagované. Odstranění commitnout a přidat `.DS_Store` do `.gitignore`, pokud tam ještě není.
