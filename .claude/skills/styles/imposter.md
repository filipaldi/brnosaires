# Imposter

## The solution

Centrally position an element over its positioning container (or viewport):

```css
.imposter {
  position: absolute;
  inset-block-start: 50%;
  inset-inline-start: 50%;
  transform: translate(-50%, -50%);
  max-inline-size: 100%;
  max-block-size: 100%;
}
```

`transform: translate(-50%, -50%)` repositions relative to the element's own dimensions — no need to know width/height ahead of time.

## With margin (gap from container edges)

```css
.imposter {
  position: absolute;
  inset-block-start: 50%;
  inset-inline-start: 50%;
  transform: translate(-50%, -50%);
  max-inline-size: calc(100% - 2rem);  /* 1rem gap on each side */
  max-block-size: calc(100% - 2rem);
}
```

## Fixed (viewport-relative)

Use a custom property to toggle between absolute and fixed:

```css
.imposter {
  position: var(--positioning, absolute);
  inset-block-start: 50%;
  inset-inline-start: 50%;
  transform: translate(-50%, -50%);
  max-inline-size: calc(100% - 2rem);
  max-block-size: calc(100% - 2rem);
}
```

```html
<!-- Fixed (follows viewport on scroll — use for dialogs) -->
<div class="imposter" style="--positioning: fixed">
  <!-- dialog content -->
</div>
```

## Important notes

- The positioning container must have `position: relative` set
- `position: absolute` removes the element from flow — use sparingly
- `z-index` is only necessary when source order doesn't determine correct layering
- For dialogs: always handle keyboard focus management (see Inclusive Components)

## Props API

| Name | Type | Default | Description |
|---|---|---|---|
| breakout | boolean | false | Whether to allow overflow beyond positioning container |
| margin | string | `0` | Minimum space between imposter and container edges |
| fixed | boolean | false | Use `position: fixed` instead of `absolute` |
