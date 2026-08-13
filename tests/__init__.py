"""Test suite for the Brnos Aires build.

Plain `unittest`, no third-party runner, so it costs the project no new
dependency and runs anywhere Python does:

    python -m unittest discover -s tests -v

Importing this package puts `plugins/` and `scripts/` on `sys.path`, because
that is how Pelican loads the plugins at build time (PLUGIN_PATHS) and how the
scripts are invoked (as files, not as a package).
"""
import logging
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The plugins warn loudly by design; without a configured handler Python's
# lastResort handler prints every WARNING to stderr and drowns the test output.
# Installing a root handler at CRITICAL swallows them — and unlike
# logging.disable(), which is a global kill switch checked before anything
# else, it leaves assertLogs() able to capture the very warnings some tests
# assert on.
logging.basicConfig(level=logging.CRITICAL)

for _directory in ("", "plugins", "scripts"):
    _path = os.path.join(REPO_ROOT, _directory)
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Imported by test modules purely for the side effect above; giving it a name
# makes that dependency explicit instead of relying on import order.
plugin_path = os.path.join(REPO_ROOT, "plugins")
script_path = os.path.join(REPO_ROOT, "scripts")

_BUILD = {}


def build_site():
    """Build the real site with publishconf.py into a private directory.

    Private, not the repo's `output/`: that one is whatever the last manual
    build left behind, and anything else running in the tree can be halfway
    through rewriting it. Built once per test session and reused.

    Returns the output path, or raises unittest.SkipTest if Pelican is not
    importable (so the pure-unit tests still run on a bare interpreter).
    """
    import subprocess
    import tempfile
    import unittest

    if "path" in _BUILD:
        return _BUILD["path"]
    try:
        import pelican  # noqa: F401
    except ImportError:
        raise unittest.SkipTest("pelican not installed")

    destination = tempfile.mkdtemp(prefix="brnosaires-build-")
    environment = dict(os.environ, PYTHONPATH=REPO_ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "pelican", "content",
         "-s", "publishconf.py", "-o", destination],
        cwd=REPO_ROOT, env=environment, capture_output=True, text=True)
    if result.returncode != 0:
        raise AssertionError("pelican build failed:\n"
                             + result.stdout[-4000:] + result.stderr[-4000:])
    _BUILD["path"] = destination
    _BUILD["log"] = result.stdout + result.stderr
    return destination


def build_log():
    build_site()
    return _BUILD["log"]
