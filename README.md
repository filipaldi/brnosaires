# Brnos Aires — web

## 👋 Co chceš udělat?

| Chci… | Jdi sem |
|---|---|
| ✏️ **Upravit** existující akci/lekci (datum, čas, cenu) | Nejjednodušeji ve formuláři na [/admin/](https://brnosaires.com/admin/) → **Akce**. Ručně: [content/events/RRRR/MM/](content/events/) podle měsíce konání. Co měnit a na co bacha → [Akce: přidat a upravit](docs/AKCE.md#upravit-existující-akci). |
| ➕ **Přidat** milongu, workshop nebo jednorázovou akci | [Akce: přidat a upravit](docs/AKCE.md) — postup za 5 minut. |
| 🔁 **Přidat / upravit pravidelnou lekci** (každý týden / měsíc) | [Pravidelná lekce přes `recurrence:`](docs/AKCE.md#pravidelná-lekce-přes-recurrence) — jeden soubor, ne dvanáct. |
| 🔗 Přidat termín do **série** (Milonga u Draka, Tango & Pizza) | [Série](docs/SERIE.md). |
| 📄 Upravit běžnou **stránku** (o nás, milongy, lekce, FAQ) | [content/pages/](content/pages/) — viz tabulka „Nejčastěji upravované stránky" níže. |
| 🌍 Napsat **anglickou** verzi stránky | [Anglická verze](docs/ANGLICKA-VERZIA.md). |
| 🔑 Dostat se poprvé do **/admin/** nebo přidat dalšího editora | [Přístup do /admin/](docs/PRISTUP.md). |
| 📦 Něco jiného (oznámení, pikoška, obrázky, navigace…) | Tabulka [Kam co patří](#kam-co-patří-méně-časté-typy) níže. |

🛠️ Vývojář (build, struktura, nasazení)? Skoč na [Pro vývojáře](#pro-vývojáře).

---

Statický web argentinského tanga v Brně, postavený na [Pelicanu](https://getpelican.com/). Detaily žijí v dokumentech v [docs/](docs/); tahle stránka je rozcestník.

## Kam co patří (méně časté typy) 🗂️

Časté úkoly řeší rozcestník nahoře. Tady je zbytek:

| Co potřebuješ | Kam jít |
|---|---|
| 📢 Oznámení | [content/announcements/](content/announcements/) |
| ✨ Pikošky | [content/curiosities/](content/curiosities/) |
| 🕺 Osoby (DJ, lektoři) | [content/people/](content/people/) |
| 🖼️ Obrázky | [content/images/](content/images/) |
| 🧭 Navigace v hlavičce a patičce | [content/navigation/](content/navigation/) |
| 🌐 Marathon (anglicky, samostatný sub-web) | [content/pages/marathon/](content/pages/marathon/) |
| 🤖 Soubory pro AI asistenty (`/llms.txt`) | [content/llm/](content/llm/) |

**📄 Nejčastěji upravované stránky:**

| Stránka | Soubor |
|---|---|
| Milongy v Brně | [content/pages/milongy.md](content/pages/milongy.md) |
| Kalendář | [content/pages/kalendar.md](content/pages/kalendar.md) |
| Lekce | [content/pages/lekce.md](content/pages/lekce.md) |
| O nás | [content/pages/o-nas.md](content/pages/o-nas.md) |
| Pikošky (přehled) | [content/pages/pikosky.md](content/pages/pikosky.md) |

## Pro vývojáře 🛠️

```bash
source venv/bin/activate
pelican content -s pelicanconf.py                # build → output/
pelican --listen --port 41234                    # serve output/ (v druhém terminálu, NE --autoreload)
```

Workflow je „build manuálně, prohlížeč ručně refreshni" — žádný autoreload.

| Dokument | O čem to je |
|---|---|
| [Nastavení prostředí](docs/setup.md) | Python, virtualenv, závislosti, struktura projektu. |
| [Lokální testování](docs/local-testing.md) | Lokální server, port 41234, náhled na telefonu, ladění buildu. |
| [Nasazení](docs/publishing.md) | GitHub Actions → GitHub Pages, automatický build dvakrát denně. |
| [SEO + sociální kartičky](docs/SEO.md) | *Proč* je web takhle poskládaný: kanonická URL, `<base href>`, JSON-LD, `hreflang`, mechanika hubů. |
| [Discoverability pro LLM](docs/LLMS.md) | Generování `/llms.txt`, `/llms-full.txt` a `.md` zrcadel. |
| [Widget systém](docs/WIDGETS.md) | Tagy `<widget-*>` v těle markdownu (kalendář, seznam akcí). Pro editory i vývojáře. |

## 💡 Jak přispět

Nápady, chyby a plán rozvoje se vedou v **GitHub Issues**. Kdokoli s GitHub účtem může otevřít nový issue nebo komentovat existující.

- **Kanban board:** [Brnos Aires - Plán rozvoje](https://github.com/users/filipaldi/projects/2) - sloupce *Nápady* / *Pracuje se* / *Hotovo*.
- **Seznam issues:** [github.com/filipaldi/brnosaires/issues](https://github.com/filipaldi/brnosaires/issues)
- **Nový nápad / bug:** [otevřít issue](https://github.com/filipaldi/brnosaires/issues/new)

## 🔗 Související

- **Návod pro Claude Code agenty:** [.claude/CLAUDE.md](.claude/CLAUDE.md) (jen pro vývojáře pracující s agenty)
