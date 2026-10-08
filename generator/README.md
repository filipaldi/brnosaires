# Generátor tvarov Brnos Aires — fáza 1

Parametrický generátor základných tvarov písma v jazykoch SVG. Jadro je čistý
JavaScript (ES moduly, Node 22, nulové závislosti); na PNG slúži headless
Chromium cez Playwright z globálnych `node_modules`, ak je nainštalovaný.

Geometria sa počíta v dielikoch (1 dielik = 1 jednotka, 1 dielik ≈ výška
x-height písma). Osi **Weight** a **Contrast** (0–100) určujú hrúbky ťahov
`heavy` a `hair`, všetky ostatné rozmery sú odvodené z nich podľa pomerov
v [`proporcie.json`](./proporcie.json) — tam sa ladia proporcie tvarov,
predvolené parametre aj mapa referenčných glifov.

## Príkazy

Zoznam typov tvarov a ich parametrov:

```sh
node generator/cli.js typy
```

Jeden tvar do tesne orezaného SVG (1 dielik = 100 px, okraj 0,25 dielika):

```sh
node generator/cli.js tvar --typ oblouk --weight 60 --contrast 80 --out /tmp/oblouk.svg
```

Vzorkovník — mriežka typov × Weight, voliteľne so značením spojov
(`--spoje`) a PNG (`--png`):

```sh
node generator/cli.js vzorkovnik --spoje --out /tmp/vzorkovnik.svg --png
```

Bez `--png` stačí Node; pri `--png` sa hľadá Playwright v globálnych
`node_modules` (`npm root -g`) a prehliadač v `PLAYWRIGHT_BROWSERS_PATH`.
Chýbajúci Playwright alebo Chromium nezhavaruje beh — SVG sa zapíše vždy.

## Testy

```sh
cd generator && npm test
```

Výstup je deterministický: rovnaké vstupy dávajú bajtovo rovnaké SVG.
