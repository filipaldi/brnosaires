"""
og_image — derive a scraper-safe JPEG twin of every `preview_image` and expose
it as `content.og_image`.

WHY THIS EXISTS
---------------
`preview_image` feeds three different consumers at once:

  1. the on-page `<img>` (article header, category listing, event card),
  2. `og:image` / `twitter:image`,
  3. the schema.org `"image"` field.

Consumer 1 is a browser and handles AVIF fine. Consumers 2 and 3 are *not*
browsers. Facebook's, LinkedIn's, WhatsApp's and Slack's link scrapers decode a
fixed, short list of raster formats and AVIF is not on it — they fetch the URL,
fail to decode it, and render the share as a bare text card. Google's structured
data likewise documents jpg/png/gif/webp only. Two thirds of this site's pages
shipped an AVIF `og:image`, i.e. two thirds of shares looked broken on the one
channel the site actually has.

Changing `preview_image` itself to JPEG would fix the share and regress the
page — the AVIF is there because it is several times smaller. So instead this
plugin keeps `preview_image` exactly as authored and *derives* a JPEG next to
it, under `/og/<same path>.jpg`. Templates keep using `preview_image` for the
visible `<img>` and switch to `og_image` for the two machine consumers.

Formats already on every scraper's list (jpg/jpeg/png) are passed through
untouched — `og_image` is then just `preview_image` and nothing is written.
Everything else (avif, webp, jfif, and the uppercase `.JPEG`/`.JPG` variants,
whose content type GitHub Pages does not reliably set) gets a derivative.

HOW IT HOOKS IN
---------------
Two signals, because the path has to be known before the answer can be
computed:

  `all_generators_finalized` — every generator's context is built but nothing
  is on disk yet, and templates have not rendered. This is the last moment at
  which setting `content.og_image` still reaches the templates, so the path is
  *decided* here (and the conversion queued).

  `finalized` — output is fully written. The queued conversions run here, so a
  failed decode can never take the build down with it: the derivative is
  simply missing and the template already emitted its URL. That is the same
  failure mode as a mistyped `preview_image`, not a worse one.

DELETE_OUTPUT_DIRECTORY wipes `output/` at the start of a run, so the
derivatives are rebuilt every time; ~100 images cost a couple of seconds.
"""
import logging
import os
from urllib.parse import quote, unquote

from pelican import signals

logger = logging.getLogger(__name__)

# Extensions every link scraper decodes. Anything else gets a JPEG twin.
# Lowercase comparison, but note `.JPEG` deliberately does NOT pass: the
# uppercase spelling is what GitHub Pages serves without a reliable
# `Content-Type: image/jpeg`, which trips the stricter scrapers.
PASSTHROUGH_EXTENSIONS = (".jpg", ".jpeg", ".png")

# Subdirectory of OUTPUT_PATH holding the derivatives.
OG_DIR = "og"

# Facebook/LinkedIn render large cards at 1200px wide; past that is upload
# weight nobody sees. Never upscale — a small source stays small.
MAX_EDGE = 1200

# Below this, scrapers refuse the large card and fall back to a thumbnail or to
# nothing. Emitting one anyway contradicts the rule in base.html — no og:image
# beats one that cannot be rendered — so a source this small is dropped, not
# warned about. (The live case is an emoji, images/unnamed/1f642.avif, used as
# an article's preview.)
MIN_EDGE = 200

JPEG_QUALITY = 82

_JOBS = {}  # output relative path -> absolute source path


def _passthrough(ref):
    # Exact (lowercase) match only — see PASSTHROUGH_EXTENSIONS on why `.JPEG`
    # is deliberately not equivalent to `.jpeg` here.
    return os.path.splitext(ref)[1] in PASSTHROUGH_EXTENSIONS


def _resolve_source(ref, content_root):
    """Map a `preview_image` value onto a file under the content root.

    Values are root-relative URLs (`/images/foo.avif`) and `images` is a
    STATIC_PATH, so the URL path doubles as the path under `content/`. Some
    values arrived from the Notion import percent-encoded, so try the literal
    spelling first and the decoded one second — in that order, because a
    filename is allowed to contain a literal `%`.
    """
    rel = ref.lstrip("/")
    for candidate in (rel, unquote(rel)):
        path = os.path.normpath(os.path.join(content_root, candidate))
        # Refs come from the repo, but normpath + a containment check costs
        # nothing and keeps `../` out of the build.
        if not path.startswith(os.path.join(content_root, "")):
            continue
        if os.path.isfile(path):
            return path, candidate
    return None, rel


def _too_small(source):
    """True if the source cannot make a large card.

    Checked here rather than at conversion time: by the time the derivative is
    written the template has already emitted its URL, so declining then would
    ship a 404 instead of nothing. Reads the header only — Pillow gives .size
    without decoding the pixels.
    """
    try:
        from PIL import Image
    except ImportError:
        return False
    try:
        with Image.open(source) as image:
            return min(image.size) < MIN_EDGE
    except Exception:  # noqa: BLE001 — a file we cannot open fails later anyway
        return False


def _derivative_path(rel):
    """`images/a/b.avif` -> `og/images/a/b.avif.jpg`.

    The source extension is kept, not replaced. Mirroring the tree alone stops
    two files with the same basename in different folders colliding, but not
    `foo.avif` and `foo.webp` in the SAME folder — those would have shared one
    derivative, and two unrelated articles would have shared one social card.
    """
    return os.path.join(OG_DIR, rel + ".jpg")


def _iter_content(generators):
    """Every Content object that reaches a template.

    Translations live on their own generator list (see i18n_fallback) and are
    written to disk just like originals, so they need `og_image` too.
    """
    buckets = (
        "articles", "translations", "drafts", "drafts_translations",
        "hidden_articles", "hidden_translations",
        "pages", "hidden_pages", "draft_pages", "draft_translations",
    )
    for generator in generators:
        for bucket in buckets:
            for content in getattr(generator, bucket, None) or []:
                yield content


def _assign(generators):
    settings = None
    for generator in generators:
        settings = getattr(generator, "settings", None) or settings
    if not settings:
        return

    content_root = os.path.abspath(settings.get("PATH", "content"))
    seen = set()
    missing = 0

    for content in _iter_content(generators):
        ref = getattr(content, "preview_image", None)
        if not ref or not isinstance(ref, str):
            continue
        if _passthrough(ref):
            # Encoded like the derivative branch below, because the value is a
            # URL and some sources have a space in the filename
            # (`images/events/2026/brunch milonga.jpg`). Decoded first so a ref
            # that arrived already encoded is not encoded twice.
            content.og_image = quote(unquote(ref), safe="/")
            continue

        source, rel = _resolve_source(ref, content_root)
        if source is None:
            # A dead `preview_image`. The visible <img> is already broken; do
            # not add a second broken URL on top of it.
            if ref not in seen:
                logger.warning("og_image: no such file for preview_image %s (%s)",
                               ref, getattr(content, "source_path", "?"))
                missing += 1
            seen.add(ref)
            continue

        if _too_small(source):
            logger.warning("og_image: %s is under %dpx on its short edge — no "
                           "social card for %s", ref, MIN_EDGE,
                           getattr(content, "source_path", "?"))
            continue

        out_rel = _derivative_path(rel)
        _JOBS[out_rel] = source
        # Percent-encoded: a value that resolved through the unquote fallback
        # comes back decoded, and `content/images/events/2026/brunch
        # milonga.avif` was shipping an og:image URL with a raw space in it.
        content.og_image = "/" + quote(out_rel.replace(os.sep, "/"), safe="/")

    logger.info("og_image: %d derivative(s) queued, %d unresolved preview_image(s)",
                len(_JOBS), missing)


def _convert(pelican):
    if not _JOBS:
        return
    try:
        from PIL import Image
    except ImportError:
        # Without Pillow the og:image URLs point at files that will not exist.
        # Loud, but still not a reason to fail a content build.
        logger.error("og_image: Pillow is not installed — %d social preview(s) "
                     "will 404. Install requirements.txt.", len(_JOBS))
        return

    output_path = pelican.settings["OUTPUT_PATH"]
    written = failed = 0

    for out_rel, source in sorted(_JOBS.items()):
        destination = os.path.join(output_path, out_rel)
        try:
            with Image.open(source) as image:
                image.load()
                # AVIF and PNG can carry alpha; JPEG cannot. Flatten onto white
                # rather than letting Pillow raise or produce a black matte.
                if image.mode in ("RGBA", "LA", "P"):
                    image = image.convert("RGBA")
                    flattened = Image.new("RGB", image.size, (255, 255, 255))
                    flattened.paste(image, mask=image.split()[-1])
                    image = flattened
                elif image.mode != "RGB":
                    image = image.convert("RGB")

                if max(image.size) > MAX_EDGE:
                    image.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                image.save(destination, "JPEG", quality=JPEG_QUALITY,
                           optimize=True, progressive=True)
                written += 1
        except Exception as exc:  # noqa: BLE001 — one bad image must not stop the build
            logger.warning("og_image: could not convert %s: %s", source, exc)
            failed += 1

    logger.info("og_image: %d social preview(s) written to %s/, %d failed",
                written, OG_DIR, failed)
    _JOBS.clear()


def register():
    signals.all_generators_finalized.connect(_assign)
    signals.finalized.connect(_convert)
