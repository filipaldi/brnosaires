# Plán rozvoje

Plánované funkce, známé problémy a úklidové úkoly pro web Brnos Aires. Položky jsou seskupeny podle typu; každá odkazuje zpět na zdroj, ze kterého vychází.

---

## Plánované funkce

- [ ] **Anglická lokalizace nadpisů ve widgetech.** Nadpisy skupin ve widgetech (např. *„Týden od 3.2. do 9.2. 2026"*) jsou dnes pouze česky. Podle [docs/WIDGETS.md:177](WIDGETS.md#L177) lze angličtinu doplnit nastavením `DEFAULT_LANG = "en"` a úpravou šablony, aby tuto hodnotu používala.

- [ ] **Automatické kontroly před publikací.** Dnešní deploy workflow (`.github/workflows/deploy.yml`) buildne a nasadí web bez dalších kontrol. Doplnit CI job, který poběží při každém pushi / PR: sestaví web s `publishconf.py`, ověří frontmatter akcí (povinná a parsovatelná pole `date` a `event-start`) a zkontroluje odkazy ve složce `output/`.

- [ ] **Dokončit LLM / SEO vrstvu.** Commity [ecfcf62](../../../commit/ecfcf62) (stránka LLM Info) a [f73dcfd](../../../commit/f73dcfd) (robots) jsou prvními kroky. Chybí pravděpodobně: strukturovaná data JSON-LD `Event` na stránkách akcí, ověřený `sitemap.xml`, Open Graph / Twitter card metadata v šablonách akcí a stránek a audit kanonických URL.

---

## Známé problémy

- [ ] **Zastaralá syntaxe widgetů v dokumentaci lokálního testování.** [docs/local-testing.md:94](local-testing.md#L94) stále uvádí `<div data-widget="calendar" data-filter="milonga">`, ale [docs/WIDGETS.md:93](WIDGETS.md#L93) uvádí, že widgety používají formu tagu `<widget-*>` bez prefixu `data-`. Uvedený příklad se nevyrenderuje.

- [ ] **README.md je pouze česky, `docs/*.md` pouze anglicky.** Rozhodnout jazykovou politiku (dvojjazyčná dokumentace? angličtina pro vývojáře, čeština pro editory?) a sjednotit ji.

- [ ] **Nepřesný strom obsahu v setup dokumentaci.** [docs/setup.md:63](setup.md#L63) uvádí `classes/` jako složku na nejvyšší úrovni `content/`, ale lekce jsou ve skutečnosti v `content/events/classes/` (viz `pelicanconf.py` a `.claude/CLAUDE.md`).
