# Lokální testování

## Obsah

- [Vývojový server](#vývojový-server)
- [Build příkazy](#build-příkazy)
- [Testování widgetů](#testování-widgetů)
- [Testování metadat akce](#testování-metadat-akce)
- [Testování změn šablon](#testování-změn-šablon)
- [Debugování](#debugování)
- [Testování v prohlížečích](#testování-v-prohlížečích)
- [Testování výkonu](#testování-výkonu)
- [Validace obsahu](#validace-obsahu)
- [Automatizované testování](#automatizované-testování)
- [Checklist před nasazením](#checklist-před-nasazením)
- [Související dokumenty](#související-dokumenty)

## Vývojový server

### Pracovní postup: builduj ručně, servíruj staticky — žádný `--autoreload`

**Nepoužíváme `--autoreload`.** Web si přebuilduješ sám pomocí `pelican content` pokaždé, když změníš obsah, šablonu nebo nastavení, a pak v prohlížeči uděláš hard-reload. Server je obyčejný statický file server (`pelican --listen`) — servíruje `output/` a sám nikdy nic nepřebudovává. Je to záměr: na tomhle stroji se `--autoreload` pere se Spotlightem / Time Machine, které do `output/` neustále šahají (vznikají rozbité, částečné buildy), a hlavně chceš mít sám pod kontrolou, kdy se `output/` regeneruje — ne aby se to dělo při každém stisku klávesy. Drž se **jednoho** serveru na **jednom** portu (41234) — nezakládej jednorázové servery na jiných portech.

```bash
# Aktivuj virtualenv
source venv/bin/activate  # macOS/Linux
# nebo
venv\Scripts\activate     # Windows

# 1. Builduj web (spouštěj znovu po každé změně)
pelican content -s pelicanconf.py

# 2. V jiném shellu pusť server na output/ (nech ho běžet; NEpřebudovává)
pelican --listen --port 41234
```

Cyklus: uprav soubory → znovu spusť `pelican content -s pelicanconf.py` → hard-reload `http://localhost:41234/` (`Cmd+Shift+R`).

**Volby:**
- `--listen`: spustí statický HTTP server (servíruje `output/`, nic nepřebudovává)
- `--port 41234`: naváže na pevný, ne-defaultní port (viz „Volba portu" níže)
- (`--autoreload` schválně vynecháváme. Pokud ho někdy chceš na rychlou jednorázovou seanci, dobrá — ale zdokumentovaný a opakovatelný postup je ruční rebuild výše.)

### Volba portu — `41234`

Schválně se vyhýbáme defaultnímu portu Pelicanu 8000. Koliduje s Djangem, http-serverem, pythonovským `http.server` a desítkami dalších vývojářských nástrojů, jakmile něco z toho běží. Pevný port v neregistrovaném user-port rozsahu (30000–48000) znamená:

- Port zůstává napříč seancemi stejný, takže záložky, MCP browser taby a poznámky pořád fungují.
- Je dost vysoko nad běžnými dev defaulty, ale pod hranicí ephemeral portů OS (49152 na macOS), takže si ho OS automaticky nezabere.
- Pokud `lsof -i :41234` ukáže, že je obsazený, **přeskoč** na jiný nesousední port (např. 38765, 43210) a aktualizuj tenhle soubor plus [.claude/CLAUDE.md](../.claude/CLAUDE.md) — neber prostě další číslo v řadě.

### Otevření lokálního webu

V prohlížeči otevři: `http://localhost:41234`

### Náhled na telefonu / jiném zařízení (stejná Wi-Fi)

`localhost` funguje jen na samotném Macu. Abys web otevřel na iPhonu (nebo
jakémkoli jiném zařízení ve stejné síti), nejdřív builduj a pak pusť statický
server navázaný na **všechny** rozhraní:

```bash
source venv/bin/activate
pelican content -s pelicanconf.py                       # build (spouštěj znovu po úpravách)
pelican --listen --bind 0.0.0.0 --port 41234            # servíruj output/ na všech rozhraních (žádný autoreload)
```

Pak zjisti LAN IP Macu a otevři ji z telefonu:

```bash
ipconfig getifaddr en0   # např. 192.168.0.73  (en1 na starších Macech / Ethernetu)
```

Na telefonu (Safari): `http://<ta-ip>:41234/` — např. `http://192.168.0.73:41234/`

Poznámky:
- `pelicanconf.py` má `RELATIVE_URLS = True`, takže interní odkazy se vůči
  IP adrese vyřeší bez problému — není potřeba sahat na `SITEURL`. Na testování
  ze zařízení nepoužívej `publishconf.py` (jeho absolutní `https://brnosaires.com`
  URL by skákaly mimo web).
- Když poprvé bindneš na `0.0.0.0`, macOS může vyhodit jednorázový firewall
  dialog „povolit příchozí spojení pro Python" — povol to. (System Settings → Network → Firewall.)
- LAN IP se může změnit, když se znovu připojíš k Wi-Fi / přepneš síť — pokud
  telefon přestane načítat, spusť znovu `ipconfig getifaddr en0`.
- **Safari Web Inspector**: připoj iPhone k Macu přes USB → Safari → menu
  Develop → [tvůj iPhone] → inspektuj živou stránku (DOM/console/network).
- Pokud síť blokuje provoz mezi zařízeními (některé firemní/guest Wi-Fi),
  použij místo toho tunel: `cloudflared tunnel --url http://localhost:41234`
  (veřejná HTTPS URL, bez registrace) nebo `ngrok http 41234`.

### Zastavení serveru

V terminálu stiskni `Ctrl+C`

### Uvolnění portu (když je potřeba)

**macOS/Linux** — najdi, kdo ho drží, a pak ho zabij (běžným `kill`, ne `kill -9`; agent harness `kill -9` blokuje):
```bash
lsof -nP -iTCP:41234 -sTCP:LISTEN     # kdo poslouchá (PID + příkaz)
lsof -ti:41234 | xargs kill           # zabij podle portu
lsof -ti:41234 || echo "41234 free"   # ověř
```
Statický server je taky `pelican` proces, takže `pkill -f 'venv/bin/pelican'` funguje rovněž (ale `pkill` je v agent harnessu blokovaný — pouští ho člověk).

**Windows:**
```bash
netstat -ano | findstr :41234
taskkill /PID <PID> /F
```

## Build příkazy

### Vývojový build

```bash
pelican content -s pelicanconf.py
```

- Používá konfiguraci `pelicanconf.py`
- Generuje web do adresáře `output/`
- Relativní URL pro lokální testování

### Produkční build

```bash
pelican content -s publishconf.py
```

- Používá konfiguraci `publishconf.py`
- Absolutní URL pro produkci
- Stejný výstupní adresář

### Clean build

```bash
# Nejdřív smaž výstupní adresář, pak builduj
rm -rf output/   # macOS/Linux  (rmdir /s output na Windows)
pelican content -s pelicanconf.py
```

Nebo použij vestavěný clean od Pelicanu:
```bash
pelican content -s pelicanconf.py --delete-output-directory
```

> **Pozor (agent harness):** `rm -rf`, `rmdir` a `--delete-output-directory` (slovo „delete") jsou blokované dangerous-command hookem — spouští je člověk. A taky: pokud se `output/` znovu objevuje hned po smazání, něco pořád běží a buildí — skoro vždycky to bývá zaběhnutý `pelican --autoreload` (přesně proto ho nepoužíváme) nebo náhledový server editoru. Najdi ho přes `ps aux | grep pelican | grep -v grep` a `lsof -ti:41234`.

## Testování widgetů

### 1. Vytvoř testovací stránku

Vytvoř `content/pages/test-widgets.md`:

```markdown
---
title: Widget Test
slug: test-widgets
---

## Calendar (events)

<widget-calendar filter_by_type="milonga" days="14"></widget-calendar>

```

### 2. Otevři testovací stránku

Přejdi na: `http://localhost:41234/test-widgets.html`

### 3. Ověř widgety

- Zkontroluj, že filtrované akce se zobrazují
- Otestuj různé atributy widgetů

## Testování metadat akce

### 1. Vytvoř testovací akci

Vytvoř `content/events/test-event.md`:

```markdown
---
title: Test Event
date: 2026-01-17 18:00:00
event-start: 2026-01-17 18:00:00
event-end: 2026-01-17 22:30:00
slug: test-event
---

This is a test event.
```

### 2. Ověř zobrazení akce

- Zkontroluj, že se akce zobrazuje ve filtrovaných seznamech
- Ověř, že se data zobrazují správně

### 3. Otestuj přístup k metadatům

Dočasně přidej do šablon debug výstup:

```jinja2
{{ event.metadata }}
{{ event.start }}
{{ event.metadata.get('event-start') }}
```

## Testování změn šablon

### 1. Uprav šablonu

Změň šablonu v [`theme/templates/`](../theme/templates/)

### 2. Builduj

Znovu spusť `pelican content -s pelicanconf.py` (nepoužíváme `--autoreload` — viz [poznámku k pracovnímu postupu](#pracovni-postup-builduj-rucne-serviruj-staticky--zadny---autoreload) nahoře). Sleduj výstup tohoto příkazu kvůli chybám v šablonách.

### 3. Refresh prohlížeče

Hard refresh: `Cmd+Shift+R` (macOS) nebo `Ctrl+Shift+R` (Windows)

### 4. Kontrola chyb

Ve výstupu `pelican content` sleduj:
- Syntaktické chyby v šablonách
- Chybějící proměnné
- Import chyby

## Debugování

### Zapnutí debug výstupu

Přidej do [`pelicanconf.py`](../pelicanconf.py):

```python
DEBUG = True
```

### Kontrola kontextu šablon

Přidej do šablony debug blok:

```jinja2
{% if DEBUG %}
  <pre>{{ articles | list | length }} articles</pre>
  <pre>{{ pages | list | length }} pages</pre>
{% endif %}
```

### Prohlížení vygenerovaného HTML

1. Builduj web: `pelican content -s pelicanconf.py`
2. Otevři adresář `output/`
3. Prohlédni si vygenerované HTML soubory
4. Zkontroluj developer tools v prohlížeči

### Časté problémy

**Widgety se nerenderují:**
- Zkontroluj, že se `process_widgets()` volá v `page.html`
- Ověř, že syntaxe widgetu odpovídá [Widget systém](WIDGETS.md)
- Sleduj terminál kvůli chybám v šablonách

**Akce se nezobrazují:**
- Ověř, že akce jsou v [`content/events/`](../content/events/)
- Zkontroluj formát metadat `event-start`
- Ověř, že `ARTICLE_PATHS` obsahuje `"events"`

**Problémy se zobrazením dat:**
- Zkontroluj formát metadat: `YYYY-MM-DD HH:MM:SS`
- Ověř přístup k datetime objektu
- Otestuj přes `{{ event.metadata.get('event-start') }}`

## Testování v prohlížečích

### Otestuj ve více prohlížečích

- Chrome/Edge
- Firefox
- Safari
- Mobilní prohlížeče (responzivní design)

### Kontrola console

Otevři developer tools v prohlížeči:
- Sleduj JavaScriptové chyby
- Ověř načítání CSS
- Zkontroluj síťové requesty

### Responzivní testování

- Otestuj různé velikosti obrazovky
- Použij device emulation v dev tools prohlížeče
- Otestuj na skutečných mobilních zařízeních — viz [Náhled na telefonu / jiném zařízení](#nahled-na-telefonu--jinem-zarizeni-stejna-wi-fi) výše, recept s `--bind 0.0.0.0`

## Testování výkonu

### Doba buildu

Změř dobu buildu:
```bash
time pelican content -s pelicanconf.py
```

### Velikosti souborů

Zkontroluj velikost výstupního adresáře:
```bash
du -sh output/
```

### Načítání stránek

Použij dev tools prohlížeče:
- Záložka Network pro časy načítání
- Záložka Performance pro renderování
- Lighthouse pro audit

## Validace obsahu

### Validace Markdownu

Zkontroluj syntaxi markdownu:
- Formát frontmatteru
- Syntaxi odkazů
- Cesty k obrázkům

### Validace metadat

Ověř metadata akcí:
- Povinná pole jsou vyplněná
- Formát data je správný
- Slug má platný tvar

### Kontrola odkazů

- Interní odkazy fungují
- Externí odkazy jsou platné
- Obrázky se načítají správně

## Automatizované testování

### Build skript

Vytvoř `test-build.sh`:

```bash
#!/bin/bash
set -e

echo "Building site..."
pelican content -s pelicanconf.py

echo "Checking for errors..."
if [ $? -eq 0 ]; then
    echo "Build successful!"
else
    echo "Build failed!"
    exit 1
fi
```

### Spuštění testů

```bash
chmod +x test-build.sh
./test-build.sh
```

## Checklist před nasazením

Před publikací ověř:

- [ ] Web se builduje bez chyb
- [ ] Všechny widgety se renderují správně
- [ ] Akce se zobrazují se správnými daty
- [ ] Obrázky se načítají
- [ ] Odkazy fungují (interní i externí)
- [ ] Responzivní design funguje
- [ ] Žádné chyby v console
- [ ] Produkční build funguje (`publishconf.py`)

## Související dokumenty

- [EDITING.md](EDITING.md) — průvodce metadaty pro editory
- [LLMS.md](LLMS.md) — LLM endpointy a optimalizace
- [SEO.md](SEO.md) — architektura SEO a multilingual mirror
- [WIDGETS.md](WIDGETS.md) — syntaxe a chování `<widget-*>` tagů
- [publishing.md](publishing.md) — nasazení
- [setup.md](setup.md) — příprava prostředí
- [GitHub Issues](https://github.com/filipaldi/brnosaires/issues) - plán dalších kroků
- [../README.md](../README.md) — hlavní README repozitáře
