# Sidebar

## The solution

One element has a fixed sidebar width; the other takes all remaining space. Wraps to vertical when content is too narrow — no `@media` queries needed.

```css
.sidebar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s1);
}

/* Sidebar element */
.sidebar > :first-child {
  flex-basis: 20rem;
  flex-grow: 1;
}

/* Non-sidebar (main content) */
.sidebar > :last-child {
  flex-basis: 0;
  flex-grow: 999;
  min-inline-size: 50%;
}
```

The `min-inline-size: 50%` forces wrapping when the non-sidebar would be less than 50% of the container — the point at which a sidebar stops being a sidebar.

## Intrinsic sidebar width

Omit `flex-basis` on the sidebar to let its content determine the width:

```css
.sidebar > :first-child {
  flex-grow: 1;
}
```

## Props API

| Name | Type | Default | Description |
|---|---|---|---|
| side | string | `left` | Which element is the sidebar (`left` or `right`) |
| sideWidth | string | — | Sidebar width when adjacent (omit for content-based) |
| contentMin | string | `50%` | Min width of content before wrapping |
| space | string | `var(--s1)` | Gap between elements |
| noStretch | boolean | false | Use natural heights instead of equal heights |

## Examples

```html
<!-- Media object -->
<sidebar-l space="var(--s2)" sideWidth="15rem" noStretch>
  <img src="..." alt="..." />
  <p><!-- text --></p>
</sidebar-l>

<!-- Search bar (button is sidebar, right side) -->
<form>
  <sidebar-l side="right" space="0" contentMin="66.666%">
    <input type="text">
    <button>Search</button>
  </sidebar-l>
</form>
```
