# Vibe to Pro

A field manual on Claude Code, built from the official [CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (385 releases, `0.2.21` → `2.1.260`) and independently fact-checked against current documentation before anything is taught.

**[Read the course →](https://atypical-consulting.github.io/vibe-to-pro/)**

## What this is

Fourteen modules that take a "vibe-coder" — someone who prompts and hopes — to a professional Claude Code practice: permissions and sandboxing, memory, skills, plan mode, sub-agents, hooks, MCP, checkpoints, git worktrees, background workflows, plugins, and CI/CD.

## Method

1. **Extract** — every changelog entry across 385 versions is reviewed for major features (bugfixes excluded).
2. **Verify** — each candidate feature is checked independently against current docs on `code.claude.com`.
3. **Classify** — every fact is marked `confirmed`, `corrected` (behavior has since changed), or `unverifiable`.
4. **Publish** — only confirmed/corrected facts make it into the course, each with its source link. Unverifiable claims are dropped, never presented as fact.

## Structure

```
docs/
  index.html   — landing page
  cours.html   — the course (French)
```

Served via GitHub Pages from `main` / `docs`.

## License

MIT — see [LICENSE](LICENSE).
