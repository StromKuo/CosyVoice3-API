"""Patch wetext so frontend init is offline-first and never hard-fails on
ModelScope metadata APIs when a complete local cache exists.

- Uses modelscope's official local_files_only=True first
- Verifies the FSTs wetext actually needs exist on disk
- Falls back to the original online snapshot_download for fresh deployments
"""

import pathlib
import wetext

pkg_dir = pathlib.Path(wetext.__file__).resolve().parent
target = pkg_dir / "wetext.py"
s = target.read_text()

OLD = 'repo_dir = snapshot_download("pengzhendong/wetext")'
NEW = "repo_dir = _wetext_repo_dir()"

HELPER = '''

_WETEXT_REQUIRED = (
    "zh/tn/tagger.fst", "zh/tn/verbalizer.fst",
    "en/tn/tagger.fst", "en/tn/verbalizer.fst",
)


def _wetext_repo_dir():
    """Offline-first wetext resource dir; online download only as fallback."""
    import os
    try:
        d = snapshot_download("pengzhendong/wetext", local_files_only=True)
        if all(os.path.isfile(os.path.join(d, f)) for f in _WETEXT_REQUIRED):
            return d
    except Exception:
        pass
    return snapshot_download("pengzhendong/wetext")

'''

IMPORT_ANCHOR = "from modelscope import snapshot_download"

if OLD not in s:
    # diagnostic: show what the file actually contains around snapshot_download
    for i, line in enumerate(s.splitlines(), 1):
        if "snapshot_download" in line:
            print(f"  L{i}: {line!r}")
    raise SystemExit(f"pattern not found in {target} — wetext package changed upstream")

s = s.replace(OLD, NEW)
assert IMPORT_ANCHOR in s, "modelscope import anchor not found"
s = s.replace(IMPORT_ANCHOR, IMPORT_ANCHOR + "\n" + HELPER, 1)
target.write_text(s)
print(f"patched {target}: offline-first wetext resource loading")
