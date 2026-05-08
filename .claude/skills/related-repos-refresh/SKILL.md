---
name: related-repos-refresh
description: Refresh the [related-repos.md](../../../related-repos.md) survey of GitHub projects responding to the war.gov PURSUE UAP/UFO release of 2026-05-08. Use when the user asks to "refresh / rescan / update the related-repos survey", "check for new UAP repos", "see what's changed in the UAP repo landscape", or sets up periodic monitoring. Searches GitHub for new repos, detects deletions and star/commit deltas in tracked repos, prepends a snapshot to the history section, updates entries, and commits + pushes via SSH.
---

# related-repos-refresh

Automates the scan + diff + report + commit cycle that has been done by hand twice already in [related-repos.md](../../../related-repos.md). The skill does not replace judgment — Claude still decides whether new candidates are genuinely UAP-relevant, whether star deltas are material, and how to phrase the snapshot summary. The script does the mechanical GitHub queries.

## Workflow

1. **Run the scan script** — produces a structured markdown report on stdout:

   ```
   bash .claude/skills/related-repos-refresh/scripts/scan.sh
   ```

   Output sections:
   - `## Tracked repos` — every repo currently linked from `related-repos.md`, with current stars / forks / last-push / deletion status.
   - `## NEW candidates` — repos surfaced by keyword searches that are post-2026-04-01 and not yet tracked.
   - `## Summary` — counts of existing / deleted / new.

2. **Read `related-repos.md`** to anchor what's already there. Especially look at:
   - The "Snapshot history" section at the top — what was true at the last refresh?
   - The "Out of scope" section — repos already triaged as not relevant; do not re-flag these as new.
   - The "Removed / archived" section — repos already known to be 404; do not re-flag the deletion as news.

3. **Triage NEW candidates with judgment**:
   - **In-scope signal**: description mentions war.gov, PURSUE, UAP / UFO disclosure, May 2026 release, declassified files, the Pentagon UFO portal.
   - **Out-of-scope signal**: video games (e.g. UFO 50), generic data-warehouse / governance projects, unrelated `gov` substring matches, personal portfolio stubs with no UAP content.
   - **Material star delta**: ≥ +5 stars on a tracked repo, or doubling, or any change that crosses a round number worth noting (10, 25, 50, 100).
   - **Material commit/activity delta**: a previously empty/stub repo that now has code, or a previously tracked repo that has materially changed direction.

4. **Update [related-repos.md](../../../related-repos.md)**:
   - **Always** prepend a new entry to the `## Snapshot history` section at the top, even if nothing changed. Format:
     ```markdown
     - **YYYY-MM-DD, ~HH:MM UTC** (release + ~Nh): K projects tracked. **+X new** (`repo1`, `repo2`, ...). **−Y**: <name> deleted/archived <one-line note>. Notable star deltas: <list>. <Anything else worth noting in one sentence.>
     ```
     If nothing changed, write: `**+0 new, −0 deleted, no material star deltas.**` Still record the timestamp.
   - For each new in-scope repo: add an entry under the most appropriate group section ("Mirrors and converted archives" / "Searchable archives, reading rooms, and RAG interfaces" / "Download / automation tooling" / "Datasets and analyser skills" / "Structured analysis and databases" / "Analysis and commentary" / "Manifest snapshots and source captures" / "Pre-release / adjacent" / "Out of scope"). Pattern of an entry: `### [owner/name](url) — N ★, M forks` then *italic creation timestamp*, then 2–4 sentences on purpose / approach / tech / current state, ending with a short architectural note if relevant.
   - For deleted repos: move the entry to `## Removed / archived` with strikethrough on the original link, an explanation, and (if we preserved a fork at vfp2) a link to the preservation. Don't re-flag if already in this section.
   - For existing repos with material changes: update the inline `— N ★, M forks` line and any commit count, but **do not rewrite the prose** unless the project's substance has changed.

5. **Commit and push**:
   - Stage only the changed file: `git add related-repos.md`
   - Commit message format:
     ```
     related-repos: refresh — +<X> new, −<Y> deleted, traction deltas

     Snapshot at <timestamp> (release + ~Nh).

     New: <comma-separated list with one-line notes>
     Removed: <list with reasons>
     Star deltas (material): <list of "name X→Y">
     <Optional: one-paragraph architectural observation if anything notable>
     ```
   - Push: `git push` (the user's `~/.ssh/config` `Host *` already routes `github.com` to `id_ed25519.spinsphere`, which has admin on `vfp2`). If push fails for ssh-key reasons, fall back to:
     ```
     GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519.spinsphere -o IdentitiesOnly=yes" git push
     ```

6. **Report back to the user** with a tight summary: how many new in-scope repos, how many deletions, headline star deltas, and what was committed. Don't paste the full scan output unless asked.

## Search keywords used by the script

The script runs these queries against `gh search repos` and deduplicates:

- `war.gov UFO`
- `PURSUE UAP`
- `UAP disclosure 2026`
- `declassified UFO PURSUE`
- `war.gov UAP`

If the user reports they've seen a relevant repo not surfaced by the script, **add it manually to the markdown** — the keyword set is best-effort, not exhaustive. If a new keyword is reliably surfacing relevant repos, edit `scripts/scan.sh` to include it.

## What the script does NOT do

- It does not fetch READMEs of new repos. If a new candidate looks worth a substantive entry rather than a one-liner, fetch the repo with `gh repo view <owner>/<name> --json description,readme` or use `WebFetch` on the GitHub URL.
- It does not fork repos. Forking to `vfp2/` is a deliberate decision per repo; the user has historically chosen which to fork. Surface candidates; don't auto-fork.
- It does not run on a schedule. Use [Claude Code's `/loop` or `/schedule` skills](https://docs.claude.com/) to wrap this skill if periodic execution is wanted.

## Notes on the scan script

- Tracked repos are extracted by regex (`github\.com/owner/name`) from `related-repos.md`. This means the *source of truth* for what is tracked is the markdown itself — there is no separate registry to keep in sync.
- The script skips `vfp2/*` URLs (those are the user's own forks, not external projects to track).
- "Post-2026-04-01" is the heuristic for "this could plausibly relate to the May 2026 release". Adjust in the script if a meaningful older repo surfaces.
- The script is idempotent and read-only (no writes, no API mutations).
