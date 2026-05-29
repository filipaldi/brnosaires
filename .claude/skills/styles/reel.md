# Reel

## The solution

Horizontal scrolling container — native browser scrolling, no carousel JS:

```css
.reel {
  display: flex;
  overflow-x: auto;
  scrollbar-color: var(--color-light) var(--color-dark);
}

.reel::-webkit-scrollbar {
  block-size: 1rem;
}

.reel::-webkit-scrollbar-track {
  background-color: var(--color-dark);
}

.reel::-webkit-scrollbar-thumb {
  background-color: var(--color-dark);
  background-image: linear-gradient(
    var(--color-dark) 0,
    var(--color-dark) 0.25rem,
    var(--color-light) 0.25rem,
    var(--color-light) 0.75rem,
    var(--color-dark) 0.75rem
  );
}
```

## Spacing between children

Use `margin-inline-start` (not `gap`) to keep correct behaviour when not wrapping:

```css
.reel > * + * {
  margin-inline-start: var(--s1);
}
```

## Fixed-height image reel

```css
.reel {
  block-size: 50vh;
}

.reel > img {
  block-size: 100%;
  width: auto;
}
```

## Overflow padding (progressive enhancement)

Add bottom padding only when actually overflowing, using a ResizeObserver + `.overflowing` class:

```css
.reel.overflowing {
  padding-block-end: var(--s0);
}
```

```js
const reels = Array.from(document.querySelectorAll('.reel'));
const toggleOverflowClass = elem => {
  elem.classList.toggle('overflowing', elem.scrollWidth > elem.clientWidth);
};
for (let reel of reels) {
  if ('ResizeObserver' in window) {
    new ResizeObserver(entries => {
      toggleOverflowClass(entries[0].target);
    }).observe(reel);
  }
}
```

## Props API

| Name | Type | Default | Description |
|---|---|---|---|
| itemWidth | string | — | Width for each child item |
| space | string | `var(--s1)` | Space between items |
| height | string | `auto` | Height of the reel |
| noBar | boolean | false | Hide the scrollbar |

## Use cases

- Horizontally browsable categories (events, photos, products)
- "Sausage links" navigation (scrollable menu bar)
