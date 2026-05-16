# Nastavení vývojového prostředí

## Obsah

- [Předpoklady](#předpoklady)
- [Počáteční nastavení](#počáteční-nastavení)
- [Struktura projektu](#struktura-projektu)
- [Konfigurační soubory](#konfigurační-soubory)
- [Cesty k obsahu](#cesty-k-obsahu)
- [Stránkování](#stránkování)
- [Konfigurace theme](#konfigurace-theme)
- [Proměnné prostředí](#proměnné-prostředí)
- [Ověření](#ověření)
- [Nastavení IDE](#nastavení-ide)
- [Řešení problémů](#řešení-problémů)
- [Související dokumenty](#související-dokumenty)

## Předpoklady

- Python 3.8 nebo vyšší
- pip (správce balíčků Pythonu)
- Git

## Počáteční nastavení

### 1. Naklonování repozitáře

```bash
git clone <repository-url>
cd brnos-aires-web
```

### 2. Vytvoření virtualenvu

```bash
python3 -m venv venv
```

### 3. Aktivace virtualenvu

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Instalace závislostí

```bash
pip install -r requirements.txt
```

**Závislosti:**
- `pelican[markdown]` – generátor statického webu
- `notion-client` – klient Notion API (pro migrace)
- `python-dotenv` – správa proměnných prostředí
- `requests` – HTTP knihovna
- `pytz` – podpora časových zón
- `unidecode` – práce s Unicode textem

## Struktura projektu

```
brnos-aires-web/
├── content/
│   ├── events/
│   │   ├── YYYY/MM/        # jednorázové akce
│   │   └── classes/        # pravidelné lekce
│   ├── pages/              # statické stránky včetně rozcestníků sérií a měsíčních stránek
│   ├── announcements/      # oznámení
│   ├── curiosities/        # kuriozity
│   ├── people/             # lidé
│   ├── images/             # obrázky
│   ├── llm/                # zdroj pro /llms.txt a /llms-full.txt
│   └── navigation/         # navigační menu (main.md, footer.md, marathon.md + .en.md sourozenci)
├── theme/                  # Pelican theme
│   ├── templates/          # Jinja2 šablony
│   └── static/             # CSS, JS, fonty
├── migration-scripts/      # nástroje pro migraci z Notionu
├── output/                 # vygenerovaný web (gitignored)
├── pelicanconf.py          # vývojová konfigurace
├── publishconf.py          # produkční konfigurace
└── requirements.txt        # Python závislosti
```

## Konfigurační soubory

### pelicanconf.py

Vývojová konfigurace:
- `SITEURL = ""` – prázdné pro lokální vývoj
- `RELATIVE_URLS = True` – relativní URL pro lokální testování
- `OUTPUT_PATH = "output"` – výstupní adresář buildu
- `DELETE_OUTPUT_DIRECTORY = True` – čistý build při každém spuštění

### publishconf.py

Produkční konfigurace:
- `SITEURL = "https://brnosaires.com"` – produkční URL
- `RELATIVE_URLS = False` – absolutní URL pro produkci
- Dědí všechna nastavení z [pelicanconf.py](../pelicanconf.py)

## Cesty k obsahu

Konfigurováno v [pelicanconf.py](../pelicanconf.py):

- `PAGE_PATHS = ["pages"]` – statické stránky
- `ARTICLE_PATHS = ["announcements", "events", "classes", "curiosities", "people"]` – článkový obsah
- `STATIC_PATHS = [...]` – statické soubory (obrázky atd.)

## Stránkování

Pelican automaticky stránkuje kategorie, když je v nich víc článků, než kolik povoluje limit.

### Aktuální konfigurace

- `DEFAULT_PAGINATION = 10` – zobrazuje 10 článků na stránku

### Jak to funguje

Když má kategorie víc než 10 článků, Pelican vytvoří víc stránek:

- kategorie **announcement** (72 článků): vytvoří `announcement.html`, `announcement2.html`, … `announcement8.html`
- kategorie **events** (29 článků): vytvoří `events.html`, `events2.html`, `events3.html`
- kategorie **class** (14 článků): vytvoří `class.html`, `class2.html`

Každá stránka má odkazy na předchozí/další a indikuje aktuální číslo stránky (např. „Page 1 / 3").

### Úprava stránkování

Pro změnu počtu článků na stránku uprav `DEFAULT_PAGINATION` v [pelicanconf.py](../pelicanconf.py):

```python
DEFAULT_PAGINATION = 20  # Show 20 articles per page
```

Pro úplné vypnutí stránkování kategorií:

```python
CATEGORY_PAGINATION = False
```

Pozn.: Vypnutí stránkování vytvoří jednu stránku se všemi články, což může být u velkých kategorií pomalé.

### Výstupní soubory

Stránkované kategorie se generují do `output/category/`:
- `category/announcement.html` – první stránka oznámení
- `category/announcement2.html` – druhá stránka oznámení
- `category/events.html` – první stránka událostí
- atd.

Nejde o duplikáty, ale o sekvenční stránky stejné kategorie.

## Konfigurace theme

- `THEME = "theme"` – adresář s [theme](../theme/)
- `THEME_STATIC_PATHS = ["static"]` – statické soubory theme

## Proměnné prostředí

Pokud používáš migration scripts, vytvoř soubor `.env`:

```bash
NOTION_API_KEY=your_api_key_here
```

## Ověření

### Test instalace

```bash
pelican --version
```

Měl by vypsat číslo verze Pelicanu.

### Testovací build

```bash
pelican content -s pelicanconf.py
```

Měl by vygenerovat web do adresáře `output/` bez chyb.

## Nastavení IDE

### Doporučená rozšíření

- **Markdown**: pro editaci obsahových souborů
- **Jinja2**: pro zvýrazňování syntaxe šablon
- **Python**: pro Python skripty
- **YAML**: pro syntaxi frontmatteru

### Konfigurace editoru

**VS Code:**
- Nainstaluj rozšíření „Pelican" (pokud je dostupné)
- Nastav asociace markdown souborů
- Nastav Python interpreter na `venv`

## Řešení problémů

### Problémy s virtualenvem

**Problém:** příkaz `python3` nenalezen
**Řešení:** použij `python` místo toho, nebo nainstaluj Python 3

**Problém:** příkaz `pip` nenalezen
**Řešení:** nainstaluj pip: `python -m ensurepip --upgrade`

### Problémy s instalací závislostí

**Problém:** instalace `pelican` selhává
**Řešení:**
- Aktualizuj pip: `pip install --upgrade pip`
- Nainstaluj s: `pip install pelican[markdown]`

**Problém:** chyby s oprávněními
**Řešení:** používej virtualenv (nepoužívej `sudo`)

### Konfigurační problémy

**Problém:** build selhává s chybami cest
**Řešení:**
- Ověř, že existuje adresář [content/](../content/)
- Zkontroluj, že cesty v [pelicanconf.py](../pelicanconf.py) jsou správné
- Ujisti se, že existuje adresář s [theme](../theme/)

## Související dokumenty

- [Úprava obsahu](EDITING.md) – jak editovat obsah
- [Discoverability pro LLM](LLMS.md) – LLM endpointy a mirrory
- [SEO + sociální kartičky](SEO.md) – SEO a architektura
- [Widget systém](WIDGETS.md) – systém widgetů
- [Lokální testování](local-testing.md) – běh vývojového serveru
- [Nasazení](publishing.md) – proces nasazení
- [GitHub Issues](https://github.com/filipaldi/brnosaires/issues) – plán a nápady
- [Brnos Aires — web](../README.md) – hlavní README projektu
