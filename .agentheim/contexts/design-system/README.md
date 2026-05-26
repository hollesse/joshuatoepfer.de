# Design System

## Purpose
The visual identity layer for joshuatoepfer.de — defines the Jekyll theme, dark mode
implementation, typography scale, color palette, and reusable component patterns.
Every frontend feature in any BC must depend on this context's styleguide task
(`design-system-001`) before implementing any UI. This is a gate, not a guideline.

## Classification
Supporting

## Actors
- **Joshua** — sole designer and developer; signs off on the styleguide before any
  frontend work in other BCs begins

## Ubiquitous language
- **Token** — a named design variable (color, spacing, font size) exposed as a CSS
  custom property
- **Dark mode** — the primary visual mode using a dark background palette; implemented
  via `prefers-color-scheme` media query with optional manual toggle
- **Component** — a reusable Jekyll `_include` with a defined HTML structure and
  associated styles
- **Typography scale** — the defined set of font sizes and line heights used consistently
  across the site

## Aggregates
Not applicable.

## Key events
- `StyleguideApproved` — Joshua has reviewed and signed off on the design system;
  frontend work in other BCs may proceed

## Key commands
- Define color tokens
- Define typography scale
- Implement and verify dark mode

## Relationships with other contexts
- **Consumed by:** website (conformist — website adapts to this BC's design decisions)

## Open questions
- Custom Jekyll theme from scratch, or fork of a minimal existing theme (e.g., Minima)?
