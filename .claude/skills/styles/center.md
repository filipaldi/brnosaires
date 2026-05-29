# Center

## The solution

Use `margin-inline: auto` with `max-inline-size` and logical properties:

```css
.center {
  box-sizing: content-box;
  max-inline-size: var(--measure);
  margin-inline: auto;
}
```

Add minimum gutters on narrow viewports:

```css
.center {
  box-sizing: content-box;
  max-inline-size: 60ch;
  margin-inline: auto;
  padding-inline-start: var(--s1);
  padding-inline-end: var(--s1);
}
```

## Intrinsic centering

Add Flexbox to also center child elements based on their natural widths:

```css
.center {
  box-sizing: content-box;
  max-inline-size: 60ch;
  margin-inline: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}
```

## Props API

| Name | Type | Default | Description |
|---|---|---|---|
| max | string | `var(--measure)` | A CSS max-width value |
| andText | boolean | false | Also `text-align: center` |
| gutters | string | 0 | Min space on either side |
| intrinsic | boolean | false | Center children by content width |

## Examples

```html
<!-- Single column page -->
<box-l>
  <center-l>
    <stack-l>
      <!-- flow content -->
    </stack-l>
  </center-l>
</box-l>

<!-- Documentation layout (sidebar + centered main) -->
<sidebar-l contentMin="66.666%" sideWidth="10rem">
  <stack-l role="navigation"><!-- nav items --></stack-l>
  <div>
    <center-l role="main"><!-- main content --></center-l>
  </div>
</sidebar-l>

<!-- Vertically and horizontally centered -->
<cover-l centered="center-l">
  <center-l intrinsic>
    <p>I am in the absolute center.</p>
  </center-l>
</cover-l>
```
