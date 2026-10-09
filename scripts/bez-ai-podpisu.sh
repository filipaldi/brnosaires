#!/bin/sh
# Every commit is signed by a human. This script rejects AI-attributed
# commits: no agent in the message, no agent as author or committer.
#   --msg <file>         check a commit message file + pending identities
#                        (called from .githooks/commit-msg)
#   --range <rev-range>  check every commit in the range; a lone rev means
#                        just that commit (called from CI)
# Exit 0 = clean, 1 = violation found, 2 = usage or git error.

# Agent names and provider domains that must never sign a commit.
NAMES='claude|anthropic|glm|zhipu|z[.]ai|openai|chatgpt|codex|copilot|gemini|cursor|devin|aider'
MAIL='@anthropic[.]com|@openai[.]com|@z[.]ai'
W='(^|[^[:alpha:]])'; END='([^[:alpha:]]|$)'   # portable word edges for grep -E

FIX='Prepíš správu / autora, autorom je vždy skutočný človek.'
bad=0
fail() { printf 'AI PODPIS: %s\n  %s\n' "$1" "$FIX" >&2; bad=1; }

check_msg() { # $1 = where, $2 = message file (POSIX sh: no locals — distinct names)
    mwhere=$1 mfile=$2
    grep -iEq "^[[:space:]]*co-authored-by:.*($NAMES|$MAIL)" "$mfile" &&
        fail "$mwhere: co-author trailer v správe uvádza AI agenta alebo bota"
    grep -iEq "generated (with|by).*($NAMES|$W(ai)$END|$W(bot)$END)" "$mfile" &&
        fail "$mwhere: správa hlási, že ju vygenerovalo AI"
    grep -iEq 'claude[.]ai/code|claude[.]com/claude-code' "$mfile" &&
        fail "$mwhere: správa obsahuje odkaz na nástroj Claude Code"
    grep -iEq '^[[:space:]]*claude-session:' "$mfile" &&
        fail "$mwhere: správa obsahuje session trailer nástroja Claude"
    grep -iq '🤖.*generated' "$mfile" &&
        fail "$mwhere: správa obsahuje robot emoji s generovacím podpisom"
}

check_ident() { # $1 = where, $2 = "Name <email>"
    iwhere=$1 id=$2
    name=${id%% <*}; mail=${id#*<}; mail=${mail%>*}
    # GitHub web merges ("GitHub <noreply@github.com>") match nothing here and pass.
    printf '%s\n' "$name" | grep -iEq "$W($NAMES)$END" &&
        fail "$iwhere: meno '$name' je AI agent, nie človek"
    printf '%s\n' "$mail" | grep -iEq "$MAIL" &&
        fail "$iwhere: e-mail '$mail' patrí AI poskytovateľovi"
}

case $1 in
    --msg)
        [ $# -eq 2 ] && [ -f "$2" ] || {
            echo "bez-ai-podpisu: --msg potrebuje súbor so správou" >&2; exit 2; }
        check_msg 'nový commit' "$2"
        a=$(git var GIT_AUTHOR_IDENT) || exit 2
        c=$(git var GIT_COMMITTER_IDENT) || exit 2
        a=${a% *}; a=${a% *}; c=${c% *}; c=${c% *}   # strip " <unix time> <tz>"
        check_ident 'autor nového commitu' "$a"
        check_ident 'committer nového commitu' "$c"
        ;;
    --range)
        [ $# -eq 2 ] || { echo "bez-ai-podpisu: --range potrebuje rozsah" >&2; exit 2; }
        case $2 in
            *..*) revs=$(git rev-list "$2") || exit 2 ;;
            *)    revs=$(git rev-list -1 "$2") || exit 2 ;;   # lone rev: that commit only
        esac
        tmp=$(mktemp) || exit 2
        trap 'rm -f "$tmp"' EXIT
        for rev in $revs; do
            where="commit $(git log -1 --format='%h %s' "$rev")"
            git log -1 --format=%B "$rev" >"$tmp"
            check_msg "$where" "$tmp"
            check_ident "$where: autor" "$(git log -1 --format='%an <%ae>' "$rev")"
            check_ident "$where: committer" "$(git log -1 --format='%cn <%ce>' "$rev")"
        done
        ;;
    *)
        echo "usage: $0 --msg <file> | --range <rev-range>" >&2; exit 2 ;;
esac
exit $bad
