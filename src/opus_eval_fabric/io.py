from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any
from .model import ActionPacket, EvidencePacket, MissionPacket, ModelPacket

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate_shape(data: dict[str, Any]) -> list[str]:
    errors=[]
    for k in ("mission","evidence","model","action"):
        if k not in data: errors.append(f"missing top-level field: {k}")
    if "evidence" in data:
        for k in ("source","provenance"):
            if k not in data["evidence"]: errors.append(f"missing evidence.{k}")
    if "model" in data and "claim" not in data["model"]: errors.append("missing model.claim")
    if "action" in data and "action" not in data["action"]: errors.append("missing action.action")
    return errors

def mission_from_dict(data: dict[str, Any]) -> MissionPacket:
    e,m,a=data["evidence"],data["model"],data["action"]
    return MissionPacket(
        mission=data["mission"],
        evidence=EvidencePacket(e["source"],e["provenance"],e.get("observed_at"),e.get("uncertainty","UNKNOWN"),e.get("content_hash")),
        model=ModelPacket(m["claim"],tuple(m.get("assumptions",[])),m.get("proof_obligation","empirical"),m.get("model_class","working_model")),
        action=ActionPacket(a["action"],a.get("authority","none"),a.get("side_effect","none"),a.get("rollback"),a.get("readback")),
        metadata=data.get("metadata",{}),
    )
