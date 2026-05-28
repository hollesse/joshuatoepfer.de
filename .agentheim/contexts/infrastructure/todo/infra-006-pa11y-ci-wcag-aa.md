---
id: infra-006
title: "Automated WCAG AA checks via pa11y-ci in CI (light + dark mode)"
status: todo
type: feature
context: infrastructure
created: 2026-05-28
completed:
commit:
depends_on: []
blocks: [design-system-002]
tags: [ci, accessibility, wcag, pa11y, github-actions]
related_adrs: []
related_research: []
prior_art: [infra-001, infra-003]
---

## Why
`design-system-002` (light-mode accent contrast) showed that a real WCAG
AA regression can sit in the codebase for weeks without being noticed —
the failure was only caught by manual measurement during the
design-system-003 refinement. As the site fills up with INNOQ-synced
posts whose body HTML we don't author directly, the risk of an
accessibility regression slipping in only grows.

Joshua decided 2026-05-28: defer the actual accent fix; instead, build
the automated check first. Once pa11y-ci reports concrete failures, the
accent-fix conversation gets clearer data (which pages, which elements,
exactly which contrast ratios) and can be re-refined.

This task also catches future regressions from:
- Synced INNOQ posts whose body markup has poor contrast (unlikely but
  worth detecting)
- Token tweaks (the lurking risk after any `_sass/_tokens.scss` change)
- Layout changes that affect text-on-background relationships
- New pages added to the website BC

## What
Add a GitHub Actions workflow `.github/workflows/accessibility.yml` that
builds the site, serves it, and runs `pa11y-ci` against a known list of
URLs in **both** `data-mode="dark"` (the default) and `data-mode="light"`.

The workflow fails (red, blocking PR merge) if any URL × mode
combination produces a WCAG 2.1 AA violation. Joshua sees the failure in
the GH Actions tab and the PR check status.

A `.pa11yci.json` config in the repo root lists the URLs, the WCAG
standard, and the `actions` script that flips `data-mode` for the
light-mode pass.

## Decisions (all baked in for the worker)

### Tool: pa11y-ci via ephemeral npx
- No `package.json` is added to the repo. The project stays Ruby-first.
- The workflow uses `npx --yes pa11y-ci@<pinned-version>` to run the
  check on demand. Pin the latest stable version of pa11y-ci as of
  task-execution date.
- Node is pre-installed in `ubuntu-latest`; no `actions/setup-node`
  step needed.

### WCAG standard: 2.1 AA
- pa11y-ci default. Catches both 4.5:1 (body text) and 3:1 (large text /
  UI components) contrast requirements, plus all other AA criteria
  (alt text, landmarks, focus order, etc.).

### Triggers
- `pull_request` against `main` — gates merging
- `push` to `main` — catches regressions if anything bypasses PR review
- `workflow_dispatch` — manual re-run for debugging

### Page coverage (URL list)
The seven implemented routes plus one representative post page:
- `/`
- `/blog/`
- `/talks/`
- `/ueber-mich/`
- `/impressum/`
- `/datenschutz/`
- `/posts/2026/05/27/hello-welt/` — the only post currently

Listed in `.pa11yci.json` under `urls`. When new posts land via the sync
workflow (`infra-004`), the URL list does **not** auto-expand — explicit
opt-in keeps the test fast and predictable. A future task may add
glob-based discovery if needed.

### Light + dark mode coverage
Each URL is tested **twice**:

1. **Dark mode** (default) — pa11y-ci's standard configuration.
2. **Light mode** — pa11y-ci `actions` config runs JavaScript before the
   audit: `["evaluate: document.documentElement.dataset.mode = 'light'"]`
   to flip the `data-mode` attribute (which is how the site's mode
   mechanism works per ADR-0005). This catches light-mode-specific
   contrast failures (precisely what `design-system-002` is about).

This is implemented as two top-level entries per URL in the pa11yci
config, or as a single URL with a per-URL `actions` override — worker
picks whichever pa11y-ci configures more cleanly.

### Fail mode: yes
- A single WCAG 2.1 AA violation on any URL × mode combination → workflow
  fails. No "warning-only" mode for AA criteria — A and AA are required
  for the site Joshua wants to ship.
- AAA criteria are not checked (would be over-restrictive for a
  text-heavy editorial site).

### Build + serve approach
1. `actions/checkout@v4`
2. `actions/setup-ruby@v1` with Bundler caching (matches the existing
   `deploy.yml` pattern)
3. `bundle install`
4. `bundle exec jekyll build`
5. Start a local server in the background: `bundle exec jekyll serve --no-watch --skip-initial-build --detach` (or `npx serve _site -p 4000` if simpler). Wait for `localhost:4000` to be reachable (small bash loop with `curl`).
6. `npx --yes pa11y-ci@<pinned-version>` — reads `.pa11yci.json`, runs all checks.
7. Workflow exits with pa11y-ci's exit code.

## Files delivered

| File | Purpose |
| --- | --- |
| `.github/workflows/accessibility.yml` | The workflow described above |
| `.pa11yci.json` | URL list, WCAG standard config, light-mode `actions` script |
| `infrastructure/README.md` | New "Accessibility checks" sub-section under existing CI section pointing at the workflow + the config file, plus a one-liner on how Joshua can run pa11y-ci locally (`npx pa11y-ci` after `bundle exec jekyll serve` in another terminal) |

## Acceptance criteria

- [ ] `.github/workflows/accessibility.yml` exists with triggers on `pull_request`, `push` to `main`, and `workflow_dispatch`.
- [ ] Workflow checks out, builds Jekyll, serves the build, runs `npx --yes pa11y-ci@<version>` against the served site, and exits non-zero on any failure.
- [ ] `.pa11yci.json` is present at repo root, lists the seven URLs above, uses WCAG 2.1 AA standard.
- [ ] Each URL is tested in **both** dark mode (default) and light mode (via a `data-mode="light"` JS injection). The light-mode test reproducibly catches the current `design-system-002` contrast failures (amber/coral/lime light-mode accents against `#f7f7f5`) — confirm by running the workflow once on a PR branch and inspecting the failure output.
- [ ] `bundle exec jekyll build` still passes (no impact on the build itself).
- [ ] `infrastructure/README.md` has an "Accessibility checks" section explaining the workflow, the config file location, and how to run pa11y-ci locally.
- [ ] First run of the workflow on a PR branch **expectedly fails** — this is the proof that the check is wired correctly. The failure surfaces the exact accent × URL combinations that `design-system-002` will need to address. Document the first failure output in the task's Outcome section as a hand-off to `design-system-002`'s next refinement.

## Notes
- This task is intentionally **scoped to building the check, not fixing what it finds**. The first failed run is the success criterion. Joshua then re-refines `design-system-002` with the concrete pa11y-ci output and picks a fix path (likely option C from the conversation — `color: inherit` for `.post-body a`, no token changes).
- Worker should NOT attempt to "fix" the contrast issue to make the check pass. That's `design-system-002`'s job. The first PR for this task should ship with a red workflow — Joshua reviews the failure output, then merges anyway, signaling that the check is correctly catching the known issue. (Optionally: temporarily allow the workflow to fail without blocking the PR for this specific task's commit — but that's brittle. Simpler: merge with a known red workflow run that's marked "expected" in the PR description.)
- Future enhancements (not in scope):
  - Glob-based URL discovery once the post count grows
  - Integration with axe-core for a second tool's-eye check
  - Storybook-style component-level accessibility tests
  - Per-PR comment summarising violations
- The choice between `bundle exec jekyll serve` vs `npx serve _site` for the local server step: both work. Worker picks the one that integrates more cleanly with pa11y-ci's URL list (relative `/blog/` vs absolute `http://localhost:4000/blog/`). `pa11y-ci`'s URL list is absolute by default; either way it'll need `http://localhost:4000` prepended.
- pa11y-ci version: pin to whatever is the latest stable when the task is worked. Version-pinning matters for reproducibility; allow Dependabot or manual bumps to update it.
- The `_site/` path is `.gitignore`'d (per `infra-001`), so the workflow always builds fresh — that's the correct behaviour.
- This task does NOT add Lighthouse, axe-core, or any other accessibility tool. `pa11y-ci` is the chosen single tool. Stacking tools is a future consideration if the audit surface grows.
- The workflow does not run on commits to the `gh-pages` branch (if any) or feature branches that haven't opened a PR. The `push to main` + `pull_request` combo is sufficient.
