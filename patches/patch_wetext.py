"""Patch wetext to prefer the local modelscope cache and skip all network calls
when the FST resources are already present (avoids ModelScope rate-limit 403s
that otherwise break frontend init even with a complete local cache)."""

import pathlib
import wetext

p = pathlib.Path(wetext.__file__)
s = p.read_text()

old = 'repo_dir = snapshot_download("pengzhendong/wetext")'
new = (
    'import os as _os; '
    '_local = _os.path.expanduser("~/.cache/modelscope/hub/pengzhendong/wetext"); '
    'repo_dir = _local if _os.path.exists(_os.path.join(_local, "zh", "tn", "tagger.fst")) '
    'else snapshot_download("pengzhendong/wetext")'
)

assert old in s, "wetext.py pattern not found — wetext package changed upstream"
p.write_text(s.replace(old, new))
print("patched wetext: local cache first, network only as fallback")
