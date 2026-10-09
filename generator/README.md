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
node generator/cli.js tvar --typ polkruh --weight 60 --contrast 80 --out /tmp/polkruh.svg
```

Vzorkovník — mriežka typov × Weight, voliteľne so značením spojov
(`--spoje`), pohľadom na skladbu z primitív (`--primitivy`) a PNG (`--png`):

```sh
node generator/cli.js vzorkovnik --spoje --out /tmp/vzorkovnik.svg --png
```

`--primitivy` kreslí každý diel tvaru osobitne vo farbe svojej primitívy
(obdĺžnik, prstenec, krivka, vnútorný roh — legenda je v hlavičke listu),
polopriehľadne, takže prekryvy primitív sú viditeľné a diery sú vyseknuté
bielo.

Bez `--png` stačí Node; pri `--png` sa hľadá Playwright v globálnych
`node_modules` (`npm root -g`) a prehliadač v `PLAYWRIGHT_BROWSERS_PATH`.
Chýbajúci Playwright alebo Chromium nezhavaruje beh — SVG sa zapíše vždy.

## Testy

```sh
cd generator && npm test
```

Výstup je deterministický: rovnaké vstupy dávajú bajtovo rovnaké SVG.

## Kompozícia (fáza 2)

Rozmiestni tvary na formát okolo zón a zapíše SVG s vrstvami `pattern`,
`fotky`, `text`, `spadavka`. Zadanie je jeden JSON súbor: formát, grid,
kresba (Weight, Contrast, Zaoblenie), kompozícia, variant, inverzia, zóny.
Príklady: [`priklady/plagat-a2.json`](priklady/plagat-a2.json),
[`priklady/nahlad-akcie.json`](priklady/nahlad-akcie.json).

```sh
node generator/cli.js kompozicia --spec generator/priklady/plagat-a2.json --variant 7 --out /tmp/plagat.svg --png
```

`--variant` prepíše variant zo súboru. Rovnaký súbor a variant dajú vždy
rovnaký obrázok. Hustotu, medzery a prevod veľkosti na parametre tvarov
ladíš v `proporcie.json` v časti `kompozicia`. Každý prvok patrí do nejakej reťaze.
`kompozicia.retazenieDlzka` je [min, max] počet prvkov v jednej nakreslenej reťazi.
`kompozicia.pomery` je podiel každého typu v jednej reťazi v percentách (0 až 100,
berie sa ako podiel zo súčtu): dĺžka reťaze sa rozdelí na kvóty po typoch, napr.
reťaz s 10 prvkami a nohou na 30 % má 3 nohy. Kruh z kvóty leží vedľa reťaze, kvapka
z kvóty visí pozdĺž rovnej nohy (rovnobežne, krk zapustený). Kvapky, ktorými končí
každá čiara, sú navyše nad kvótou.
`kompozicia.velkosti` je `{ typ: [min, max] }`, rozsah veľkosti po typoch. Pri kvapke
je to jej šírka (predvolene 1–2). Starý globálny `velkost` už neexistuje (staré
zadania sa prevedú).
Typy sú noha, polkruh (Polooblúk), stvrtkruh (Štvrťoblúk), kvapka a kruh. Šiesty typ,
stvrtoblouk (Štvrťoblúk s pätkou), sa nevolí: zapne sa sám, keď má kresba kontrast,
ako prechod z tenkého do hrubého. Zaoblenie majú len nohy, oblúky nikdy. Webové
rozhranie volá to isté jadro, viď [`ui/README.md`](ui/README.md).
