# Brnos Aires — web

Statický web argentinského tanga v Brně, postavený na [Pelicanu](https://getpelican.com/). Tento dokument je **rozcestník** — najdeš tu rychlé odkazy do obsahu, mapu dokumentace a stručně, jak je projekt poskládaný. Detaily žijí v jednotlivých dokumentech v [docs/](docs/).

## Obsah

1. [Rychlé odkazy do obsahu (pro editory)](#rychlé-odkazy-do-obsahu-pro-editory)
2. [Dokumentace](#dokumentace)
3. [Pracovní postup pro editory (ve zkratce)](#pracovní-postup-pro-editory-ve-zkratce)
4. [Pracovní postup pro vývojáře (ve zkratce)](#pracovní-postup-pro-vývojáře-ve-zkratce)
5. [Struktura projektu (vysoká úroveň)](#struktura-projektu-vysoká-úroveň)
6. [Související](#související)

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

Všechny dokumenty jsou česky. Krátké shrnutí toho, kde se co dočteš:

| Dokument | Pro koho | O čem to je |
|---|---|---|
| [Úprava obsahu](docs/EDITING.md) | Editoři | **Metadata v hlavičce souboru** (frontmatter) — co napsat do `event-start`, `series:`, `preview_image`, jak fungují anglické verze (`.en.md`), jak založit hub pravidelné série, měsíční stránky milong, soubory pro AI asistenty. |
| [Widget systém](docs/WIDGETS.md) | Editoři + vývojáři | Tagy `<widget-*>` v těle markdownu: `<widget-calendar>`, `<widget-calendar-link>`, `<widget-articles>`. Atributy, filtry, příklady. |
| [SEO + sociální kartičky](docs/SEO.md) | Vývojáři | *Proč* je web takhle poskládaný: kanonická URL strategie, `<base href>`, JSON-LD, anglická verze a `hreflang`, evergreen měsíční stránky, mechanika hubů. |
| [Discoverability pro LLM](docs/LLMS.md) | Vývojáři | Generování `/llms.txt`, `/llms-full.txt` a `.md` zrcadel pro AI asistenty. |
| [Nastavení vývojového prostředí](docs/setup.md) | Vývojáři | Příprava lokálního prostředí (Python, virtualenv, závislosti, struktura projektu). |
| [Lokální testování](docs/local-testing.md) | Vývojáři | Spuštění lokálního serveru, port 41234, náhled na telefonu, ladění buildu, testování widgetů a šablon. |
| [Nasazení](docs/publishing.md) | Vývojáři | Jak se web nasazuje (GitHub Actions → GitHub Pages, automatický build dvakrát denně). |
| [Plán rozvoje](docs/ROADMAP.md) | Všichni | Plánované funkce, známé chyby, úklidové úkoly, hotové milníky. |

## Pracovní postup pro editory (ve zkratce)

1. Najdi nebo vytvoř soubor ve správné složce (viz tabulka výše).
2. Vyplň hlavičku (frontmatter) podle [Úprava obsahu](docs/EDITING.md) — povinná pole jsou `title`, `slug`, `date`, u akcí navíc `event-type`, `event-start`, `event-end`, `event-location`.
3. Napiš tělo v Markdownu. Widgety (`<widget-*>`) vlož kamkoli v těle — viz [Widget systém](docs/WIDGETS.md).
4. Commitni (přes GitHub web UI nebo GitHub Desktop). Web se sestaví automaticky dvakrát denně (06:00 a 18:00 UTC); pokud potřebuješ rychlejší aktualizaci, vyžádej si ruční build u vývojáře.

**Soubor můžeš upravit dvěma způsoby:**

- **Přes GitHub web UI** — stačí prohlížeč a GitHub účet. Otevři soubor v repu, klikni na tužku (✏️), uprav, dole napiš krátký commit message, klikni „Commit changes". Vhodné pro krátké textové úpravy.
- **Přes [GitHub Desktop](https://desktop.github.com/)** — naklonuj repo do počítače, edituj v libovolném textovém editoru, v GitHub Desktopu commitni a klikni „Push origin". Vhodné pro nahrávání obrázků a více souborů najednou.

Co je Markdown, co je frontmatter, jak se zachází se slugy a obrázky — popsáno v [Úprava obsahu](docs/EDITING.md).

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

## Související

- **Plán a hotové milníky:** [Plán rozvoje](docs/ROADMAP.md)
- **Návod pro Claude Code agenty:** [.claude/CLAUDE.md](.claude/CLAUDE.md) (jen pro vývojáře pracující s agenty)
