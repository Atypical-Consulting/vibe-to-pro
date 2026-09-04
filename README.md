# Vibe to Pro

A field manual on Claude Code, built from the official [CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (385 releases, `0.2.21` to `2.1.260`) and independently fact-checked against current documentation before anything is taught. Available in French, English, Spanish, and Simplified Chinese.

**[Read the course →](https://atypical-consulting.github.io/vibe-to-pro/)**

## What this is

Fourteen chapters that take a "vibe-coder" (someone who prompts and hopes) to a professional Claude Code practice: permissions and sandboxing, memory, skills, plan mode, sub-agents, hooks, MCP, checkpoints, git worktrees, background workflows, plugins, and CI/CD. Each chapter has its own page: a short teaching lesson, a table of verified facts, two active-recall quizzes, and a hands-on exercise with a worked solution.

## Method

1. **Extract**: every changelog entry across 385 versions is reviewed for major features (bugfixes excluded).
2. **Verify**: each candidate feature is checked independently against current docs on `code.claude.com`.
3. **Classify**: every fact is marked `confirmed`, `corrected` (behavior has since changed), or `unverifiable`.
4. **Publish**: only confirmed/corrected facts make it into the course, each with its source link. Unverifiable claims are dropped, never presented as fact.

Full detail, including examples of discarded facts, on the [methodology page](https://atypical-consulting.github.io/vibe-to-pro/methodology.html).

## Structure

```
docs/
  index.html          landing page (French)
  methodology.html   verification methodology (French)
  prologue.html       chapter 00
  control.html       chapter 01
  ...                 one file per chapter (see the sidebar for the full list)
  epilogue.html       chapter 13
  assets/
    theme.css         shared design tokens and layout
    course.js         progress tracking, quizzes, code-block copy buttons
  en/
    (same structure, English)
  es/
    (same structure, Spanish)
  zh/
    (same structure, Simplified Chinese)
```

Every chapter page is self-contained and links to the next and previous one. Code samples use [Prism](https://prismjs.com/) for syntax highlighting with a copy button; progress and quiz results are tracked per-browser in `localStorage`, nothing is sent to a server. Served via GitHub Pages from `main` / `docs`.

## Maintaining the course

Two Claude Code skills automate the recurring maintenance work (`.claude/skills/`):

- **`add-language`**: adds a new language mirror (like `docs/en/`), translating all 16 pages and wiring up the language selector. Backed by `scripts/i18n/` (a generic HTML text-node extractor/injector that never touches code samples, plus a script that regenerates the `<select>` on every page from `scripts/i18n/languages.json`).
- **`refresh-changelog`**: pulls in a new Claude Code CHANGELOG version, verifies new candidate facts against current docs, and bumps the site's stats everywhere they're cited. Backed by `scripts/refresh/` (`site-meta.json` holds the counters as a single source of truth; `find_stale_numbers.py` finds every place a number is cited so a refresh doesn't miss one).

## License

MIT, see [LICENSE](LICENSE).
