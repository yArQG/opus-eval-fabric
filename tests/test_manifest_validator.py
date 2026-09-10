from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_manifest import validate_manifest


class ManifestValidatorTests(unittest.TestCase):
    def _fixture(self, *, extra: bool = False) -> tuple[Path, Path]:
        root = Path(tempfile.mkdtemp(prefix="opus-manifest-"))
        payload = root / "payload.txt"
        payload.write_text("stable\n", encoding="utf-8")
        if extra:
            (root / "shadow.txt").write_text("unlisted\n", encoding="utf-8")
        data = payload.read_bytes()
        manifest = root / "MANIFEST.json"
        manifest.write_text(
            json.dumps({
                "schema_version": "0.2",
                "files": [{
                    "path": "payload.txt",
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }],
            }),
            encoding="utf-8",
        )
        return root, manifest

    def test_declared_entries_pass_and_unlisted_files_are_explicit(self):
        root, manifest = self._fixture(extra=True)
        result = validate_manifest(root, manifest)
        self.assertEqual(result["status"], "PARTIAL_INVENTORY")
        self.assertEqual(result["checked_files"], 1)
        self.assertEqual(result["unlisted_files"], ["shadow.txt"])

    def test_strict_mode_blocks_partial_inventory(self):
        root, manifest = self._fixture(extra=True)
        result = validate_manifest(root, manifest, strict=True)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["errors"])

    def test_digest_mismatch_fails_closed(self):
        root, manifest = self._fixture()
        (root / "payload.txt").write_text("tampered\n", encoding="utf-8")
        result = validate_manifest(root, manifest)
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("sha256 mismatch: payload.txt", result["errors"])

    def test_unsafe_path_fails_closed(self):
        root, manifest = self._fixture()
        manifest.write_text(json.dumps({"files": [{"path": "../outside", "bytes": 0, "sha256": "0" * 64}]}), encoding="utf-8")
        result = validate_manifest(root, manifest)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("unsafe manifest path" in item for item in result["errors"]))
