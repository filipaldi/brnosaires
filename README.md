# Brnos Aires — web

## 👋 Co chceš udělat?

| Chci… | Jdi sem |
|---|---|
| ✏️ **Upravit** existující akci nebo lekci (datum, čas, cenu) | Formulář na [/admin/](https://brnosaires.com/admin/) → **Akce**. Na co bacha → [Akce: přidat a upravit](docs/AKCE.md#upravit-existující-akci). |
| ➕ **Přidat** milongu, workshop nebo jednorázovou akci | Formulář na [/admin/](https://brnosaires.com/admin/) → **Akce** → **New**. Podrobně → [Akce: přidat a upravit](docs/AKCE.md). |
| 🔁 **Přidat / upravit pravidelnou lekci** (každý týden / měsíc) | Tentýž formulář, jen v poli **Opakování** vybereš „Každý týden". Proč jeden soubor a ne dvanáct → [Pravidelná lekce](docs/AKCE.md#pravidelná-lekce-přes-recurrence). |
| 🔗 Přidat termín do **série** (Milonga u Draka, Tango & Pizza) | [Série](docs/SERIE.md). |
| 📄 Upravit běžnou **stránku** (o nás, milongy, lekce, FAQ) | [content/pages/](content/pages/) — viz tabulka „Nejčastěji upravované stránky" níže. |
| 🌍 Napsat **anglickou** verzi stránky | [Anglická verze](docs/ANGLICKA-VERZIA.md). |
| 🔑 Dostat se poprvé do **/admin/** nebo přidat dalšího editora | [Přístup do /admin/](docs/PRISTUP.md). |
| 📦 Něco jiného (oznámení, pikoška, obrázky, navigace…) | Tabulka [Kam co patří](#kam-co-patří-méně-časté-typy) níže. |

Všechno výš se dělá ve formuláři na [/admin/](https://brnosaires.com/admin/). Poprvé tam potřebuješ přístup — [jak na to](docs/PRISTUP.md).

🛠️ Vývojář (build, struktura, nasazení)? Skoč na [Pro vývojáře](#pro-vývojáře). Soubory jde upravovat i ručně v repozitáři, ale je to cesta pro vývojáře: formulář hlídá tvar hlavičky a jméno souboru, ruční zápis nehlídá nic.

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

- **Co se dělá teď:** tři [připnuté issues](https://github.com/filipaldi/brnosaires/issues) nahoře v seznamu, plus [aktuální milestone](https://github.com/filipaldi/brnosaires/milestones). Zbytek pořadí nemá schválně — proč, viz [AGENTS.md](AGENTS.md#planning-what-gets-worked-on-next).
- **Seznam issues:** [github.com/filipaldi/brnosaires/issues](https://github.com/filipaldi/brnosaires/issues)
- **Nový nápad / bug:** [otevřít issue](https://github.com/filipaldi/brnosaires/issues/new)

## 🔗 Související

- **Návod pro Claude Code agenty:** [.claude/CLAUDE.md](.claude/CLAUDE.md) (jen pro vývojáře pracující s agenty)
