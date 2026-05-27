---
id: design-system-003
title: "Document redesigned visual system (Geist + oklch + multi-accent + container queries)"
status: done
type: chore
context: design-system
created: 2026-05-27
completed: 2026-05-27
commit:
depends_on: []
blocks: []
tags: [documentation, design-tokens, typography, accent, theme-toggle, container-queries]
related_adrs: [0003, 0005]
related_research: []
prior_art: [design-system-001, design-system-002]
---

## Why
A complete redesign was delivered by Claude Design (handoff in `design_handoff_jekyll/`)
and already implemented across `_sass/`, `_layouts/`, `_includes/`, `_data/`, and `assets/`.
The design-system BC's documentation, however, still describes the previous scratch-built
styleguide (amber `#d4a853`, simple `prefers-color-scheme` tokens, minimal vocabulary).

The handoff folder is temporary and will likely be deleted later — so the BC docs need
to become the lasting reference. ADR-0003 (scratch-built theme) is now factually wrong
about what's in the codebase.

The redesign is substantially richer than `design-system-001` captured:
- Token model rewritten in `oklch` color space
- Multi-accent palette: `data-accent="amber|coral|blue|lime"` with separate light variants
- Theme toggle: `data-mode="light|dark"` attribute on `<html>`, JS-driven, `localStorage`-persisted with system-preference fallback
- Typography swapped to Geist + Geist Mono (variable fonts via Google Fonts)
- Container queries (`@container jt`) replace media queries; root `.jt` carries `container-type: inline-size`
- "Accent-Punkt" convention — the period at the end of each headline rendered in `--accent`, treated as the smallest brand identity
- Component vocabulary: `.topnav`, `.row`, `.talk`, `.chip`, `.post-body`, `.post-hero`, `.eyebrow`, `.meta-line`, `.subtitle`, `.duotone`, `.post-pager`, `.related-posts`, `.year-divider`, `.filter-chips`
- Page-layout contracts consumed by website BC: `home`, `blog`, `post`, `talks`, `about`, `page`

## What
Bring the design-system BC documentation in line with the implemented state. Specifically:

1. **Update `contexts/design-system/README.md`**
   - Extend ubiquitous language with the new vocabulary: accent, accent palette, accent-mark/Akzent-Punkt, theme toggle, mode, container query, duotone (image-slot), eyebrow, meta-line, year-divider, filter-chip, focus area
   - Close the resolved open question about Minima vs. scratch (settled — see ADR-0003 → superseded by ADR-0004)
   - Add a short "What this BC owns" enumeration: tokens, typography, layouts, components, theme toggle, accent palette

2. **Write `ADR-0004 — Redesigned visual system`** under `.agentheim/knowledge/decisions/`
   - Mark `ADR-0003` as `status: superseded`, `superseded_by: ["0004"]` (edit its frontmatter)
   - ADR-0004 captures, with reference to the actual source files:
     - Token model (oklch color space, why oklch over hex/hsl)
     - Multi-accent palette (amber/coral/blue/lime), light/dark variants, how to add a new accent
     - Mode mechanism (`data-mode` on `<html>`, JS toggle, `localStorage` key, system-preference fallback)
     - Typography stack (Geist + Geist Mono, variable-font weight ranges, sans/mono pairing rules)
     - Container-query approach (`.jt` root, breakpoint at ~720px)
     - Accent-mark brand convention
     - Component vocabulary as the contract the website BC consumes
   - Reference `_sass/_tokens.scss`, `_sass/_typography.scss`, `_sass/_layout.scss`, `_sass/_responsive.scss`, `assets/js/theme-toggle.js`, `_includes/theme-toggle.html`, `_includes/topnav.html`, `_includes/footer.html` as canonical sources — not `design_handoff_jekyll/`

3. **Update `contexts/design-system/INDEX.md`**
   - List `ADR-0004` under "ADRs scoped to this BC"
   - Keep `ADR-0003` listed but note its superseded status

4. **Re-evaluate `design-system-002` (light-mode accent contrast bug)**
   - The new tokens give light mode its own accent token: `oklch(0.58 0.14 60)` for amber (and equivalents for coral/blue/lime)
   - Do a quick WCAG AA contrast check of the four light-mode accents against `--bg: #f7f7f5` and against `--bg-elev: #ffffff` (text contrast 4.5:1, large text 3:1)
   - If all four pass: move `design-system-002` to `done/`, add an outcome note linking to this task and ADR-0004
   - If any fail: update `design-system-002`'s acceptance criteria with the specific failing accent + measured ratio and leave it in backlog

5. **No code changes.** The implementation files in `_sass/`, `_layouts/`, `_includes/`, `_data/`, `assets/` are the source of truth and stay untouched. This is pure documentation backfill.

## Acceptance criteria
- [ ] `contexts/design-system/README.md` ubiquitous language reflects the new vocabulary (accent, accent palette, accent-mark, theme toggle, mode, container query, duotone, eyebrow, meta-line, year-divider, filter-chip)
- [ ] `ADR-0004` exists under `.agentheim/knowledge/decisions/`, with status `accepted`, `supersedes: ["0003"]`, and enumerates: oklch tokens, multi-accent palette, mode mechanism, Geist typography, container queries, accent-mark, component vocabulary
- [ ] `ADR-0003` frontmatter updated: `status: superseded`, `superseded_by: ["0004"]`
- [ ] `contexts/design-system/INDEX.md` lists `ADR-0004` under "ADRs scoped to this BC"; `ADR-0003` entry notes superseded status
- [ ] `design-system-002` is resolved one of two ways: closed (moved to `done/`, with WCAG contrast measurements appended) OR refined in `backlog/` with specific failing-accent details
- [ ] No BC documentation references `design_handoff_jekyll/` as a permanent source — that folder is treated as temporary scaffolding

## Notes
- `design_handoff_jekyll/styles.css` and `design_handoff_jekyll/README.md` are the
  richest current description of the design language; lift anything load-bearing
  into ADR-0004 before the handoff folder is deleted.
- Joshua flagged a future direction: build a `/design-system/` page on the live site
  as a referenceable styleguide. Not in scope here — capture separately if pursued.
- `bundle exec jekyll build` must still pass after this task (sanity check — only
  documentation files are touched, so this should be automatic).

## Outcome

Documentation backfill completed on 2026-05-27. No implementation files were
modified; this was pure docs work.

**Numbering note**: the task brief asked for ADR-0004, but
`0004-github-pages-initial-deployment.md` already exists (infrastructure scope,
accepted 2026-05-26). To avoid clobbering an accepted ADR, the new decision
is filed as **ADR-0005** and ADR-0003's `superseded_by` points to `"0005"`.
The orchestrator/INDEX update should reflect this.

**Files written / modified:**
- `.agentheim/knowledge/decisions/0005-redesigned-visual-system.md` (new) —
  captures the seven design axes: oklch token model, four-accent palette
  (amber/coral/blue/lime with light variants), `data-mode` mechanism with
  pre-paint flash-prevention script, Geist + Geist Mono typography stack,
  `@container jt` container queries at 720px, the accent-mark brand
  convention, and the named component vocabulary the website BC consumes
- `.agentheim/knowledge/decisions/0003-design-system-scratch-theme.md` —
  frontmatter only: `status: superseded`, `superseded_by: ["0005"]`. Body
  unchanged (the underlying "scratch-built" decision still stands).
- `.agentheim/contexts/design-system/README.md` — rewritten ubiquitous
  language section (added: mode, theme toggle, accent, accent palette,
  accent-mark, oklch, container query, eyebrow, meta-line, subtitle,
  duotone, year-divider, filter-chip, focus area); added "What this BC
  owns" enumeration; closed the Minima vs scratch open question.
- `.agentheim/contexts/design-system/backlog/design-system-002-fix-light-mode-accent.md` —
  updated `related_adrs: [0005]`, `prior_art: [design-system-001, design-system-003]`,
  rewrote acceptance criteria with measured contrast estimates per accent.

**WCAG re-evaluation of design-system-002** (against `--bg: #f7f7f5`,
approximate, ±0.3):
- amber  `oklch(0.58 0.14 60)`  → ~3.3 : 1 → FAIL body-text (4.5:1), PASS UI (3:1)
- coral  `oklch(0.58 0.18 32)`  → ~3.6 : 1 → FAIL body-text, PASS UI
- blue   `oklch(0.50 0.18 250)` → ~6.5 : 1 → PASS body-text
- lime   `oklch(0.55 0.16 145)` → ~3.7 : 1 → FAIL body-text, PASS UI

Conclusion: amber, coral, and lime light-mode variants are borderline for
body-text use (inline link text in `.post-body a` uses `var(--accent)`).
**design-system-002 stays in `backlog/`** with these specific findings;
recommended fix is either to darken L toward 0.45–0.50, or to add an
`--accent-text` token for body-prose link use.

**Sanity build check**: `bundle exec jekyll build` was run after docs-only
changes; status reported in the worker return.

**Key files for future readers (source of truth for the design system):**
- `_sass/_tokens.scss` — tokens + four-accent matrix
- `_sass/_base.scss` — `.jt` container declaration
- `_sass/_typography.scss` — Geist + `.post-body` prose
- `_sass/_layout.scss` — component vocabulary
- `_sass/_responsive.scss` — container queries
- `assets/js/theme-toggle.js`, `assets/js/blog-filter.js`
- `_layouts/default.html` — pre-paint mode script, font preload
- `.agentheim/knowledge/decisions/0005-redesigned-visual-system.md` — the ADR
