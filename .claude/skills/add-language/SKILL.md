---
name: add-language
description: >
  Add a new language mirror of the vibe-to-pro course (like docs/en/) --
  translates all 16 pages, wires up the language selector, updates the
  sitemap and README. Use whenever the user asks to add a language,
  translate the course, add Spanish/German/Portuguese/etc. support,
  internationalize the site, or mentions scripts/i18n/ -- including French
  phrasings like "ajoute l'espagnol", "traduis le cours en...", "ajoute une
  langue", "nouvelle langue" -- even if they don't name this skill directly.
---

# Add a language

The course lives as static HTML: French at `docs/*.html` (the default,
no prefix) and English at `docs/en/*.html` (mirrored filenames). Adding a
language means producing a third mirror, e.g. `docs/es/*.html`, translated,
with every cross-link and the language selector updated everywhere.

Read this whole file before touching anything -- the steps depend on each
other and skipping the verification steps is how a past run shipped literal
`\"` characters into the live site.

## 0. Decide the language and code

Ask the user if not already clear: which language, and what two-letter code
(`es`, `de`, `pt`, ...). The code becomes the directory name under `docs/`
and the option label shown in the selector (uppercased, e.g. `ES`).

## 1. Register it in `scripts/i18n/languages.json`

Add an entry: `"es": {"label": "ES", "dir": "es", "aria": "Idioma"}`. `dir`
is the path segment under `docs/` (empty string only for `fr`, the default).
`aria` is the accessible label for that language's own `<select>` (translate
"Language").

## 2. Fix a glossary BEFORE fanning out per-page translation

This step exists because the first real run of this skill (adding Spanish)
produced THREE different translations of the site's own brand title
("Del Vibe-Coding al Oficio" / "a la Profesión" / "a lo Profesional") from
three parallel agents who each translated it fresh inside their own page.
Nothing was wrong with any individual agent's work -- the bug was giving
16 agents a shared string with no fixed answer. Fix that before it happens
again: translate this short list ONCE yourself (or with a single agent
call), and paste the resulting glossary VERBATIM into every per-page
agent's prompt in step 4, not just into a separate find/replace pass:

- The site-wide brand title (e.g. "Du Vibe-Coding au Métier") -- this
  appears inside the per-page extracted units (sidebar `<h1>`, every
  page's `<title>`), so it must be fixed before any page is translated,
  not patched after.
- The 14 sidebar module titles (`Prologue`, `Contrôle & sécurité`,
  `Mémoire`, ... -- read them from any current `docs/*.html` sidebar).
  Tell agents explicitly: **the "&" between the two halves is a literal
  HTML entity glued in the page template outside the translatable text
  spans, not something the pipeline can change -- it must stay "&" in
  every language, matching the existing French and English pages. Do not
  translate it to "y"/"and"/"et".** (A prior run wasted agent effort on
  this because the instruction said to render it as "y"; most agents
  caught the contradiction themselves by checking a sibling page, but
  don't rely on that.)
- The short repeated UI strings: `Progression`, `Marquer comme lu`,
  `Précédent`, `Suivant`, `Vérifier`, `Exact.`, `Pas tout à fait.`, `Test
  de niveau`, `Quiz éclair`, `Méthodologie`, `Retour à l'accueil`, `Ce
  qu'il faut retenir`, `Exercice pratique`, `Solution & vérification`.

Keep this glossary at hand for `course.js` too: its locale strings live in
a `LOCALES` map (`{en: {...}, fr: {...}, es: {...}}`) selected by
`document.documentElement.lang` -- add your language's branch there with
the same wording as the glossary (done/verified/copy/copied/ago). Note the
`ago` suffix is appended AFTER the number (`"2 " + ago`), which fits
suffix-style phrasing (French "j", English "days ago") but not a
prefix-style one (Spanish "hace 2 días" needs the word BEFORE the number);
if the new language needs a prefix, either accept a terser elliptical form
(what the Spanish rollout did: "2 días", dropping "hace") or extend the
template -- don't silently ship a grammatically backwards string.

## 3. Copy the page skeletons

For each of the 16 FR pages (`index.html`, `methodology.html`, and the 14
chapter pages), copy `docs/<file>.html` to `docs/<code>/<file>.html`.
Chapter pages need the asset path prefixed (mirroring how `docs/en/` does
it): `assets/theme.css` -> `../assets/theme.css`, `assets/course.js` ->
`../assets/course.js`. `index.html`/`methodology.html` carry their CSS
inline, so no asset-path change is needed for those two.

File slugs are neutral English words on purpose (`control.html`,
`memory.html`, `scale.html`, `methodology.html`, etc.), the same across
every language -- only the CONTENT is translated, not the URL. This was a
deliberate fix: the site originally used French words as filenames even on
the English pages (`memoire.html`, `echelle.html`...), which read as
incoherent to a non-French reader. Don't introduce a new French (or any
other language's) word into a filename when adding a language -- reuse the
existing slug.

## 4. Extract, translate, inject the body text

Use `scripts/i18n/extract_text.py` -- a generic tool that walks the HTML,
skips `<script>`, `<style>`, `<code>`, `<pre>` and `<option>` (commands,
code samples, and language-code labels must never be translated), and pulls
out every real text node by exact position:

```bash
python scripts/i18n/extract_text.py extract docs/<code>/infra.html units.json
```

`units.json` is `{"t0": "text", "t1": "text", ...}` in document order.
Translate the VALUES only -- never add, remove, or rename keys, that's what
makes injection exact.

Each page's extract-translate-inject cycle is independent of every other
page's, so don't do all 16 serially in one context if you can avoid it.
Prefer whatever parallelism is actually available this turn: the Workflow
tool's `pipeline()` if multi-agent orchestration is active, otherwise spawn
one subagent per page via the Agent tool in a single batched call (each
subagent runs extract, translates its own units.json, and injects). Only
fall back to doing all 16 yourself, one at a time, if neither is available
-- it works, it's just slower and burns more of your own context on
translation text you don't need to keep around afterward.

Translation prompt rules (same discipline as the FR cleanup pass used for
English): translate everything to natural, technical, direct target-language
prose; never touch a numbered version, a product name (Claude Code,
CLAUDE.md, SKILL.md), or anything that looks like a command fragment that
slipped into a unit; keep the site's no-em-dash convention in the target
language too; return exactly the same key set, always. Paste the step-2
glossary VERBATIM into every one of these prompts -- that's what actually
prevents the inconsistency, not a post-hoc find/replace.

Then inject:

```bash
python scripts/i18n/extract_text.py inject docs/<code>/infra.html units_translated.json docs/<code>/infra.html
```

`inject` re-parses the CURRENT file and asserts the span count matches the
units file -- if the page changed shape since extraction (or you're
injecting into the wrong file) it fails loudly instead of silently
misplacing text. Re-extract from the current file if that happens; don't
force it.

## 5. Fix the mechanical bits inject can't reach

`inject` only replaces text nodes, so it will NOT touch:
- `<html lang="fr">` -> `<html lang="<code>">`
- `<title>`, meta `description`/`og:*`/`twitter:*` `content=` attributes
  (translate these directly, they're a handful of short lines per page)
- `<link rel="canonical">` and `og:url` -- point at the new `docs/<code>/...`
  URL
- the UI strings from step 2 (course.js `LOCALES` map, and any UI string
  baked directly into HTML like button labels -- these come from step 2's
  glossary, which you already handed to the step-4 agents, so this should
  already agree; it's here as the thing to double-check if it doesn't)
- `index.html` and `methodology.html` don't load `course.js` -- they carry
  their own small inline `<script>` (freshness-date text, and the language
  selector's change listener). `extract_text.py` correctly leaves JS string
  literals alone, which means their hardcoded FR text (e.g. `' · il y a '
  + days + ' j'`) survives untouched into the new language's copy and only
  shows up when the script actually runs in a browser -- it won't show in
  a text diff or an em-dash/quote grep. Check both inline scripts by hand
  and translate any literal UI string in them.

## 6. Propagate the language selector to every page

This is the one step that touches files OUTSIDE the new language's own
directory: every existing FR and EN page needs a new `<option>` added to its
selector so users can reach the new language from anywhere.

```bash
python scripts/i18n/add_lang_option.py
```

This rebuilds every page's `<select class="lang-switch">` from
`languages.json`, computing the correct relative path from each page's own
directory. It's idempotent -- run it any time after editing
`languages.json` and it only touches files whose selector actually changed.
Diff the result before committing; it should ONLY touch `<select>` blocks.

## 7. Update sitemap.xml and README

Add the 16 new URLs to `docs/sitemap.xml` (mirror the `en/` block). Add the
language to the README's language list.

## 8. Verify before committing

- **Consistency audit across the 16 pages.** Fanning translation out to
  parallel agents (step 4) means no single agent saw all 16 outputs. Even
  with the step-2 glossary in hand, check for drift: grep every page for
  the brand title and confirm it's byte-identical everywhere; diff the
  sidebar nav block across all 14 chapter pages (strip the `active` class
  first) and confirm they're identical; spot-check the quiz button text,
  feedback prefixes ("Correct."/"Not quite." equivalents), and section
  headings for the same wording on every page. A prior run needed several
  rounds of exactly this kind of sweep to catch drift the glossary alone
  didn't prevent.
- Grep the new pages for `&nbsp;[:?!;]` -- French's pre-punctuation
  non-breaking space sits in template glue outside the translatable spans,
  so it survives translation invisibly. Strip it wherever the target
  language doesn't use that convention (most don't).
- `git diff --stat` -- should show 16 new `docs/<code>/*.html` files, the
  existing pages with only `<select>` diffs, `languages.json`,
  `course.js`, `sitemap.xml`, `README.md`.
- Grep the new pages for `\"` (the exact bug that shipped once already) and
  for `—` (em dash -- the site's house style has none, in any language).
- Open 2-3 of the new pages locally in a browser (chrome-devtools MCP if
  available): check the page renders, the selector lists all languages with
  the right one marked selected, quizzes and copy buttons still work (they
  key off classes, not language, so should just work), and there's no
  horizontal overflow on mobile (375px width).
- Follow the live-verification discipline from past fixes on this site:
  after pushing, poll the GitHub Pages build status and re-check on the
  actual deployed URL, not just the local file -- this project has been
  bitten before by fixes that looked right locally but weren't visible live.
