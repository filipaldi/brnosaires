# Přístup do /admin/

Formulář na [brnosaires.com/admin](https://brnosaires.com/admin/) zapisuje přímo do tohohle repozitáře — každé uložení je commit do větve `main`. Kdo tam smí, se proto neřídí žádným seznamem uživatelů v CMS, ale **právem zapisovat do repozitáře na GitHubu**. Odebrat někomu přístup znamená odebrat mu ho tam.

## Chci editovat: registrace za pět minut

Potřebuješ účet na GitHubu a pozvánku do repozitáře. O pozvánku požádej správce (viz [níž](#chci-přidat-editora)) — bez ní se přihlásit nedá, i kdyby ti CMS token vzalo.

1. **Účet.** [github.com/signup](https://github.com/signup), pokud ho ještě nemáš. Stačí e-mail a heslo.
2. **Pozvánka.** Přijde na e-mail („invited you to collaborate"). Klikni na **Accept invitation**. Bez toho kroku pozvánka po týdnu propadne.
3. **Otevři [brnosaires.com/admin](https://brnosaires.com/admin/)** a klikni na **„Sign In Using Access Token"**.
4. **Vygeneruj token.** V dialogu je odkaz na GitHub, kde je formulář **předvyplněný**: jméno „Sveltia CMS" a oprávnění **Contents: write**. Ty vybereš jen:
   - **Resource owner / Repository access** → `filipaldi/brnosaires`,
   - **Expiration** → jak dlouho má token platit (po vypršení se prostě přihlásíš znovu).

   Pak **Generate token** a token zkopíruj — GitHub ho ukáže jen jednou.
5. **Vlož token** zpátky do dialogu v /admin/ a jsi uvnitř.

Token si prohlížeč zapamatuje, takže tohle děláš jednou (a pak znovu, až vyprší). Když se přihlašuješ z jiného počítače nebo z telefonu, vygeneruj si další — tokenů může být víc a jde je kdykoli zrušit v [nastavení GitHubu](https://github.com/settings/personal-access-tokens).

**Token je heslo.** Neposílej ho mailem ani do chatu. Když ti unikne, zruš ho na tomtéž místě a udělej si nový.

## Chci přidat editora

Potřebuješ být vlastník repozitáře nebo mít roli *Admin*.

1. GitHub → [filipaldi/brnosaires](https://github.com/filipaldi/brnosaires) → **Settings** → **Collaborators and teams**.
2. **Add people**, najdi člověka podle jména účtu nebo e-mailu.
3. Role **Write**. Míň nestačí (nešlo by uložit), víc není potřeba — *Admin* by mu dovolil měnit nastavení repozitáře i mazat ho.
4. Pošli mu odkaz na [registraci výš](#chci-editovat-registrace-za-pět-minut). Pozvánku musí přijmout sám.

Odebrání je na téže stránce, ikonka koše u jména. Tokeny, které si ten člověk vygeneroval, tím přestanou pro tenhle repozitář fungovat.

## Proč tam není „Přihlásit přes GitHub"

Klasické OAuth tlačítko potřebuje běžící server, který vymění kód za token ([sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth) nebo podobný relay). Ten tenhle web nemá a kvůli jednomu tlačítku by se musel hostovat a udržovat. Token dělá totéž a nestojí nic navíc, takže je v konfiguraci nastavené `auth_methods: [token]` a nabídka ukazuje jen jeho.

Kdyby se to někdy chtělo změnit, přibude do `backend:` v [content/extra/admin/config.yml](../content/extra/admin/config.yml) klíč `base_url:` s adresou toho relaye a `auth_methods` se odstraní.

## Když se přihlášení nepovede

| Co se stane | Co s tím |
|---|---|
| „Not Found" nebo prázdný seznam akcí | Účet nemá právo zapisovat do repozitáře, nebo pozvánka nebyla přijata. |
| „Bad credentials" | Token je špatně zkopírovaný (mezera navíc) nebo už vypršel. Udělej nový. |
| Přihlásí to, ale uložení skončí chybou | Token nemá **Contents: write**, typicky když se generoval ručně mimo předvyplněný odkaz. |
| Chyba v konfiguraci na přihlašovací obrazovce | To není o účtu — rozbil se `config.yml`. Případ pro vývojáře. |

## Související

- [Akce: přidat a upravit](AKCE.md) — co s formulářem dělat, když už jsi uvnitř.
- [Publikování](publishing.md) — kdy se změna objeví na webu.
