# Rozhranie generátora — fáza 4

Webové rozhranie generátora: hore jedna lišta, pod ňou plátno. Beží priamo
v prehliadači, bez build kroku a bez závislostí.

## Spustenie

```sh
node generator/ui/serve.js
```

Otvor `http://localhost:41235/generator/ui/`. Server servíruje koreň
repozitára, takže jadro (`/generator/core/`) aj fonty
(`/theme/static/fonts/`) sa nahrajú na tie isté adresy ako v produkcii.

## Čo kde je

| Súbor | Obsah |
|---|---|
| `serve.js` | malý statický server (port 41235) |
| `index.html`, `ui.css` | kostra stránky a štýl (čierno-biely) |
| `ui.js` | lišta, popovery, plátno, zóny, skratky, ukladanie stavu |
| `engine.js` | adapter: natiahne `core/kompozicia`, kým neexistuje, použije `stub.js` |
| `stub.js` | náhradný engine (rovnaké API, náhodné rozmiestnenie so seedom) |
| `viewer.js` | prehliadač tvarov (skratka `T`) |
| `export.js` | SVG priamo, PNG/AVIF cez canvas s vloženými fontmi |
| `smoke.mjs` | smoke test cez Playwright so štyrmi screenshotmi |

## Práca s rozhraním

- **Zóna:** potiahni po prázdnom mieste, prichytáva sa na dieliky. Začni
  písať → textová zóna; pretiahni fotku → fotková zóna. Presun ťahaním,
  veľkosť za rohy. Vybraná zóna má pod sebou lištu s parametrami.
- **Fotka:** dvojklik prepne posun a zoom (ťahaj, koliesko), ďalší dvojklik
  alebo `Esc` ukončí.
- **Skratky:** ← → variant, `R` náhodný variant, `I` inverzia, `E` export,
  `T` prehliadač tvarov, `Delete` zmaže vybranú zónu, `Esc` zavrie.
- **Predvoľba** (v ponuke formátu): uloží/načíta parametre bez variantu a
  bez zón ako JSON.

Stav sa automaticky ukladá do `localStorage`; náhodný variant tlačidlom `⟳`
je jediné miesto, kde rozhranie ťahá náhodu (engine zostáva deterministický).

## Náhradný engine

Kým nevznikne `generator/core/kompozicia/` (fáza 2), rozhranie zobrazuje v
rohu poznámku „náhradný engine“ a kreslí `stub.js`: rovnaké API
(`normalizujSpec`, `komponuj`), triviálne rozmiestnenie so seedom z variantu.
Po doplnení jadra sa prepne automaticky, bez zmeny v rozhraní.

## Smoke test

```sh
node generator/ui/smoke.mjs [adresár-pre-screenshoty]
```

Vyžaduje Playwright v globálnych `node_modules` (`npm root -g`) a Chromium v
`PLAYWRIGHT_BROWSERS_PATH`. Server si podľa potreby sám spustí a vypne.
