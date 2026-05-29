# Frame

Scoped to: `components.css`

## The solution

Create a container with a fixed aspect ratio that crops its content (images, video, canvas) without distortion:

```css
.frame {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.frame > img,
.frame > video {
  inline-size: 100%;
  block-size: 100%;
  object-fit: cover;
}
```

`object-fit: cover` crops replaced elements (`<img>`, `<video>`) to fill the frame without stretching.

`overflow: hidden` + Flexbox centering handles non-replaced elements (text, canvas, etc.).

## Responsive aspect ratio

Change ratio based on viewport orientation:

```css
@media (orientation: portrait) {
  .frame {
    aspect-ratio: 1 / 1;
  }
}
```

## Notes

- `object-position` defaults to `50% 50%` (center crop). Adjust if the focal point differs.
- Prefer `<img>` over CSS background images — background images can't have alt text and are removed by some high-contrast themes.
- Use `<img>` inside the Frame for content images; background images only for purely decorative purposes.

## Props API

| Name | Type | Default | Description |
|---|---|---|---|
| ratio | string | `16 / 9` | The aspect ratio (e.g. `"1 / 1"`, `"4 / 3"`) |

## Examples

```html
<!-- 16:9 image crop -->
<frame-l>
  <img src="photo.avif" alt="Description" />
</frame-l>

<!-- Square ratio -->
<frame-l ratio="1/1">
  <img src="portrait.avif" alt="Description" />
</frame-l>
```
