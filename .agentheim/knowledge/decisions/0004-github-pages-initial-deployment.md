---
id: "0004"
title: "Use GitHub Pages as initial deployment target"
scope: infrastructure
status: accepted
date: 2026-05-26
supersedes: []
superseded_by: []
related_tasks: []
related_research: []
---

# ADR 0004: Use GitHub Pages as initial deployment target

## Context
ADR-0001 specified Netlify as the hosting platform. Before any Netlify site was configured,
the decision was revisited: GitHub Pages requires zero additional service setup (the repo is
already on GitHub) and is the fastest path to a live deployment. Netlify remains a planned
future host once the site is established and a custom domain is in place.

The repository `hollesse/joshuatoepfer.de` is a project repository (not `<username>.github.io`),
so GitHub Pages serves the site at `https://hollesse.github.io/joshuatoepfer.de/` with
baseurl `/joshuatoepfer.de` until a custom domain is configured.

## Decision
Deploy to GitHub Pages via GitHub Actions using the official pages deployment actions
(`actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages`).
The `netlify.toml` file is kept in the repository unchanged for the eventual Netlify migration.

## Consequences
### Positive
- Zero additional service configuration — GitHub Pages is enabled in repo settings only
- Official actions handle baseurl automatically for project pages
- No secrets or tokens needed; GitHub manages deployment auth via OIDC
- `netlify.toml` stays in the repo, so migration to Netlify requires only adding the Netlify
  site connection and removing the GitHub Pages workflow

### Negative
- Project page URL (`/joshuatoepfer.de` baseurl) is awkward until a custom domain is set;
  all internal links must use `relative_url` filter (already done in templates)
- GitHub Pages has a soft limit of 1 GB repo size and 100 GB/month bandwidth — fine for a
  personal blog, worth knowing

### Neutral
- `JEKYLL_ENV=production` is still set; SEO tags and feed are generated the same way
- `netlify.toml` in the repo is inert until a Netlify site is connected

## Alternatives considered
- **Keep Netlify from the start** — Requires creating a Netlify account, connecting the repo,
  and configuring the site before seeing a live URL. More setup for the same outcome at this stage.
- **GitHub Pages from branch (`gh-pages`)** — Older pattern, requires a separate deploy step
  and a `gh-pages` branch. The Actions-based approach is simpler and is GitHub's recommended
  current method.

## Migration path to Netlify (when ready)
1. Create a Netlify site connected to the repository
2. Configure the custom domain on Netlify
3. Delete `.github/workflows/deploy.yml` (or replace it with a no-op)
4. The `netlify.toml` already has the correct build config
