# Publishing Guide

## Overview

This guide covers deploying the Brnos Aires website to production. The site is a static Pelican site that can be deployed to various hosting platforms.

## Pre-Deployment Checklist

Before publishing:

- [ ] All content reviewed and approved
- [ ] Site builds successfully with `publishconf.py`
- [ ] All widgets render correctly
- [ ] Events have correct metadata (`date`, `event-start`, `event-end`)
- [ ] Images optimized and loading correctly
- [ ] Links verified (internal and external)
- [ ] No console errors in browser
- [ ] Responsive design tested

## Build for Production

### Production Build Command

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Build with production config
pelican content -s publishconf.py
```

**Configuration differences:**
- `SITEURL = "https://brnosaires.com"` (absolute URLs)
- `RELATIVE_URLS = False` (absolute URLs for production)
- All other settings from `pelicanconf.py`

### Verify Build

```bash
# Check output directory
ls -la output/

# Verify HTML files generated
find output/ -name "*.html" | wc -l

# Check for errors in build output
pelican content -s publishconf.py 2>&1 | grep -i error
```

**Note:** The `output/category/` directory will contain paginated category pages (e.g., `announcement.html`, `announcement2.html`, etc.) when categories have more articles than the pagination limit. This is expected behaviour. See `setup.md` for pagination configuration details.

## Deployment Methods

### Method 1: FTP/SFTP Upload

**Steps:**

1. Build production site:
   ```bash
   pelican content -s publishconf.py
   ```

2. Upload `output/` directory contents to web server:
   ```bash
   # Using rsync
   rsync -avz output/ user@server:/path/to/webroot/
   
   # Using scp
   scp -r output/* user@server:/path/to/webroot/
   ```

3. Verify deployment:
   - Visit `https://brnosaires.com`
   - Check all pages load
   - Verify widgets work

### Method 2: Git-Based Deployment

**If using Git hooks or CI/CD:**

1. Commit changes:
   ```bash
   git add .
   git commit -m "Update content"
   git push
   ```

2. Server pulls and builds:
   ```bash
   # On server
   git pull
   source venv/bin/activate
   pelican content -s publishconf.py
   # Copy output/ to webroot
   ```

### Method 3: Static Hosting (Netlify, Vercel, etc.)

**Configuration:**

1. Build command:
   ```bash
   pelican content -s publishconf.py
   ```

2. Publish directory: `output`

3. Build settings:
   - Python version: 3.8+
   - Install command: `pip install -r requirements.txt`
   - Build command: `pelican content -s publishconf.py`

## Post-Deployment Verification

### 1. Check Homepage

Visit `https://brnosaires.com` and verify:
- Page loads correctly
- Images display
- Navigation works
- No console errors

### 2. Test Widgets

Visit pages with widgets:
- `https://brnosaires.com/tango-milongy-brno.html`
- `https://brnosaires.com/tango-kalendar-brno.html`

Verify:
- Filtered events display
- Calendar month shows events
- Dates formatted correctly

### 3. Test Events

Visit event pages:
- Check event dates display
- Verify `event-start` and `event-end` work
- Test event links

### 4. Check URLs

Verify:
- All internal links work
- External links valid
- Images load from correct paths
- No 404 errors

### 5. Validate HTML

Use online validators:
- W3C HTML Validator
- Google Search Console
- Lighthouse audit

## Rollback Procedure

If deployment has issues:

### Quick Rollback

1. Restore previous `output/` directory:
   ```bash
   # If backed up
   cp -r output.backup/* output/
   rsync -avz output/ user@server:/path/to/webroot/
   ```

2. Or rebuild previous version:
   ```bash
   git checkout <previous-commit>
   pelican content -s publishconf.py
   # Deploy output/
   ```

### Content Rollback

1. Revert content changes:
   ```bash
   git checkout <previous-commit> content/
   ```

2. Rebuild and redeploy

## Maintenance

### Regular Updates

**Content updates:**
1. Edit content files in `content/`
2. Test locally
3. Build and deploy

**Template updates:**
1. Edit templates in `theme/templates/`
2. Test locally with `--autoreload`
3. Build and deploy

### Monitoring

**Check regularly:**
- Site accessibility
- Widget functionality
- Event display
- Broken links
- Image loading

**Tools:**
- Google Search Console
- Uptime monitoring
- Error logging (if configured)

## Troubleshooting

### Build Fails

**Check:**
- Python version (3.8+)
- Dependencies installed
- Configuration file syntax
- Content file syntax

**Debug:**
```bash
pelican content -s publishconf.py --debug
```

### Widgets Not Working

**Check:**
- Widget syntax in content
- Template includes `process_widgets()`
- Events have correct metadata
- Build completed without errors

### Date Display Issues

**Check:**
- Event metadata format: `YYYY-MM-DD HH:MM:SS`
- `event-start` field present
- Template uses standardized access pattern

### Images Not Loading

**Check:**
- Image paths: `{static}/images/filename.jpg`
- Images in `content/images/`
- `STATIC_PATHS` includes `"images"`

## Security Considerations

### Content Security

- Review user-generated content
- Validate external links
- Sanitize markdown input (if allowing user input)

### Server Security

- Keep Pelican updated
- Use HTTPS
- Secure file permissions
- Regular backups

## Backup Strategy

### Content Backup

```bash
# Backup content directory
tar -czf content-backup-$(date +%Y%m%d).tar.gz content/

# Backup to remote location
scp content-backup-*.tar.gz backup-server:/backups/
```

### Full Site Backup

```bash
# Backup entire project
tar -czf site-backup-$(date +%Y%m%d).tar.gz \
  --exclude='venv' \
  --exclude='output' \
  --exclude='__pycache__' \
  .
```

### Automated Backups

Set up cron job or scheduled task:
```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/project && tar -czf backups/content-$(date +\%Y\%m\%d).tar.gz content/
```

## Performance Optimization

### Build Optimization

- Minimize template processing
- Optimize images before upload
- Use CDN for static assets (if applicable)

### Site Performance

- Enable gzip compression
- Use browser caching
- Optimize images
- Minify CSS/JS (if applicable)

## Next Steps

- See `local-testing.md` for testing before deployment
- See `setup.md` for environment setup
- See `WIDGETS.md` for widget system details
