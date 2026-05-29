# Stack

## The problem

Margin is really a property of the relationship between two proximate elements, not of the element itself. Setting `margin-bottom` on a `p` is problematic because it's not context sensitive — a `:last-child` paragraph produces a redundant margin that doubles up with parent padding.

## The solution

Style the context, not the individual element. The Stack injects margin between elements via their common parent:

```css
.stack > * + * {
  margin-block-start: 1.5rem;
}
```

Using the adjacent sibling combinator (`+`), `margin-block-start` is only applied where the element is preceded by another element. This is known as the "owl" (`* + *`).

## Recursive variant

Remove the child combinator to inject margins at any nesting level:

```css
.stack * + * {
  margin-block-start: 1.5rem;
}
```

## Nested variants

```css
[class^='stack'] > * {
  margin-block: 0;
}

.stack-large > * + * {
  margin-block-start: 3rem;
}

.stack-small > * + * {
  margin-block-start: 0.5rem;
}
```

## Splitting the stack

Make the Stack a Flexbox context to push elements to the top/bottom with `auto` margin:

```css
.stack {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.stack > * + * {
  margin-block-start: var(--space, 1.5rem);
}

/* Split after 2nd child */
.stack > :nth-child(2) {
  margin-block-end: auto;
}
```

## Generated CSS

```css
.stack {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.stack > * {
  margin-block: 0;
}

.stack > * + * {
  margin-block-start: var(--space, 1.5rem);
}
```

## Props API

| Name | Type | Default | Description |
|---|---|---|---|
| space | string | `var(--s1)` | A CSS margin value |
| recursive | boolean | false | Apply spaces recursively |
| splitAfter | number | — | Element index after which to split with auto margin |

## Examples

```html
<!-- Basic -->
<stack-l>
  <h2>...</h2>
  <img src="..." />
  <p>...</p>
</stack-l>

<!-- Nested -->
<stack-l space="3rem">
  <h2>...</h2>
  <stack-l space="1.5rem">
    <p>...</p>
    <p>...</p>
  </stack-l>
</stack-l>

<!-- Recursive -->
<stack-l recursive>
  <div>...</div>
  <div>
    <div>...</div>
    <div>...</div>
  </div>
</stack-l>

<!-- List semantics -->
<stack-l role="list">
  <div role="listitem">...</div>
  <div role="listitem">...</div>
</stack-l>
```
