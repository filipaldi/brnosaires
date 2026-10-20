# Chci přidat editora

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
| Přihlásí to, ale uložení skončí chybou | Token nemá právo zapisovat — zkontroluj, že má zaškrtnuté `public_repo`. |
| Token vypadá správně, a stejně to nepustí dál | Je to fine-grained token. Ty tady nefungují; udělej klasický. |
| Chyba v konfiguraci na přihlašovací obrazovce | To není o účtu — rozbil se `config.yml`. Případ pro vývojáře. |

## Související

- [Akce: přidat a upravit](AKCE.md) — co s formulářem dělat, když už jsi uvnitř.
- [Publikování](publishing.md) — kdy se změna objeví na webu.
