# Přístup do /admin/

Formulář na [brnosaires.com/admin](https://brnosaires.com/admin/) zapisuje přímo do tohohle repozitáře — každé uložení je commit do větve `main`. Kdo tam smí, se proto neřídí žádným seznamem uživatelů v CMS, ale **právem zapisovat do repozitáře na GitHubu**. Odebrat někomu přístup znamená odebrat mu ho tam.

## Chci editovat: registrace za pět minut

Potřebuješ účet na GitHubu a pozvánku do repozitáře. O pozvánku požádej správce (viz [níž](#chci-přidat-editora)) — bez ní se přihlásit nedá, i kdyby ti CMS token vzalo.

1. **Účet.** [github.com/signup](https://github.com/signup), pokud ho ještě nemáš. Stačí e-mail a heslo.
2. **Pozvánka.** Přijde na e-mail („invited you to collaborate"). Klikni na **Accept invitation**. Bez toho kroku pozvánka po týdnu propadne.
3. **Otevři [brnosaires.com/admin](https://brnosaires.com/admin/)** a klikni na **„Sign In Using Access Token"**.
4. **Vygeneruj token — klasický, ne fine-grained.**

   ⚠️ V dialogu je odkaz na GitHub, ale vede na **fine-grained** token, a ten tady **nefunguje**. Odkaz ignoruj a jdi na [github.com/settings/tokens](https://github.com/settings/tokens/new) → **Generate new token (classic)**.

   - **Note** → cokoli, ať poznáš, k čemu je (např. „Brnos Aires /admin/").
   - **Expiration** → jak dlouho má token platit (po vypršení se prostě přihlásíš znovu).
   - **Scopes** → zaškrtni **`public_repo`**. Repozitář je veřejný, takže víc není potřeba; celé `repo` funguje taky, jen dává přístup i k soukromým repozitářům, které s tímhle webem nesouvisí.

<img width="1536" height="996" alt="token-settings" src="https://github.com/user-attachments/assets/862f83f8-0dd7-43f4-8032-bc2f2ca2ed3c" />


   Pak **Generate token** a token zkopíruj — GitHub ho ukáže jen jednou.
5. **Vlož token** zpátky do dialogu v /admin/ a jsi uvnitř.

Token si prohlížeč zapamatuje, takže tohle děláš jednou (a pak znovu, až vyprší). Když se přihlašuješ z jiného počítače nebo z telefonu, vygeneruj si další — tokenů může být víc a jde je kdykoli zrušit v [nastavení GitHubu](https://github.com/settings/tokens).

**Token je heslo.** Neposílej ho mailem ani do chatu. Když ti unikne, zruš ho na tomtéž místě a udělej si nový.
