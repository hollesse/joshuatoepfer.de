---
id: infra-001
title: "Decision: Jekyll + Netlify base configuration"
type: decision
status: done
context: infrastructure
depends_on: []
completed: 2026-05-26
---

# Decision: Jekyll + Netlify base configuration

## What needs to be decided
Lock down the exact Jekyll version, the Netlify configuration (publish directory,
build command, Ruby version), and the GitHub Actions workflow structure for the
main deploy pipeline (push to main → build → deploy).

## Acceptance criteria
- [x] ADR committed under `.agentheim/knowledge/decisions/0001-jekyll-netlify-setup.md`
- [x] `netlify.toml` or equivalent Netlify config is in the repo root
- [x] GitHub Actions deploy workflow (`.github/workflows/deploy.yml`) is defined
- [x] `Gemfile` with pinned Jekyll version is present
- [x] Justification in the ADR matches the draft below (or user-amended version)

## Notes (ADR draft)

**Context:** joshuatoepfer.de is a personal site built by a single developer. The user
already uses Jekyll for other static sites and wants to remain on it. Netlify is the
chosen host. The goal is maximum simplicity and low maintenance overhead.

**Decision:** Use Jekyll (latest stable) with Netlify for hosting. GitHub Actions
triggers a build-and-deploy on every push to main. Ruby version pinned in `.ruby-version`
to avoid build surprises on Netlify.

**Positives:**
- Familiar toolchain — no new framework to learn
- Netlify handles SSL, CDN, and preview deploys out of the box
- GitHub Actions is already used for content sync (see infra-002)

**Negatives:**
- Jekyll's Ruby dependency adds some local setup friction
- Not as fast to build as newer SSGs (Astro, Hugo) but irrelevant at personal-site scale

**Alternatives considered:**
- Hugo — faster, no Ruby dependency, but unfamiliar; switching cost not justified
- Astro — modern but overkill for a content-first personal site

## Outcome

ADR written at `.agentheim/knowledge/decisions/0001-jekyll-netlify-setup.md` capturing
the Jekyll 4.4.1 + Netlify + GitHub Actions decision with full context and alternatives.

Config files created:
- `netlify.toml` — build command, publish dir, Ruby version, preview deploy contexts
- `.github/workflows/deploy.yml` — CI build on push to main (Netlify GitHub integration
  handles production deploys; workflow validates builds and uploads artifact)
- `Gemfile` — Jekyll 4.4.1 pinned with jekyll-feed, jekyll-seo-tag, jekyll-sitemap
- `.ruby-version` — 3.4.2 (read by both `ruby/setup-ruby` action and Netlify)
