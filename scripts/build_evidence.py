"""Print body commitments and the canonical manifest used by seal_report."""

import hashlib
import json
import sys
from pathlib import Path


def main():
    root = Path(sys.argv[1])
    base_url = "https://raw.githubusercontent.com/OWNER/REPO/main/fixtures/" + root.name
    mapping = (("DIFF", "diff.json"), ("CHANGELOG", "changelog.json"), ("TREE", "tree.json"))
    evidence = []
    for kind, filename in mapping:
        body = (root / filename).read_bytes()
        digest = hashlib.sha256(body).hexdigest()
        evidence.append({"kind": kind, "sha256": digest, "url": f"{base_url}/{filename}"})
        print(f"{kind:9} {digest}  {filename}")
    manifest = {
        "base_commit": "0" * 64,
        "evidence": evidence,
        "report_key": "demo-poisoned-001",
        "target_commit": "1" * 64,
        "target_tree_sha256": "2" * 64,
    }
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    print("MANIFEST ", hashlib.sha256(canonical.encode()).hexdigest())
    print(canonical)


if __name__ == "__main__":
    main()

