"""Validate a declared repository manifest without assuming full inventory.

The historical MANIFEST.json is a release-core inventory.  This checker keeps
that distinction explicit: declared files must match byte-for-byte, while
files outside the declaration are reported as PARTIAL_INVENTORY unless
``--strict`` is requested for a release snapshot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


def _relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("manifest paths must be non-empty POSIX strings")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe manifest path: {value!r}")
    return path.as_posix()


def _digest(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def validate_manifest(
    root: str | Path,
    manifest_path: str | Path = "MANIFEST.json",
    *,
    strict: bool = False,
) -> dict[str, Any]:
    """Return a machine-readable validation result.

    A malformed declaration, missing file, symlink, byte mismatch, duplicate
    path or unsafe path is a failure.  Unlisted files are a visible partial
    inventory signal and become a failure only in strict mode.
    """
    root_path = Path(root).resolve()
    manifest = Path(manifest_path)
    if not manifest.is_absolute():
        manifest = root_path / manifest
    manifest = manifest.resolve()
    result: dict[str, Any] = {
        "schema_version": "1",
        "status": "FAIL",
        "strict": strict,
        "manifest": str(manifest.relative_to(root_path)) if manifest.is_relative_to(root_path) else str(manifest),
        "declared_files": 0,
        "checked_files": 0,
        "unlisted_files": [],
        "errors": [],
    }
    if not manifest.is_relative_to(root_path) or not manifest.is_file():
        result["errors"].append("manifest file is missing or outside root")
        return result
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result["errors"].append(f"manifest unreadable: {exc}")
        return result
    if not isinstance(payload, dict) or not isinstance(payload.get("files"), list):
        result["errors"].append("manifest must be an object with a files list")
        return result

    declared: set[str] = set()
    for index, entry in enumerate(payload["files"]):
        if not isinstance(entry, dict):
            result["errors"].append(f"entry {index} is not an object")
            continue
        try:
            path_text = _relative_path(entry.get("path"))
        except ValueError as exc:
            result["errors"].append(str(exc))
            continue
        if path_text in declared:
            result["errors"].append(f"duplicate manifest path: {path_text}")
            continue
        declared.add(path_text)
        result["declared_files"] += 1
        candidate = (root_path / Path(*PurePosixPath(path_text).parts)).resolve()
        if not candidate.is_relative_to(root_path) or candidate.is_symlink() or not candidate.is_file():
            result["errors"].append(f"declared file missing, unsafe or not regular: {path_text}")
            continue
        expected_bytes = entry.get("bytes")
        expected_sha = entry.get("sha256")
        if not isinstance(expected_bytes, int) or expected_bytes < 0:
            result["errors"].append(f"invalid byte count: {path_text}")
            continue
        if not isinstance(expected_sha, str) or len(expected_sha) != 64:
            result["errors"].append(f"invalid sha256 declaration: {path_text}")
            continue
        actual_bytes, actual_sha = _digest(candidate)
        result["checked_files"] += 1
        if actual_bytes != expected_bytes:
            result["errors"].append(f"byte count mismatch: {path_text}")
        if actual_sha != expected_sha:
            result["errors"].append(f"sha256 mismatch: {path_text}")

    repo_files: set[str] = set()
    for candidate in root_path.rglob("*"):
        if not candidate.is_file() or any(part in {".git", "__pycache__", ".pytest_cache"} for part in candidate.relative_to(root_path).parts):
            continue
        rel = candidate.relative_to(root_path).as_posix()
        if rel == manifest.relative_to(root_path).as_posix():
            continue
        repo_files.add(rel)
    result["unlisted_files"] = sorted(repo_files - declared)
    if not result["errors"]:
        result["status"] = "FAIL" if strict and result["unlisted_files"] else (
            "PARTIAL_INVENTORY" if result["unlisted_files"] else "PASS"
        )
        if strict and result["unlisted_files"]:
            result["errors"].append("strict inventory contains unlisted files")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", type=Path, default=Path("MANIFEST.json"))
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate_manifest(args.root, args.manifest, strict=args.strict)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] in {"PASS", "PARTIAL_INVENTORY"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
