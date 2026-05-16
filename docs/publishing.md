# Nasazení (publikace)

Tento dokument popisuje, **jak se obsah dostane na produkci** (`https://brnosaires.com`). Pro většinu úprav nemusíš dělat nic ručně — stačí commitnout do `main` a počkat na další automatický build.

## Obsah

1. [Jak to funguje ve zkratce](#jak-to-funguje-ve-zkratce)
2. [Co workflow dělá](#co-workflow-dělá)
3. [Když potřebuješ rychlejší nasazení](#když-potřebuješ-rychlejší-nasazení)
4. [Co dělat při selhání buildu](#co-dělat-při-selhání-buildu)
5. [Lokální produkční build (pro kontrolu před commitem)](#lokální-produkční-build-pro-kontrolu-před-commitem)
6. [Co kontrolovat po nasazení (manuální checklist)](#co-kontrolovat-po-nasazení-manuální-checklist)
7. [Rollback (vrácení změny)](#rollback-vrácení-změny)
8. [Konfigurace GitHub Pages](#konfigurace-github-pages)
9. [Související](#související)

## Jak to funguje ve zkratce

Produkční nasazení běží přes **GitHub Actions → GitHub Pages**. Workflow je definovaný v [.github/workflows/deploy.yml](../.github/workflows/deploy.yml).

Build se spouští:

- **Automaticky dvakrát denně** podle cronu: `0 6,18 * * *` (06:00 a 18:00 UTC, tj. 07:00/08:00 a 19:00/20:00 v Brně podle zimního/letního času).
- **Ručně na vyžádání** přes `workflow_dispatch` — vývojář může build spustit kdykoli z GitHub UI (Actions → *Build and Deploy* → *Run workflow*) nebo přes `gh workflow run`.

**Push do `main` build neaktivuje sám o sobě** — změna se zveřejní až při dalším naplánovaném buildu (max ~12 hodin), nebo když někdo workflow spustí ručně.

## Co workflow dělá

Soubor [.github/workflows/deploy.yml](../.github/workflows/deploy.yml) má dva joby:

### Job 1: `build`

1. **Checkout** repozitáře (`actions/checkout@v4`).
2. **Setup Python 3.11** (`actions/setup-python@v5`).
3. **Instalace závislostí**: `pip install -r requirements.txt`.
4. **Build s Pelicanem**: `PYTHONPATH=. pelican content -s publishconf.py` — produkční konfigurace s `SITEURL = "https://brnosaires.com"` a `RELATIVE_URLS = False`.
5. **CNAME pro vlastní doménu**: `echo "brnosaires.com" > output/CNAME` (GitHub Pages tak ví, na jaké doméně web běží).
6. **Setup Pages** (`actions/configure-pages@v4`).
7. **Upload artefaktu** — obsah `output/` se nahraje jako GitHub Pages artefakt (`actions/upload-pages-artifact@v3`).

### Job 2: `deploy`

Po úspěšném buildu (`needs: build`) se artefakt nasadí na GitHub Pages přes `actions/deploy-pages@v4`. URL nasazené verze (`https://brnosaires.com`) se zobrazí jako výstup workflow.

## Když potřebuješ rychlejší nasazení

Stačí v GitHub UI spustit workflow ručně:

1. Otevři **Actions** v repu.
2. Vlevo vyber **Build and Deploy**.
3. Vpravo nahoře klikni na **Run workflow** → větev `main` → **Run workflow**.

Případně z příkazové řádky (pokud máš nainstalovaný `gh` CLI):

```bash
gh workflow run "Build and Deploy"
gh run watch    # sleduj průběh
```

Build trvá obvykle 1–2 minuty, deploy dalších ~30 sekund. Celkem do 3 minut je změna na produkci.

## Co dělat při selhání buildu

Pokud workflow spadne (červený křížek v Actions), nejčastější příčiny:

| Chyba | Příčina | Co s tím |
|---|---|---|
| Selhal `pelican content` | Chyba v markdownu, šabloně nebo metadatech akce (např. nevalidní formát data ve frontmatteru, chybějící `event-start`) | Otevři log Actions, najdi konkrétní soubor a oprav |
| Selhal `pip install` | `requirements.txt` má rozbitou nebo neexistující verzi balíku | Lokálně ověř `pip install -r requirements.txt`, případně aktualizuj `requirements.txt` |
| Build proběhne, ale deploy selže | GitHub Pages mají dočasný výpadek nebo omezení (rate limit) | Zkusit znovu spustit workflow za chvíli |
| Build se vůbec nespustí | Workflow byl zakázán nebo se větev nejmenuje `main` | Zkontroluj **Actions → Build and Deploy → … → Enable workflow** |

Lokální build pro reprodukci chyby:

```bash
source venv/bin/activate
pelican content -s publishconf.py
```

Pokud projde lokálně a v CI ne, podívej se na rozdíly v Python verzi (CI = 3.11) a v `requirements.txt`.

## Lokální produkční build (pro kontrolu před commitem)

```bash
source venv/bin/activate
pelican content -s publishconf.py
```

**Rozdíly proti dev konfiguraci v [pelicanconf.py](../pelicanconf.py):**

- `SITEURL = "https://brnosaires.com"` — odkazy jsou absolutní.
- `RELATIVE_URLS = False` — nemůžeš to otevřít přes `file://` a očekávat funkční odkazy, takže pro „prohlédnout output/" radši stavěj přes `pelicanconf.py`.

Stavěj přes `publishconf.py` jen tehdy, když chceš ověřit, že absolutní URL a JSON-LD obsahují správné prefixy.

## Co kontrolovat po nasazení (manuální checklist)

Po významnější změně se hodí přejít přes pár stránek a podívat se, jestli něco není rozbité:

- [ ] Homepage [brnosaires.com](https://brnosaires.com/) se načítá, obrázky a navigace fungují.
- [ ] [/kalendar/](https://brnosaires.com/kalendar/) zobrazuje budoucí akce.
- [ ] [/milongy/](https://brnosaires.com/milongy/) má aktuální seznam.
- [ ] Detail nějaké nedávno upravené akce vypadá správně (data, místo, popis).
- [ ] Žádné chyby v konzoli prohlížeče (Cmd+Alt+I → Console).
- [ ] Měsíční stránka odpovídající aktuálnímu měsíci (`/milongy-brno-<měsíc>/`) má obsah.

Pro důkladnější procházku existuje subagent `ux-visual-once-over` (viz [.claude/CLAUDE.md](../.claude/CLAUDE.md)), který obejde web Playwrightem a vrátí per-stránku pass/fail report.

## Rollback (vrácení změny)

GitHub Pages drží pouze poslední nasazenou verzi — neexistuje „one click rollback". Postup, když je potřeba něco rychle vrátit:

1. V repu identifikuj problematický commit (`git log`, případně v GitHub UI).
2. Vrať změnu přes `git revert <sha>` (vytvoří nový commit, který původní změnu odčiní), commit pushni.
3. Spusť workflow ručně (viz výše), aby se nasazená verze obnovila do 3 minut.

Pro úplný snapshot historie webu je k dispozici git historie samotná — celý obsah je verzovaný v `content/`.

## Konfigurace GitHub Pages

Nastavení Pages v repu (jednorázové, už proběhlo):

- **Source**: GitHub Actions (ne „Deploy from a branch" — workflow staví a deployuje sám).
- **Custom domain**: `brnosaires.com` (CNAME se generuje při buildu, viz krok 5 workflow).
- **Enforce HTTPS**: zapnuto.

DNS pro `brnosaires.com` ukazuje CNAME na `<owner>.github.io` (správa domény je mimo repo).

## Související

- [Nastavení vývojového prostředí](setup.md) — příprava lokálního prostředí.
- [Lokální testování](local-testing.md) — lokální build a testování před commitem.
- [SEO + sociální kartičky](SEO.md) — co se v produkčním buildu generuje (kanonická URL, sitemap, JSON-LD).
- [Widget systém](WIDGETS.md) — widgety v markdownu.
- [Úprava obsahu](EDITING.md) — frontmatter a metadata.
- [GitHub Issues](https://github.com/filipaldi/brnosaires/issues) - plán rozvoje (mj. [#26 Automatické kontroly před publikací](https://github.com/filipaldi/brnosaires/issues/26) - návrh CI jobu validujícího frontmatter před deployem).
- [Brnos Aires — web](../README.md) — hlavní rozcestník.
