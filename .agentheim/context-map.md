# Context map

## Contexts

### website
- **Purpose:** The Jekyll site itself — content model (posts, talks, pages), layouts,
  templates, and the structures that turn markdown source files into a coherent personal
  website for readers and conference organizers.
- **Core language:** post, syndicated post, personal post, talk, appearance, tag, collection,
  layout, frontmatter
- **Classification:** core
- **Key actors:** readers, conference organizers, Joshua (as author and content curator)

### design-system
- **Purpose:** The visual identity layer — Jekyll theme, dark mode implementation,
  typography scale, color palette, spacing, and reusable layout patterns. All frontend
  work in any BC depends on this context's styleguide before building any UI.
- **Core language:** token, dark mode, component, typography scale, color palette
- **Classification:** supporting
- **Key actors:** Joshua (sole designer/developer, signs off on the styleguide)

### infrastructure
- **Purpose:** Everything that makes the site run and stay current — Netlify deployment
  configuration, GitHub Actions CI/CD pipeline, and the automated sync workflows that
  pull content from innoq.com and open pull requests. Owns globally-true operational
  concerns; BC-local concerns stay in the originating BC.
- **Core language:** build, deploy, sync workflow, sync PR, pipeline
- **Classification:** supporting
- **Key actors:** GitHub Actions (automated runner), Joshua (PR reviewer), Netlify (host)

## Relationships

- **website → design-system:** Conformist. The Jekyll site consumes the theme and tokens
  defined in the design-system; it adapts to what design-system provides.
- **infrastructure → website:** Infrastructure builds and deploys the website's artifacts.
  Sync workflows create content files that land in the website's Jekyll collections.
- **infrastructure → design-system:** Infrastructure deploys all built artifacts, including
  those from the design-system.
