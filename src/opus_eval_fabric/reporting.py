from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def write_json_report(report: dict[str, Any], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def write_junit_report(report: dict[str, Any], path: str | Path) -> None:
    suite = ET.Element(
        "testsuite",
        {
            "name": report.get("suite_id", "opus-benchmark"),
            "tests": str(report["summary"]["total"]),
            "failures": str(report["summary"]["failed"]),
        },
    )
    for item in report["results"]:
        case = ET.SubElement(
            suite,
            "testcase",
            {"classname": item["case_id"], "name": item["variant_id"]},
        )
        if not item["matched"]:
            failure = ET.SubElement(case, "failure", {"message": "verdict mismatch"})
            failure.text = (
                f"expected={item['expected']} observed={item['observed']} "
                f"fingerprint={item['mission_sha256']}"
            )
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(suite).write(p, encoding="utf-8", xml_declaration=True)
