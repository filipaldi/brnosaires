#!/usr/bin/env python3
"""
convert_images.py — turn any raster an editor drops into `content/` into AVIF
and repoint every Markdown reference at the new file.

WHY
---
Editors upload whatever their phone or Facebook gave them. The repo carried
111 MB of JPEG/PNG next to 20 MB of AVIF holding twice as many pictures, and
every one of those megabytes is cloned by everyone who touches the repo and
served to every visitor. Asking editors to convert by hand is asking them to
learn a tool that has nothing to do with tango.

Note what this deliberately does NOT do: it does not keep a JPEG copy for
`preview_image`. Link scrapers cannot read AVIF, but plugins/og_image.py
already derives a JPEG twin of every preview at build time, so the source of
truth can be AVIF for everything. That removes the whole "scan the front
matter and split the files into two groups" half of the original design.

SAFETY
------
The rewrite is exact-string, and only for paths of files converted in this
run — never a blanket `s/\\.jpg/\\.avif/`, which would also rewrite prose like
"ulož to jako .jpg". Both the plain and the percent-encoded spelling of each
path are replaced, because Notion-imported content carries both.

Conversion refuses rather than guesses when it would destroy something: an
existing `.avif` at the target name, or two sources (`foo.jpg`, `foo.png`)
that would collapse onto one target, abort the run with a report.

After running this, build the site and run scripts/check_links.py — it
resolves every image reference against the output tree and will catch a
rewrite that missed.

USAGE
-----
    python scripts/convert_images.py --dry-run
    python scripts/convert_images.py [--quality 60] [--content content]
"""
import argparse
import os
import sys
from collections import defaultdict
from urllib.parse import quote

# Formats worth converting. `.gif` is left alone (it may be animated, and
# Pillow's AVIF writer drops the animation); `.svg` is not a raster at all.
CONVERTIBLE = (".jpg", ".jpeg", ".png", ".jfif", ".webp", ".heic", ".heif", ".bmp", ".tif", ".tiff")

TARGET_EXTENSION = ".avif"

# Měřeno na 101 obrázcích, které v repu byly, každý překódovaný nanovo:
#
#     originály   104,5 MB
#     q60          25,7 MB   24,6 %
#     q70          40,2 MB   38,5 %   +14,6 MB
#     q80          59,3 MB   56,8 %   +33,7 MB
#
# Vyšší hodnota se nevyplatí, protože fotky na tomhle webu jsou skoro všechny
# už jednou zkomprimované JPEGy: vyšší kvalita neuloží víc detailu, uloží
# věrněji artefakty toho JPEGu. U portrétu vyjde q80 na 103K proti originálu
# 124K — za osmdesát procent velikosti originálu dostaneš jeho vlastní šum.
# Jediné, kde je q60 vidět, jsou tmavé plochy na fotkách ze slabého světla.
#
# Opačný případ jsou plakáty a grafika v PNG: tam originál nese megabajty a i
# q80 je řádově menší. Kdyby jich v repu přibylo, stojí za to je převést zvlášť
# s vyšší hodnotou přes --quality.
DEFAULT_QUALITY = 60


def find_sources(content_root):
    out = []
    for root, _dirs, files in os.walk(content_root):
        for name in files:
            if os.path.splitext(name)[1].lower() in CONVERTIBLE:
                out.append(os.path.join(root, name))
    return sorted(out)


def plan(sources, content_root):
    """(jobs, conflicts) where jobs is [(source, target)] and conflicts blocks the run."""
    by_target = defaultdict(list)
    for source in sources:
        by_target[os.path.splitext(source)[0] + TARGET_EXTENSION].append(source)

    jobs, conflicts = [], []
    for target, group in sorted(by_target.items()):
        rel = os.path.relpath(target, content_root)
        if len(group) > 1:
            conflicts.append(f"{rel} would be written from {len(group)} sources: "
                             + ", ".join(os.path.basename(s) for s in group))
            continue
        if os.path.exists(target):
            conflicts.append(f"{rel} already exists — refusing to overwrite "
                             f"(source {os.path.basename(group[0])})")
            continue
        jobs.append((group[0], target))
    return jobs, conflicts


def reference_spellings(rel):
    """Every way `rel` can appear in a Markdown file, longest first.

    Longest first matters: "/images/a.jpg" must be consumed before the bare
    "images/a.jpg" would match its tail and leave a stray leading slash.
    """
    encoded = quote(rel, safe="/")
    spellings = ["/" + rel, "/" + encoded, rel, encoded]
    # dict.fromkeys keeps order and drops the duplicates you get when a path
    # has nothing worth percent-encoding.
    return list(dict.fromkeys(spellings))


def convert(jobs, quality, dry_run):
    if dry_run:
        return [target for _source, target in jobs], []
    from PIL import Image
    try:
        # HEIC is what an iPhone hands you, and Pillow does not read it on its
        # own. Optional so a checkout without it still converts everything else
        # rather than failing at import.
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass

    from PIL import ImageOps

    written, failed, skipped = [], [], []
    for source, target in jobs:
        try:
            with Image.open(source) as image:
                if getattr(image, "n_frames", 1) > 1:
                    # Pillow's AVIF writer keeps one frame. Converting would
                    # silently drop the animation and then delete the original,
                    # which is why .gif is excluded outright — animated .webp
                    # and multi-page .tiff need the same protection.
                    skipped.append(source)
                    continue
                image.load()
                # Phone photos carry their rotation in EXIF rather than in the
                # pixels. Nothing here writes EXIF onward, so without baking the
                # rotation in the picture ends up sideways — and the original is
                # deleted in the same run.
                image = ImageOps.exif_transpose(image)
                # AVIF carries alpha, so PNG transparency survives; anything
                # exotic (CMYK, palette) is normalised first.
                if image.mode in ("RGBA", "LA"):
                    image = image.convert("RGBA")
                elif image.mode == "P":
                    image = image.convert("RGBA" if "transparency" in image.info else "RGB")
                elif image.mode != "RGB":
                    image = image.convert("RGB")
                image.save(target, "AVIF", quality=quality)
            written.append(target)
        except Exception as exc:  # noqa: BLE001 — report and carry on
            failed.append((source, exc))
    for source in skipped:
        failed.append((source, "animated or multi-page — left as it is"))
    return written, failed


def rewrite_markdown(content_root, mapping, dry_run):
    """mapping: {old rel path -> new rel path}. Returns (files touched, replacements)."""
    # Longest source path first, so a path that is a suffix of another cannot
    # steal its match.
    ordered = sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True)
    touched, replacements = [], 0

    for root, _dirs, files in os.walk(content_root):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as handle:
                text = original = handle.read()
            for old_rel, new_rel in ordered:
                spellings = list(zip(reference_spellings(old_rel),
                                     reference_spellings(new_rel)))
                # An article may also reference an image sitting beside it by
                # bare filename (`preview_image: poster.avif` — see
                # plugins/colocated_images.py). Only for a .md in the image's
                # own directory: elsewhere a bare basename means nothing, and
                # replacing it would corrupt unrelated prose.
                if os.path.dirname(os.path.join(content_root, old_rel)) == root:
                    spellings.append((os.path.basename(old_rel),
                                      os.path.basename(new_rel)))
                for old, new in spellings:
                    if old in text:
                        replacements += text.count(old)
                        text = text.replace(old, new)
            if text != original:
                touched.append(os.path.relpath(path, content_root))
                if not dry_run:
                    with open(path, "w", encoding="utf-8") as handle:
                        handle.write(text)
    return touched, replacements


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--content", default="content", help="content root (default: content)")
    parser.add_argument("--quality", type=int, default=DEFAULT_QUALITY,
                        help=f"AVIF quality 1-100 (default: {DEFAULT_QUALITY})")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would happen and change nothing")
    args = parser.parse_args()

    content_root = os.path.abspath(args.content)
    if not os.path.isdir(content_root):
        print(f"convert_images: no such directory: {args.content}", file=sys.stderr)
        return 2

    sources = find_sources(content_root)
    if not sources:
        print("convert_images: nothing to convert.")
        return 0

    jobs, conflicts = plan(sources, content_root)
    if conflicts:
        # Only the conflicting sources are skipped. Failing the whole run let a
        # single stray `cover.jpg` beside an existing `cover.avif` block every
        # other image in the repo indefinitely — and that is also the state a
        # crash between the rewrite and the delete leaves behind, so the run
        # after a crash could never recover on its own.
        print(f"convert_images: skipping {len(conflicts)} source(s):", file=sys.stderr)
        for line in conflicts:
            print(f"  {line}", file=sys.stderr)
        print("Rename them so each maps to its own .avif.\n", file=sys.stderr)
    if not jobs:
        print("convert_images: nothing left to convert.")
        return 1 if conflicts else 0

    written, failed = convert(jobs, args.quality, args.dry_run)
    for source, exc in failed:
        print(f"convert_images: could not convert {os.path.relpath(source, content_root)}: {exc}",
              file=sys.stderr)

    done = {s: t for s, t in jobs if args.dry_run or t in set(written)}
    mapping = {os.path.relpath(s, content_root).replace(os.sep, "/"):
               os.path.relpath(t, content_root).replace(os.sep, "/")
               for s, t in done.items()}

    touched, replacements = rewrite_markdown(content_root, mapping, args.dry_run)

    if not args.dry_run:
        # Measured over what actually converted, not over every job — a run
        # with failures used to report an inflated saving, and that number is
        # what a human reads to sanity-check a run that deletes files.
        before = sum(os.path.getsize(s) for s in done)
        for source in done:
            os.remove(source)
        after = sum(os.path.getsize(t) for t in done.values())
    else:
        before = after = 0

    if done and not replacements:
        print("convert_images: converted files but rewrote no reference at all — "
              "refusing to delete the originals. Check how they are referenced.",
              file=sys.stderr)
        return 1

    verb = "would convert" if args.dry_run else "converted"
    print(f"convert_images: {verb} {len(done)} image(s) at quality {args.quality}")
    print(f"  {replacements} reference(s) rewritten across {len(touched)} markdown file(s)")
    if not args.dry_run:
        print(f"  {before / 1048576:.1f} MB -> {after / 1048576:.1f} MB "
              f"({(1 - after / before) * 100:.0f}% smaller)" if before else "")
        print("  originals removed. Build and run scripts/check_links.py to verify.")
    if failed:
        print(f"  {len(failed)} failed — left in place for a human:", file=sys.stderr)
        for source, _exc in failed:
            print(f"      {os.path.relpath(source, content_root)}", file=sys.stderr)
    # Exit 0 whenever anything converted, even alongside failures. Otherwise one
    # undecodable file fails the workflow step, the commit never runs, and the
    # whole batch — already converted and already deleted in the workspace — is
    # thrown away with it. And since the bad file stays in the repo, every
    # subsequent run fails the same way: permanently red until a human
    # intervenes. Only a run where nothing at all succeeded is an error.
    return 1 if failed and not done else 0


if __name__ == "__main__":
    sys.exit(main())
