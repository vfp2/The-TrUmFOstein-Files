#!/usr/bin/env bash
# scan.sh — discover GitHub repos responding to the war.gov PURSUE UAP release.
#
# Outputs a structured markdown report on stdout. The companion SKILL.md
# explains how Claude consumes this output to update related-repos.md, commit,
# and push. The script itself is read-only and idempotent.
#
# Run from anywhere; the script auto-locates the repo root via its own path.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
RELATED="$REPO_ROOT/related-repos.md"

if [ ! -f "$RELATED" ]; then
    echo "ERROR: $RELATED not found" >&2
    echo "       (expected to find related-repos.md at the repo root)" >&2
    exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
    echo "ERROR: gh CLI not found on PATH" >&2
    exit 2
fi
if ! command -v jq >/dev/null 2>&1; then
    echo "ERROR: jq not found on PATH" >&2
    exit 2
fi

cd "$REPO_ROOT"

NOW_HUMAN=$(date -u +"%Y-%m-%d %H:%M UTC")
NOW_EPOCH=$(date -u +%s)
RELEASE_EPOCH=$(date -u -d "2026-05-08T13:00:00Z" +%s 2>/dev/null || echo "$NOW_EPOCH")
HOURS_SINCE_RELEASE=$(( (NOW_EPOCH - RELEASE_EPOCH) / 3600 ))

echo "# related-repos refresh scan"
echo
echo "*Scan time: ${NOW_HUMAN} (release + ~${HOURS_SINCE_RELEASE}h)*"
echo

# ===== 1. Extract tracked repos =====================================
# Match github.com/owner/name patterns, dedup, exclude self-refs and non-repo paths.
# Strip `gist.github.com/...` and `gist.githubusercontent.com/...` urls first
# so we don't mistake a gist hash for a repo name.
TRACKED=$(sed -E 's|gist\.github(usercontent)?\.com/[^ )]*||g' "$RELATED" \
    | grep -oE 'github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+' \
    | sed 's|github\.com/||; s|\.$||' \
    | sort -u \
    | grep -v '^vfp2/' \
    | grep -vE '^(orgs|gist|gists|raw|blob|tree|releases|users)$' \
    | grep -vE '/(blob|tree|releases|raw|wiki|issues|pulls|actions)$' \
    | grep -vE '/[a-f0-9]{20,}$' \
    || true)

TRACKED_COUNT=$(printf '%s\n' "$TRACKED" | grep -c . || echo 0)

echo "## Tracked repos: ${TRACKED_COUNT}"
echo
echo "| Repo | Status | Stars | Forks | Last push |"
echo "|------|--------|-------|-------|-----------|"

DELETED_LIST=()
EXISTING_COUNT=0

while IFS= read -r repo; do
    [ -z "$repo" ] && continue
    info=$(gh api "repos/${repo}" 2>/dev/null || true)
    if [ -z "$info" ] || echo "$info" | jq -e 'has("message") and (.message == "Not Found")' >/dev/null 2>&1; then
        echo "| \`${repo}\` | **DELETED (404)** | — | — | — |"
        DELETED_LIST+=("$repo")
    else
        stars=$(printf '%s' "$info" | jq -r '.stargazers_count // 0')
        forks=$(printf '%s' "$info" | jq -r '.forks_count // 0')
        pushed=$(printf '%s' "$info" | jq -r '.pushed_at // "?"')
        echo "| \`${repo}\` | ok | ${stars} | ${forks} | ${pushed} |"
        EXISTING_COUNT=$((EXISTING_COUNT + 1))
    fi
done <<< "$TRACKED"
echo

# ===== 2. Run keyword searches =====================================
echo "## Keyword searches"
echo
echo "Queries run:"

QUERIES=(
    "war.gov UFO"
    "PURSUE UAP"
    "UAP disclosure 2026"
    "declassified UFO PURSUE"
    "war.gov UAP"
)
ALL=$(mktemp)
trap 'rm -f "$ALL" "${ALL}.uniq" 2>/dev/null' EXIT

for q in "${QUERIES[@]}"; do
    count_before=$(wc -l < "$ALL" 2>/dev/null || echo 0)
    gh search repos "$q" --limit 30 \
        --json name,owner,description,url,createdAt,stargazersCount \
        2>/dev/null \
        | jq -r '.[] | [.owner.login + "/" + .name, .createdAt, .stargazersCount, (.description // "" | gsub("\t|\n|\r"; " ")), .url] | @tsv' \
        >> "$ALL" || true
    count_after=$(wc -l < "$ALL")
    echo "- \`${q}\` → +$((count_after - count_before)) hits"
done
echo

sort -u "$ALL" > "${ALL}.uniq"
TOTAL_UNIQUE=$(wc -l < "${ALL}.uniq")
echo "Total unique repos returned across all searches: ${TOTAL_UNIQUE}"
echo

# ===== 3. New candidates =================================================
# Filter: not in TRACKED, not vfp2/*, created on/after 2026-04-01.
echo "## NEW candidates (post 2026-04-01, not tracked)"
echo
echo "| Repo | Created | Stars | Description |"
echo "|------|---------|-------|-------------|"

NEW_COUNT=0
NEW_NAMES=()
while IFS=$'\t' read -r full_name created stars desc url; do
    [ -z "$full_name" ] && continue
    # Skip if already tracked
    if printf '%s\n' "$TRACKED" | grep -qFx "$full_name"; then
        continue
    fi
    # Skip vfp2 self-references
    [[ "$full_name" == vfp2/* ]] && continue
    # Skip pre-April 2026
    if [[ "$created" < "2026-04-01" ]]; then
        continue
    fi
    desc_trunc=$(printf '%s' "$desc" | cut -c1-110 | tr '|' '/')
    echo "| [\`${full_name}\`](${url}) | ${created} | ${stars} | ${desc_trunc} |"
    NEW_COUNT=$((NEW_COUNT + 1))
    NEW_NAMES+=("$full_name")
done < "${ALL}.uniq"

if [ "$NEW_COUNT" -eq 0 ]; then
    echo "| _(no new candidates)_ | | | |"
fi
echo
echo "Total new candidates: ${NEW_COUNT}"
echo

# ===== 4. Summary ============================================================
echo "## Summary"
echo
echo "- **Tracked existing**: ${EXISTING_COUNT}"
echo "- **Tracked but deleted (404)**: ${#DELETED_LIST[@]}"
if [ "${#DELETED_LIST[@]}" -gt 0 ]; then
    for r in "${DELETED_LIST[@]}"; do
        echo "  - \`${r}\`"
    done
fi
echo "- **New candidates (post 2026-04-01, not tracked)**: ${NEW_COUNT}"
if [ "$NEW_COUNT" -gt 0 ] && [ "$NEW_COUNT" -le 20 ]; then
    for r in "${NEW_NAMES[@]}"; do
        echo "  - \`${r}\`"
    done
fi
echo
echo "*Scan complete.*"
