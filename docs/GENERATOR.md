# Generátor grafiky z komponentov písma

Plán. Nič z toho ešte nie je postavené.

## Cieľ

Procedurálne generovať grafiku pre web a propagačné materiály z tých istých tvarov, z ktorých je vyskladané písmo Brnos Aires. Tvary sa na seba napájajú a menia hrúbku podľa optickej veľkosti.

## Rozhodnutia

- **Tvary sú parametrická geometria v kóde**, nie krivky z Glyphs. Dajú sa natiahnuť na ľubovoľnú dĺžku a šírku bez deformácie zaoblení a kvapiek.
- **Proporcie v jednom súbore** (`proporcie.json`): polomery, kontrast, uhly, pomery kvapky. Ak sa zmení písmo, upravia sa tu čísla.
- **Hrúbka je parameter.** Optická veľkosť je vzorec: čím väčší tvar vo výsledku, tým tenšia vlasová linka voči plnej hmote.
- **Jedno jadro v JavaScripte, dva vstupy:** webové rozhranie (pre človeka) a príkazový riadok (pre agenta a pre build webu).
- **Veľkosť tvarov** je jeden spoločný rozsah (napr. 20–60 % kratšej strany formátu). Výnimky pre jednotlivé typy až neskôr, ak budú treba.
- **Rozmery formátu zadáva používateľ:** šírka × výška, mm alebo px, pri mm DPI, spadávka. Predvoľby (A2, A3, IG, web) sú len skratky.
- **Seed:** rovnaké číslo alebo text dá vždy rovnaký výsledok.
- **Bez textúry „pseudo-písma“.**
- **Animácia až v neskoršej fáze.**
- **Na webe AVIF**, JPEG pre sociálne siete vyrobí existujúci `plugins/og_image.py`. Pre Affinity SVG, voliteľne PNG.
- **Používa zatiaľ len autor písma.** Cieľom je, aby si web pri builde generoval vlastné náhľady, pozadia a dekorácie.

## Typy tvarov

Spoločné parametre všetkých typov: hrúbka vlasovej linky a hrúbka plnej hmoty (riadi ich optická veľkosť), otočenie o 90°, zrkadlenie.

| # | Typ | Parametre |
|---|---|---|
| 1 | Noha | dĺžka, hrúbka (vlas / plná), zaoblenie konca |
| 2 | Oblúk | šírka, výška, kontrast vlas → plná, strana plnej nohy |
| 3 | Vrchol | uhol každej nohy (aj zvislá), šírka klinu |
| 4 | Koleno | hrúbka, vonkajší a vnútorný polomer |
| 5 | Hmota so štrbinou | dĺžka, šírka, šírka štrbiny |
| 6 | Háčik s kvapkou | výška, polomer ohybu, veľkosť kvapky, hrúbka nohy (vlas / plná) |
| 7 | Nota | dĺžka a hrúbka nohy, počet kvapiek, rozostup, veľkosť kvapiek, strana |
| 8 | Kvapka | veľkosť, smer špičky |
| 9 | Kruh | priemer, hrúbka obrysu (vlas / plná) |
| 10 | Bod | priemer |

**Kvapka a prechod oblúka** z vlasovej linky do plnej nohy majú ručne ladené krivky. Ak ich geometria z kódu nepriblíži dosť verne, prenesú sa z písma presne ako krivka a parametre ich budú len posúvať a škálovať.

### Pravidlá skladania

- **Napojenie:** tvary sa dotýkajú a plynulo prechádzajú (noha + oblúk, vrchol so zvislou nohou).
- **Odsadenie:** tvar stojí nad druhým s medzerou (kruh nad nohou).

Body napojenia vyplývajú z geometrie (konce nôh, päty oblúka), netreba ich kresliť.

## Ako to funguje

```
proporcie.json ──► jadro ──┬─► webové rozhranie ──► SVG / PNG
                           ├─► CLI (agent) ──────► SVG / PNG / AVIF
                           └─► build webu ───────► náhľady, pozadia
```

### Plagát (kompozícia s výrezom)

1. Formát, spadávka, seed, rozsah veľkosti.
2. Zóny nakreslené myšou na plátne, alebo načítané zo šablóny z Affinity (SVG s vrstvami `text` a `fotky`).
3. Generátor rozmiestni tvary okolo zón.
4. Ďalší seed = ďalší variant. Rozloženie zón sa dá uložiť a použiť pre celú sériu.

**Textová zóna:** skutočný text vysádzaný písmom Brnos Aires alebo Nunito (veľkosť, zarovnanie, riadkovanie, ligatúry, `ss01`). Pattern obteká reálne písmená.

**Fotková zóna:** fotka pretiahnutím, posun a zoom.
- *Rámik:* obdĺžnik, tvary ho obtekajú alebo sa naň napájajú.
- *Maska:* fotka vložená do plnej hmoty veľkého tvaru.
- *Prekrytie:* vlasová linka prechádza cez fotku.

**Správanie zóny voči patternu:** prázdna / presah iba vlasovou linkou / okraj (tvar sa na zónu napojí).

**Export do Affinity:** SVG s vrstvami `pattern`, `text`, `fotky`, `spadavka`. Text ako upraviteľný alebo v krivkách.

### Vzor (dlaždice)

Tvary v mriežke, otáčané a zrkadlené, napojené podľa pravidiel skladania.

### Web

- **Náhľady akcií:** editor si vyberie, či akcia dostane fotku alebo vygenerovaný pattern. Pri patterne je seed slug akcie, takže obrázok je stály.
- **Pozadia a dekorácie stránok.**
- Build potrebuje Node v `.github/workflows/deploy.yml`.

## Fázy

| # | Výsledok | Odhad |
|---|---|---|
| 1 | Všetkých 10 typov v kóde, prehliadač s posuvníkmi parametrov, porovnanie s písmom | 1–2 sedenia |
| 2 | Plagát: formát, seed, rozsah veľkosti, optická veľkosť, skladanie, export SVG/PNG | 1 sedenie |
| 3 | Zóny: text so sadzbou, fotka (rámik + maska), šablóna z Affinity | 1–2 sedenia |
| 4 | Vzor (dlaždice) | 1 sedenie |
| 5 | CLI a build webu: náhľady akcií, pozadia | 1 sedenie |
| 6 | Animácia a export videa | neskôr |

## Otvorené otázky

- Na ktorých stránkach budú pozadia a dekorácie.
- Adresa webového rozhrania (skrytá, `noindex`).
- Overiť, ako Affinity načíta SVG masku, pred prvým ostrým plagátom.
