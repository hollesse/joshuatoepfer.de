---
id: "0003"
title: "Build design system from scratch rather than forking Minima"
scope: design-system
status: accepted
date: 2026-05-26
supersedes: []
superseded_by: []
related_tasks: [design-system-001]
related_research: []
---

# ADR 0003: Build design system from scratch rather than forking Minima

## Context
joshuatoepfer.de needs a custom visual identity: dark-mode-first, minimalist, typography-driven.
The task notes offered two approaches: fork the Minima gem and strip it back, or build
from scratch with a custom `_layouts/default.html` and SCSS partials.

## Decision
Build from scratch using plain SCSS partials (`_tokens`, `_base`, `_typography`, `_layout`)
imported via `assets/css/main.scss`. No theme gem dependency.

## Consequences
### Positive
- Zero third-party theme dependency — no upstream changes to track or merge
- Full control over every CSS rule — nothing to fight against or override
- The design tokens are the only source of truth for colors, spacing, and typography
- Staying lean keeps the `Gemfile` minimal

### Negative
- No scaffold to copy from — every pattern is hand-rolled
- No built-in pagination, tag pages, or other Minima conveniences; those must be added explicitly by the website BC

### Neutral
- SCSS compilation is handled by Jekyll's built-in Sass processor; no additional build tool needed

## Alternatives considered
- **Fork Minima** — Lower initial effort, but Minima's HTML structure and class names would need constant fighting to match the custom visual direction. The maintenance cost shifts from "write CSS" to "override CSS". Not worth it for a single-developer personal site.
