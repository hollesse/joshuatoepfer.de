---
id: infra-003
title: "Spike: Walking skeleton — Jekyll boots and deploys to Netlify"
type: spike
status: done
completed: 2026-05-26
context: infrastructure
depends_on: [infra-001, infra-002]
---

# Spike: Walking skeleton

## Goal
Prove that the full stack runs end-to-end: Jekyll builds successfully, Netlify deploys
the result, and a visitor can load a page at the joshuatoepfer.de URL. Feature-thin,
architecture-thick — no real content needed, just proof the pipeline works.

## Acceptance criteria
- [x] `bundle exec jekyll build` completes without errors locally
- [ ] A push to main triggers the GitHub Actions deploy workflow (requires push — not verifiable locally)
- [ ] Netlify publishes the build and the site is reachable at the configured URL (requires deploy — not verifiable locally)
- [x] At least one sample post renders correctly (any placeholder content)
- [x] The `_talks` collection is wired up (even if empty — it needs to exist for later tasks)
- [x] `netlify.toml` and `Gemfile.lock` are committed (reproducible builds)

## Notes
This is the project's first working prototype. It does not need to look good — that is
the design-system's job. It needs to exist and be reachable. Keep it as thin as possible;
resist the urge to add features here.

After this task is done, the design-system styleguide task (design-system-001) is unblocked.

## Verifier note (iteration 1)

REASONS:
- `Gemfile.lock` exists on disk but is untracked (not committed). A fresh `git clone` would have no `Gemfile.lock`, breaking reproducible builds.
- `_talks/` is an empty directory — git does not track empty directories. No `.gitkeep` was added, so the directory won't survive a fresh clone.

SUGGESTED_FIX: Add `_talks/.gitkeep` (empty file) to make the directory trackable in git. Then re-run `bundle exec jekyll build` to confirm it still passes. The orchestrator will include `Gemfile.lock` in the git add.

ITERATION_HINT: likely-fixable

## Outcome
Created the minimal Jekyll skeleton: `_config.yml` (with `_talks` collection wired up),
`_layouts/default.html`, `index.html`, `_posts/2026-05-26-hello-world.md`, and generated
`Gemfile.lock` via `bundle install`. `bundle exec jekyll build` completes without errors
and the sample post renders to `_site/posts/2026/05/26/hello-world/`. Remote criteria
(GitHub Actions trigger, Netlify URL) require a push to main to verify.
