# Box

## The problem

All the ensuing layouts deal in arranging boxes together; distributing them in some way such that they form a composite visual structure. The Box's role within this layout system is to take care of any styles that are intrinsic to individual elements — styles which are not dictated, inherited, or inferred from the meta-layouts to which an individual element may be subjected.

## The solution

Padding is different from margin — it reaches into an element; it is introspective. The Box element should have padding on all sides, or no sides at all.

```css
.box {
  padding: var(--s1);
}

* {
  box-sizing: border-box;
}
```

## The visible box

A Box is only really a Box if it has a box-like shape. The most common methods use either border or a background.

```css
.box {
  --color-light: #fff;
  --color-dark: #000;
  color: var(--color-dark);
  background-color: var(--color-light);
  padding: var(--s1);
  border: var(--border-thin) solid;
}

.box * {
  color: inherit;
}

.box.invert {
  color: var(--color-light);
  background-color: var(--color-dark);
}
```

Use a transparent outline for high contrast mode support (instead of relying on background alone):

```css
.box {
  outline: 0.125rem solid transparent;
  outline-offset: -0.125rem;
}
```

## Props API

| Name | Type | Default | Description |
|---|---|---|---|
| padding | string | `var(--s1)` | A CSS padding value |
| borderWidth | string | `var(--border-thin)` | A CSS border-width value |
| invert | boolean | false | Whether to apply an inverted theme |

## Examples

```html
<!-- Basic -->
<box-l><!-- contents --></box-l>

<!-- Box with header (nested) -->
<box-l padding="0">
  <box-l borderWidth="0" invert>head</box-l>
  <box-l borderWidth="0">body</box-l>
</box-l>
```
