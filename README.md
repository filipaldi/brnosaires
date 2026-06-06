# Brnos Aires — web

## Co chceš udělat?

| Chci… | Jdi sem |
|---|---|
| **Upravit** existující akci/lekci (datum, čas, cenu) | Najdi soubor → [content/events/](content/events/) (jednorázové) nebo [content/events/classes/](content/events/classes/) (pravidelné lekce). Co měnit a na co bacha → [Přidat a upravit akci](docs/PRIDAT-AKCIU.md#upravit-existující-akci). |
| **Přidat** milongu, workshop nebo jednorázovou akci | [Přidat a upravit akci](docs/PRIDAT-AKCIU.md) — postup za 5 minut. |
| **Přidat / upravit pravidelnou lekci** (každý týden / měsíc) | [Pravidelná lekce přes `recurrence:`](docs/PRIDAT-AKCIU.md#pravidelná-lekce-přes-recurrence) — jeden soubor, ne dvanáct. |
| Přidat termín do **série** (Milonga u Draka, Tango & Pizza) | [Série](docs/SERIE.md). |
| Upravit běžnou **stránku** (o nás, milongy, lekce, FAQ) | [content/pages/](content/pages/) — viz tabulka „Nejčastěji upravované stránky" níže. |
| Napsat **anglickou** verzi stránky | [Anglická verze](docs/ANGLICKA-VERZIA.md). |
| Něco jiného (oznámení, pikoška, obrázky, navigace…) | Tabulka [Kam co patří](#rychlé-odkazy-do-obsahu-pro-editory) níže. |

Vývojář (build, struktura, nasazení)? Skoč na [Pracovní postup pro vývojáře](#pracovní-postup-pro-vývojáře-ve-zkratce).

---

Statický web argentinského tanga v Brně, postavený na [Pelicanu](https://getpelican.com/). Detaily žijí v dokumentech v [docs/](docs/); tahle stránka je rozcestník.

## Rychlé odkazy do obsahu (pro editory)

| Co potřebuješ | Kam jít |
|---|---|
| Akce v roce 2026 | [content/events/2026/](content/events/2026/) |
| Opakující se lekce | [content/events/classes/](content/events/classes/) |
| Stránky webu | [content/pages/](content/pages/) |
| Huby pravidelných sérií (Milonga u Draka, Tango & Pizza…) | [content/pages/series/](content/pages/series/) |
| Stránky konkrétních akcí (Tango víkend, Tango léto…) | [content/pages/events/](content/pages/events/) |
| Marathon (anglicky, samostatný sub-web) | [content/pages/marathon/](content/pages/marathon/) |
| Oznámení | [content/announcements/](content/announcements/) |
| Pikošky | [content/curiosities/](content/curiosities/) |
| Osoby (DJ, lektoři) | [content/people/](content/people/) |
| Obrázky | [content/images/](content/images/) |
| Navigace v hlavičce a patičce | [content/navigation/](content/navigation/) |
| Soubory pro AI asistenty (`/llms.txt`) | [content/llm/](content/llm/) |

**Nejčastěji upravované stránky:**

| Stránka | Soubor |
|---|---|
| Milongy v Brně | [content/pages/milongy.md](content/pages/milongy.md) |
| Kalendář | [content/pages/kalendar.md](content/pages/kalendar.md) |
| Lekce | [content/pages/lekce.md](content/pages/lekce.md) |
| O nás | [content/pages/o-nas.md](content/pages/o-nas.md) |
| Pikošky (přehled) | [content/pages/pikosky.md](content/pages/pikosky.md) |

## Dokumentace

Všechny dokumenty jsou česky. Editorské nahoře, vývojářské pod čarou:

| Dokument | Pro koho | O čem to je |
|---|---|---|
| [Přidat akci](docs/PRIDAT-AKCIU.md) | Editoři | **Nejčastější úkol.** Přidat milongu/workshop/lekci za 5 minut: zkopíruj hlavičku, pojmenuj soubor, vyplň pole, commitni. Na konci „Akce se neobjavila? Pět důvodů". |
| [Pole v hlavičce](docs/EDITING.md) | Editoři | Referenční přehled všech metadat (frontmatteru) a co se kde zobrazí. Slovník polí pro detail. |
| [Série](docs/SERIE.md) | Editoři | Pravidelné série (Milonga u Draka, Tango & Pizza): série vs hub, přidat instanci, založit sérii. |
| [Měsíční stránky](docs/MESACNE-STRANKY.md) | Editoři | Měsíční přehledy milong (`/milongy-brno-kveten/` …), co (ne)měnit. |
| [Anglická verze](docs/ANGLICKA-VERZIA.md) | Editoři | `.en.md` sourozenci stránek, navigace per-jazyk, `translate: false`. |
| [Widget systém](docs/WIDGETS.md) | Editoři + vývojáři | Tagy `<widget-*>` v těle markdownu: `<widget-calendar>`, `<widget-calendar-link>`, `<widget-articles>`. Atributy, filtry, příklady. |
| [SEO + sociální kartičky](docs/SEO.md) | Vývojáři | *Proč* je web takhle poskládaný: kanonická URL strategie, `<base href>`, JSON-LD, anglická verze a `hreflang`, evergreen měsíční stránky, mechanika hubů. |
| [Discoverability pro LLM](docs/LLMS.md) | Vývojáři | Generování `/llms.txt`, `/llms-full.txt` a `.md` zrcadel pro AI asistenty. |
| [Nastavení vývojového prostředí](docs/setup.md) | Vývojáři | Příprava lokálního prostředí (Python, virtualenv, závislosti, struktura projektu). |
| [Lokální testování](docs/local-testing.md) | Vývojáři | Spuštění lokálního serveru, port 41234, náhled na telefonu, ladění buildu, testování widgetů a šablon. |
| [Nasazení](docs/publishing.md) | Vývojáři | Jak se web nasazuje (GitHub Actions → GitHub Pages, automatický build dvakrát denně). |

## Pracovní postup pro editory (ve zkratce)

1. Najdi nebo vytvoř soubor ve správné složce (viz tabulka výše).
2. Vyplň hlavičku (frontmatter) a tělo. Akci provede krok za krokem [Přidat akci](docs/PRIDAT-AKCIU.md); slovník všech polí je v [Pole v hlavičce](docs/EDITING.md); widgety (`<widget-*>`) v [Widget systém](docs/WIDGETS.md).
3. Commitni. Web se sestaví automaticky dvakrát denně (06:00 a 18:00 UTC); potřebuješ rychleji, vyžádej si ruční build u vývojáře.

**Soubor můžeš upravit dvěma způsoby:**

- **Přes GitHub web UI** — stačí prohlížeč a GitHub účet. Otevři soubor v repu, klikni na tužku (✏️), uprav, dole napiš krátký commit message, klikni „Commit changes". Vhodné pro krátké textové úpravy.
- **Přes [GitHub Desktop](https://desktop.github.com/)** — naklonuj repo do počítače, edituj v libovolném textovém editoru, v GitHub Desktopu commitni a klikni „Push origin". Vhodné pro nahrávání obrázků a více souborů najednou.

## Pracovní postup pro vývojáře (ve zkratce)

```bash
source venv/bin/activate
pelican content -s pelicanconf.py                # build → output/
pelican --listen --port 41234                    # serve output/ (v druhém terminálu, NE --autoreload)
```

Workflow je „build manuálně, prohlížeč ručně refreshni" — žádný autoreload. Podrobnosti, telefoní náhled a řešení problémů: [Lokální testování](docs/local-testing.md). Konfigurace prostředí: [Nastavení vývojového prostředí](docs/setup.md).

## Struktura projektu (vysoká úroveň)

```
content/        # obsah (markdown)
theme/          # Pelican šablona — templates/ + static/
plugins/        # vlastní pluginy (calendarium, recurring_events, widget_processor, i18n_fallback, ...)
docs/           # tahle dokumentace
pelicanconf.py  # konfigurace pro dev (RELATIVE_URLS=True)
publishconf.py  # konfigurace pro produkci (SITEURL = "https://brnosaires.com")
.github/workflows/deploy.yml   # CI: build + deploy na GitHub Pages
```

Pro snadnější otevírání: [content/](content/), [theme/](theme/), [plugins/](plugins/), [docs/](docs/), [pelicanconf.py](pelicanconf.py), [publishconf.py](publishconf.py), [.github/workflows/deploy.yml](.github/workflows/deploy.yml).

Detail jednotlivých složek a souborů: [Nastavení vývojového prostředí](docs/setup.md) a [SEO + sociální kartičky](docs/SEO.md).

## Jak přispět

Nápady, chyby a plán rozvoje se vedou v **GitHub Issues**. Kdokoli s GitHub účtem může otevřít nový issue nebo komentovat existující.

- **Kanban board:** [Brnos Aires - Plán rozvoje](https://github.com/users/filipaldi/projects/2) - sloupce *Nápady* / *Pracuje se* / *Hotovo*.
- **Seznam issues:** [github.com/filipaldi/brnosaires/issues](https://github.com/filipaldi/brnosaires/issues)
- **Nový nápad / bug:** [otevřít issue](https://github.com/filipaldi/brnosaires/issues/new)

## Související

- **Návod pro Claude Code agenty:** [.claude/CLAUDE.md](.claude/CLAUDE.md) (jen pro vývojáře pracující s agenty)
