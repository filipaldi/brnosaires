# Cluster

## The problem

Groups of elements that differ in length and are liable to wrap — buttons, tags, keywords, nav links — need fluid distribution without unsightly gaps or doubles spaces from inline-block approaches.

## The solution

Flexbox with `gap`:

```css
.cluster {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space, 1rem);
  justify-content: flex-start;
  align-items: center;
}
```

## Use cases

- Buttons at the end of forms
- Lists of tags or keywords
- Page header with logo + navigation (use `justify-content: space-between` and `align-items: center`)

## Props API

| Name | Type | Default | Description |
|---|---|---|---|
| justify | string | `flex-start` | A CSS `justify-content` value |
| align | string | `flex-start` | A CSS `align-items` value |
| space | string | `var(--s1)` | A CSS gap value |

## Examples

```html
<!-- Basic -->
<cluster-l>
  <!-- child elements -->
</cluster-l>

<!-- List semantics (recommended for groups of similar elements) -->
<cluster-l role="list">
  <div role="listitem">...</div>
  <div role="listitem">...</div>
</cluster-l>
```
