# Generátor grafiky z komponentov písma

Plán. Nič z toho ešte nie je postavené.

## Cieľ

Procedurálne generovať grafiku pre web a propagačné materiály z tých istých tvarov, z ktorých je vyskladané písmo Brnos Aires. Tvary sa na seba napájajú a menia hrúbku podľa toho, na čo sa grafika robí.

## Rozhodnutia

- **Tvary sú parametrická geometria v kóde**, nie krivky z Glyphs. Dajú sa natiahnuť na ľubovoľnú dĺžku a šírku bez deformácie zaoblení a kvapiek.
- **Všetko je relatívne k mriežke.** Formát má mriežku odvodenú od šírky, veľkosti a hrúbky sa merajú v dielikoch. Milimetre ani pixely v dizajnových pravidlách nie sú.
- **Hrúbku riadia dve osi, Weight a Contrast.** Samostatná optická veľkosť nie je, nastavuje sa práve týmito osami.
- **Jedno jadro v JavaScripte, dva vstupy:** webové rozhranie (pre človeka) a príkazový riadok (pre agenta a pre build webu).
- **Seed:** rovnaké nastavenie a rovnaký seed dajú vždy rovnaký výsledok.
- **Bez textúry „pseudo-písma“.**
- **Animácia až v neskoršej fáze.**
- **Na webe AVIF**, JPEG pre sociálne siete vyrobí existujúci `plugins/og_image.py`. Pre tlač a ďalšiu úpravu SVG, voliteľne PNG.
- **Používa zatiaľ len autor písma.** Cieľom je, aby si web pri builde generoval vlastné náhľady, pozadia a dekorácie.

## Parametre

Jednotka **dielik** = šírka formátu / počet stĺpcov.

### Formát

V rozhraní pod `420 × 594 mm · Grid 8 ▾`, spolu s mriežkou a predvoľbou.

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Šírka × výška | číslo + jednotka (mm / px) | Predvoľby A2, A3, IG, web sú len skratky |
| DPI | číslo | Len pri mm, pre PNG |
| Spadávka | mm | Technická, pre tlač. Na plátne je vždy jemne vyznačená. |

### Mriežka

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Grid (N stĺpcov) | celé číslo | Dielik = šírka / N, štvorcový |
| Zvyšok výšky | okraje / natiahnutie / presah a orez | Keď výška nie je násobkom dielika. Volí sa podľa potreby. |

### Kresba

V rozhraní pod `Parametre ▾`, spolu s farbami a kompozíciou.

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Weight | 0–100 % | Hrúbka plnej hmoty v % dielika. 0 % = veľa bieleho, 100 % = biele sa takmer zatvorí. |
| Contrast | 0–100 % | Vlasová linka v % plnej hmoty. 0 % = monolineárne, 100 % = najtenší vlas. |

Polomery, veľkosť kvapky a šírka štrbiny sa odvodia z Weight a Contrast. Vzorce sú v `proporcie.json`, aby sa dali doladiť podľa písma.

### Kompozícia

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Veľkosť | min–max v dielikoch | Hlavný rozmer tvaru, napr. 1–6 |
| Variácia | 0–100 % | 0 % = všetky tvary rovnako veľké, 100 % = celý rozsah |
| Rozloženie | rovnomerne / veľa malých a pár veľkých / len krajné hodnoty | Pomer malých a veľkých tvarov |
| Typy | výber z 10 typov | Ktoré tvary sa smú použiť |
| Rozmiestnenie | voľné / dlaždice | Voľné = kompozícia s výrezom, dlaždice = vzor v mriežke |

### Variant (seed)

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Seed | číslo alebo text | Z neho sa odvodí náhodné rozmiestnenie. Rovnaký seed = rovnaký obrázok. V rozhraní sa volá **Variant**. Na webe je to slug akcie. |

### Farby

Len čierna a biela.

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Inverzia | nie / áno | Nie = čierne tvary na bielom, áno = biele na čiernom |

### Zóny

Spoločné pre každú zónu:

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Typ | text / fotka | Určí sa obsahom: začneš písať = text, pretiahneš fotku = fotka |
| Poloha a veľkosť | v dielikoch | Prichytené na mriežku |
| Správanie | prázdna / presah vlasovou linkou / okraj | Ako sa k zóne správa pattern |

Textová zóna:

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Text | reťazec | Skutočný text, vysádzaný v náhľade |
| Písmo | Brnos Aires / Nunito | Ligatúry a `ss01` fungujú |
| Veľkosť písma | v dielikoch | |
| Zarovnanie | vľavo / na stred / vpravo | |
| Riadkovanie | násobok veľkosti | |

Fotková zóna:

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Fotka | súbor (pretiahnutím) | |
| Režim | rámik / maska / prekrytie | Maska = fotka v plnej hmote veľkého tvaru |
| Posun, zoom | čísla | Poloha fotky v ráme alebo maske |

### Export

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Súbor | SVG / PNG / AVIF | |
| Text | upraviteľný / krivky | Len SVG |

SVG má vrstvy `pattern`, `text`, `fotky`, `spadavka`.

### Predvoľby

Uložená kombinácia všetkých parametrov okrem seedu, napr. „plagát A2“ alebo „náhľad akcie“. Build webu používa predvoľbu.

### Technická poistka

Vlasová linka nikdy nie je tenšia ako 1 px výstupu, pri tlači 0,1 mm. Jediná absolútna hodnota, zasiahne len pri extrémoch.

## Typy tvarov

Rozmery sú v dielikoch. Hrúbky berú z Weight a Contrast, pri každom tvare sa len volí, či je časť vlasová alebo plná. Všetky typy sa dajú otočiť o 90° a zrkadliť.

Každý tvar je poskladaný z troch prvkov:

1. **Obdĺžnik** so zaoblenými rohmi.
2. **Prstenec** so stálou hrúbkou (štvrť, polkruh, celý kruh). Napája sa na obdĺžniky pozdĺž (polkruh spája dve rovnobežné nohy) alebo kolmo v rohu (plný blok priložený k jeho vonkajšej hrane, vnútorný kruh vyrezaný z bloku).
3. **Krivka** od dizajnéra, zatiaľ kvapka. Má dva mastre (krk 10 a 40 jednotiek) a interpoluje sa tak, aby krk mal hrúbku vlasovej čiary.

**Zaoblenie** je globálna os ako Weight a Contrast (0–100 %, podiel z polovice hrúbky ťahu). Zaobľuje sa každý viditeľný roh, vonkajší aj vnútorný. Ostré ostávajú len miesta, kde sa dva prvky napájajú, lebo tam roh nie je vidieť.

| # | Typ | Parametre |
|---|---|---|
| 1 | Noha | dĺžka, vlas / plná |
| 2 | Oblúk | šírka, výška, strana plnej nohy, hrubnutie (stála / plynulá) |
| 3 | Hmota so štrbinou | dĺžka |
| 4 | Háčik s kvapkou | výška, polomer ohybu, veľkosť kvapky, noha vlas / plná |
| 5 | Nota | dĺžka nohy, počet kvapiek, rozostup, veľkosť kvapiek, strana, noha vlas / plná |
| 6 | Kvapka | veľkosť |
| 7 | Kruh | priemer, obrys vlas / plný |
| 8 | Bod | priemer |

Vrchol (A) zo sady vypadol, z obdĺžnikov nevyzeral dobre. Koleno nie je samostatný typ: vzniká pri skladaní napojením hranola (nohy) na oblúk.

### Pravidlá skladania

- **Napojenie:** tvary sa dotýkajú a plynulo prechádzajú (noha + oblúk).
- **Odsadenie:** tvar stojí nad druhým s medzerou (kruh nad nohou).

Body napojenia vyplývajú z geometrie (konce nôh, päty oblúka), netreba ich kresliť.

## Ako to funguje

```
proporcie.json + predvoľby ──► jadro ──┬─► webové rozhranie ──► SVG / PNG
                                       ├─► CLI (agent) ──────► SVG / PNG / AVIF
                                       └─► build webu ───────► náhľady, pozadia
```

### Postup

1. Formát a grid, potom parametre (alebo predvoľba).
2. Zóny ťahaním na gride.
3. Generátor rozmiestni tvary okolo zón.
4. Ďalší seed = ďalší variant. Predvoľba sa dá použiť pre celú sériu.

**Rozmiestnenie dlaždice:** tvary v mriežke, otáčané a zrkadlené, napojené podľa pravidiel skladania. Zóny fungujú rovnako.

### Web

- **Náhľady akcií:** editor si vyberie, či akcia dostane fotku alebo vygenerovaný pattern. Pri patterne je seed slug akcie, takže obrázok je stály.
- **Pozadia a dekorácie stránok.**
- Build potrebuje Node v `.github/workflows/deploy.yml`.

## Rozhranie

Jedna stránka pre počítač, mobil sa nerieši. Hore jedna lišta, pod ňou plátno. Žiadne bočné panely, žiadne režimy.

```
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│ 420 × 594 mm · Grid 8 ▾     Parametre ▾          ◀ Variant 42 ▶ ⟳          75 %      Export   │
├───────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                               │
│                 ┌────────────────────────────────────────────────────────────┐                │
│                 │ · ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ · · · ◜◝ · · · · · · · ·  │                │
│                 │ · ┃ MILONGA DE OTOÑO|          ┃ · · · ▌▐ · · · · · · · ·  │                │
│                 │ · ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ · · · ▌▐ · · · · · · · ·  │                │
│                 │ · ╭─────────────────────────────────────╮ · · · · · · ·    │                │
│                 │ · │ Brnos A. ▾ 1,5 ▾ ⫷ ≡ ⫸  ● ○ ○   ✕   │ · · · · · · ·    │                │
│                 │ · ╰─────────────────────────────────────╯ · · · · · · ·    │                │
│                 │ ·  ▌▌ · · · ┌───────────────┐ · · · ● · · · · · · · ·      │                │
│                 │ ·   ◝ · · · │ FOTKA (maska) │ · · · · · · ◢ · · · · ·      │                │
│                 │ · · · · · · └───────────────┘ · · · · · ◢▌ · · · · ·       │                │
│                 │ · · ┌┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┐ · · · · · · · ·      │                │
│                 │ · · ┆ Píš text alebo pretiahni fotku ┆ · · · · · · · ·     │                │
│                 │ · · └┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┘ · · · · · · · ·      │                │
│                 └────────────────────────────────────────────────────────────┘                │
│                                                                                               │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Lišta

Zľava doprava v poradí, v akom sa pri práci používa:

| Položka | Ako často | Obsah |
|---|---|---|
| `420 × 594 mm · Grid 8 ▾` | raz na začiatku | Po kliknutí: predvoľba (načítať / uložiť), rozmer a jednotka, DPI, spadávka, Grid, zvyšok výšky |
| `Parametre ▾` | občas | Weight, Contrast, inverzia, veľkosť, variácia, rozloženie, typy, rozmiestnenie (voľné / dlaždice) |
| `◀ Variant 42 ▶ ⟳` | neustále | Predchádzajúci, číslo variantu (dá sa prepísať), ďalší, náhodný |
| `75 %` | podľa potreby | Zoom plátna |
| `Export` | raz na konci | SVG / PNG / AVIF, text upraviteľný alebo v krivkách |

V rozhraní sa píšu slová, nie symboly. Slovo „seed“ sa v rozhraní nepoužíva, je to **Variant**.

### Plátno

- **Nová zóna:** ťahaním po prázdnom mieste. Prichytáva sa na dieliky. Prázdna zóna ukáže výzvu „Píš text alebo pretiahni fotku“.
  - Začneš písať → textová zóna.
  - Pretiahneš fotku do zóny → fotková zóna.
  - Pretiahneš fotku na prázdne miesto → fotková zóna vznikne tam, na veľkosť dielikov pod kurzorom.
- **Presun a zmena veľkosti:** ťahaním zóny a jej rohov.
- **Fotka:** dvojklik prepne na posun a zoom fotky.
- **Vybraná zóna** má pod sebou malú plávajúcu lištu: pri texte písmo, veľkosť, zarovnanie a správanie (prázdna / presah / okraj), pri fotke režim (rámik / maska / prekrytie). ✕ zónu zmaže.
- **Čiary gridu** sa ukážu samy, keď ťaháš zónu. Inak sú skryté, prepínač netreba.
- **Spadávka** je vždy jemne vyznačená.

### Skratky

← → variant, `R` náhodný variant, `I` inverzia, `E` export, `Esc` zavrie lištu alebo ponuku, `T` prehliadač tvarov.

### Prehliadač tvarov

Nástroj na ladenie tvarov a `proporcie.json`, nie bežná práca. Vo fáze 1 ho nahrádzajú vzorkovníky z CLI. Otvára sa skratkou `T` cez celé okno.

- Vybraný typ vo veľkom.
- Posuvníky Weight, Contrast, Zaoblenie a parametrov vybraného typu.
- Pod tým všetky typy naraz pri aktuálnych osiach.

## Fázy

Najprv jadro a CLI, rozhranie až potom. Tvary sa ladia cez vzorkovníky: obrázok, kde je tvar v sérii hodnôt vedľa seba (napr. Weight 0, 25, 50, 75, 100 %) a vedľa vzorky písma.

| # | Výsledok | Odhad |
|---|---|---|
| 1 | Jadro s typmi a CLI: vzorkovníky, PNG/SVG | 1–2 sedenia |
| 2 | CLI kompozícia: formát, grid, parametre, variant, zóny zo súboru, voľné rozmiestnenie | 1–2 sedenia |
| 3 | Build webu: náhľady akcií, pozadia | 1 sedenie |
| 4 | UI: lišta a plátno, zóny ťahaním, prehliadač tvarov | 2 sedenia |
| 5 | Rozmiestnenie dlaždice | 1 sedenie |
| 6 | Animácia a export videa | neskôr |

**Zóny v CLI** sa zadávajú súborom (JSON) s polohou a veľkosťou v dielikoch, napr. text „MILONGA“ v stĺpci 1, riadku 1, veľkosť 6 × 2. Rozhranie vo fáze 4 vytvára ten istý súbor myšou.

## Na neskôr

Nebránia začať, riešia sa až pri príslušnej fáze.

- Na ktorých stránkach budú pozadia a dekorácie (fáza 3).
- Adresa webového rozhrania (fáza 4).
