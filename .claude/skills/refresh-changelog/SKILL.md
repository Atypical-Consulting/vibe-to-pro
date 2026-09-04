---
name: refresh-changelog
description: >
  Refresh the vibe-to-pro course when a new Claude Code CHANGELOG version
  ships -- verifies new candidate facts, updates affected chapters, and
  bumps the site's stats/freshness numbers everywhere they're cited. Use
  when the user asks to update the course for a new Claude Code release,
  refresh the changelog, or mentions scripts/refresh/.
---

# Refresh the course for a new CHANGELOG version

This course's whole premise is that every fact is verified against current
docs, not recalled from memory (see `docs/methodologie.html`). A refresh
that skips verification breaks that premise for whatever it touches, so
don't shortcut step 3.

State lives in `scripts/refresh/site-meta.json`: `last_version`,
`verified_date`, and the four headline counts (`versions_analyzed`,
`candidate_features`, `confirmed_or_updated`, `kept_facts`). Treat it as the
single source of truth -- the HTML files cite these numbers in ~15 places
across 5 files and it's easy to miss one by hand.

## 1. Find what's new

Fetch the current CHANGELOG (`https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md`,
or ask the user for a pasted range) and take every version entry strictly
newer than `last_version` in site-meta.json. If there are none, stop --
nothing to do.

## 2. Extract candidate facts

For each new version entry, pull out feature-level bullets (not internal
refactors or minor bug fixes -- same bar the original extraction used: does
this change how a user interacts with Claude Code). For each candidate,
note which existing module it belongs to (`prologue, controle, memoire,
skills, plan, agents, hooks, mcp, rewind, git, echelle, plugins, infra,
epilogue` -- match by subject, e.g. a hooks flag goes to `hooks`). A
candidate that doesn't fit any existing module is a signal the course might
need a 15th chapter -- flag it for the user rather than inventing one.

## 3. Verify every candidate independently

For each candidate fact, check it against CURRENT documentation on
`code.claude.com` (a dedicated search per fact, never from memory -- this is
the one rule this whole course is built on). Classify each:
- **confirmed** -- matches current docs as described in the changelog
- **corrected** -- changed since the changelog entry; note what's current
- **unverifiable** -- can't confirm against current docs; discard it,
  same as the original pipeline did for ~24 candidates

Run verification in parallel across candidates (they're independent), but
don't skip any -- an unverified fact in this course is a bug, not a
shortcut.

## 4. Update the affected chapter pages

For each module with a confirmed/corrected fact:
- Add or update a `.fact` block in that module's "Ce qu'il faut retenir"
  section (`docs/<module>.html` AND `docs/en/<module>.html` -- translate the
  new fact's `t`/`h` text the same way the rest of that section was
  translated). Match the existing markup exactly: `<div class="fact">`
  (add ` key` to the class only for a fact genuinely central to the
  module, same bar as the existing key facts), version badge, `confirmed`/
  `corrected` status badge, source link.
- Update that module's `data-freshness` date (on the module's freshness
  indicator) to today.
- If a fact makes an existing fact in the course wrong or outdated, correct
  that fact in place rather than leaving both -- don't let confirmed facts
  silently go stale next to a newer corrected one.

## 5. Bump site-meta.json and find every citation

Before editing: `python scripts/refresh/find_stale_numbers.py` lists every
file:line currently citing the OLD numbers -- this is your checklist.

Update `scripts/refresh/site-meta.json`: `last_version` to the newest
version processed, `verified_date` to today, `versions_analyzed` +=
(number of new CHANGELOG versions processed), `candidate_features` +=
(candidates extracted in step 2), `confirmed_or_updated` += (confirmed +
corrected count), `kept_facts` += (facts actually added to a chapter, which
may be fewer than confirmed+corrected if some just update an existing fact
rather than adding a new one).

Then update every line `find_stale_numbers.py` listed: `docs/index.html`,
`docs/en/index.html`, `docs/methodologie.html`, `docs/en/methodologie.html`,
`docs/og-image.html` (stats + regenerate `docs/og-image.png` from it if you
have a way to render it, otherwise flag that it's stale), plus the
colophon/footnote text in `docs/epilogue.html` and its `en/` mirror if it
cites the version count.

Run `find_stale_numbers.py` again pointing at a saved copy of the OLD
site-meta.json (`git show HEAD:scripts/refresh/site-meta.json >
old-meta.json && python scripts/refresh/find_stale_numbers.py
old-meta.json`) -- zero hits confirms nothing was missed. Watch for
overlapping numbers between old and new (e.g. old `kept_facts=98` also
being a version number elsewhere) producing false negatives; read the
diff, don't just trust the count.

## 6. Verify before committing

- No em dashes, no `\"` literal sequences, in anything you wrote.
- Every new/changed fact has a real, working source link.
- `git diff` should touch: the affected `docs/<module>.html` +
  `docs/en/<module>.html` pairs, `docs/index.html`, `docs/en/index.html`,
  `docs/methodologie.html`, `docs/en/methodologie.html`, `docs/og-image.html`,
  `scripts/refresh/site-meta.json`. Anything else is a sign of scope creep
  or a missed file.
- Push, then follow this project's established live-verification habit:
  poll the GitHub Pages build status and re-check the actual deployed
  pages, not just local files, before telling the user it's done.

Commit message should name the version range covered (e.g. "Refresh course
for Claude Code v2.1.261-v2.1.270") so the history doubles as a changelog
of what the course itself has absorbed.
