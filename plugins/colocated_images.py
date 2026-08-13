"""
colocated_images — let a one-off article keep its picture in the same folder as
its `.md`, referenced by bare filename.

    content/curiosities/moudre-obrazky.md
    content/curiosities/moudre-obrazky.avif   <- next to it

    preview_image: moudre-obrazky.avif        <- no path, no leading slash

`/images/...` stays the canonical home for anything shared, and every existing
absolute path keeps working untouched. This only adds a second option for the
case where an image belongs to exactly one article and nothing else.

WHY A PLUGIN AND NOT STATIC_PATHS
---------------------------------
The obvious implementation — add the article directories to STATIC_PATHS and
let Pelican copy siblings — also copies every `.md` source into the output
tree, and it copies the image to a path that mirrors the *source* layout
rather than the article's URL. Resolving it here instead means the image lands
next to the page that uses it and nothing else tags along.

THE GUARD
---------
Co-location is wrong for two kinds of article, and wrong silently:

  `recurrence:` — recurring_events expands one source file into many
  occurrences. The image would be copied to the source article's URL only.

  `series:` — the hub page aggregates instances and expects the image URL to
  be stable across them.

The original ticket proposed writing that rule in the editor docs. Docs do not
stop anyone, and the failure mode is a 404 that only shows up on a page nobody
opens until the event is next week. So the rule lives here: those articles get
a warning in the build log and their value is left alone.
"""
import logging
import os
import shutil

from pelican import signals

logger = logging.getLogger(__name__)

_COPIES = {}  # output-relative destination -> absolute source path

# Rewritten preview_image value -> absolute source file. og_image reads this:
# once the value points into the output tree there is no way to find the
# original under content/ any more, and the English clones synthesized by
# i18n_fallback inherit the rewritten value without inheriting any attribute
# we could have hung on the original object.
SOURCE_BY_REF = {}


def _is_bare_filename(value):
    return bool(value) and isinstance(value, str) and "/" not in value and "\\" not in value


def _blocking_field(content):
    """Name of the field that makes co-location unsafe here, or None."""
    meta = getattr(content, "metadata", None) or {}
    for field in ("recurrence", "series"):
        if meta.get(field):
            return field
    return None


def _iter_content(generator):
    buckets = ("articles", "translations", "drafts", "drafts_translations",
               "draft_translations", "hidden_articles", "hidden_translations",
               "pages", "hidden_pages", "draft_pages")
    for bucket in buckets:
        for content in getattr(generator, bucket, None) or []:
            yield content


def _resolve(generator):
    resolved = 0
    for content in _iter_content(generator):
        name = getattr(content, "preview_image", None)
        if not _is_bare_filename(name):
            continue

        source_path = getattr(content, "source_path", None)
        if not source_path:
            continue
        # Checked before the file exists, so an author who did both wrong things
        # is told the one that matters — the rule, not the typo.
        blocker = _blocking_field(content)
        if not blocker and not os.path.isfile(
                os.path.join(os.path.dirname(source_path), name)):
            logger.warning("colocated_images: %s has preview_image: %s but no such "
                           "file sits beside it", source_path, name)
            continue

        source = os.path.join(os.path.dirname(source_path), name)
        if blocker:
            logger.warning("colocated_images: %s sets '%s:', so its image cannot live "
                           "beside the .md — every occurrence would 404. Move %s to "
                           "content/images/ and use an absolute path.",
                           source_path, blocker, name)
            continue

        url = (getattr(content, "url", "") or "").lstrip("/")
        destination = os.path.join(url, name) if url else name
        _COPIES[destination] = source
        ref = "/" + destination.replace(os.sep, "/")
        SOURCE_BY_REF[ref] = source
        # Both, and metadata first: the English clones i18n_fallback builds are
        # constructed from `metadata`, so a value written only onto the
        # attribute would not reach them.
        content.metadata["preview_image"] = ref
        content.preview_image = ref
        resolved += 1

    if resolved:
        logger.info("colocated_images: %d co-located preview image(s) resolved", resolved)


def _copy(pelican):
    if not _COPIES:
        return
    output_path = pelican.settings["OUTPUT_PATH"]
    for destination, source in sorted(_COPIES.items()):
        full = os.path.join(output_path, destination)
        try:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            shutil.copyfile(source, full)
        except OSError as exc:
            logger.warning("colocated_images: could not copy %s: %s", source, exc)
    logger.info("colocated_images: %d image(s) copied next to their page", len(_COPIES))
    _COPIES.clear()


def register():
    # `*_generator_finalized`, not `all_generators_finalized`: widget_processor
    # renders <widget-articles/> into the page body during this same signal, so
    # a value rewritten any later would already have been baked into the HTML
    # in its bare form. This plugin is listed first in PLUGINS for the same
    # reason — signal handlers fire in PLUGINS order.
    signals.article_generator_finalized.connect(_resolve)
    signals.page_generator_finalized.connect(_resolve)
    signals.finalized.connect(_copy)
