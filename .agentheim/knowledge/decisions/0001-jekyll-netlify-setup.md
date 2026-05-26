---
id: "0001"
title: "Jekyll + Netlify base configuration"
status: accepted
date: 2026-05-26
deciders: [joshua]
---

# ADR-0001: Jekyll + Netlify base configuration

## Context

joshuatoepfer.de is a personal site built and maintained by a single developer (Joshua
Töpfer). Joshua already uses Jekyll for other static sites and wants to remain on a
familiar toolchain. The hosting platform is Netlify. The goal is maximum simplicity and
low maintenance overhead, not cutting-edge build performance.

## Decision

Use **Jekyll 4.4.1** (latest stable) as the static site generator, **Netlify** for
hosting, and **GitHub Actions** for CI. A build-and-deploy workflow triggers on every
push to `main`. The Ruby version is pinned in `.ruby-version` (and mirrored in
`netlify.toml`) to avoid build surprises across local environments and Netlify's build
image.

Build command: `bundle exec jekyll build`
Publish directory: `_site`
Ruby version: 3.4.2

## Consequences

### Positive
- Familiar toolchain — no new framework to learn, reducing ramp-up time
- Netlify handles SSL, CDN, atomic deploys, and preview deploys out of the box
- GitHub Actions is already used for the content sync workflow (ADR-0002), so CI
  infrastructure is shared

### Negative
- Jekyll's Ruby dependency adds local setup friction compared to binary SSGs
- Build speed is slower than Hugo or Astro, but irrelevant at personal-site scale (< 200
  pages expected)

## Alternatives considered

| Alternative | Reason rejected |
|-------------|-----------------|
| Hugo        | Faster and no Ruby dependency, but unfamiliar; switching cost not justified for a personal site |
| Astro       | Modern and capable, but overkill for a content-first personal site with no interactive components |
| Eleventy    | Closer to Jekyll's philosophy, but still requires learning a new config system |
