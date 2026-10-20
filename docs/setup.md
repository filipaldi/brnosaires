# Development Environment Setup

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd brnos-aires-web
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `pelican[markdown]` - Static site generator
- `notion-client` - Notion API client (for migrations)
- `python-dotenv` - Environment variable management
- `requests` - HTTP library
- `pytz` - Timezone support
- `unidecode` - Unicode text handling

## Project Structure

```
brnos-aires-web/
├── content/              # Content files
│   ├── events/          # Event markdown files
│   ├── pages/           # Page markdown files
│   ├── announcements/    # Announcement files
│   ├── classes/         # Class information
│   └── images/          # Image assets
├── theme/               # Pelican theme
│   ├── templates/       # Jinja2 templates
│   └── static/          # CSS, JS, fonts
├── migration-scripts/    # Notion migration tools
├── output/              # Generated site (gitignored)
├── pelicanconf.py       # Development configuration
├── publishconf.py       # Production configuration
└── requirements.txt     # Python dependencies
```

## Configuration Files

### pelicanconf.py

Development configuration:
- `SITEURL = ""` - Empty for local development
- `RELATIVE_URLS = True` - Relative URLs for local testing
- `OUTPUT_PATH = "output"` - Build output directory
- `DELETE_OUTPUT_DIRECTORY = True` - Clean build on each run

### publishconf.py

Production configuration:
- `SITEURL = "https://brnosaires.com"` - Production URL
- `RELATIVE_URLS = False` - Absolute URLs for production
- Inherits all settings from `pelicanconf.py`

## Content Paths

Configured in `pelicanconf.py`:

- `PAGE_PATHS = ["pages"]` - Static pages
- `ARTICLE_PATHS = ["announcements", "events", "classes"]` - Article content
- `STATIC_PATHS = ["images"]` - Static assets

## Pagination

Pelican automatically paginates category pages when there are more articles than the pagination limit.

### Current Configuration

- `DEFAULT_PAGINATION = 10` - Shows 10 articles per page

### How It Works

When a category has more than 10 articles, Pelican creates multiple paginated pages:

- **announcement** category (72 articles): Creates `announcement.html`, `announcement2.html`, ... `announcement8.html`
- **events** category (29 articles): Creates `events.html`, `events2.html`, `events3.html`
- **class** category (14 articles): Creates `class.html`, `class2.html`

Each page shows navigation links to previous/next pages and indicates the current page number (e.g., "Page 1 / 3").

### Customising Pagination

To change the number of articles per page, modify `DEFAULT_PAGINATION` in `pelicanconf.py`:

```python
DEFAULT_PAGINATION = 20  # Show 20 articles per page
```

To disable pagination for categories entirely:

```python
CATEGORY_PAGINATION = False
```

Note: Disabling pagination will create a single page with all articles, which may be slow to load for large categories.

### Output Files

Paginated category pages are generated in `output/category/`:
- `category/announcement.html` - First page of announcements
- `category/announcement2.html` - Second page of announcements
- `category/events.html` - First page of events
- etc.

These are not duplicate files, but sequential pages of the same category listing.

## Theme Configuration

- `THEME = "theme"` - Theme directory
- `THEME_STATIC_PATHS = ["static"]` - Theme static files

## Environment Variables

If using migration scripts, create `.env` file:

```bash
NOTION_API_KEY=your_api_key_here
```

## Verification

### Test Installation

```bash
pelican --version
```

Should output Pelican version number.

### Build Test

```bash
pelican content -s pelicanconf.py
```

Should generate site in `output/` directory without errors.

## IDE Setup

### Recommended Extensions

- **Markdown**: For editing content files
- **Jinja2**: For template syntax highlighting
- **Python**: For Python scripts
- **YAML**: For frontmatter syntax

### Editor Configuration

**VS Code:**
- Install "Pelican" extension (if available)
- Set markdown file associations
- Configure Python interpreter to use `venv`

## Troubleshooting

### Virtual Environment Issues

**Problem:** `python3` command not found
**Solution:** Use `python` instead, or install Python 3

**Problem:** `pip` command not found
**Solution:** Install pip: `python -m ensurepip --upgrade`

### Dependency Installation Issues

**Problem:** `pelican` installation fails
**Solution:** 
- Upgrade pip: `pip install --upgrade pip`
- Install with: `pip install pelican[markdown]`

**Problem:** Permission errors
**Solution:** Use virtual environment (don't use `sudo`)

### Configuration Issues

**Problem:** Build fails with path errors
**Solution:** 
- Verify `content/` directory exists
- Check `pelicanconf.py` paths are correct
- Ensure theme directory exists

## Deployment

Production deployment is fully automated via GitHub Actions — see `.github/workflows/deploy.yml`.

### Automatic builds

The workflow runs twice daily (06:00 and 18:00 UTC) via cron, and on demand via the **Run workflow** button on the Actions tab (the `workflow_dispatch` trigger). Use the manual trigger when a content change needs to go live immediately instead of waiting for the next scheduled build.

Each run:
1. Builds with `PYTHONPATH=. pelican content -s publishconf.py` (the `PYTHONPATH=.` is required so Pelican can import local plugins from `plugins/`).
2. Writes a `CNAME` file for the `brnosaires.com` custom domain.
3. Publishes `output/` as a GitHub Pages artifact.

### Producing a production build locally

To reproduce what CI publishes — useful when debugging a production-only issue:

```bash
source venv/bin/activate
PYTHONPATH=. pelican content -s publishconf.py
```

Pass `--debug` for verbose output when a build fails unexpectedly:

```bash
PYTHONPATH=. pelican content -s publishconf.py --debug
```

### Post-deployment smoke test

After a deploy, spot-check <https://brnosaires.com>:

- Homepage loads, images display, navigation works, no console errors
- Widget-driven pages render events: `/tango-milongy-brno.html`, `/tango-kalendar-brno.html`
- A recent event page shows correct `event-start` / `event-end`
- No 404s on internal links from the homepage

### Rolling back

Because deploys are git-driven, the rollback is `git revert <bad-commit> && git push`. The next scheduled run — or a manual `workflow_dispatch` — will republish the prior state.

## Next Steps

- See `local-testing.md` for running the development server
- See `WIDGETS.md` for widget system documentation
