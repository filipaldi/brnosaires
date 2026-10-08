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
- **Na webe AVIF**, JPEG pre sociálne siete vyrobí existujúci `plugins/og_image.py`. Pre Affinity SVG, voliteľne PNG.
- **Používa zatiaľ len autor písma.** Cieľom je, aby si web pri builde generoval vlastné náhľady, pozadia a dekorácie.

## Parametre

Jednotka **dielik** = šírka formátu / počet stĺpcov.

### Formát

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Šírka × výška | číslo + jednotka (mm / px) | Predvoľby A2, A3, IG, web sú len skratky |
| DPI | číslo | Len pri mm, pre PNG |
| Spadávka | mm | Technická, pre tlač |

### Mriežka

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Stĺpce (N) | celé číslo | Dielik = šírka / N, štvorcový |
| Zvyšok výšky | okraje / natiahnutie / presah a orez | Keď výška nie je násobkom dielika. Volí sa podľa potreby. |

### Kresba

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
| Seed | číslo alebo text | Na webe slug akcie |

### Farby

Len čierna a biela.

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Inverzia | nie / áno | Nie = čierne tvary na bielom, áno = biele na čiernom |

### Zóny

Spoločné pre každú zónu:

| Parameter | Hodnoty | Poznámka |
|---|---|---|
| Typ | text / fotka | |
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

Zóny sa dajú aj načítať zo šablóny z Affinity: SVG s vrstvami `text` a `fotky`.

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

| # | Typ | Parametre |
|---|---|---|
| 1 | Noha | dĺžka, vlas / plná, zaoblenie konca |
| 2 | Oblúk | šírka, výška, strana plnej nohy |
| 3 | Vrchol | uhol každej nohy (aj zvislá), šírka klinu |
| 4 | Koleno | vonkajší a vnútorný polomer |
| 5 | Hmota so štrbinou | dĺžka, šírka |
| 6 | Háčik s kvapkou | výška, polomer ohybu, veľkosť kvapky, noha vlas / plná |
| 7 | Nota | dĺžka nohy, počet kvapiek, rozostup, veľkosť kvapiek, strana |
| 8 | Kvapka | veľkosť, smer špičky |
| 9 | Kruh | priemer, obrys vlas / plný |
| 10 | Bod | priemer |

**Kvapka a prechod oblúka** z vlasovej linky do plnej nohy majú ručne ladené krivky. Ak ich geometria z kódu nepriblíži dosť verne, prenesú sa z písma presne ako krivka a parametre ich budú len posúvať a škálovať.

### Pravidlá skladania

- **Napojenie:** tvary sa dotýkajú a plynulo prechádzajú (noha + oblúk, vrchol so zvislou nohou).
- **Odsadenie:** tvar stojí nad druhým s medzerou (kruh nad nohou).

Body napojenia vyplývajú z geometrie (konce nôh, päty oblúka), netreba ich kresliť.

## Ako to funguje

```
proporcie.json + predvoľby ──► jadro ──┬─► webové rozhranie ──► SVG / PNG
                                       ├─► CLI (agent) ──────► SVG / PNG / AVIF
                                       └─► build webu ───────► náhľady, pozadia
```

### Plagát

1. Formát, mriežka, kresba, kompozícia.
2. Zóny nakreslené myšou na plátne, alebo načítané zo šablóny z Affinity.
3. Generátor rozmiestni tvary okolo zón.
4. Ďalší seed = ďalší variant. Predvoľba sa dá použiť pre celú sériu.

### Vzor (dlaždice)

Tvary v mriežke, otáčané a zrkadlené, napojené podľa pravidiel skladania.

### Web

- **Náhľady akcií:** editor si vyberie, či akcia dostane fotku alebo vygenerovaný pattern. Pri patterne je seed slug akcie, takže obrázok je stály.
- **Pozadia a dekorácie stránok.**
- Build potrebuje Node v `.github/workflows/deploy.yml`.

## Rozhranie

Jedna stránka, tri záložky. Rozhranie je pre počítač, mobil sa nerieši.

### Záložka Plagát

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  BRNOS AIRES · GENERÁTOR      [ Plagát ]  Vzor   Tvary      Predvoľba: A2 ▾ ⇩   │
├──────────────────┬───────────────────────────────────────────┬──────────────────┤
│ FORMÁT           │  Seed [ 42 ]  ◀  ⟳  ▶   ▦ mriežka         │ ZÓNA: Text 1     │
│ 420 × 594 mm     │  ☐ spadávka  ◐ inverzia                   │                  │
│ DPI 300 · 3 mm   │ ┌───────────────────────────────────────┐ │ Poloha 1,1  6×2  │
│                  │ │ · · · · · · · · · · · · · · · · · · · │ │ Správanie        │
│ MRIEŽKA          │ │ ·┌──────────────────────┐ · · ◜◝ · · ·│ │ ● prázdna        │
│ Stĺpce   [ 8 ]   │ │ ·│ MILONGA DE OTOÑO     │ · · ▌▐ · · ·│ │ ○ presah vlasom  │
│ Zvyšok  okraje ▾ │ │ ·└──────────────────────┘ · · ▌▐ · · ·│ │ ○ okraj          │
│                  │ │ ·  ◟▌ · · · · · · · · · · · ▌▐ · · ·  │ │                  │
│ KRESBA           │ │ ·  ▌▌ · ┌───────────────┐ · · · · · · │ │ Text             │
│ Weight   ──●──   │ │ ·  ▌▌ · │               │ · · ● · · · │ │ [MILONGA DE OTO] │
│ Contrast ────●─  │ │ ·   ◝ · │     FOTKA     │ · · · · ◢ · │ │ Písmo Brnos A. ▾ │
│                  │ │ · · · · │    (maska)    │ · · · ◢▌ ·  │ │ Veľkosť 1,5      │
│ KOMPOZÍCIA       │ │ · · · · └───────────────┘ · · · · · · │ │ Zarovnanie ⫷ ≡ ⫸ │
│ Veľkosť  1 – 6   │ │ · · ┌────────────────────────────┐ · ·│ │ Riadkovanie 1,1  │
│ Variácia ───●─   │ │ · · │ 17. 10. · 20:00 · BRNO     │ · ·│ │                  │
│ Rozloženie    ▾  │ │ · · └────────────────────────────┘ · ·│ │ [ Zmazať zónu ]  │
│ Typy ▣▣▣▣▣▣▣▣▣▣  │ │ · · · · · · · · · · · · · · · · · · · │ │                  │
│                  │ └───────────────────────────────────────┘ │                  │
│ ZÓNY             │                                           │                  │
│ [+ Text][+ Fotka]│  História seedov                          │                  │
│ [⇪ Šablóna SVG]  │  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐            │                  │
│                  │  │38│ │39│ │40│ │41│ │42│ │  │            │                  │
│ EXPORT           │  └──┘ └──┘ └──┘ └──┘ └──┘ └──┘            │                  │
│ SVG ▾ · krivky ▾ │                                           │                  │
│ [ Exportovať ]   │                                           │                  │
└──────────────────┴───────────────────────────────────────────┴──────────────────┘
```

- **Ľavý panel:** všetky parametre v poradí z tabuľky Parametre.
- **Stred:** plátno s mriežkou. Zóny sa kreslia ťahaním a presúvajú myšou, prichytávajú sa na dieliky.
- **Lišta nad plátnom:** seed (◀ predchádzajúci, ⟳ náhodný, ▶ ďalší), prepínače mriežky, spadávky a inverzie.
- **História seedov:** náhľady posledných variantov, kliknutím sa k variantu vrátiš.
- **Pravý panel:** vlastnosti vybranej zóny. Bez výberu je prázdny.
- **Predvoľba (vpravo hore):** načítanie a uloženie celého nastavenia okrem seedu.

### Záložka Vzor

Rovnaké rozloženie ako Plagát, bez zón a bez pravého panelu. Plátno ukazuje dlaždice.

### Záložka Tvary

Prehliadač jednotlivých typov (fáza 1). Slúži na ladenie tvarov a `proporcie.json`.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  BRNOS AIRES · GENERÁTOR        Plagát   Vzor  [ Tvary ]                         │
├──────────────────┬───────────────────────────────────────────────────────────────┤
│ TYP              │                                                               │
│ ○ Noha           │      ┌───────────────────┐   ┌───────────────────┐            │
│ ● Oblúk          │      │                   │   │                   │            │
│ ○ Vrchol         │      │      ╭─────╮      │   │   (písmo pre      │            │
│ ○ Koleno         │      │      │     ▐█     │   │    porovnanie)    │            │
│ ○ Hmota so štrb. │      │      │     ▐█     │   │                   │            │
│ ○ Háčik s kvap.  │      │      │     ▐█     │   │        n          │            │
│ ○ Nota           │      │      ╵     ▐█     │   │                   │            │
│ ○ Kvapka         │      └───────────────────┘   └───────────────────┘            │
│ ○ Kruh           │        tvar z generátora       vzorka písma                   │
│ ○ Bod            │                                                               │
│                  │   ☐ prekryť písmom  ☐ body napojenia  ▦ mriežka               │
│ KRESBA           │                                                               │
│ Weight   ──●──   │   Všetky typy naraz:                                          │
│ Contrast ────●─  │   ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐                    │
│                  │   │▌ ││∩ ││Λ ││┌ ││U ││ʃ ││♪ ││● ││○ ││· │                    │
│ PARAMETRE TYPU   │   └──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘                    │
│ Šírka    2 diel. │                                                               │
│ Výška    3 diel. │                                                               │
│ Plná noha vpravo │                                                               │
└──────────────────┴───────────────────────────────────────────────────────────────┘
```

- **Vľavo:** výber typu, Weight a Contrast, parametre vybraného typu.
- **Stred:** tvar z generátora vedľa vzorky písma. Prepínač „prekryť písmom“ ich položí cez seba, aby bolo vidno rozdiel v krivkách.
- **Dole:** všetky typy naraz pri aktuálnom Weight a Contrast.

## Fázy

| # | Výsledok | Odhad |
|---|---|---|
| 1 | Všetkých 10 typov v kóde, prehliadač s posuvníkmi Weight, Contrast a parametrov typu, porovnanie s písmom | 1–2 sedenia |
| 2 | Plagát: formát, mriežka, kompozícia, seed, export SVG/PNG, predvoľby | 1 sedenie |
| 3 | Zóny: text so sadzbou, fotka (rámik + maska), šablóna z Affinity | 1–2 sedenia |
| 4 | Vzor (dlaždice) | 1 sedenie |
| 5 | CLI a build webu: náhľady akcií, pozadia | 1 sedenie |
| 6 | Animácia a export videa | neskôr |

## Na neskôr

Nebránia začať, riešia sa až pri príslušnej fáze.

- Na ktorých stránkach budú pozadia a dekorácie (fáza 5).
- Adresa webového rozhrania (fáza 5).
- Ako Affinity načíta SVG masku, doladí sa pri prvom ostrom plagáte.
