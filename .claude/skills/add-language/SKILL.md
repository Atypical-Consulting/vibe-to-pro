---
name: add-language
description: >
  Add a new language mirror of the vibe-to-pro course (like docs/en/) --
  translates all 16 pages, wires up the language selector, updates the
  sitemap and README. Use when the user asks to add a language, translate
  the course into a new language, or mentions scripts/i18n/.
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

## 2. Translate the fixed UI strings once

Every page repeats the same boilerplate: "Progression", "Retour à
l'accueil", quiz button text, "Vérifier", etc. Do NOT run these through the
per-page pipeline below -- that would translate ~30 identical strings 16
times over and risk inconsistent wording. Instead, list every literal FR
UI string you can find outside chapter body text (grep `docs/*.html` for
short repeated labels: `Progression`, `Marquer comme lu`, `Précédent`,
`Suivant`, `Vérifier`, `Exact.`, `Pas tout à fait.`, `Test de niveau`, `Quiz
éclair`, `Méthodologie`, `Retour à l'accueil`, section headings like `Ce
qu'il faut retenir`, `Exercice pratique`, `Solution & vérification`) and
translate that short list with a single agent call. Keep the result at hand
for step 4's find/replace pass, and for `course.js`'s `L` locale object
(add a new branch alongside the existing `isEN` one, keyed on
`document.documentElement.lang === "<code>"`).

## 3. Copy the page skeletons

For each of the 16 FR pages (`index.html`, `methodologie.html`, and the 14
chapter pages), copy `docs/<file>.html` to `docs/<code>/<file>.html`.
Chapter pages need the asset path prefixed (mirroring how `docs/en/` does
it): `assets/theme.css` -> `../assets/theme.css`, `assets/course.js` ->
`../assets/course.js`. `index.html`/`methodologie.html` carry their CSS
inline, so no asset-path change is needed for those two.

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
makes injection exact. Do this per page with a `pipeline()` over the 16
files so one page's translation doesn't block another's:

```js
const PAGES = ["index","methodologie","prologue","controle","memoire","skills",
               "plan","agents","hooks","mcp","rewind","git","echelle","plugins",
               "infra","epilogue"]
// for each page: extract -> agent(translate units.json) -> write translated json -> inject
```

Translation prompt rules (same discipline as the FR cleanup pass used for
English): translate everything to natural, technical, direct target-language
prose; never touch a numbered version, a product name (Claude Code,
CLAUDE.md, SKILL.md), or anything that looks like a command fragment that
slipped into a unit; keep the site's no-em-dash convention in the target
language too; return exactly the same key set, always.

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
- the UI strings from step 2 (course.js `L` object, and any UI string baked
  directly into HTML like button labels -- these come from step 2's list,
  find/replace them by hand since `extract_text.py` already pulled them out
  as regular translatable units in step 4; just make sure the step-2 list
  and step-4 translations agree so the same phrase isn't translated two
  different ways on the same page)

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

- `git diff --stat` -- should show 16 new `docs/<code>/*.html` files, the
  32 existing pages with only `<select>` diffs, `languages.json`,
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
