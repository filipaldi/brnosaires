# Local Testing Guide

## Development Server

### Start Development Server

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Start Pelican with auto-reload
pelican content -s pelicanconf.py --autoreload --listen
```

**Options:**
- `--autoreload`: Automatically rebuild on file changes
- `--listen`: Start HTTP server on port 8000

### Access Local Site

Open browser to: `http://localhost:8000`

### Stop Server

Press `Ctrl+C` in terminal

### Kill Port (if needed)

**macOS/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Build Commands

### Development Build

```bash
pelican content -s pelicanconf.py
```

- Uses `pelicanconf.py` configuration
- Generates site in `output/` directory
- Relative URLs for local testing

### Production Build

```bash
pelican content -s publishconf.py
```

- Uses `publishconf.py` configuration
- Absolute URLs for production
- Same output directory

### Clean Build

```bash
# Delete output directory first
rm -rf output/  # macOS/Linux
rmdir /s output  # Windows

# Then build
pelican content -s pelicanconf.py
```

Or use Pelican's built-in clean:
```bash
pelican content -s pelicanconf.py --delete-output-directory
```

## Testing Widgets

### 1. Create Test Page

Create `content/pages/test-widgets.md`:

```markdown
---
title: Widget Test
slug: test-widgets
---

## Calendar (events)

<div data-widget="calendar" data-filter="milonga"></div>

```

### 2. View Test Page

Navigate to: `http://localhost:8000/test-widgets.html`

### 3. Verify Widgets

- Check filtered events appear
- Test different widget attributes

## Testing Event Metadata

### 1. Create Test Event

Create `content/events/test-event.md`:

```markdown
---
title: Test Event
date: 2026-01-17 18:00:00
event-start: 2026-01-17 18:00:00
event-end: 2026-01-17 22:30:00
slug: test-event
---

This is a test event.
```

### 2. Verify Event Display

- Check event appears in filtered lists
- Verify dates display correctly

### 3. Test Metadata Access

Add debug output to templates temporarily:

```jinja2
{{ event.metadata }}
{{ event.start }}
{{ event.metadata.get('event-start') }}
```

## Testing Template Changes

### 1. Edit Template

Modify template in `theme/templates/`

### 2. Auto-Reload

With `--autoreload` flag, changes rebuild automatically

### 3. Refresh Browser

Hard refresh: `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows)

### 4. Check for Errors

Watch terminal output for:
- Template syntax errors
- Missing variables
- Import errors

## Debugging

### Enable Debug Output

Add to `pelicanconf.py`:

```python
DEBUG = True
```

### Check Template Context

Add debug block to template:

```jinja2
{% if DEBUG %}
  <pre>{{ articles | list | length }} articles</pre>
  <pre>{{ pages | list | length }} pages</pre>
{% endif %}
```

### View Generated HTML

1. Build site: `pelican content -s pelicanconf.py`
2. Open `output/` directory
3. View generated HTML files
4. Check browser developer tools

### Common Issues

**Widgets not rendering:**
- Check `process_widgets()` is called in `page.html`
- Verify widget syntax matches README.md
- Check terminal for template errors

**Events not appearing:**
- Verify events in `content/events/`
- Check `event-start` metadata format
- Verify `ARTICLE_PATHS` includes `"events"`

**Date display issues:**
- Check metadata format: `YYYY-MM-DD HH:MM:SS`
- Verify datetime object access
- Test with `{{ event.metadata.get('event-start') }}`

## Browser Testing

### Test in Multiple Browsers

- Chrome/Edge
- Firefox
- Safari
- Mobile browsers (responsive design)

### Check Console

Open browser developer tools:
- Check for JavaScript errors
- Verify CSS loading
- Check network requests

### Responsive Testing

- Test different screen sizes
- Use browser dev tools device emulation
- Test on actual mobile devices

## Performance Testing

### Build Time

Measure build time:
```bash
time pelican content -s pelicanconf.py
```

### File Sizes

Check output directory size:
```bash
du -sh output/
```

### Page Load

Use browser dev tools:
- Network tab for load times
- Performance tab for rendering
- Lighthouse for audit

## Content Validation

### Validate Markdown

Check markdown syntax:
- Frontmatter format
- Link syntax
- Image paths

### Validate Metadata

Verify event metadata:
- Required fields present
- Date format correct
- Slug format valid

### Check Links

- Internal links work
- External links valid
- Images load correctly

## Automated Testing

### Build Script

Create `test-build.sh`:

```bash
#!/bin/bash
set -e

echo "Building site..."
pelican content -s pelicanconf.py

echo "Checking for errors..."
if [ $? -eq 0 ]; then
    echo "Build successful!"
else
    echo "Build failed!"
    exit 1
fi
```

### Run Tests

```bash
chmod +x test-build.sh
./test-build.sh
```

## Pre-Deployment Checklist

Before publishing, verify:

- [ ] Site builds without errors
- [ ] All widgets render correctly
- [ ] Events display with correct dates
- [ ] Images load properly
- [ ] Links work (internal and external)
- [ ] Responsive design works
- [ ] No console errors
- [ ] Production build works (`publishconf.py`)

## Next Steps

- See `publishing.md` for deployment
- See `WIDGETS.md` for widget details
- See `setup.md` for environment setup
