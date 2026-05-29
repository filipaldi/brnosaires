# Grid

## The solution

Responsive grid using CSS Grid's `auto-fit` + `minmax()` + `min()` — no JavaScript, no `@media` queries:

```css
.grid {
  display: grid;
  grid-gap: 1rem;
}

@supports (width: min(250px, 100%)) {
  .grid {
    grid-template-columns: repeat(auto-fit, minmax(min(250px, 100%), 1fr));
  }
}
```

The `min()` function prevents overflow in containers narrower than the minimum: it returns `100%` when `250px` would exceed it, so columns collapse to a single-column layout gracefully.

## Why not Flexbox?

Flexbox grids (`flex: 1 1 30ch`) allow growth to different widths, breaking column alignment. CSS Grid's `auto-fit` keeps columns equal width.

## Why not plain minmax?

`minmax(250px, 1fr)` overflows in containers narrower than `250px`. The `min(250px, 100%)` fix solves this purely in CSS.

## Use cases

Card grids, product listings, teaser grids. Compose with Box + Stack for card components:

```html
<div class="grid" style="--min: 20rem">
  <box-l>
    <stack-l>
      <h3>Card title</h3>
      <p>Card content</p>
    </stack-l>
  </box-l>
  <!-- more cards -->
</div>
```
