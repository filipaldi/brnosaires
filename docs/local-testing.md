# Local Testing Guide

## Development Server

### The workflow: build manually, serve statically — no `--autoreload`

**We do not use `--autoreload`.** You rebuild the site yourself with `pelican content` whenever you change content, theme, or settings, then hard-reload the browser. The server is a plain static file server (`pelican --listen`) — it serves `output/` and never rebuilds it. This is deliberate: on this machine `--autoreload` interacts badly with Spotlight/Time Machine churning `output/` (torn, partial builds), and more importantly you want to control exactly when `output/` is regenerated rather than have it happen on every keystroke. Stick to **one** server on **one** port (41234) — don't spin up throwaway servers on other ports.

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# 1. Build the site (re-run this every time you change something)
pelican content -s pelicanconf.py

# 2. In a separate shell, serve output/ (leave it running; it does NOT rebuild)
pelican --listen --port 41234
```

Loop: edit files → re-run `pelican content -s pelicanconf.py` → hard-reload `http://localhost:41234/` (`Cmd+Shift+R`).

**Options:**
- `--listen`: start the HTTP static server (serves `output/`, no rebuilding)
- `--port 41234`: bind on a fixed non-default port (see "Port choice" below)
- (We intentionally omit `--autoreload`. If you ever want it for a quick throwaway session, fine — but the documented, repeatable workflow is the manual rebuild above.)

### Port choice — `41234`

We deliberately avoid Pelican's default port 8000. It collides with Django, http-server, Python's `http.server`, and dozens of other dev tools the moment they're running. Picking a fixed port in the unregistered user-port range (30000–48000) means:

- The port stays the same across sessions, so bookmarks, MCP browser tabs, and notes all keep working.
- It's high enough to be above common dev defaults but below the OS ephemeral port floor (49152 on macOS), so the OS won't auto-grab it.
- If `lsof -i :41234` ever shows it busy, **jump** to a different non-adjacent port (e.g. 38765, 43210) and update this file plus [.claude/CLAUDE.md](../.claude/CLAUDE.md) — don't pick the next sequential number.

### Access Local Site

Open browser to: `http://localhost:41234`

### Preview on a phone / other device (same Wi-Fi)

`localhost` only works on the Mac itself. To open the site on an iPhone (or any
other device on the same network), build first, then run the static server bound
to **all** interfaces:

```bash
source venv/bin/activate
pelican content -s pelicanconf.py                       # build (re-run after edits)
pelican --listen --bind 0.0.0.0 --port 41234            # serve output/ on all interfaces (no autoreload)
```

Then find the Mac's LAN IP and open it from the phone:

```bash
ipconfig getifaddr en0   # e.g. 192.168.0.73  (en1 on older Macs / Ethernet)
```

On the phone (Safari): `http://<that-ip>:41234/` — e.g. `http://192.168.0.73:41234/`

Notes:
- `pelicanconf.py` has `RELATIVE_URLS = True`, so internal links resolve fine
  against the IP address — no need to touch `SITEURL`. Don't use `publishconf.py`
  for device testing (its absolute `https://brnosaires.com` URLs would jump off-site).
- First time you bind to `0.0.0.0`, macOS may pop a one-time "allow incoming
  connections for Python" firewall prompt — allow it. (System Settings → Network → Firewall.)
- The LAN IP can change when you reconnect to Wi-Fi / switch networks — re-run
  `ipconfig getifaddr en0` if the phone stops loading.
- **Safari Web Inspector**: connect the iPhone to the Mac via USB → Safari →
  Develop menu → [your iPhone] → inspect the live page (DOM/console/network).
- If the network blocks device-to-device traffic (some corporate/guest Wi-Fi),
  use a tunnel instead: `cloudflared tunnel --url http://localhost:41234`
  (public HTTPS URL, no signup) or `ngrok http 41234`.

### Stop Server

Press `Ctrl+C` in terminal

### Kill Port (if needed)

**macOS/Linux** — find what's holding it, then kill (plain `kill`, not `kill -9`; the agent harness blocks `kill -9`):
```bash
lsof -nP -iTCP:41234 -sTCP:LISTEN     # who's listening (PID + command)
lsof -ti:41234 | xargs kill           # kill by port
lsof -ti:41234 || echo "41234 free"   # verify
```
The static server is also a `pelican` process, so `pkill -f 'venv/bin/pelican'` works too (but `pkill` is blocked in the agent harness — a human runs it).

**Windows:**
```bash
netstat -ano | findstr :41234
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
# Delete output directory first, then build
rm -rf output/   # macOS/Linux  (rmdir /s output on Windows)
pelican content -s pelicanconf.py
```

Or use Pelican's built-in clean:
```bash
pelican content -s pelicanconf.py --delete-output-directory
```

> **Heads-up (agent harness):** `rm -rf`, `rmdir`, and `--delete-output-directory` (the word "delete") are blocked by the dangerous-command hook — a human runs those. Also: if `output/` keeps reappearing right after you delete it, something is still running a build — it's almost always a stray `pelican --autoreload` (which is exactly why we don't use it) or an editor's preview server. Find it with `ps aux | grep pelican | grep -v grep` and `lsof -ti:41234`.

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

Navigate to: `http://localhost:41234/test-widgets.html`

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

### 2. Rebuild

Re-run `pelican content -s pelicanconf.py` (we don't use `--autoreload` — see [the workflow note](#the-workflow-build-manually-serve-statically--no---autoreload) at the top). Watch this command's output for template errors.

### 3. Refresh Browser

Hard refresh: `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows)

### 4. Check for Errors

Watch the `pelican content` output for:
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
- Test on actual mobile devices — see [Preview on a phone / other device](#preview-on-a-phone--other-device-same-wi-fi) above for the `--bind 0.0.0.0` recipe

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
