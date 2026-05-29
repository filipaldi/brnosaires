---
name: styles
description: CSS authoring rules for Brnos Aires — check existing variables and utilities before writing any new CSS. Includes Every Layout primitive reference. Use when editing any CSS file.
paths:
  - "**/*.css"
  - "theme/static/css/**"
---

## CSS Rules

**NEVER create new CSS before checking existing styles.**

CSS lives in `theme/static/css/`:
- `variables.css` — check **first** for all custom properties
- `layout.css` — layout utilities (see Every Layout docs below)
- `spacing.css` — spacing utilities
- `aesthetic.css` — visual/decorative utilities
- `typography.css` — type utilities
- `components.css` — component shorthands (see Frame doc)

## Adding New Utilities

- Discuss what kind of utility is needed and how it fits the existing system
- Get user confirmation before defining a new utility

## Adding New Components

- Components are shorthands for underlying utility classes
- **DO NOT** define component styles when fewer than 3 utility classes are involved

## Every Layout Reference

These layout primitives are used in this project. Read the relevant doc when working with each:

- **Box** — `${CLAUDE_SKILL_DIR}/box.md`
- **Stack** — `${CLAUDE_SKILL_DIR}/stack.md`
- **Cluster** — `${CLAUDE_SKILL_DIR}/cluster.md`
- **Center** — `${CLAUDE_SKILL_DIR}/center.md`
- **Sidebar** — `${CLAUDE_SKILL_DIR}/sidebar.md`
- **Grid** — `${CLAUDE_SKILL_DIR}/grid.md`
- **Reel** — `${CLAUDE_SKILL_DIR}/reel.md`
- **Imposter** — `${CLAUDE_SKILL_DIR}/imposter.md`
- **Frame** — `${CLAUDE_SKILL_DIR}/frame.md` (scoped to `components.css`)
