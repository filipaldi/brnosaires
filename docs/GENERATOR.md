# Generátor grafiky z komponentov písma

Plán. Nič z toho ešte nie je postavené.

## Cieľ

Procedurálne generovať grafiku pre web a propagačné materiály z tých istých komponentov, z ktorých je vyskladané písmo Brnos Aires (háčik s kvapkou, oblúk, stĺp, vrchol, roh, U, C…). Komponenty sa na seba napájajú a menia hrúbku podľa optickej veľkosti.

## Rozhodnutia

- **Zdroj pravdy je `.glyphs` súbor** v repe. Ručný export sa nerobí.
- **Interpoláciu robí generátor sám** medzi mastrami a osami Smart Components, rovnako ako variabilný font.
- **Jedno jadro v JavaScripte, dva vstupy:** webové rozhranie (pre človeka) a príkazový riadok (pre agenta a pre build webu).
- **Veľkosť komponentov** je jeden spoločný rozsah (napr. 20–60 % kratšej strany formátu). Výnimky pre jednotlivé tvary až neskôr, ak budú treba.
- **Rozmery formátu zadáva používateľ:** šírka × výška, mm alebo px, pri mm DPI, spadávka. Predvoľby (A2, A3, IG, web) sú len skratky.
- **Seed:** rovnaké číslo alebo text dá vždy rovnaký výsledok.
- **Bez textúry „pseudo-písma“.**
- **Animácia až v neskoršej fáze.**
- **Na webe AVIF**, JPEG pre sociálne siete vyrobí existujúci `plugins/og_image.py`. Pre Affinity SVG, voliteľne PNG.
- **Používa zatiaľ len autor písma.** Cieľom je, aby si web pri builde generoval vlastné náhľady, pozadia a dekorácie.

## Ako to funguje

```
.glyphs ──► prevodník ──► parts.json ──► jadro ──┬─► webové rozhranie ──► SVG / PNG
 (repo alebo                                     ├─► CLI (agent) ──────► SVG / PNG / AVIF
  pretiahnutý                                    └─► build webu ───────► náhľady, pozadia
  do prehliadača)
```

### Prevodník `.glyphs` → `parts.json`

- Jeden súbor `parts.json` so všetkými komponentmi: krivky zo všetkých mastrov, osi, kotvy.
- Napísaný v JS, aby ten istý kód bežal pri builde (Node) aj v prehliadači. Webové rozhranie tak prijme `.glyphs` pretiahnutím a dá sa vyskúšať rozpracovaná verzia ešte pred commitom.
- Kotvy na napojenie (`connect_*`) dorobí autor v Glyphs. Názvy navrhneme po prvom prečítaní súboru.

### Plagát (kompozícia s výrezom)

1. Formát, spadávka, seed, rozsah veľkosti.
2. Zóny nakreslené myšou na plátne, alebo načítané zo šablóny z Affinity (SVG s vrstvami `text` a `fotky`).
3. Generátor rozmiestni komponenty okolo zón.
4. Ďalší seed = ďalší variant. Rozloženie zón sa dá uložiť a použiť pre celú sériu.

**Textová zóna:** skutočný text vysádzaný písmom Brnos Aires alebo Nunito (veľkosť, zarovnanie, riadkovanie, ligatúry, `ss01`). Pattern obteká reálne písmená.

**Fotková zóna:** fotka pretiahnutím, posun a zoom.
- *Rámik:* obdĺžnik, komponenty ho obtekajú alebo sa naň napájajú.
- *Maska:* fotka vložená do plnej hmoty veľkého komponentu.
- *Prekrytie:* vlasová linka prechádza cez fotku.

**Správanie zóny voči patternu:** prázdna / presah iba vlasovou linkou / okraj (komponent sa na zónu napojí).

**Export do Affinity:** SVG s vrstvami `pattern`, `text`, `fotky`, `spadavka`. Text ako upraviteľný alebo v krivkách.

### Vzor (dlaždice)

Komponenty v mriežke, otáčané a zrkadlené, napojené cez kotvy.

### Web

- **Náhľady akcií:** editor si vyberie, či akcia dostane fotku alebo vygenerovaný pattern. Pri patterne je seed slug akcie, takže obrázok je stály.
- **Pozadia a dekorácie stránok.**
- Build potrebuje Node v `.github/workflows/deploy.yml`.

## Fázy

| # | Výsledok | Odhad |
|---|---|---|
| 1 | Prevodník `.glyphs` → `parts.json`, prehliadač komponentov s posuvníkmi osí | 1 sedenie |
| 2 | Plagát: formát, seed, rozsah veľkosti, optická veľkosť, export SVG/PNG | 1 sedenie |
| 3 | Zóny: text so sadzbou, fotka (rámik + maska), šablóna z Affinity | 1–2 sedenia |
| 4 | Vzor napojený cez kotvy | 1–2 sedenia |
| 5 | CLI a build webu: náhľady akcií, pozadia | 1 sedenie |
| 6 | Animácia a export videa | neskôr |

## Otvorené otázky

- Je zdroj `.glyphs` alebo `.glyphspackage`? Balík je priečinok a pretiahnutie do prehliadača ho spracuje inak.
- Názvy kotiev (po fáze 1).
- Na ktorých stránkach budú pozadia a dekorácie.
- Adresa webového rozhrania (skrytá, `noindex`).
- Overiť, ako Affinity načíta SVG masku, pred prvým ostrým plagátom.
